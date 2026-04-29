---
schema_version: "1.0"
date: "2026-04-29"
source_file: "examples/mobile-banking-app/sample-report/risk-scores.md"
target_path: "examples/mobile-banking-app/architecture.md"
classification: "security"
rescan_scope: "full"
carry_forward_count: null
---

# WellnessBank Mobile Banking Application — Compensating Controls Report

## 1. Executive Summary

**31** threats analyzed | **0** Control Found | **8** Partial Control | **23** No Control Found

**Coverage**: 0.0% Found | 25.8% Partial | 74.2% Missing

**Risk Reduction**: 199.8 inherent → 186.9 residual (**6.5%** reduction)

**Highest-Risk Unmitigated Finding**: E-1 — WellnessBankDebugActivity — Composite 8.5 (High)

> Note: The highest-risk finding with no control at all is E-1 (composite 8.5). S-5 (Critical, 9.3) has a partial control (basic auth session) that reduces residual to 7.0 (High). E-1 has zero compensating control and remains at full inherent risk.

| Metric | Value |
|--------|-------|
| Analysis date | 2026-04-29 |
| Source file | `examples/mobile-banking-app/sample-report/risk-scores.md` |
| Target codebase | `examples/mobile-banking-app/architecture.md` |
| Schema version | 1.0 |

> **Analysis scope note**: This analysis treats `architecture.md` as the canonical control surface because this is a synthesized example baseline with no real source code. Control detection is derived from the architecture's explicit declarations of present and absent controls. Declared controls (HTTPS/TLS in transit on three flows, basic auth/session flow, SharedPreferences MODE_PRIVATE isolation) are classified as Partial where they exist but are structurally insufficient; all 11 explicitly absent controls are classified as Missing. SOURCE_DATE_EPOCH=1700000000 per ADR-021.

**Coverage Distribution:**

| Status | Count | Percentage |
|--------|-------|------------|
| Control Found | 0 | 0.0% |
| Partial Control | 8 | 25.8% |
| No Control Found | 23 | 74.2% |
| **Total** | **31** | **100%** |

---

## 2. Coverage Matrix

Threats grouped by residual severity (Critical first, then High, Medium, Low). Within each group, threats are sorted by residual score descending.

### High Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| E-1 | — | WellnessBankDebugActivity | M8 Privilege-Gain: Exported Debug Activity Bypassing Auth Boundary | 8.5 | High | No Control Found | 8.5 | High |
| E-2 | — | MoneyTransferActivity | Unauthorized Money Transfer via Intent Hijacking and Privilege Escalation | 8.3 | High | No Control Found | 8.3 | High |
| T-3 | — | MoneyTransferActivity | Mobile IPC Input Validation (M4) — Intent Hijacking into Money Movement | 8.1 | High | No Control Found | 8.1 | High |
| T-4 | — | WellnessBank Android Client | Insufficient Mobile Binary Protections (M7) | 7.7 | High | No Control Found | 7.7 | High |
| I-4 | — | WellnessBank Android Client | Insufficient Mobile Cryptography (M10) | 7.5 | High | No Control Found | 7.5 | High |
| S-5 | — | Mobile Banking Customer | Long-Lived Session Token Replay | 9.3 | Critical | Partial Control | 7.0 | High |
| I-2 | — | WellnessBank Android Client | Inadequate Mobile Privacy Controls (M6) | 7.0 | High | No Control Found | 7.0 | High |
| I-7 | — | WellnessBankCredentialCache | Insecure Mobile Data Storage (M9) — Credential Cache | 7.0 | High | No Control Found | 7.0 | High |
| R-3 | — | Mobile Banking Customer | Deniable Financial Transactions | 7.0 | High | No Control Found | 7.0 | High |

### Medium Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| R-1 | — | WellnessBank Android Client | M8 Accountability-Loss: Mobile Audit Log Gaps | 6.9 | Medium | No Control Found | 6.9 | Medium |
| I-8 | — | WellnessBank Android Client | Debug Log PII Leakage via Logcat | 6.8 | Medium | No Control Found | 6.8 | Medium |
| S-3 | — | WellnessBank Android Client | Credential Theft via SharedPreferences Extraction | 6.8 | Medium | Partial Control | 5.1 | Medium |
| D-2 | — | WellnessBank Backend API | Missing Rate Limiting on Backend Transaction API | 6.2 | Medium | No Control Found | 6.2 | Medium |
| R-4 | — | WellnessBankDebugActivity | Unlogged Debug Activity Invocations | 6.1 | Medium | No Control Found | 6.1 | Medium |
| T-1 | — | WellnessAnalyticsSDK | Mobile Supply Chain Integrity (M2) — Analytics SDK | 6.1 | Medium | No Control Found | 6.1 | Medium |
| T-2 | — | WellnessPaySDK | Mobile Supply Chain Integrity (M2) — Payment SDK | 6.1 | Medium | No Control Found | 6.1 | Medium |
| I-3 | — | WellnessBankLocalDB | Insecure Mobile Data Storage (M9) — Local Database | 6.0 | Medium | No Control Found | 6.0 | Medium |
| T-6 | — | WellnessBankCredentialCache | Credential Cache Tampering via SharedPreferences Overwrite | 5.9 | Medium | No Control Found | 5.9 | Medium |
| S-2 | — | WellnessBank Android Client | Insecure Mobile Authentication/Authorization (M3) | 7.3 | High | Partial Control | 5.5 | Medium |
| T-5 | — | WellnessBankLocalDB | Unencrypted Local Database Tampering | 5.7 | Medium | No Control Found | 5.7 | Medium |
| E-3 | — | WellnessBank Backend API | Server-Side Authorization Gap for Debug-Initiated Operations | 5.6 | Medium | No Control Found | 5.6 | Medium |
| I-9 | — | WellnessBank Backend API | Backend API Verbose Error Response Exposure | 5.6 | Medium | No Control Found | 5.6 | Medium |
| R-2 | — | WellnessBank Backend API | Missing Backend Audit Trail on Transaction Operations | 5.6 | Medium | No Control Found | 5.6 | Medium |
| S-1 | — | WellnessBank Android Client | Improper Mobile Credential Usage (M1) | 7.0 | High | Partial Control | 5.3 | Medium |
| I-1 | — | WellnessBank Android Client | Insecure Mobile Communication (M5) — Client-to-Backend | 6.4 | Medium | Partial Control | 4.8 | Medium |
| D-4 | — | WellnessBankCredentialCache | Credential Store Corruption Leading to Denial of Service | 4.9 | Medium | No Control Found | 4.9 | Medium |
| D-1 | — | WellnessBank Android Client | Client-Side Resource Exhaustion via Unconstrained SDK I/O | 4.6 | Medium | No Control Found | 4.6 | Medium |
| I-6 | — | WellnessPaySDK | Insecure Mobile Communication (M5) — Payment SDK Egress | 5.8 | Medium | Partial Control | 4.4 | Medium |
| D-3 | — | WellnessBankLocalDB | Local Database Saturation | 4.3 | Medium | No Control Found | 4.3 | Medium |

### Low Residual Severity

| Threat ID | CF | Component | Threat | Inherent Score | Inherent Severity | Control Status | Residual Score | Residual Severity |
|-----------|----|-----------|--------|----------------|-------------------|----------------|----------------|-------------------|
| I-5 | — | WellnessAnalyticsSDK | Insecure Mobile Communication (M5) — Analytics SDK Egress | 4.9 | Medium | Partial Control | 3.7 | Low |
| S-4 | — | WellnessBank Backend API | Missing Token Binding on Backend Session | 4.8 | Medium | Partial Control | 3.6 | Low |

### Summary Statistics

| Residual Severity | Count | Percentage |
|-------------------|-------|------------|
| Critical | 0 | 0.0% |
| High | 9 | 29.0% |
| Medium | 20 | 64.5% |
| Low | 2 | 6.5% |
| **Total** | **31** | **100%** |

---

## 3. Control Details

Per-control evidence showing detected security controls with their location, architectural evidence, and threat coverage. Because the codebase target is `architecture.md` (a synthesized example with no real source files), evidence references the architecture document itself. Only Partial controls are listed here; no Control Found entries exist for this baseline.

### Encryption (Partial)

#### ENC-01 — HTTPS/TLS In-Transit on Client-to-Backend Flow

**Category**: Encryption | **Status**: Partial Control | **Effectiveness**: Moderate

**Detected in**: `examples/mobile-banking-app/architecture.md:42`

```text
MobileClient -->|"Transaction Request (HTTPS)"| BackendAPI
BackendAPI -->|"Transaction Response (HTTPS)"| MobileClient
```

> Architecture declares HTTPS on the primary client→backend transaction flow. TLS is present but certificate pinning is explicitly absent (Network Boundary section: "TLS established without certificate pinning configured on the client side"). This is a partial control: transport encryption exists but is vulnerable to MITM on rogue networks.

**Effectiveness Assessment**:

Detailed effectiveness assessment available in P1 (User Story 6).

**Threats Partially Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| I-1 | WellnessBank Android Client | Insecure Mobile Communication (M5) — Client-to-Backend | 6.4 | 0.25 | 4.8 |

---

#### ENC-02 — HTTPS/TLS on Analytics SDK Egress

**Category**: Encryption | **Status**: Partial Control | **Effectiveness**: Moderate

**Detected in**: `examples/mobile-banking-app/architecture.md:47`

```text
AnalyticsSDK -->|"Telemetry Payload (HTTPS)"| AnalyticsProvider
```

> Architecture declares HTTPS on the analytics egress flow. Certificate pinning absent on this flow. Partial encryption control.

**Threats Partially Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| I-5 | WellnessAnalyticsSDK | Insecure Mobile Communication (M5) — Analytics SDK Egress | 4.9 | 0.25 | 3.7 |

---

#### ENC-03 — HTTPS/TLS on Payment SDK Egress

**Category**: Encryption | **Status**: Partial Control | **Effectiveness**: Moderate

**Detected in**: `examples/mobile-banking-app/architecture.md:49`

```text
PaymentSDK -->|"Payment Authorization Request (HTTPS)"| PaymentProvider
PaymentProvider -->|"Payment Confirmation (HTTPS)"| PaymentSDK
```

> Architecture declares HTTPS on payment authorization and confirmation flows. Certificate pinning absent. Partial encryption control.

**Threats Partially Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| I-6 | WellnessPaySDK | Insecure Mobile Communication (M5) — Payment SDK Egress | 5.8 | 0.25 | 4.4 |

---

### Authentication (Partial)

#### AUTH-01 — Basic Authentication Flow with MODE_PRIVATE Storage

**Category**: Authentication | **Status**: Partial Control | **Effectiveness**: Moderate

**Detected in**: `examples/mobile-banking-app/architecture.md:37`

```text
EndUser -->|"Login Credentials (UI Input)"| MobileClient
MobileClient -->|"Persist Username + Auth Token"| CredentialCache
CredentialCache -->|"Restored Credentials on App Launch"| MobileClient
```

> Architecture declares a credential ingestion and session restoration flow. A basic authentication mechanism exists. However: no Android Keystore protection, no biometric step-up, no session TTL, no token rotation, and no EncryptedSharedPreferences. This is the minimum viable auth flow — structurally present but critically underprotected.

**Effectiveness Assessment**:

Detailed effectiveness assessment available in P1 (User Story 6).

**Threats Partially Mitigated by This Control**:

| Threat ID | Component | Threat | Inherent Score | Reduction Factor | Residual Score |
|-----------|-----------|--------|----------------|------------------|----------------|
| S-5 | Mobile Banking Customer | Long-Lived Session Token Replay | 9.3 | 0.25 | 7.0 |
| S-1 | WellnessBank Android Client | Improper Mobile Credential Usage (M1) | 7.0 | 0.25 | 5.3 |
| S-2 | WellnessBank Android Client | Insecure Mobile Authentication/Authorization (M3) | 7.3 | 0.25 | 5.5 |
| S-3 | WellnessBank Android Client | Credential Theft via SharedPreferences Extraction | 6.8 | 0.25 | 5.1 |
| S-4 | WellnessBank Backend API | Missing Token Binding on Backend Session | 4.8 | 0.25 | 3.6 |

---

## 4. Recommendations

Actionable recommendations for threats classified as "No Control Found" or "Partial Control," sorted by composite risk score descending (highest risk gaps first).

### Critical / High Risk Gaps

#### 1. E-1 — WellnessBankDebugActivity (Composite: 8.5, High)

**Current Status**: No Control Found

**What to Implement**: Remove or disable `WellnessBankDebugActivity` from the production release build using a ProGuard/R8 keep rule exclusion or build-variant manifest merging. In the release manifest, ensure `android:exported="false"` or remove the Activity declaration entirely. Add a `BuildConfig.DEBUG` runtime guard at the Activity's `onCreate` that immediately finishes the Activity and logs a security event when `BuildConfig.DEBUG == false`. Additionally implement Play Integrity API attestation at app startup so tampered APKs with debug Activities re-enabled cannot authenticate.

**Where to Implement**: `app/src/main/AndroidManifest.xml` (exported attribute), `app/src/release/res/` (release-variant manifest overlay), `WellnessBankDebugActivity.java/.kt` (runtime guard), `app/build.gradle` (release build type configuration).

**Reference Patterns**: Android `BuildConfig.DEBUG` runtime guard, Play Integrity API (`com.google.android.play:integrity`), ProGuard/R8 `-dontwarn` + build-variant manifest merge rules, Android Gradle `buildTypes { release { minifyEnabled true } }`.

**Effort Estimate**: Medium — build configuration change plus one-time Activity guard addition; Play Integrity integration is a new API call at app startup.

---

#### 2. E-2 — MoneyTransferActivity (Composite: 8.3, High)

**Current Status**: No Control Found

**What to Implement**: Add `android:exported="false"` to `MoneyTransferActivity` in the production manifest to prevent external apps from firing Intents. If cross-app Intent support is legitimately required, add `android:permission="com.wellnessbank.mobile.permission.MONEY_TRANSFER"` with `protectionLevel="signature"` so only apps signed with the WellnessBank certificate can invoke this Activity. Add per-Intent caller verification in `onNewIntent` and `onCreate` using `getCallingPackage()` and comparing against an allowlist of trusted package signatures. Implement Intent extras schema validation before passing any amount or recipient field into the money-movement flow.

**Where to Implement**: `app/src/main/AndroidManifest.xml` (exported + permission attributes), `MoneyTransferActivity.java/.kt` (caller verification + extras validation).

**Reference Patterns**: `android:exported="false"`, `android:permission` with `protectionLevel="signature"`, `Activity.getCallingPackage()`, Android `PendingIntent.getCreatorPackage()`, OWASP M4 Intent validation patterns.

**Effort Estimate**: Medium — manifest attribute change is trivial; caller verification and schema validation require new code in the Activity.

---

#### 3. T-3 — MoneyTransferActivity (Composite: 8.1, High)

**Current Status**: No Control Found

**What to Implement**: Implement Intent extras schema validation in `MoneyTransferActivity.onCreate` and `onNewIntent`. Validate all expected extras (recipient account number format, transfer amount range, currency code enum) before any value is used in the money-movement flow. Reject the Intent and finish the Activity if any extra fails validation. Add `android:permission` with signature protection level (see E-2) as a layered control. The input validation must be server-side duplicated at the Backend API — the client-side validation is defense-in-depth but the backend MUST independently validate all transaction parameters before executing a transfer.

**Where to Implement**: `MoneyTransferActivity.java/.kt` (client-side extras validation), `WellnessBank Backend API` transaction endpoint (server-side parameter validation).

**Reference Patterns**: Android `Bundle` type-safe accessors with explicit null/range checks, backend Joi/Zod/Pydantic schema for transaction parameters, OWASP M4 IPC input validation.

**Effort Estimate**: Medium — validation schema is new code but the pattern is straightforward; server-side duplicate is part of good practice and likely already partially present.

---

#### 4. T-4 — WellnessBank Android Client (Composite: 7.7, High)

**Current Status**: No Control Found

**What to Implement**: Enable ProGuard/R8 code obfuscation in the release build configuration (`minifyEnabled true`, `proguardFiles getDefaultProguardFile('proguard-android-optimize.txt')`) to raise the cost of static reverse engineering. Add root-detection logic at app startup and before security-critical operations (transaction confirmation, payment authorization) using a multi-signal detection approach: check for `su` binary presence, test-keys build tag, write access to `/system`, and Magisk manager package. Integrate Play Integrity API (or RootBeer as a lighter alternative) to block operation on compromised devices. Add basic debugger-attach detection with `android.os.Debug.isDebuggerConnected()` at sensitive flow entry points.

**Where to Implement**: `app/build.gradle` (ProGuard/R8 enablement), `app/proguard-rules.pro` (custom keep rules), main Application class `onCreate` (root/integrity check at startup), `TransactionConfirmationActivity.java/.kt` and `PaymentAuthorizationFlow.java/.kt` (per-operation integrity check).

**Reference Patterns**: Android Gradle `minifyEnabled true`, `com.scottyab:rootbeer` (root detection), Play Integrity API (`com.google.android.play:integrity`), `android.os.Debug.isDebuggerConnected()`, OWASP M7 binary protection patterns.

**Effort Estimate**: High — ProGuard enablement is low-effort but requires careful keep-rule tuning to prevent runtime crashes; root detection + Play Integrity integration is a new subsystem requiring testing across device variants.

---

#### 5. I-4 — WellnessBank Android Client (Composite: 7.5, High)

**Current Status**: No Control Found

**What to Implement**: Replace the custom 4-digit PIN PBKDF2 derivation with Android Keystore-backed AES-256-GCM key generation. The user's biometric or device PIN unlocks a hardware-backed key in the Keystore; no raw key material is ever exposed in the application process. If a PIN-based fallback is required, use PBKDF2-HMAC-SHA256 with at least 310,000 iterations (OWASP 2023 recommendation) and a cryptographically random 256-bit salt stored separately from the derived key material. Replace the credential cache encryption with EncryptedSharedPreferences backed by the Keystore master key.

**Where to Implement**: Credential persistence module (currently writing to `WellnessBankCredentialCache`), key derivation utility class, `EncryptedSharedPreferences` initialization in Application class.

**Reference Patterns**: Android `KeyStore` + `KeyGenParameterSpec` with `PURPOSE_ENCRYPT | PURPOSE_DECRYPT`, `androidx.security.crypto.EncryptedSharedPreferences`, `BiometricPrompt` with `CryptoObject`, PBKDF2 with 310,000+ iterations and random salt (OWASP CRS v4.0.1 §6.2.2).

**Effort Estimate**: High — this requires replacing the existing cryptographic design with a Keystore-backed architecture; all existing credential caches must be migrated on upgrade.

---

#### 6. S-5 — Mobile Banking Customer (Composite: 9.3, Critical)

**Current Status**: Partial Control (basic auth session flow exists)

**What to Implement**: Harden the existing authentication session flow by enforcing short session token TTLs (15–30 minutes for financial app sessions per PCI DSS guidance), implementing token rotation on each authenticated request, adding device-binding to session tokens using the Android Keystore attestation key, and enforcing biometric re-authentication before money-movement operations. The current flow persists a long-lived token in MODE_PRIVATE SharedPreferences — replace with EncryptedSharedPreferences backed by a Keystore key that requires biometric confirmation to decrypt. Add server-side session validation that checks token age, device fingerprint, and rejects replayed tokens.

**Where to Implement**: `WellnessBankCredentialCache` data layer (EncryptedSharedPreferences migration), session management module (TTL enforcement + rotation), `MoneyTransferActivity` and payment flow entry points (biometric re-auth gate), Backend API session validation middleware.

**Reference Patterns**: `androidx.security.crypto.EncryptedSharedPreferences`, `BiometricPrompt` with `CryptoObject`, JWT short-expiry with refresh token rotation, Android Keystore device attestation, OAuth 2.0 PKCE for mobile.

**Effort Estimate**: High — session architecture redesign affecting client, credential store, and backend session validation simultaneously.

---

#### 7. I-2 — WellnessBank Android Client (Composite: 7.0, High)

**Current Status**: No Control Found

**What to Implement**: Add `FLAG_SECURE` to all Activities that display financial data (account balances, transaction history, payment screens). This single-call addition prevents the Android system from including the Activity content in the recents thumbnail and blocks screen-recording apps from capturing financial data. Call `window.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)` in the `onCreate` of all financial-data Activities, or apply it globally from the Application class via an `ActivityLifecycleCallbacks` listener.

**Where to Implement**: All financial-data-displaying Activities (`AccountBalanceActivity`, `TransactionHistoryActivity`, `MoneyTransferActivity`, `PaymentActivity`) and any Fragment containing financial data. Alternatively, apply globally via `Application.registerActivityLifecycleCallbacks`.

**Reference Patterns**: `WindowManager.LayoutParams.FLAG_SECURE`, `Application.ActivityLifecycleCallbacks` for global enforcement, Android `View.setFilterTouchesWhenObscured(true)`.

**Effort Estimate**: Low — single flag addition; global enforcement via lifecycle callbacks is a minor architectural change.

---

#### 8. I-7 — WellnessBankCredentialCache (Composite: 7.0, High)

**Current Status**: No Control Found

**What to Implement**: Replace plain `SharedPreferences` (`MODE_PRIVATE`) with `EncryptedSharedPreferences` backed by an Android Keystore master key. The migration path: on first run after upgrade, read existing plaintext credentials, re-persist in encrypted form, and delete the plaintext file. All subsequent reads and writes use the encrypted API transparently. This addresses both I-7 (credential cache confidentiality) and contributes to S-1 and S-5 remediation.

**Where to Implement**: Credential cache initialization code (wherever `getSharedPreferences("credentials", MODE_PRIVATE)` is called), Application class upgrade migration block.

**Reference Patterns**: `androidx.security.crypto.EncryptedSharedPreferences`, `androidx.security.crypto.MasterKey` (Keystore-backed), Android Security Crypto library (`implementation "androidx.security:security-crypto:1.1.0-alpha06"`).

**Effort Estimate**: Low — direct API replacement; migration of existing data on upgrade adds one-time initialization code.

---

#### 9. R-3 — Mobile Banking Customer (Composite: 7.0, High)

**Current Status**: No Control Found

**What to Implement**: Implement transaction non-repudiation at the Backend API by generating an immutable, tamper-evident audit record for every money-movement event. Each record must include: authenticated user identity (sub from JWT), transaction timestamp (server-authoritative, not client-supplied), transaction parameters (amount, recipient, currency), originating session token fingerprint, and a server-side HMAC over the record using a key held in the backend's secret store. Store audit records in a separate append-only audit log table with no DELETE or UPDATE permissions granted to the API service account.

**Where to Implement**: Backend API transaction processing middleware (pre-execution audit entry), dedicated `AuditLog` database table with append-only permissions, secret management integration for the HMAC key.

**Reference Patterns**: Append-only audit log table with row-level security (PostgreSQL RLS, or a separate DB user with INSERT-only grants), HMAC-SHA256 over the transaction record, structured logging to immutable log sink (CloudWatch, Splunk, ELK with write-once policy), PSD2 Article 25 strong-authentication audit trail requirements.

**Effort Estimate**: High — new backend subsystem (audit log table, HMAC signing, append-only permission model) requiring schema migration and API layer changes.

---

### Medium Risk Gaps

#### 10. R-1 — WellnessBank Android Client (Composite: 6.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Replace all `Log.d("auth", ...)` statements that include username, token, or any PII with structured security event logging that routes to the Backend API audit trail. On the client, replace debug log calls with a no-op security event emitter in release builds (`BuildConfig.DEBUG` guard). Forward security-critical events (login success/failure, token refresh, permission denial, session expiry) to the backend audit log as part of the normal authenticated API flow.

**Where to Implement**: All locations containing `Log.d` / `Log.v` / `Log.i` calls with authentication material (search for `Log.d("auth"`, `Log.d("token"`, `Log.d("session"`), Backend API `/audit` endpoint for client event forwarding.

**Reference Patterns**: `BuildConfig.DEBUG` conditional logging, Android `Timber` library with release tree that discards debug logs, backend `/audit` event ingestion endpoint with authenticated POST.

**Effort Estimate**: Medium — requires finding and replacing all debug log calls with security event emitters; backend audit endpoint is new.

---

#### 11. I-8 — WellnessBank Android Client (Composite: 6.8, Medium)

**Current Status**: No Control Found

**What to Implement**: Remove all `Log.d` / `Log.v` calls that include credentials, tokens, usernames, or any PII from the production codebase. Apply a lint rule (`android.lint.disable` or a custom Lint check) that flags log calls with auth-adjacent strings as compile-time errors. In the release ProGuard configuration, add a rule to strip all `Log.d` and `Log.v` calls: `-assumenosideeffects class android.util.Log { public static *** d(...); public static *** v(...); }`.

**Where to Implement**: ProGuard/R8 configuration (`app/proguard-rules.pro`), all source files containing `Log.d("auth"`, `Log.d("token"`, `Log.d("user"` (direct removal), custom Lint check in `lint-checks` module.

**Reference Patterns**: ProGuard `-assumenosideeffects` for `Log.d/v` stripping, `Timber` library with `DebugTree` only in DEBUG builds, Android `StrictMode` for catching accidental PII logging in development.

**Effort Estimate**: Low — ProGuard rule addition is a single line; source cleanup is mechanical but requires comprehensive search.

---

#### 12. S-3 — WellnessBank Android Client (Composite: 6.8, Medium)

**Current Status**: Partial Control (MODE_PRIVATE isolation)

**What to Implement**: Harden the existing MODE_PRIVATE SharedPreferences by migrating to `EncryptedSharedPreferences` (see I-7 recommendation). Additionally, set `android:allowBackup="false"` in the application manifest to prevent ADB backup extraction of the credential file on pre-Android-12 devices. Disable Google Drive auto-backup for the SharedPreferences directory by adding a `backup_rules.xml` that excludes `shared_prefs/credentials.xml`.

**Where to Implement**: `app/src/main/AndroidManifest.xml` (`allowBackup` and `fullBackupContent` attributes), `app/src/main/res/xml/backup_rules.xml` (exclusion rules for credential SharedPreferences file).

**Reference Patterns**: `android:allowBackup="false"`, Android `BackupAgent` with selective exclusion, `EncryptedSharedPreferences` (addresses the underlying storage gap), OWASP M1 credential storage hardening.

**Effort Estimate**: Low — manifest attribute change and backup rules XML addition; underlying encryption migration covered by I-7.

---

#### 13. I-1 — WellnessBank Android Client (Composite: 6.4, Medium)

**Current Status**: Partial Control (HTTPS declared but no certificate pinning)

**What to Implement**: Implement certificate pinning on the WellnessBank Backend API connection. Add a `network_security_config.xml` with a `<pin-set>` declaration for the backend's leaf certificate or intermediate CA public key hash. Define a backup pin for rotation purposes. Set `expiration` to align with the certificate renewal schedule. Update the `android:networkSecurityConfig` attribute in the manifest. Implement a pin rotation strategy: when backend certificates are rotated, publish updated Network Security Config via app update before the old pin expires.

**Where to Implement**: `app/src/main/res/xml/network_security_config.xml` (new file with pin-set), `app/src/main/AndroidManifest.xml` (`android:networkSecurityConfig` attribute on `<application>`).

**Reference Patterns**: Android Network Security Configuration (`network_security_config.xml`), `<pin-set expiration="YYYY-MM-DD"><pin digest="SHA-256">...</pin></pin-set>`, OkHttp `CertificatePinner` as a programmatic alternative, OWASP M5 certificate pinning implementation guide.

**Effort Estimate**: Medium — Network Security Config is declarative and straightforward; pin rotation operational process requires coordination with backend certificate management.

---

#### 14. D-2 — WellnessBank Backend API (Composite: 6.2, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement rate limiting on the Backend API transaction endpoints using a sliding-window rate limiter keyed on authenticated user ID. Configure separate limits for: read operations (balance/history queries), write operations (transfer initiation), and authentication attempts (login/token refresh). Add exponential backoff responses (HTTP 429 with `Retry-After` header) on limit breach. Implement global IP-based rate limiting at the API gateway or load balancer layer as a defense-in-depth measure against unauthenticated flooding.

**Where to Implement**: Backend API middleware layer (user-keyed rate limiting on `/transactions`, `/transfer`, `/pay` endpoints), API gateway or reverse proxy (IP-keyed global limiter), Redis or in-memory store for rate limit counters.

**Reference Patterns**: `express-rate-limit` with Redis store (`rate-limiter-flexible`), API gateway rate limiting (AWS API Gateway, Kong, nginx `limit_req_zone`), `429 Too Many Requests` with `Retry-After` header, PCI DSS v4.0 Requirement 6.4.1 (login rate limiting).

**Effort Estimate**: Medium — middleware addition with Redis integration; API gateway configuration is a low-effort operational change.

---

#### 15. R-4 — WellnessBankDebugActivity (Composite: 6.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Add structured security event logging to `WellnessBankDebugActivity` capturing every invocation: timestamp, calling package (via `getCallingPackage()`), action name, and extras summary. Forward these events to the Backend API audit log. This is a defense-in-depth measure; the primary remediation for E-1 (Activity removal) is the correct fix — logging should accompany, not replace, removal.

**Where to Implement**: `WellnessBankDebugActivity.java/.kt` `onCreate` and `onNewIntent`, Backend API audit ingestion endpoint.

**Reference Patterns**: Android `getCallingPackage()` for caller attribution, structured audit log POST to backend, `PackageManager.getPackageInfo` for caller signature verification.

**Effort Estimate**: Low — logging code addition; dependent on E-1 removal for full remediation.

---

#### 16. T-1 — WellnessAnalyticsSDK (Composite: 6.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement SDK supply chain integrity controls for the WellnessAnalyticsSDK. Pin the SDK dependency to an exact version with a cryptographic checksum verification in the Gradle dependency configuration. Add the SDK's published checksum (SHA-256) to `gradle.lockfile` or use Gradle dependency verification (`verification-metadata.xml`) to reject SDK artifacts with unexpected checksums. Establish an SDK update review process: before updating to a new SDK version, review the changelog and diff against the previous pinned checksum. Scope the SDK's manifest permissions to the minimum required.

**Where to Implement**: `app/build.gradle` (exact version pinning), `gradle/verification-metadata.xml` (checksum verification), `app/src/main/AndroidManifest.xml` (permission scoping review).

**Reference Patterns**: Gradle dependency verification (`./gradlew --write-verification-metadata sha256`), `gradle.lockfile` dependency locking, OWASP M2 supply chain integrity controls, Google Play SDK Index for verified SDK provenance.

**Effort Estimate**: Medium — Gradle verification setup requires one-time configuration; ongoing process for update review is an operational commitment.

---

#### 17. T-2 — WellnessPaySDK (Composite: 6.1, Medium)

**Current Status**: No Control Found

**What to Implement**: Apply the same supply chain integrity controls as T-1 to the WellnessPaySDK. Given the payment data sensitivity, apply additional scrutiny: verify the SDK publisher's PCI DSS compliance documentation, confirm the SDK is listed on the Google Play SDK Index with verified provenance, and implement a runtime attestation check that the loaded SDK binary matches the pinned checksum. Do not auto-update the payment SDK — require explicit engineering review for each version bump.

**Where to Implement**: `app/build.gradle` (version pinning for WellnessPaySDK), `gradle/verification-metadata.xml` (checksum), release checklist (SDK update review gate).

**Reference Patterns**: Gradle dependency verification, Google Play SDK Index verified provenance, PCI DSS v4.0 Requirement 6.3 (software supply chain security), `PackageManager` signature verification for runtime SDK integrity.

**Effort Estimate**: Medium — same as T-1; additional PCI DSS compliance verification is a process requirement.

---

#### 18. I-3 — WellnessBankLocalDB (Composite: 6.0, Medium)

**Current Status**: No Control Found

**What to Implement**: Replace the plain SQLite database (`WellnessBankLocalDB`) with SQLCipher for Android (`net.zetetic:android-database-sqlcipher`) to provide AES-256 encryption of the entire database file at rest. Generate the encryption key using Android Keystore and unlock it via biometric authentication. Additionally, set `android:allowBackup="false"` or add a `backup_rules.xml` excluding the database file to prevent Google Drive backup of the unencrypted database. Implement a maximum retention policy (e.g., purge transactions older than 90 days from local cache).

**Where to Implement**: Database initialization module (replace `SQLiteOpenHelper` with `SQLiteOpenHelper` from SQLCipher), Keystore key generation for the DB encryption key, `app/src/main/AndroidManifest.xml` (backup exclusion).

**Reference Patterns**: `net.zetetic:android-database-sqlcipher:4.5.4`, Android Keystore for SQLCipher key management, `android:allowBackup="false"`, OWASP M9 secure data storage patterns.

**Effort Estimate**: High — SQLCipher integration requires replacing all `android.database.sqlite` imports with SQLCipher equivalents and coordinating key management with the Keystore; existing data migration required.

---

#### 19. T-6 — WellnessBankCredentialCache (Composite: 5.9, Medium)

**Current Status**: No Control Found

**What to Implement**: Migrate from plain `SharedPreferences` to `EncryptedSharedPreferences` (see I-7 and S-3). Once encrypted, root-level file modification requires both root access AND knowledge of the Keystore-protected encryption key, significantly raising the bar for T-6's tampering scenario. Add integrity checking: on each credential load, verify a stored HMAC over the token value using a separate Keystore key to detect tampering.

**Where to Implement**: Credential cache data layer (shared with I-7 remediation), HMAC verification in the credential read path.

**Reference Patterns**: `EncryptedSharedPreferences` with Keystore master key, HMAC-SHA256 for integrity check over stored token, Android `KeyStore.getEntry("hmac-key")` for HMAC key retrieval.

**Effort Estimate**: Low — integral with the I-7/S-3 migration; HMAC addition is incremental.

---

#### 20. S-2 — WellnessBank Android Client (Composite: 7.3, High)

**Current Status**: Partial Control (basic auth flow exists)

**What to Implement**: Harden the existing authentication flow by adding biometric re-authentication before all money-movement operations (`MoneyTransferActivity`, payment flows). Implement per-session re-authentication for sensitive actions using `BiometricPrompt` with a `CryptoObject` backed by a Keystore key. Add token expiry enforcement on the client (check token age before each API call; force re-login if expired). Implement risk-based authentication triggers: flag transactions above a threshold amount or to new payees for additional challenge.

**Where to Implement**: `MoneyTransferActivity.java/.kt` (biometric gate before transfer submission), `PaymentAuthorizationFlow.java/.kt`, session management module (token age validation), Backend API (risk-based challenge response for flagged transactions).

**Reference Patterns**: `BiometricPrompt` with `CryptoObject`, Android `KeyguardManager.isKeyguardSecure()`, server-side risk scoring for transaction step-up, OAuth 2.0 `acr_values` for step-up authentication.

**Effort Estimate**: High — biometric integration with Keystore-backed CryptoObject across multiple Activities is a cross-cutting change; risk-based authentication requires backend scoring logic.

---

#### 21. T-5 — WellnessBankLocalDB (Composite: 5.7, Medium)

**Current Status**: No Control Found

**What to Implement**: SQLCipher encryption (see I-3) addresses both the confidentiality and integrity concerns for the local database. Additionally, set `android:allowBackup="false"` to prevent extraction of the database via Google Drive backup. As a defense-in-depth measure, implement application-level row-level integrity checks (store a HMAC over critical transaction record fields) to detect tampering even if the SQLCipher layer is bypassed.

**Where to Implement**: Database layer (shared with I-3 SQLCipher migration), transaction record schema (add `record_hmac` column), `app/src/main/AndroidManifest.xml` (allowBackup).

**Reference Patterns**: SQLCipher (see I-3), HMAC-SHA256 per-row integrity, `android:allowBackup="false"`, OWASP M9 integrity patterns.

**Effort Estimate**: High — integral with I-3 SQLCipher migration.

---

#### 22. E-3 — WellnessBank Backend API (Composite: 5.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement server-side request integrity validation at the Backend API that rejects requests originating from debug-Activity-initiated flows. Since the backend cannot directly inspect Android Activity provenance, the control must be architectural: issue short-lived, one-time-use request tokens bound to specific operations (transfer initiation, payment authorization) that are generated only after normal authenticated UI flows — not after debug Activity bypass. Consider Play Integrity API attestation tokens as a prerequisite for sensitive operations: the mobile client includes a fresh attestation token with each transaction request; the backend verifies it before processing.

**Where to Implement**: Backend API transaction authorization middleware (attestation verification), Mobile client (Play Integrity token acquisition before sensitive API calls), attestation verification service (backend).

**Reference Patterns**: Play Integrity API server-side verification (`https://playintegrity.googleapis.com/v1/{packageName}:decodeIntegrityToken`), one-time operation tokens (HMAC-bound nonces), OWASP Mobile Security Testing Guide §4.8 (app integrity).

**Effort Estimate**: High — Play Integrity backend integration is a new verification subsystem; one-time operation tokens require client + backend changes.

---

#### 23. I-9 — WellnessBank Backend API (Composite: 5.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Replace verbose error responses with generic client-facing error messages. Configure the Backend API error handler to return standardized error payloads (e.g., `{ "error": "BAD_REQUEST", "request_id": "uuid" }`) with no stack traces, field names, ORM details, or service internals. Log the full diagnostic information server-side (keyed by `request_id`) for internal debugging. Apply this to all error categories: validation errors, database errors, unexpected exceptions, and 404s.

**Where to Implement**: Backend API global error handler middleware, all controller catch blocks, logging framework configuration (separate diagnostic log sink from API response layer).

**Reference Patterns**: RFC 7807 Problem Details (`application/problem+json`), `express-async-errors` with centralized error handler, structured internal logging with `request_id` correlation, OWASP ASVS v4.0 §7.4 (error handling).

**Effort Estimate**: Medium — global error handler replacement; requires reviewing all existing error response paths to ensure no information leaks remain.

---

#### 24. R-2 — WellnessBank Backend API (Composite: 5.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement a Backend API audit trail for all transaction operations. Every state-changing operation (account read with PII, transfer initiation, transfer execution, payment authorization, balance inquiry) must generate an append-only audit log entry containing: authenticated user sub, operation type, resource identifier, request parameters (sanitized), outcome (success/failure), server timestamp, and source IP. Store audit logs in a write-only sink separate from the operational database (dedicated audit table with INSERT-only API service account, or external SIEM/log aggregation).

**Where to Implement**: Backend API audit logging middleware (applied to all state-changing routes), dedicated audit log database table or log aggregation pipeline, API service account permission scoping.

**Reference Patterns**: Append-only audit table with PostgreSQL RLS, structured logging middleware (`morgan` + `winston` with audit stream), PCI DSS v4.0 Requirement 10 (audit log requirements for cardholder data environments), SOC 2 logging controls.

**Effort Estimate**: High — new backend subsystem (audit log schema, middleware, write-only permissions, log retention policy).

---

#### 25. D-4 — WellnessBankCredentialCache (Composite: 4.9, Medium)

**Current Status**: No Control Found

**What to Implement**: The EncryptedSharedPreferences migration (I-7) raises the bar for T-6 tampering. For D-4 specifically, add defensive read-with-fallback logic in the credential cache: if the SharedPreferences file is unreadable, corrupt, or fails HMAC verification, initiate a graceful re-authentication prompt rather than a crash loop. Store a backup token refresh mechanism so the user is not permanently locked out if the credential cache is corrupted. Limit the blast radius of corruption to a re-login prompt.

**Where to Implement**: Credential cache read path (graceful fallback to re-login on corruption), token refresh logic.

**Reference Patterns**: Try-catch with fallback to re-authentication, `EncryptedSharedPreferences` (naturally handles decrypt failures), Android `onSharedPreferenceChangeListener` for corruption detection.

**Effort Estimate**: Low — defensive read logic; integral with I-7 migration.

---

#### 26. D-1 — WellnessBank Android Client (Composite: 4.6, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement SDK I/O budgets in the WellnessBank Android Client to constrain the network and battery resource consumption of embedded SDKs. Use `WorkManager` with quota constraints to schedule non-urgent SDK operations (analytics flushing, telemetry batching) rather than allowing real-time unbounded network calls. Set SDK initialization timeouts. Monitor battery impact via `BatteryManager` metrics in the Application health reporting.

**Where to Implement**: SDK initialization code in Application class, analytics flush scheduling (`WorkManager` job), payment SDK network call wrapper with timeout configuration.

**Reference Patterns**: Android `WorkManager` with `NetworkType.CONNECTED` + `RequiresBatteryNotLow()` constraints, `OkHttpClient.Builder().callTimeout(30, TimeUnit.SECONDS)`, Android `JobScheduler` for deferred SDK operations.

**Effort Estimate**: Medium — SDK wrapper refactoring to use WorkManager; timeout configuration is low-effort.

---

#### 27. I-6 — WellnessPaySDK (Composite: 5.8, Medium)

**Current Status**: Partial Control (HTTPS declared but no certificate pinning)

**What to Implement**: Extend certificate pinning to the WellnessPaySDK payment authorization flow (WellnessPaySDK → Third-Party Payment Provider). Since the SDK controls its own network client, the pinning must be implemented within the SDK or via an OkHttp `CertificatePinner` wrapper injected into the SDK's HTTP client at initialization. If the SDK does not expose a way to inject a custom HTTP client, configure Android's `network_security_config.xml` with a `<domain includeSubdomains="true">` entry for the payment provider's domain with the appropriate public key pin.

**Where to Implement**: `app/src/main/res/xml/network_security_config.xml` (domain-level pin for payment provider domain), SDK initialization code (OkHttp `CertificatePinner` injection if SDK exposes the interface).

**Reference Patterns**: Android Network Security Configuration `<pin-set>`, OkHttp `CertificatePinner.Builder().add("api.wellnesspay.example", "sha256/...")`, OWASP M5 payment SDK certificate pinning.

**Effort Estimate**: Medium — Network Security Config addition is declarative; SDK HTTP client injection depends on SDK API surface.

---

### Low Risk Gaps

#### 28. I-5 — WellnessAnalyticsSDK (Composite: 4.9, Medium)

**Current Status**: Partial Control (HTTPS declared but no certificate pinning)

**What to Implement**: Add a `<domain>` entry for the Third-Party Analytics Provider in `network_security_config.xml` with certificate pinning. Given that analytics data has lower sensitivity than payment or credential data, a single leaf certificate pin (with one backup pin) is sufficient. Coordinate with the analytics provider on their certificate rotation schedule.

**Where to Implement**: `app/src/main/res/xml/network_security_config.xml` (domain-level pin for analytics provider domain).

**Reference Patterns**: Android Network Security Configuration pin-set, OWASP M5 analytics SDK pinning.

**Effort Estimate**: Low — declarative XML addition; lowest priority given analytics data sensitivity.

---

#### 29. S-4 — WellnessBank Backend API (Composite: 4.8, Medium)

**Current Status**: Partial Control (HTTPS with basic session validation implied)

**What to Implement**: Implement device binding for Backend API session tokens. When a session token is issued at login, record the requesting device's identifier (derived from Play Integrity attestation or a stable device fingerprint) alongside the token. On each subsequent API call, verify the token's device binding against the request's device identifier. Tokens used from a different device (or without a valid attestation) are rejected. This prevents token replay from a stolen credential with no device presence.

**Where to Implement**: Backend API authentication middleware (token issuance: record device binding; token validation: verify device binding), device fingerprint derivation on the mobile client (Play Integrity token or `android.provider.Settings.Secure.ANDROID_ID`).

**Reference Patterns**: Play Integrity device integrity token bound to session JWT (`device_integrity` claim), server-side JWT `device_id` claim validation, FIDO2/WebAuthn device binding for high-assurance scenarios.

**Effort Estimate**: Medium — requires mobile client change (device identifier inclusion in auth requests) and backend change (device binding storage and validation).

---

#### 30. D-3 — WellnessBankLocalDB (Composite: 4.3, Medium)

**Current Status**: No Control Found

**What to Implement**: Implement a maximum row count or total size limit for the `WellnessBankLocalDB` cache. Configure a periodic background job (via `WorkManager`) to enforce retention policy: delete transaction records older than 90 days, keeping only the most recent N transactions. Add an initial capacity check at app startup to prevent the app from attempting to operate on an oversaturated database.

**Where to Implement**: Database maintenance module (retention policy enforcement), `WorkManager` periodic task scheduling in Application class.

**Reference Patterns**: `WorkManager` periodic job with `DELETE FROM transactions WHERE created_at < ?` SQL, Android `Room` database `@Query` with date filtering, `SQLiteDatabase.execSQL` for batch deletion.

**Effort Estimate**: Low — WorkManager job with a retention SQL query; straightforward implementation.

---

## 5. Residual Risk Summary

Comparison of inherent risk (before controls) to residual risk (after controls), showing the risk reduction achieved by existing partial controls.

### Aggregate Risk Reduction

| Metric | Value |
|--------|-------|
| Total Inherent Risk Score | 199.8 |
| Total Residual Risk Score | 186.9 |
| Delta | 12.9 |
| Overall Reduction | 6.5% |

### Per-Severity-Band Shift

Breakdown of how threats shifted between severity bands after residual risk calculation.

| Shift | Count | Examples |
|-------|-------|---------|
| Critical → High | 1 | S-5 (9.3→7.0) |
| Critical → Medium | 0 | — |
| Critical → Low | 0 | — |
| High → Medium | 2 | S-2 (7.3→5.5), S-1 (7.0→5.3) |
| High → Low | 0 | — |
| Medium → Low | 2 | I-5 (4.9→3.7), S-4 (4.8→3.6) |
| No Shift | 26 | E-1, E-2, T-3, T-4, I-4, I-2, I-7, R-3, R-1, I-8, S-3, I-1, D-2, R-4, T-1, T-2, I-3, T-6, T-5, E-3, I-9, R-2, D-4, D-1, I-6, D-3 |
| **Total** | **31** | |

### Severity Distribution Comparison

| Severity | Inherent Count | Residual Count | Change |
|----------|----------------|----------------|--------|
| Critical | 1 | 0 | −1 |
| High | 11 | 9 | −2 |
| Medium | 19 | 20 | +1 |
| Low | 0 | 2 | +2 |
| **Total** | **31** | **31** | |

### Reduction Factor Reference

| Control Status | Reduction Factor | Formula | Description |
|----------------|------------------|---------|-------------|
| Control Found | 0.50 | Inherent × 0.50 | Control detected with evidence. Residual is 50% of inherent. |
| Partial Control | 0.25 | Inherent × 0.75 | Control exists but incomplete coverage. Residual is 75% of inherent. |
| No Control Found | 0.00 | Inherent × 1.00 | No matching control detected. Residual equals inherent. |

> P1 enhancement: When control effectiveness assessment (User Story 6) is active, reduction factors upgrade from the 3-level binary model above to a 7-level effectiveness-aware model. See spec FR-011 and User Story 6 for the extended factor table.

---

## 6. Methodology

This section documents the compensating controls analysis methodology used to produce this report.

### 6.1 Control Detection

The analysis scans the target codebase for security controls across 8 categories:

| Category | What It Detects | STRIDE Mapping |
|----------|-----------------|----------------|
| **Authentication** | Login mechanisms, token validation, session management, identity verification | Spoofing |
| **Access Control** | Role checks, permission guards, authorization middleware, RBAC/ABAC patterns | Spoofing, Elevation of Privilege |
| **Input Validation** | Schema validation, sanitization, parameterized queries, type checking | Tampering |
| **Encryption** | TLS configuration, data-at-rest encryption, hashing algorithms, key management | Information Disclosure |
| **Rate Limiting** | Request throttling, circuit breakers, backpressure, quota enforcement | Denial of Service |
| **Logging/Audit** | Structured logging, audit trails, immutable logs, event tracking | Repudiation |
| **CSRF Protection** | Anti-CSRF tokens, SameSite cookies, origin validation | Tampering |
| **CSP/Security Headers** | Content-Security-Policy, HSTS, X-Frame-Options, security header middleware | Information Disclosure |

### 6.2 Classification Logic

Each scored threat receives exactly one classification based on detected controls:

| Classification | Criteria | Reduction Factor |
|----------------|----------|------------------|
| **Control Found** | A matching control is detected with file:line evidence that addresses the threat's attack vector | 0.50 |
| **Partial Control** | A control exists but does not cover all paths, vectors, or components targeted by the threat | 0.25 |
| **No Control Found** | No matching control detected in the target codebase for this threat | 0.00 |

When multiple controls address the same threat, the highest single control effectiveness is used (not additive).

### 6.3 Residual Risk Calculation

Residual risk per threat is calculated as:

```
Residual Score = Inherent Score × (1 − Reduction Factor)
```

Residual scores are clamped to [0.0, 10.0] and mapped to severity bands using the same thresholds as risk scoring:

| Severity | Residual Score Range |
|----------|---------------------|
| **Critical** | >= 9.0 |
| **High** | 7.0 – 8.9 |
| **Medium** | 4.0 – 6.9 |
| **Low** | < 4.0 |

### 6.4 Data Sources

Analysis draws on the following inputs:

- **Scored threats**: Parsed from `risk-scores.md` (canonical). All original threat metadata (ID, component, category, description, composite score, severity band) is preserved.
- **Target codebase**: `examples/mobile-banking-app/architecture.md` — this synthesized example baseline uses the architecture document as the canonical control surface. Control evidence is derived from explicit declarations of present and absent controls in the Absent-Control Inventory, Mobile-Platform Topology Indicators, Trust Boundaries, and Expected Dispatch Behavior sections.
- **STRIDE-to-control mapping**: Canonical mapping from threat categories to control categories drives which controls are searched for each threat.
- **Present controls identified**: HTTPS/TLS on three network flows (partial encryption), basic authentication/session flow with MODE_PRIVATE SharedPreferences (partial authentication).
- **Absent controls confirmed**: Android Keystore, FLAG_SECURE, SQLCipher, root detection/Play Integrity, certificate pinning, SDK supply chain verification, ProGuard/R8, structured audit logging, per-Intent caller verification, backend rate limiting, biometric step-up/token re-auth.

### 6.5 Limitations

- Static analysis only — runtime control behavior is not evaluated
- Architecture-document-only scan — this baseline has no real source files; all control evidence is derived from architectural declarations
- Binary reduction factors (P0) approximate control impact; effectiveness-aware factors available in P1
- Partial control classifications for HTTPS-present-but-unpinned and auth-flow-present-but-underprotected reflect the architecture's explicit disclosure of these inadequacies; a real codebase scan would yield more granular evidence
- ADR-036 D-7 compliance: T1474/T1626/T1398 referenced in threat descriptions are prose-only references and are not surfaced as catalog entries in this output
