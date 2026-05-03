# Data Model: F-7 Mobile Top 10 Coverage Bundle

**Feature**: 237-mobile-top-10-coverage-bundle
**Date**: 2026-04-28
**Source**: Inline §System Design + §Phase 1 in [plan.md](./plan.md)

---

## Pattern Category Architectural Indicators

The 10 (single-host M8 path) or 11 (dual-host M8 path) new Pattern Categories enrich the existing detection-tier inventory at four-or-five-agent fan-out per Heuristic A signal-class consolidation. Each Pattern Category specifies ≥4 architectural-tell indicators that gate emission via the **mobile-platform topology gate** (FR-15 spec): findings emit only when the architecture additionally exhibits ≥4 mobile-platform structural indicators from a named set. Indicator details are documented inline in [plan.md §Phase 1 → Data Model](./plan.md) — the canonical source.

### Indicator Reference Summary

| Pattern Category | Host Agent | OWASP M-item | Severity Default | Indicator Count |
|------------------|-----------|--------------|------------------|-----------------|
| Cat N+1 — Improper Mobile Credential Usage | spoofing | M1 | HIGH | 6 |
| Cat N+2 — Insecure Mobile Authentication/Authorization | spoofing | M3 | MEDIUM-HIGH | 6 |
| Cat 11 — Mobile Supply Chain Integrity | tampering | M2 | HIGH | 7 |
| Cat 12 — Mobile IPC Input Validation | tampering | M4 | MEDIUM-HIGH | 7 (with disjoint-tells annotation referencing F-1 `output-integrity` per ADR-036 D-5) |
| Cat 13 — Insufficient Mobile Binary Protections | tampering | M7 | MEDIUM | 6 |
| Cat N+1 — Insecure Mobile Communication | info-disclosure | M5 | HIGH | 6 |
| Cat N+2 — Inadequate Mobile Privacy Controls | info-disclosure | M6 | MEDIUM | 6 |
| Cat N+3 — Insecure Mobile Data Storage | info-disclosure | M9 | HIGH | 6 |
| Cat N+4 — Insufficient Mobile Cryptography | info-disclosure | M10 | HIGH | 6 |
| M8 Cat — Mobile Misconfiguration: Privilege-Gain (dual-host) | privilege-escalation | M8 | HIGH | 6 |
| M8 Cat — Mobile Misconfiguration: Accountability-Loss (dual-host) | repudiation | M8 | MEDIUM | 6 |

**Aggregate**: 10 closure rows in single-host M8 path, 11 closure rows in dual-host M8 path (per Q1 plan-time decision: dual-host).

---

## Mobile-Platform Topology Gate

A finding from any of the 10-or-11 new Pattern Categories emits ONLY when the target architecture exhibits **≥4 of the following mobile-platform structural indicators**:

1. Declared mobile client component (Android or iOS Process)
2. Credential-handling component (SharedPreferences / NSUserDefaults / Keystore / Keychain mention)
3. Secure-storage data store (SQLite on device, Realm, Room, EncryptedSharedPreferences)
4. Mobile-backend API process the client communicates with (with or without certificate pinning declaration)
5. Third-party mobile SDK integration (analytics, payment, crash-reporting, advertising)
6. Exposed debug or admin endpoint (M8 surface)
7. Mobile permissions declaration (camera, location, contacts, etc.)
8. Package-name signal (com.example.app / com.bank.mobile)
9. ContentProvider / Activity export declaration

**Architectures lacking ≥4 of these indicators emit zero new findings** — preserving SC-13 byte-identity on the 6 non-mobile baselines.

---

## Catalog-Resolvability Map

Citations split between catalog-resolvable (appear in finding `references:` array) and prose-only (appear in `mitigation` narrative ONLY):

| Citation | Catalog-Resolvable? | Placement |
|----------|---------------------|-----------|
| OWASP M1:2024 — Improper Credential Usage | YES (owasp.yaml) | `references:` array |
| OWASP M2:2024 — Inadequate Supply Chain Security | YES | `references:` array |
| OWASP M3:2024 — Insecure Authentication/Authorization | YES | `references:` array |
| OWASP M4:2024 — Insufficient Input/Output Validation | YES | `references:` array |
| OWASP M5:2024 — Insecure Communication | YES | `references:` array |
| OWASP M6:2024 — Inadequate Privacy Controls | YES | `references:` array |
| OWASP M7:2024 — Insufficient Binary Protections | YES | `references:` array |
| OWASP M8:2024 — Security Misconfiguration | YES | `references:` array |
| OWASP M9:2024 — Insecure Data Storage | YES | `references:` array |
| OWASP M10:2024 — Insufficient Cryptography | YES | `references:` array |
| MITRE ATT&CK Mobile T1474 — Supply Chain Compromise | **NO** (mitre-attack.yaml zero hits) | `mitigation` prose only |
| MITRE ATT&CK Mobile T1626 — Abuse Elevation Control Mechanism | **NO** | `mitigation` prose only |
| MITRE ATT&CK Mobile T1398 — Boot or Logon Initialization Scripts | **NO** | `mitigation` prose only |
| MASTG sections (e.g., MASTG-AUTH, MASTG-NETWORK) | NO (no MASTG taxonomy YAML) | `mitigation` prose only at section-level granularity (Q4) |
| MASVS sections (e.g., MASVS-CRYPTO, MASVS-AUTH) | NO (no MASVS taxonomy YAML) | `mitigation` prose only at section-level granularity (Q4) |

**3-of-3 prose-only on MITRE ATT&CK Mobile** is the worst-case scale at any BLP-01 enrichment feature; mirrors F-5 1-of-1 (T1496 prose-only) + F-6 3-of-6 (ATLAS prose-only) precedent. ADR-036 D-7 codifies this rule per F-A2 referential-integrity contract.

---

## Disambiguation Boundaries

Pattern Category Disambiguation subsections (architect MEDIUM-2 plan-time RESOLVED 10-decision structure with discrete D-9):

| Companion | Disambiguation Subsection |
|-----------|---------------------------|
| spoofing | Cat 1–N (generic identity-spoofing) vs Cat N+1/N+2 (mobile-specific credential storage / mobile authentication) |
| tampering | Cat 1–9 (data-tampering / supply-chain / injection / etc.) vs Cat 10 (F-6 Adversarial Input Manipulation Predictive ML) vs Cat 11/12/13 (mobile-specific). **Cat 12 cross-link to F-1 `output-integrity` boundary explicitly named per ADR-036 D-5.** |
| info-disclosure | Cat 1–N (confidentiality-leakage) vs Cat N+1/N+2/N+3/N+4 (mobile-specific transport / privacy / storage / cryptography) |
| privilege-escalation (dual-host) | Cat 1–N (broken-access-control / IDOR / role-escalation) vs Cat N+1 (mobile-specific misconfiguration enabling privilege gain) |
| repudiation (dual-host) | Cat 1–N (missing-audit-trail / log-tampering) vs Cat N+1 (mobile-specific misconfiguration enabling accountability loss) |

**5 disambiguation subsections in dual-host path; 4 in single-host fallback.**

---

## Mutation-Target Architecture: `examples/mobile-banking-app/`

The new F-7 mutation target (Q2 plan-time RESOLVED) exhibits all 6 mobile-platform topology indicators required by spec FR-10:

1. Mobile client process (Android or iOS) handling user credentials
2. Credential-handling component using SharedPreferences/NSUserDefaults instead of platform-managed Keystore/Keychain
3. Secure-storage data store (encrypted or unencrypted SQLite on device)
4. Mobile-backend API process the client communicates with
5. Third-party mobile SDK integration (analytics, payment, crash reporting)
6. At least one exposed debug or admin endpoint demonstrating M8 surface

Authoring track per team-lead MEDIUM-1 plan-time RESOLVED:
- **Wave 0.0** (Tue 2026-04-28 PM, ~2-3 hr): Architect drafts skeleton (5 of 6 indicators).
- **Wave 0.1** (Wed 2026-04-29 AM-early, ~4-5 hr): Architect + senior-backend-engineer co-author full draft (~180-220 lines, 6 of 6 indicators).

**Excluded from `BASELINE_EXAMPLES` byte-identity loop** per Q6 plan-time decision (mirrors `agentic-app`, `consumer-agent-app`, `predictive-ml-app/` precedent).
