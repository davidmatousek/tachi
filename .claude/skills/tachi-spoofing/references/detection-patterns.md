---
name: spoofing-detection-patterns
description: Externalized detection pattern catalog for STRIDE spoofing — authentication bypass, credential theft, session hijacking, federated identity attacks
consumers: [tachi-spoofing]
last_updated: 2026-04-11
---

# Spoofing Detection Patterns

## Overview

Detection vocabulary for the STRIDE Spoofing threat category. Loaded at detection start by `tachi-spoofing` agent via a single `**MANDATORY**: Read` directive.

## Targeted DFD Element Types

- **External Entity**: Users, API clients, upstream services, third-party integrations, federated identity providers
- **Process**: Backend services, microservices, API gateways, authentication middleware, token issuers

## Authentication Bypass

- Missing or weak authentication on entry points (no MFA, password-only)
- Default or hard-coded credentials in service accounts
- Authentication decisions made client-side without server validation
- Missing mutual TLS between services in zero-trust boundaries

## Credential Theft and Replay

- Tokens transmitted over unencrypted channels (HTTP instead of HTTPS)
- Long-lived tokens without rotation or revocation mechanisms
- Credentials stored in plaintext or weakly hashed (MD5, SHA-1 without salt)
- Bearer tokens without audience or issuer validation

## Session Hijacking

- Session identifiers predictable or sequentially generated
- Session tokens exposed in URLs, logs, or error messages
- Missing session binding to client fingerprint (IP, user-agent)
- No session invalidation on privilege changes (login, role change)

## Service Impersonation

- Missing service-to-service authentication in internal networks
- DNS spoofing enabling traffic redirection to attacker-controlled endpoints
- Unsigned or unverified webhooks and callbacks from external services
- Missing certificate pinning for critical upstream dependencies

## Federated Identity Attacks

- OAuth/OIDC misconfiguration (missing state parameter, open redirects)
- SAML assertion replay or signature bypass
- JWT signature algorithm confusion (accepting "none" or HS256 when RS256 expected)
- Missing issuer validation on identity tokens from external providers

## Pattern Category 6: OAuth/OIDC Token Replay and Audience Confusion

Federated identity flows (OAuth 2.0, OIDC, SAML) introduce token-replay and `aud` claim confusion attacks that basic credential patterns do not cover. This category detects architectures where access tokens, ID tokens, or assertions cross trust boundaries without declared replay protection or audience validation, enabling one service's token to be replayed against another service sharing the same issuer.

**Indicators**:

- Same access or ID token accepted by multiple distinct services from a shared issuer without per-audience `aud` claim enforcement
- `aud` claim not validated, or validated only by type (e.g., "any JWT") rather than by exact audience identifier
- Refresh tokens reused across sessions without rotation (no refresh-token-rotation declared)
- JWT `kid` header trusted without constraining the key set to a pinned JWKS endpoint (enables key confusion via attacker-controlled `kid`)
- Missing `exp` enforcement or clock-skew tolerance wider than 5 minutes
- Token material traverses a trust boundary without `jti`, `nonce`, or short TTL (no replay-window limit)
- Multi-tenant issuer serving distinct applications where tenant isolation relies on client-side claim filtering
- OAuth `state` parameter missing on authorization requests (enables CSRF on the OAuth callback)

**Primary source**:

- OWASP Top 10 2021 — A07: Identification and Authentication Failures: https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/
- CWE-287: Improper Authentication: https://cwe.mitre.org/data/definitions/287.html
- CWE-306: Missing Authentication for Critical Function: https://cwe.mitre.org/data/definitions/306.html
- CWE-345: Insufficient Verification of Data Authenticity: https://cwe.mitre.org/data/definitions/345.html

**Example**: An API gateway and a background worker share the same OIDC issuer for first-party tokens. The gateway validates `iss` and `exp` but not `aud`. An attacker intercepts an access token minted for the worker (via a server-side-request-forgery chain) and replays it against the gateway's admin endpoint. The gateway accepts it because issuer and expiry are valid — the audience mismatch is invisible. The attacker gains admin-equivalent access without stealing any credential.

**Mitigation**:

- Enforce exact `aud` claim match at every token-consuming service; reject tokens whose audience does not include the validating service's identifier
- Pin JWKS to a fixed URL and reject `kid` values not present in the current key set
- Rotate refresh tokens on every use; revoke the previous token immediately after exchange
- Require `jti` + short TTL (≤5 minutes) for all tokens crossing a trust boundary; maintain a per-service nonce cache to reject replays within the TTL window

## Pattern Category 7: Cloud IAM Role Assumption Chain Abuse

Agentic and microservice architectures increasingly rely on cross-account cloud role assumption (AWS `sts:AssumeRole`, GCP `iam.serviceAccounts.getAccessToken`, Azure Managed Identity). This category detects assume-role chains that enable lateral movement across account or project boundaries when trust policies are over-permissive, external IDs are missing, or instance metadata is reachable from attacker-controllable code.

**Indicators**:

- Assume-role chains longer than 2 hops (A assumes B assumes C assumes D) — exponentially harder to audit and contain
- Trust policy allows `sts:AssumeRole` from a principal pattern containing `*`, or from an entire account (`arn:aws:iam::111122223333:root`) without a `Condition` block
- External ID not required on cross-account role trust policies (confused-deputy protection missing)
- Cross-account role assumption permitted without MFA condition (`aws:MultiFactorAuthPresent`) on human-initiated flows
- Service account or workload identity has `iam.serviceAccounts.getAccessToken` privilege over arbitrary other service accounts
- Instance metadata service (IMDSv1) reachable from application runtime — enables SSRF-to-credential-theft
- Session tokens from assumed roles stored in logs, error traces, or shared caches
- No `sts:SessionTags` or `sts:SourceIdentity` constraints on assumed sessions — loses attribution across the chain
- Role session duration exceeds 1 hour on high-privilege roles (AWS `MaxSessionDuration`)

**Primary source**:

- MITRE ATT&CK T1078.004 — Valid Accounts: Cloud Accounts: https://attack.mitre.org/techniques/T1078/004/
- MITRE ATT&CK T1550.001 — Use Alternate Authentication Material: Application Access Token: https://attack.mitre.org/techniques/T1550/001/
- AWS IAM Security Best Practices — Confused Deputy Problem: https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html
- AWS IMDSv2 — Configuring the Instance Metadata Service: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- GCP IAM — Service Account Impersonation: https://cloud.google.com/iam/docs/service-account-impersonation
- GCP Compute — Metadata Server Overview: https://cloud.google.com/compute/docs/metadata/overview
- Azure Active Directory — Managed Identities for Azure Resources: https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview
- Azure Virtual Machines — Instance Metadata Service: https://learn.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service

**Example**: A CI/CD runner in account A assumes a deployment role in account B. The trust policy on account B's role permits `arn:aws:iam::A:root` without an external ID or source-identity condition. An unrelated workload in account A (a Lambda function processing public webhook input) is compromised via SSRF. The attacker uses the Lambda's execution role to call `sts:AssumeRole` against account B's deployment role — the trust policy grants it, because "anything in account A" is trusted. The attacker now has deployment-level access to account B's production resources without ever compromising the CI/CD runner.

**Mitigation**:

- Require unique external IDs on every cross-account trust policy; rotate the external ID when the trusting relationship changes
- Add `aws:SourceIdentity`, `aws:PrincipalTag`, or `aws:SourceVpce` conditions to narrow which caller in the trusted account can actually assume the role
- Block IMDSv1 (require IMDSv2 with hop-limit 1) on all EC2 instances and container runtimes; enforce via service control policy
- Limit assume-role chains to 2 hops maximum; audit chains via CloudTrail `AssumeRole` events with a session-identity correlation query

## Pattern Category N+1 — Improper Mobile Credential Usage (M1)

OWASP M1:2024 (Improper Credential Usage) names mobile-specific credential storage and credential lifecycle misuse as a distinct attack class from generic web/API credential theft (Pattern Categories 1–7). Where the pre-existing categories cover cross-service authentication bypass, web-tier credential theft, federated token replay, and cloud IAM role abuse, this category targets the **specific architectural-tell** of credentials persisted on a mobile device outside platform-managed secure storage (Android Keystore, iOS Keychain) or hardcoded in shipped mobile binaries. The attacker's goal is offline credential extraction from a lost or rooted/jailbroken device, or from app-bundled secrets recovered via reverse engineering. MASTG-AUTH and MASVS-CRYPTO describe the platform-managed-secure-storage and credential-lifecycle requirements at section-level granularity.

**Indicators**:

- Mobile client component declared (Android application package or iOS bundle ID; React Native / Flutter / Cordova hybrid framework) — primary mobile-platform topology indicator
- Credentials persisted in Android `SharedPreferences` (especially `MODE_PRIVATE` rather than `EncryptedSharedPreferences`), iOS `NSUserDefaults`, plaintext SQLite, or app-bundled configuration files
- No platform-managed Keystore (Android `AndroidKeyStore` provider) or iOS Keychain reference declared in credential-handling code paths
- Hardcoded API keys, tokens, or shared secrets embedded in mobile binaries (Android `strings.xml`, iOS `Info.plist`, embedded constants in compiled bytecode/binary)
- No biometric-bound key release for sensitive operations (Android `BiometricPrompt` + StrongBox-bound key, iOS Touch ID / Face ID + Secure Enclave–bound key)
- No credential rotation policy and no refresh-token rotation on each refresh — long-lived credentials persisted indefinitely on the device

**Primary source**:

- OWASP M1:2024 — Improper Credential Usage: https://owasp.org/www-project-mobile-top-10/2023-risks/m1-improper-credential-usage
- OWASP MASTG-AUTH — Mobile Application Security Testing Guide, Authentication Test Cases (section-level granularity)
- OWASP MASVS-CRYPTO — Mobile Application Security Verification Standard, Cryptography Requirements (section-level granularity)

**Example**: A mobile-banking Android app persists its session token and OAuth refresh token in `SharedPreferences` with `MODE_PRIVATE`, rather than `EncryptedSharedPreferences` from the Android Jetpack Security library. On iOS, the equivalent app stores the OAuth refresh token in `NSUserDefaults` rather than the Keychain with `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`. An attacker recovers a lost device that was never wiped, dumps the app's data partition (rooted Android) or extracts the iOS backup, and obtains valid long-lived refresh tokens that authenticate against the production banking API. The attacker uses the tokens to drain accounts before the victim notices the device is missing — no rotation, no biometric step-up, no platform-vault key release stood between the attacker and live banking sessions.

**Mitigation**:

- Persist credentials only via platform-managed secure storage: Android Keystore + `EncryptedSharedPreferences` (Jetpack Security); iOS Keychain with appropriate access-control protection class (`kSecAttrAccessibleWhenUnlockedThisDeviceOnly` or stricter)
- Bind sensitive-operation key release to biometric authentication (`BiometricPrompt.CryptoObject` on Android with StrongBox-backed keys; `LAContext` on iOS with Secure-Enclave-bound keys) so credentials cannot be recovered from a stolen device without a live user fingerprint or face match
- Rotate session and refresh tokens on each use; reject reuse of previously seen refresh tokens (refresh-token rotation with server-side revocation cache)
- Eliminate hardcoded API keys, tokens, and shared secrets from shipped mobile binaries; issue per-device credentials server-side at first launch and bind them to attestation (Play Integrity / DeviceCheck) where available
- Document the credential-lifecycle and storage choices in mobile threat-modeling artifacts (MASTG-AUTH / MASVS-CRYPTO section-level cross-reference)

## Pattern Category N+2 — Insecure Mobile Authentication / Authorization (M3)

OWASP M3:2024 (Insecure Authentication/Authorization) names mobile-specific authentication and authorization weaknesses as a distinct attack class from generic web/API authentication-bypass (Pattern Categories 1–7) and from mobile credential storage (Pattern Category N+1). Where N+1 covers where credentials live on the device, this category covers how the mobile session is established, refreshed, and elevated for high-risk operations. The attacker's goal is to bypass mobile-side authentication controls — defeating certificate pinning to MITM the production session, replaying refresh tokens against a different device, executing money-movement without biometric step-up, or trusting a client-side authorization decision that was never validated server-side. MASTG-AUTH and MASVS-AUTH describe the mobile authentication-step-up and authorization-enforcement requirements at section-level granularity.

**Indicators**:

- Mobile client component declared — primary mobile-platform topology indicator
- Bypassed certificate pinning, OR pinning enabled only on specific domains (e.g., production but not staging), OR no Network Security Config / `NSAppTransportSecurity` exception audit
- Broken or absent JWT validation on the mobile-backend session token — signature not verified, `exp` not checked, `alg=none` accepted, `kid` trusted without a pinned JWKS
- Weak refresh-token handling — no rotation on refresh, refresh tokens not bound to device fingerprint, no revocation on logout or on suspicious-device signals
- Missing step-up authentication on high-risk operations (money movement, account profile changes, KYC updates, password reset) — single-factor session token suffices for any operation
- Client-side authorization decisions not re-validated server-side — UI flows hide buttons but the underlying API endpoint accepts the operation from any authenticated client

**Primary source**:

- OWASP M3:2024 — Insecure Authentication/Authorization: https://owasp.org/www-project-mobile-top-10/2023-risks/m3-insecure-authentication-authorization
- OWASP MASTG-AUTH — Mobile Application Security Testing Guide, Authentication Test Cases (section-level granularity)
- OWASP MASVS-AUTH — Mobile Application Security Verification Standard, Authentication and Session Management (section-level granularity)

**Example**: A mobile-banking app ships with certificate pinning enabled only on `api.bank.example` (production) but not on `staging.api.bank.example`, leaving the staging endpoint reachable from production builds via a runtime flag. An attacker on a public Wi-Fi hotspot intercepts the staging endpoint's TLS session via a self-signed certificate; the production binary trusts it because no pin was configured for that host. Separately, the app's money-transfer flow accepts a session bearer token without re-prompting for biometric authentication at confirmation time — the user-experience team marked biometric step-up as "friction." The attacker, who already obtained a session cookie from the MITM, executes a money-movement transaction without the device's biometric vault ever being consulted.

**Mitigation**:

- Enforce server-side authorization on every endpoint — never trust client-side UI hiding to act as an authorization decision; every API call re-validates user role and operation eligibility
- Configure certificate pinning with backup-pin rotation across **all** environments (production, staging, sandbox); fail closed on pin mismatch, alert on rotation events; review the Network Security Config / `NSAppTransportSecurity` exception lists in CI
- Bind refresh tokens to device fingerprint (Android `getAndroidId` + Play Integrity attestation; iOS DeviceCheck) and rotate on every refresh; revoke refresh tokens server-side on logout, password change, or suspicious-device signals
- Require biometric step-up via `BiometricPrompt` (Android) / `LAContext` (iOS) on all high-risk operations: money movement, profile changes, KYC updates, password reset, new-device enrollment
- Document the mobile session-handling and step-up policy in mobile threat-modeling artifacts (MASTG-AUTH / MASVS-AUTH section-level cross-reference)

## Pattern Category Disambiguation

Pattern Categories N+1 (Improper Mobile Credential Usage / OWASP M1:2024) and N+2 (Insecure Mobile Authentication/Authorization / OWASP M3:2024) and the pre-existing Pattern Categories 1–N (generic identity/credential signal class — authentication bypass, credential theft and replay, session hijacking, service impersonation, federated identity, OAuth/OIDC token replay, cloud IAM role assumption chain abuse) share the OWASP A07:2021 / authentication-failure family at the OWASP framework level but address distinct architectural-tells and mitigation surfaces:

- **Pattern Categories 1–N** (Authentication Bypass, Credential Theft and Replay, Session Hijacking, Service Impersonation, Federated Identity Attacks, OAuth/OIDC Token Replay, Cloud IAM Role Assumption Chain Abuse — pre-existing) detect generic web/API authentication and authorization gaps at any HTTP/API surface or cross-account cloud surface. The architectural-tell is a generic API endpoint, federated identity flow, or cloud role-assumption chain — NOT a mobile-platform topology.
- **Pattern Category N+1** (Improper Mobile Credential Usage — F-7) detects mobile-specific credential storage and credential lifecycle misuse on Android / iOS / hybrid mobile clients. The architectural-tell is a declared mobile client component persisting credentials outside platform-managed secure storage (Keystore / Keychain) or hardcoding secrets in shipped mobile binaries.
- **Pattern Category N+2** (Insecure Mobile Authentication / Authorization — F-7) detects mobile-specific authentication and authorization weaknesses — bypassed certificate pinning, broken JWT validation, weak refresh-token handling, missing biometric step-up on high-risk operations, client-side authorization decisions not re-validated server-side. The architectural-tell is a declared mobile client component with mobile session-handling code paths.

The same architecture (e.g., a hybrid web+mobile system serving both browser users and a mobile app against a shared backend) may legitimately surface BOTH pre-existing Cat 1–N findings AND new Cat N+1 / Cat N+2 findings without duplication, because they target different architectural surfaces (web/API vs mobile-platform topology). They are not duplicates and MUST NOT be merged in `threat-report.md`. Architect formalizes this carve in ADR-036 Decision 9 (Pattern Category Disambiguation requirement on the F-7 spoofing companion).

## Primary Sources

- OWASP Top 10 2021 — A07: Identification and Authentication Failures
- OWASP API Security Top 10 2023 — API2: Broken Authentication
- OWASP Authentication Cheat Sheet
- OWASP Session Management Cheat Sheet
- CWE-287: Improper Authentication
- CWE-290: Authentication Bypass by Spoofing
- CWE-384: Session Fixation
- CWE-613: Insufficient Session Expiration
- MITRE ATT&CK T1078: Valid Accounts
- MITRE ATT&CK T1556: Modify Authentication Process
- MITRE ATT&CK T1550: Use Alternate Authentication Material
- NIST SP 800-63B: Digital Identity Guidelines — Authentication and Lifecycle Management
- OWASP Top 10 2021 A07 (canonical URL): https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/
- CWE-287 Improper Authentication (canonical URL): https://cwe.mitre.org/data/definitions/287.html
- CWE-306 Missing Authentication for Critical Function: https://cwe.mitre.org/data/definitions/306.html
- CWE-345 Insufficient Verification of Data Authenticity: https://cwe.mitre.org/data/definitions/345.html
- MITRE ATT&CK T1078.004 Valid Accounts: Cloud Accounts: https://attack.mitre.org/techniques/T1078/004/
- MITRE ATT&CK T1550.001 Application Access Token: https://attack.mitre.org/techniques/T1550/001/
- AWS IAM Confused Deputy Problem guidance: https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html
- AWS IMDSv2 Configuration: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html
- GCP IAM Service Account Impersonation: https://cloud.google.com/iam/docs/service-account-impersonation
- GCP Compute Metadata Server Overview: https://cloud.google.com/compute/docs/metadata/overview
- Azure Active Directory Managed Identities Overview: https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview
- Azure Virtual Machines Instance Metadata Service: https://learn.microsoft.com/en-us/azure/virtual-machines/windows/instance-metadata-service
- OWASP M1:2024 — Improper Credential Usage: https://owasp.org/www-project-mobile-top-10/2023-risks/m1-improper-credential-usage
- OWASP M3:2024 — Insecure Authentication/Authorization: https://owasp.org/www-project-mobile-top-10/2023-risks/m3-insecure-authentication-authorization
