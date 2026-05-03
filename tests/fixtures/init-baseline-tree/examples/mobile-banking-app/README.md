# `mobile-banking-app/` — F-7 (Feature 237) Mobile Top 10 Coverage Bundle Mutation Target

This directory holds the F-7 mutation target — a fictional mobile-banking application architecture (`architecture.md`) and its regenerated security-report baseline (`sample-report/security-report.pdf.baseline` after Wave 4 regeneration completes).

## Purpose

The architecture exhibits all six mobile-platform topology indicators required by FR-10 of the Feature 237 specification:

1. Mobile client process (Android or iOS) handling user credentials (Mobile Banking Client → Authentication Service)
2. Credential-handling component using SharedPreferences/NSUserDefaults instead of platform-managed Keystore/Keychain (Credential Cache reading/writing SharedPreferences)
3. Secure-storage data store (encrypted or unencrypted SQLite on device) (On-Device SQLite Store)
4. Mobile-backend API process (Mobile Backend API serving the mobile client)
5. Third-party mobile SDK integration (analytics, payment, crash reporting embedded in the mobile client)
6. At least one exposed debug or admin endpoint demonstrating M8 surface (Debug Endpoint reachable on the Mobile Backend API)

The architecture deliberately omits platform-managed key storage, certificate-pinning enforcement, biometric-binding for sensitive operations, jailbreak/root-detection, code-obfuscation, anti-tamper attestation, debug-endpoint stripping at release builds, SDK supply-chain integrity verification, and runtime-application-self-protection so that the F-7 detection pipeline emits the full ten-Pattern-Category Mobile Top 10:2024 surface (M1–M10) on a clean-slate baseline.

## Mutation Target Status

**Excluded from `tests/scripts/test_backward_compatibility.py` byte-identity loop** per Q6 plan-time RESOLVED + FR-10 (mirrors `examples/agentic-app/` F-3 + F-5 mutation-target precedent, `examples/consumer-agent-app/` F-4 mutation-target precedent, and `examples/predictive-ml-app/` F-6 mutation-target precedent). The baseline regenerated here intentionally changes when F-7 enrichment ships and again on any subsequent Mobile-Pattern-Category enrichment feature; therefore byte-identity stability against this baseline is not a backward-compatibility invariant.

See `docs/architecture/02_ADRs/ADR-021-byte-identical-baselines.md` for the byte-identity gate definition and `docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md` for F-7's specific mutation-target inclusion rationale and the canonical Mobile Top 10 sub-pattern → owning-agent mapping table.

The six non-mobile baselines that DO participate in the byte-identity loop are: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`. Those six baselines exhibit no mobile-platform topology indicators and therefore receive zero new Mobile-Pattern-Category findings from F-7 — preserving the byte-identity invariant under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.

## Regeneration

Regenerate the baseline end-to-end via the standard pipeline (run from the repository root):

```bash
cd examples/mobile-banking-app && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.threat-model && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.risk-score && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.compensating-controls && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.infographic all && \
  SOURCE_DATE_EPOCH=1700000000 /tachi.security-report
```

## Expected Findings

The expected emission (per SC-12) is at least ten new Mobile findings (≥11 if M8 splits across two host agents), with at least one finding per M1–M10. Distribution across STRIDE+AI prefix families:

- **≥2 new `S-{N}`** from `spoofing` (M1 Improper Credential Usage, M3 Insecure Authentication/Authorization)
- **≥3 new `T-{N}`** from `tampering` (M2 Inadequate Supply Chain Security, M4 Insufficient Input/Output Validation, M7 Insufficient Binary Protection)
- **≥4 new `I-{N}`** from `info-disclosure` (M5 Insecure Communication, M6 Inadequate Privacy Controls, M9 Insecure Data Storage, M10 Insufficient Cryptography)
- **≥1 (single-host) or ≥2 (dual-host) new `E-{N}` and/or `R-{N}`** from M8 Security Misconfiguration host(s) per the ADR-036 D-numbered split decision

Each new finding cites `OWASP M{N}:2024` primary in its `references:` array; section-level MASTG/MASVS cross-references appear in the mitigation narrative; MITRE ATT&CK Mobile entries (T1474, T1626, T1398) appear as prose-only in mitigation narratives (NOT in the structured `references` array, per the catalog-gap rule).

## Lineage

| Feature | Mutation Target | Purpose |
|---|---|---|
| F-3 (Feature 219) | `examples/agentic-app/` | OWASP ASI07:2026 tool-abuse enrichment (Cat 9 + Cat 10) |
| F-4 (Feature 224) | `examples/consumer-agent-app/` | OWASP ASI09:2026 human-trust-exploitation surface |
| F-5 (Feature 229) | `examples/agentic-app/` | OWASP LLM10:2025 unbounded-consumption enrichment (Cat 12-13 DoS + Cat 10-11 model-theft) |
| F-6 (Feature 232) | `examples/predictive-ml-app/` | OWASP ML Top 10:2023 coverage bundle (7 categories across 3 host agents) |
| **F-7 (Feature 237)** | **`examples/mobile-banking-app/`** | **OWASP Mobile Top 10:2024 coverage bundle (10 categories across four-or-five host agents) — BLP-01 Tier 2** |
</content>
</invoke>