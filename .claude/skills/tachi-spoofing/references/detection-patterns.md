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
