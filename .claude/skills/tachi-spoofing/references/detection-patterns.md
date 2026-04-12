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
