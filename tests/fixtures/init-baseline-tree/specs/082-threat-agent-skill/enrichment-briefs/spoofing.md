# Enrichment Brief — spoofing

**Agent type**: STRIDE
**Primary threat category**: Spoofing (Authentication / Identity)
**Created**: 2026-04-11
**Feature**: 082 — Threat Agent Skill References

## Candidate New Pattern Categories

### Category 1 — OAuth/OIDC Token Replay and Audience Confusion

- **Source**: OWASP Top 10 2021
- **Source citation**: `https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/`
- **Source item**: A07:2021 Identification and Authentication Failures; cross-references CWE-287 Improper Authentication and CWE-306 Missing Authentication for Critical Function
- **Why this category**: Current inline patterns focus on basic credential checks; modern federated identity flows (OAuth, OIDC, SAML) introduce token-replay and audience (`aud` claim) confusion attacks that inline patterns do not cover.
- **Proposed detection signal**:
  - DFD element authenticates via an external identity provider (OAuth/OIDC/SAML) without `aud` claim validation declared in the architecture
  - Token material (access token, ID token, assertion) traverses a trust boundary without declared replay-protection (nonce, jti, short TTL)
  - Multi-audience trust relationship where the same issuer serves distinct applications
- **False-positive risk**: Medium — many architectures under-document token validation details; pattern should flag for review rather than hard-fail
- **Taxonomy alignment**: STRIDE Spoofing; CWE-287, CWE-345 (Insufficient Verification of Data Authenticity)

### Category 2 — Cloud IAM Role Assumption Chain Abuse

- **Source**: MITRE ATT&CK v15+ (Enterprise)
- **Source citation**: `https://attack.mitre.org/techniques/T1078/004/`
- **Source item**: T1078.004 Valid Accounts: Cloud Accounts (also T1550.001 Application Access Token)
- **Why this category**: Agentic and microservice architectures increasingly assume cross-account cloud roles; abusable role-assumption chains (AWS `sts:AssumeRole`, GCP `iam.serviceAccounts.getAccessToken`, Azure Managed Identity) are not represented in current inline patterns.
- **Proposed detection signal**:
  - DFD element is a cloud workload that crosses AWS/GCP/Azure account or project boundaries via assumed role
  - Service account or workload identity has privilege to impersonate other service accounts
  - No declared external ID, condition key, or session tag scoping on role trust policy
- **False-positive risk**: Medium — legitimate multi-account designs use this pattern; flag for human review, not auto-reject
- **Taxonomy alignment**: STRIDE Spoofing; maps to ATT&CK TA0001 Initial Access and TA0004 Privilege Escalation tactics

### Category 3 — Session Fixation and Session Hijacking via Insufficient Binding

- **Source**: CWE Top 25 Most Dangerous Software Weaknesses 2024
- **Source citation**: `https://cwe.mitre.org/top25/archive/2024/2024_cwe_top25.html`
- **Source item**: CWE-384 Session Fixation; related CWE-613 Insufficient Session Expiration
- **Why this category**: Inline patterns do not cover session identifier rotation on privilege boundary crossings; a gap for applications that maintain long-lived sessions across privilege levels.
- **Proposed detection signal**:
  - Session identifier persists across authentication/re-authentication events without rotation
  - Session identifier is bound only to a single factor (e.g., cookie value) without channel binding (TLS token binding, IP constraint, or device fingerprint)
  - Architecture declares session storage crossing a trust boundary without integrity protection
- **False-positive risk**: Low — this is a clear anti-pattern when observed in architecture descriptions
- **Taxonomy alignment**: STRIDE Spoofing; CWE-384, CWE-613

## Source Verification Notes

- OWASP Top 10 2021 is stable; A07 renumbering from 2017's A02 is well-documented. URL is the canonical OWASP project URL.
- ATT&CK T1078.004 is the specific cloud-accounts sub-technique; general T1078 covers on-premises too. Both are valid citations; sub-technique is more precise.
- CWE-287 and CWE-306 both appear in CWE Top 25 2024 at ranks 14 and 15 respectively — verify exact ranks during Phase 3.2 extraction.
- Checked but NOT used: NIST SP 800-63B (Digital Identity Guidelines) — excellent content but serves as controls reference, not detection-signature source per approved set.
