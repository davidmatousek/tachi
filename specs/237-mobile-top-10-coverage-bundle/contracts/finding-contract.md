# Finding IR Contract: F-7 Mobile Top 10 Coverage Bundle

**Feature**: 237-mobile-top-10-coverage-bundle
**Date**: 2026-04-28
**Source**: Inline §System Design + §Phase 1 → Finding IR Contract in [plan.md](../plan.md)

---

## Purpose

Document the shape of new findings emitted by the F-7-enriched detection agents. **Note**: the canonical contract content is inlined in [plan.md](../plan.md) §Phase 1 → Finding IR Contract. This file holds the structural summary plus references-array invariants for use by the test fixture suite.

---

## Schema Conformance

All F-7 findings conform to `schemas/finding.yaml` v1.8 (unchanged; F-7 does not bump schema). Existing prefixes (`S`, `T`, `I`, `E`, `R`) used; `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"` regex covers all 5 prefix families F-7 emits into.

---

## Per-Category Contracts

### S-{N} (spoofing) — Cat N+1 (M1) and Cat N+2 (M3)

```yaml
id: "S-{N}"
category: "spoofing"
title: "{Cat N+1: Improper Mobile Credential Usage | Cat N+2: Insecure Mobile Authentication/Authorization}: {short_summary}"
severity: "medium" | "high"           # Cat N+1 default HIGH (banking/credentials); Cat N+2 default MEDIUM-HIGH
component: "{DFD External Entity | Process — mobile client | mobile-backend API}"
description: "{2-4 sentence threat narrative distinguishing mobile-specific credential storage / mobile session handling from generic web/API authentication-bypass}"
mitigation: "{platform-specific control mechanisms — Android Keystore + iOS Keychain, biometric step-up, certificate pinning with backup-pin rotation, server-side authorization enforcement. MASTG-AUTH / MASVS-AUTH cited at section-level granularity in prose}"
references:
  - "OWASP M1:2024 — Improper Credential Usage"   # REQUIRED on Cat N+1 findings
  - "OWASP M3:2024 — Insecure Authentication/Authorization"   # REQUIRED on Cat N+2 findings
```

### T-{N} (tampering) — Cat 11 (M2), Cat 12 (M4), Cat 13 (M7)

```yaml
id: "T-{N}"
category: "tampering"
title: "{Cat 11: Mobile Supply Chain Integrity | Cat 12: Mobile IPC Input Validation | Cat 13: Insufficient Mobile Binary Protections}: {short_summary}"
severity: "medium" | "high"
component: "{DFD Process | Data Store — mobile SDK / mobile client / mobile-backend API}"
description: "{2-4 sentence threat narrative; Cat 12 includes disjoint-tells annotation referencing F-1 `output-integrity` boundary per ADR-036 D-5}"
mitigation: "{control mechanisms — SDK signature verification, Intent component routing, ProGuard/R8 obfuscation, RASP. MASTG-ARCH/CODE/RESILIENCE / MASVS-PLATFORM/RESILIENCE in prose. T1474 prose-only (catalog-absent)}"
references:
  - "OWASP M2:2024 — Inadequate Supply Chain Security"   # Cat 11 REQUIRED
  - "OWASP M4:2024 — Insufficient Input/Output Validation"   # Cat 12 REQUIRED
  - "OWASP M7:2024 — Insufficient Binary Protections"   # Cat 13 REQUIRED
  # MITRE ATT&CK Mobile T1474 in mitigation prose only — NOT in references (catalog-absent per Q3 plan-time)
```

### I-{N} (info-disclosure) — Cat N+1 (M5), Cat N+2 (M6), Cat N+3 (M9), Cat N+4 (M10)

```yaml
id: "I-{N}"
category: "info-disclosure"
title: "{Cat N+1: Insecure Mobile Communication | Cat N+2: Inadequate Mobile Privacy Controls | Cat N+3: Insecure Mobile Data Storage | Cat N+4: Insufficient Mobile Cryptography}: {short_summary}"
severity: "medium" | "high"
component: "{DFD Process | Data Flow | Data Store — mobile client / mobile-backend API / device-local storage}"
description: "{2-4 sentence threat narrative}"
mitigation: "{control mechanisms — certificate pinning + TLS 1.3, FLAG_SECURE, SQLCipher, EncryptedSharedPreferences, AES-GCM. MASTG-NETWORK/PRIVACY/STORAGE/CRYPTO / MASVS-NETWORK/PRIVACY/STORAGE/CRYPTO in prose}"
references:
  - "OWASP M5:2024 — Insecure Communication"   # Cat N+1 REQUIRED
  - "OWASP M6:2024 — Inadequate Privacy Controls"   # Cat N+2 REQUIRED
  - "OWASP M9:2024 — Insecure Data Storage"   # Cat N+3 REQUIRED
  - "OWASP M10:2024 — Insufficient Cryptography"   # Cat N+4 REQUIRED
```

### E-{N} (privilege-escalation) — M8 Cat (privilege-gain variant, dual-host)

```yaml
id: "E-{N}"
category: "privilege-escalation"
title: "Mobile Security Misconfiguration — Privilege-Gain Variant: {short_summary}"
severity: "medium" | "high"           # default HIGH (privilege-gain implication)
component: "{DFD Process — mobile client | mobile-backend API}"
description: "{2-4 sentence threat narrative; references ADR-036 D-4 dual-host disjoint-tells boundary with repudiation Cat M8}"
mitigation: "{production-build flag stripping, ContentProvider/Activity export scoping with signature-level permissions, Play Integrity / DeviceCheck attestation, root-detection on security-critical UI. MASTG-PLATFORM / MASVS-PLATFORM in prose. T1626 prose-only (catalog-absent)}"
references:
  - "OWASP M8:2024 — Security Misconfiguration"   # REQUIRED
  # MITRE ATT&CK Mobile T1626 in mitigation prose only — NOT in references (catalog-absent per Q3)
```

### R-{N} (repudiation) — M8 Cat (accountability-loss variant, dual-host)

```yaml
id: "R-{N}"
category: "repudiation"
title: "Mobile Security Misconfiguration — Accountability-Loss Variant: {short_summary}"
severity: "medium" | "high"           # default MEDIUM (audit-loss implication)
component: "{DFD External Entity | Process — mobile client | mobile-backend audit pipeline}"
description: "{2-4 sentence threat narrative; references ADR-036 D-4 dual-host disjoint-tells boundary with privilege-escalation Cat M8}"
mitigation: "{structured audit logging, production-build log-statement stripping ProGuard/R8 rules, tamper-evident timestamping, crash-reporting with PII redaction. MASTG-PLATFORM / MASVS-PLATFORM in prose. T1398 prose-only (catalog-absent)}"
references:
  - "OWASP M8:2024 — Security Misconfiguration"   # REQUIRED
  # MITRE ATT&CK Mobile T1398 in mitigation prose only — NOT in references (catalog-absent per Q3)
```

---

## Mobile-Platform Topology Gate

Every finding from any of the 10-or-11 new Pattern Categories MUST emit only when the architecture exhibits ≥4 mobile-platform structural indicators. See [data-model.md](../data-model.md) §Mobile-Platform Topology Gate for the indicator set. **Architectures lacking ≥4 indicators emit zero new findings** — preserving SC-13 byte-identity on the 6 non-mobile baselines.

---

## Test Fixture Surface

10 fixture findings (single-host M8 path) or 11 (dual-host M8 path) live under `tests/scripts/fixtures/mobile_top_10_coverage_bundle/`:

- `valid_category_n_plus_1_spoofing_mobile_credential_finding.yaml` (S-{N} M1)
- `valid_category_n_plus_2_spoofing_mobile_authentication_finding.yaml` (S-{N} M3)
- `valid_category_11_tampering_mobile_supply_chain_finding.yaml` (T-{N} M2)
- `valid_category_12_tampering_mobile_ipc_finding.yaml` (T-{N} M4 with disjoint-tells annotation)
- `valid_category_13_tampering_mobile_binary_protections_finding.yaml` (T-{N} M7)
- `valid_category_n_plus_1_info_disclosure_mobile_communication_finding.yaml` (I-{N} M5)
- `valid_category_n_plus_2_info_disclosure_mobile_privacy_finding.yaml` (I-{N} M6)
- `valid_category_n_plus_3_info_disclosure_mobile_data_storage_finding.yaml` (I-{N} M9)
- `valid_category_n_plus_4_info_disclosure_mobile_cryptography_finding.yaml` (I-{N} M10)
- `valid_category_n_plus_1_privilege_escalation_mobile_misconfig_priv_gain_finding.yaml` (E-{N} M8 privilege-gain — dual-host only)
- `valid_category_n_plus_1_repudiation_mobile_misconfig_accountability_loss_finding.yaml` (R-{N} M8 accountability-loss — dual-host only)

`tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py` validates each fixture against this contract.
