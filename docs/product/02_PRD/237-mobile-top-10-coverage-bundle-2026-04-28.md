---
prd:
  number: 237
  topic: mobile-top-10-coverage-bundle
  created: 2026-04-28
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-28, status: APPROVED, notes: "Draft v2 absorbs architect MEDIUM-1 (SC-16 inverted dual/single-host labels corrected — single-host = 20 of 28 zero-edit, dual-host = 18 of 28 zero-edit) and architect MEDIUM-3 (F-6 issue #232 closed via gh issue close 232 to resolve dependency-graph hygiene). Architect MEDIUM-2 (ADR-036 D-numbered Pattern Category Disambiguation decision — 9-decision vs 10-decision structure) and team-lead MEDIUM-1/2 (plan-day overload mitigation via parallel mobile-banking-app authoring track + Day 2 AM throughput task split FR-6 → 4 sub-tasks) are deferred to plan-day spec.md / plan.md / tasks.md authoring per architect's explicit guidance ('plan-day adjudication' + 'plan stage should explicitly schedule mobile-banking-app authoring as a dedicated 6-8 hour parallel track'). LOW-1/2/3/4 cosmetic. Q1 (M8 split: dual-host default), Q2 (mobile-banking-app archetype), Q3 (MITRE ATT&CK Mobile catalog gap analysis), Q4 (MASTG/MASVS granularity = section-level default), Q5 (ADR-036 mapping table severity-hint column = yes per ADR-034/035 precedent), Q6 (mobile-banking-app baseline strategy) all deferred to plan day. Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-04-28, status: APPROVED_WITH_CONCERNS, notes: "Counts: 0 BLOCKING / 0 HIGH / 3 MEDIUM / 4 LOW. Heuristic A four-or-five-agent protocol compliance FULL: schema_version 1.8 preserved, id.pattern regex unchanged, dispatch-rules.md zero functional edit, orchestrator.md zero functional edit, finding-format-shared.md consumers list zero edit. All ten PRD-stated baselines verified accurate via wc -l (51/55/54/52/50/146/221/192/213/148). M1–M10 entries verified present in schemas/taxonomy/owasp.yaml (10/10). Signal-class assignment correctness CONFIRMED for all M1–M10 → STRIDE host mappings. ADR-035 closing forward-scope marker forecast for F-7 four-or-five-agent execution VERIFIED in source. MEDIUM-1 (SC-16 inverted labels) absorbed in v2. MEDIUM-2 (ADR-036 decision-count alignment with ADR-035 D-9 Pattern Category Disambiguation) deferred to plan day — architect chooses 10-decision (mirrors ADR-035) or 9-decision (folds disambiguation into D-2) at plan day. MEDIUM-3 (F-6 issue #232 close-out hygiene) absorbed in v2 — issue closed at PRD time. LOW-1/2/3/4 informational only. MITRE ATT&CK Mobile catalog gap verified: 3 of 3 referenced techniques (T1474/T1626/T1398) are NOT in schemas/taxonomy/mitre-attack.yaml — plan-day prose-only fallback per F-5 T1496 + F-6 ATLAS-gap precedents. Full review: .aod/results/architect-prd-237.md."}
  techlead_signoff: {agent: team-lead, date: 2026-04-28, status: APPROVED_WITH_CONCERNS, notes: "Counts: 0 BLOCKING / 0 HIGH / 2 MEDIUM / 3 LOW. Calendar verified via cal 4 2026 + cal 5 2026 (Tue 04-28 / Wed 04-29 / Thu 04-30 / Fri 05-01 / Mon 05-04 / Tue 05-05 all match exactly). All 5 dependencies satisfied: F-A1 #180 CLOSED, F-A2 #189 CLOSED, F-3 #219 CLOSED, F-5 #229 CLOSED, F-6 #232 CLOSED at PRD time (substance was satisfied via PR #235 merge 17:03:28Z; closed via gh issue close 232 to resolve close-out hygiene). All 10 line-count baselines match file system state exactly. Sizing 3.0 days defensible: F-3 → F-5 → F-6 → F-7 trajectory of 1.0 → 1.5 → 2.5 → 3.0 working days; +0.5 day step for +1-or-2 agents and +3-or-4 categories aligns with prior step pattern. Buffer ratio 67% is highest in BLP-01 enrichment-branch history but calibrated against the largest scope expansion in BLP-01 (33-67% agent count growth + new mobile-banking-app authoring + 4th-execution emergent-risk possibility). Risk register 9 entries (8 technical + 1 business) at parity with F-6. R1 HIGH probability rating empirically grounded (zero-mobile-signal grep across existing examples). MEDIUM-1 (plan-day overload — architect-critical-path 12-14 hrs Wed; recommend parallel mobile-banking-app authoring track and skeleton draft on PRD day) deferred to plan-day tasks.md. MEDIUM-2 (Day 2 AM throughput asymmetry — info-disclosure 4 cats = +33% vs F-6 densest; recommend FR-6 task split into 4 sub-tasks for mid-morning checkpoint) deferred to plan-day tasks.md. LOW-1/2/3 (F-6 issue close lag absorbed at PRD time, buffer ratio trend caveat for Tier 3, ADR-036 length forecast 350-420 monitor) cosmetic. Verdict rationale: structurally sound, dependency-satisfied, calendar-verified, sizing-defensible feasibility document. Ready for /aod.plan. Full review: .aod/results/team-lead-prd-237.md."}
source:
  idea_id: 237
  story_id: null
---

# F-7 — Mobile Top 10 Coverage Bundle [Tier 2]: Product Requirements Document

**Status**: Draft v2 (revised post-architect-APPROVED_WITH_CONCERNS MEDIUM-1 + MEDIUM-3 + team-lead-APPROVED_WITH_CONCERNS)
**Created**: 2026-04-28
**Spec**: TBD (will land at `specs/237-mobile-top-10-coverage-bundle/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-01 Tier 2 — second Tier 2 feature (Mobile-platform-coverage bundle; follows F-6 ML closure delivered 2026-04-28 via Feature 232 issue #232 closed at this PRD's authoring)
**Priority**: P1

**Revision note (2026-04-28 v2)**: Addresses architect MEDIUM-1 (SC-16 inverted dual/single-host labels — corrected so single-host M8 path = 20 of 28 zero-edit invariant and dual-host M8 path = 18 of 28; arithmetic was always correct, only the labels were swapped); architect MEDIUM-3 (F-6 issue #232 close-out hygiene — issue closed at PRD time via `gh issue close 232` with PR #235 squash-merge commit `e325375` cited in the close comment, resolving the dependency-graph reading). Architect MEDIUM-2 (ADR-036 D-numbered Pattern Category Disambiguation decision — 9 vs 10 decisions; ADR-035 had 10) and team-lead MEDIUM-1/2 (plan-day overload mitigation — recommend dedicated parallel mobile-banking-app authoring track and PRD-day-end 2-3 hour skeleton drafting; Day 2 AM throughput asymmetry — recommend FR-6 task split into 4 sub-tasks for mid-morning checkpoint verification) are deferred to plan-day spec.md / plan.md / tasks.md authoring per architect's explicit guidance ("plan-day adjudication") and team-lead's explicit guidance ("Tasks document should split FR-6 into 4 sub-tasks"). LOW-1/2/3/4 cosmetic. Repository slug `237-mobile-top-10-coverage-bundle` preserved per `.claude/rules/git-workflow.md` `NNN-descriptive-name` convention.

---

## 📋 Executive Summary

### The One-Liner

Close ten gaps in tachi's mobile-platform detection coverage by enriching the existing `spoofing`, `tampering`, `info-disclosure`, and **at least one of** `privilege-escalation` / `repudiation` agents with **10–11 new Pattern Categories** drawn from OWASP Mobile Top 10:2024 — transitioning **all ten Mobile rows (M1–M10) from Planned → Covered** with **no new agent, no new skill directory, no schema bump, no orchestrator dispatch edits, no consumers-list edit**. F-7 is the **second Tier 2 feature** in the BLP-01 11-feature initiative and the **first BLP-01 enrichment feature scoped to four-or-five host agents simultaneously** — extending the Heuristic A enrichment branch from F-3's single-agent precedent (ASI07 / `tool-abuse`), F-5's two-agent precedent (LLM10 / `denial-of-service` + `model-theft`), and F-6's three-agent precedent (ML01/03/04/06/07/08 / `tampering` + `data-poisoning` + `model-theft`) to four-or-five-agent fan-out at the STRIDE-tier.

### Problem Statement

Post-F-6, tachi ships **14 detection agents** (12 original + `output-integrity` from F-1 + `misinformation` from F-2 + `human-trust-exploitation` from F-4; F-3, F-5, and F-6 enriched existing agents without adding files). Coverage of the three OWASP AI/ML frameworks now stands at **30 of 30 entries Covered** — the OWASP AI security framework family (LLM Top 10:2025 + Agentic Top 10:2026 + ML Top 10:2023) is fully closed by tachi's existing detection agents. **The remaining strategic gap is the OWASP Mobile Top 10:2024 framework**, which targets attacks against the mobile-client / mobile-backend lifecycle (device-local credential handling, platform keychains, certificate pinning, binary protections, mobile IPC, secure storage, and mobile-specific cryptography failures).

Per the BLP-01 Coverage Matrix in `_internal/strategy/BLP-01-threat-coverage.md` §6, **all ten Mobile Top 10 items currently sit at Planned status**: M1 Improper Credential Usage, M2 Inadequate Supply Chain Security, M3 Insecure Authentication/Authorization, M4 Insufficient Input/Output Validation, M5 Insecure Communication, M6 Inadequate Privacy Controls, M7 Insufficient Binary Protections, M8 Security Misconfiguration, M9 Insecure Data Storage, and M10 Insufficient Cryptography. None has any mobile-specific detection coverage in tachi today — empirical grep across `.claude/agents/tachi/*.md` and `.claude/skills/tachi-*/references/*.md` returns **zero matches** for "OWASP Mobile", "MASTG", or "MASVS" (PRD-time verification). **F-7 closes all ten Mobile Top 10 gaps in a single bundle.**

A security analyst threat-modeling a mobile-banking app, a mobile-IoT companion app, a mobile patient-records app, or a hybrid web/mobile commerce application today gets **zero signal from tachi** on mobile-specific threats. The `spoofing` agent flags generic identity-spoofing (Categories 1–N covering authentication-bypass, credential-stuffing on web/API surfaces) but does not name **mobile credential storage in cleartext on local device** (M1 — credentials in SharedPreferences / NSUserDefaults / unencrypted SQLite without Keychain or Keystore protection) or **mobile-specific authentication-bypass via insecure session handling** (M3 — bypassed certificate pinning, broken JWT validation in mobile clients, missing biometric step-up on sensitive operations). The `tampering` agent flags generic data-tampering and supply-chain integrity (Categories 1–9 cover deserialization, SDK-dependency tampering, injection attacks; F-6 added Cat 10 for predictive-ML adversarial input) but does not name **mobile SDK and app-store distribution integrity** (M2 — unsigned mobile SDK dependencies, sideloaded APKs, missing app-store provenance checks), **mobile IPC input validation** (M4 — Android Intent injection, iOS URL-scheme injection, deep-link parameter tampering, exposed Activity/Service receivers), or **insufficient binary protections** (M7 — missing root/jailbreak detection, missing anti-tampering stubs, missing code obfuscation on shipped binaries, debug symbols in production builds). The `info-disclosure` agent flags generic confidentiality leakage (Categories 1–N cover error-message exposure, excessive API responses, side-channel leakage) but does not name **mobile insecure communication** (M5 — cleartext HTTP, missing TLS pinning, downgrade attacks against mobile clients), **mobile inadequate privacy controls** (M6 — PII in device-local caches, telemetry collection without consent, clipboard exposure, screenshot leakage), **mobile insecure data storage** (M9 — unencrypted SQLite databases, unencrypted KeyValue stores, exposed iCloud/Google-Drive backups, exposed external SD-card writes), or **mobile insufficient cryptography** (M10 — weak key derivation on PINs, custom-rolled crypto, hardcoded crypto keys in binaries, insecure PRNG seeding). And no agent today names **mobile security misconfiguration** (M8 — exposed debug endpoints in production builds, default permissions, missing root-detection in security-critical features, missing app-attestation), which is the single Mobile Top 10 entry whose signal class straddles two STRIDE agents.

Per **Heuristic A (signal-class taxonomy)** in `GUIDE-threat-coverage-research §11`, the ten Mobile Top 10 items resolve onto **four existing signal classes** (one signal class per host agent except for M8 which fans across two), not a new class — making F-7 a **four-or-five-agent enrichment bundle** rather than a new-agent feature. M1 and M3 are same-class as `spoofing`'s identity/credential signal class. M2, M4, and M7 are same-class as `tampering`'s data-integrity / supply-chain signal class. M5, M6, M9, and M10 are same-class as `info-disclosure`'s confidentiality signal class. M8 (Security Misconfiguration) presents two architectural-tell variants: misconfiguration enabling privilege gain (e.g., exposed admin/debug interfaces in production, default permissive ContentProvider exports, missing app-attestation enabling tampered-binary execution) is same-class as `privilege-escalation`'s broken-access-control surface; misconfiguration disabling accountability (e.g., missing audit logging, disabled crash reporting, debug log leakage in production) is same-class as `repudiation`'s missing-audit-trail surface — final M8 split (single-host or dual-host) is recorded in ADR-036 at plan day after Heuristic A signal-class analysis on representative architectures. Authoring a new `mobile-platform` agent would fragment Mobile Top 10 findings across eleven locations (one new agent + four-or-five existing-agent adjacencies), violate Heuristic A consolidation, and inflate the operator-attention surface for analysts threat-modeling mixed web/mobile portfolios. SDR-001 Decision 4 locked the enrichment-branch rule for same-class scope; F-3 ADR-032 demonstrated single-agent execution; F-5 ADR-034 demonstrated two-agent execution; F-6 ADR-035 demonstrated three-agent execution and **explicitly forecast** (forward scope marker, ADR-035 closing matter) that "F-7 Tier 2 OWASP Mobile Top 10 bundle at planned 5-agent fan-out may invoke the enrichment branch at single-agent or multi-agent scope depending on signal-class analysis at PRD time; F-6 establishes three-agent enrichment as a viable operational pattern beyond F-3 single-agent and F-5 two-agent precedents, with extensibility to ≥4-agent fan-out implied by structural symmetry." F-7 ships under that forecast.

### Proposed Solution

Apply **ADR-023 Decision 3 (additive-only edit discipline)** to enrich the four (or five) host agents and their companion `detection-patterns.md` files with **10–11 new Pattern Categories** drawn from OWASP Mobile Top 10:2024 (one per Mobile item, with M8 producing 1 or 2 categories depending on the plan-day signal-class split decision). Net change is **purely additive** to **8 or 10 existing files** (4–5 agent files + 4–5 companion files) plus **1 new ADR (ADR-036)** — no new agent file, no new skill directory, no schema bump, no orchestrator dispatch table edits, no `finding-format-shared.md` consumers list edit. The audit deliverable embedded in **ADR-036** is the **canonical Mobile Top 10 sub-pattern → owning-agent mapping table** assigning every Mobile Top 10 item to **exactly one or two owning agents** (with M8's split — single-host or dual-host — explicitly catalogued at plan-day adjudication).

**1. `.claude/agents/tachi/spoofing.md`** — additive metadata + Purpose extension:
   - `owasp_references` list extended with `OWASP M1:2024 — Improper Credential Usage` and `OWASP M3:2024 — Insecure Authentication/Authorization`. PRD-time verification at plan day.
   - `## Purpose` paragraph extended with 1–3 lines naming the **mobile credential storage and mobile session handling** surfaces alongside the existing identity-spoofing surface.
   - Detection Workflow Step 5 references list extended with the new OWASP Mobile + MASTG/MASVS citations.
   - Agent file remains **≤120 lines** per ADR-023 STRIDE-tier cap. PRD-time baseline: **51 lines**. Expected post-edit: 55–60 lines (margin ≥60 lines).

**2. `.claude/skills/tachi-spoofing/references/detection-patterns.md`** — append **two new Pattern Categories** after the current last pattern category (file currently 146 lines; existing categories byte-identical pre/post edit per ADR-023 Decision 3):
   - **Pattern Category N+1: Improper Mobile Credential Usage (M1)** — covers credentials persisted in SharedPreferences / NSUserDefaults / plaintext SQLite / app-bundled config files instead of platform-managed Keystore/Keychain; hardcoded API keys / secrets in mobile binaries; credential leakage via clipboard, debug logs, or backup archives. Indicators ≥4. Primary sources: `OWASP M1:2024` (primary), `MASTG-AUTH-1` and `MASVS-CRYPTO` (related). Mitigations: platform-managed secure storage (Android Keystore, iOS Keychain), credential rotation, no hardcoded secrets in shipped binaries, biometric-bound key release for sensitive operations.
   - **Pattern Category N+2: Insecure Mobile Authentication / Authorization (M3)** — covers bypassed certificate pinning, broken or absent JWT validation in mobile clients, weak refresh-token handling, missing step-up authentication for sensitive operations (e.g., money movement, profile changes), client-side authorization decisions that the server doesn't re-validate. Indicators ≥4. Primary sources: `OWASP M3:2024` (primary), `MASTG-AUTH` and `MASVS-AUTH` (related). Mitigations: server-side authorization enforcement, certificate pinning with rotation, refresh-token binding to device, biometric step-up on high-risk operations.

**3. `.claude/agents/tachi/tampering.md`** — additive metadata + Purpose extension:
   - `owasp_references` list extended with `OWASP M2:2024 — Inadequate Supply Chain Security`, `OWASP M4:2024 — Insufficient Input/Output Validation`, `OWASP M7:2024 — Insufficient Binary Protections`. PRD-time verification at plan day.
   - `## Purpose` paragraph extended with 1–3 lines naming the **mobile SDK supply-chain integrity, mobile IPC input validation, and mobile binary protections** surfaces alongside the existing data-tampering surface and the F-6 predictive-ML adversarial-input surface.
   - Detection Workflow Step 5 references list extended with the new OWASP Mobile + MASTG/MASVS citations.
   - Agent file remains **≤120 lines** per ADR-023 STRIDE-tier cap. PRD-time baseline: **55 lines**. Expected post-edit: 60–66 lines (margin ≥54 lines).

**4. `.claude/skills/tachi-tampering/references/detection-patterns.md`** — append **three new Pattern Categories** after existing **Pattern Category 10 "Adversarial Input Manipulation (Predictive ML)"** (file currently 221 lines post-F-6; existing Categories 1–10 byte-identical pre/post edit per ADR-023 Decision 3):
   - **Pattern Category 11: Mobile Supply Chain Integrity (M2)** — covers third-party mobile SDKs and libraries integrated without checksum verification or signed-artifact policy; sideloaded APK distribution paths bypassing app-store review; CocoaPods / Gradle / Swift Package Manager dependencies pulled from unsigned sources; missing app-store provenance review on production releases. Indicators ≥4. Primary sources: `OWASP M2:2024` (primary), `MASTG-ARCH` and `MITRE ATT&CK Mobile T1474 — Supply Chain Compromise` (related). Mitigations: SDK signature verification, dependency manifest pinning with reproducible builds, app-store-only distribution, supplier-provenance review gate before SDK adoption.
   - **Pattern Category 12: Mobile IPC Input Validation (M4)** — covers Android Intent injection on exposed Activity / Service / BroadcastReceiver; iOS URL-scheme injection on `application(_:open:options:)`; deep-link parameter tampering reaching trusted operations without re-validation; exported ContentProvider with no permission gates; pasteboard-injection paths into shared-clipboard handlers. Indicators ≥4. Primary sources: `OWASP M4:2024` (primary), `MASTG-CODE` and `MASVS-PLATFORM` (related). Mitigations: explicit Intent component routing, URL-scheme allowlist with parameter validation, deep-link claim verification (Android App Links / iOS Universal Links), ContentProvider permission scoping. *(Note: this category is the F-1 cross-link checkpoint — `output-integrity` agent owns LLM-output-side validation; `tampering` Cat 12 owns mobile-IPC-input-side validation. Disjoint-tells decision recorded in ADR-036.)*
   - **Pattern Category 13: Insufficient Mobile Binary Protections (M7)** — covers missing root/jailbreak detection in security-critical features (banking, payment, regulated content); missing anti-tampering stubs (RASP, integrity self-checks); missing code obfuscation on production builds; debug symbols in shipped binaries; missing emulator-detection on fraud-sensitive flows. Indicators ≥4. Primary sources: `OWASP M7:2024` (primary), `MASTG-RESILIENCE` and `MASVS-RESILIENCE` (related). Mitigations: root/jailbreak detection with policy-based response, RASP integration with attestation, ProGuard/R8 obfuscation on Android, bitcode + symbol-stripping on iOS, emulator-detection on payment and KYC flows.

**5. `.claude/agents/tachi/info-disclosure.md`** — additive metadata + Purpose extension:
   - `owasp_references` list extended with `OWASP M5:2024 — Insecure Communication`, `OWASP M6:2024 — Inadequate Privacy Controls`, `OWASP M9:2024 — Insecure Data Storage`, `OWASP M10:2024 — Insufficient Cryptography`. PRD-time verification at plan day.
   - `## Purpose` paragraph extended with 1–3 lines naming the **mobile transport security, mobile privacy controls, mobile secure storage, and mobile cryptography** surfaces alongside the existing confidentiality-leakage surface.
   - Detection Workflow Step 5 references list extended with the new OWASP Mobile + MASTG/MASVS citations.
   - Agent file remains **≤120 lines** per ADR-023 STRIDE-tier cap. PRD-time baseline: **54 lines**. Expected post-edit: 60–66 lines (margin ≥54 lines).

**6. `.claude/skills/tachi-info-disclosure/references/detection-patterns.md`** — append **four new Pattern Categories** after current last pattern category (file currently 192 lines; existing categories byte-identical pre/post edit per ADR-023 Decision 3):
   - **Pattern Category N+1: Insecure Mobile Communication (M5)** — covers cleartext HTTP traffic from mobile clients (no `usesCleartextTraffic="false"` on Android, no `NSAppTransportSecurity` exception audit on iOS); missing TLS certificate pinning enabling MITM via root-CA installation or rogue Wi-Fi; downgrade attacks via HTTP-to-HTTPS redirect handling; weak TLS cipher acceptance on mobile clients. Indicators ≥4. Primary sources: `OWASP M5:2024` (primary), `MASTG-NETWORK` and `MASVS-NETWORK` (related). Mitigations: cleartext-traffic prohibition in network security config, certificate pinning with backup-pin rotation, TLS 1.3 with strict cipher allowlist, HSTS-equivalent enforcement at app-level.
   - **Pattern Category N+2: Inadequate Mobile Privacy Controls (M6)** — covers PII / PHI persisted in device-local caches without expiry; telemetry / analytics SDKs collecting personal data without disclosure or consent gating; clipboard exposure on sensitive fields (passwords, PII); screenshot leakage on sensitive screens (no FLAG_SECURE on Android, no equivalent screenshot prevention on iOS); over-broad permission requests on first launch. Indicators ≥4. Primary sources: `OWASP M6:2024` (primary), `MASTG-PRIVACY` and `MASVS-PRIVACY` (related). Mitigations: data-minimization on caches with TTL enforcement, consent-gated telemetry with opt-out, FLAG_SECURE / equivalent screenshot prevention on PII screens, just-in-time permission prompts with graceful denial paths.
   - **Pattern Category N+3: Insecure Mobile Data Storage (M9)** — covers unencrypted SQLite / Realm / Room databases on device; unencrypted KeyValue stores (SharedPreferences plaintext, NSUserDefaults plaintext); cloud-backup leakage (iCloud / Google-Drive backup including sensitive app data without exclusion); external SD-card writes for sensitive files; world-readable file permissions on Android internal storage. Indicators ≥4. Primary sources: `OWASP M9:2024` (primary), `MASTG-STORAGE` and `MASVS-STORAGE` (related). Mitigations: SQLCipher / Realm encryption with platform-keyring-derived keys, EncryptedSharedPreferences (Android Jetpack) / Keychain-stored secrets (iOS), `allowBackup="false"` on Android with sensitive data partitioning, internal-storage-only writes for sensitive files.
   - **Pattern Category N+4: Insufficient Mobile Cryptography (M10)** — covers weak key derivation on user PINs (low PBKDF2 iteration counts, no salting, no per-device entropy); custom-rolled crypto algorithms in mobile binaries; hardcoded symmetric keys in shipped binaries; insecure PRNG seeding (e.g., `java.util.Random` for security purposes); deprecated cipher suites (DES, RC4, MD5, SHA1) for sensitive operations. Indicators ≥4. Primary sources: `OWASP M10:2024` (primary), `MASTG-CRYPTO` and `MASVS-CRYPTO` (related). Mitigations: platform-provided key derivation (Argon2id / scrypt / PBKDF2 with ≥600k iterations), platform crypto APIs only (no custom algorithms), key derivation from platform-keyring-bound material, SecureRandom for all cryptographic randomness, AES-GCM and SHA-256+ as the minimum baseline.

**7. `.claude/agents/tachi/privilege-escalation.md` and/or `.claude/agents/tachi/repudiation.md`** — M8 split host agent(s); decision recorded in ADR-036 at plan day:
   - **Default plan-day path (PRD recommendation)**: M8 splits across **both** `privilege-escalation` (privilege-gain variant) AND `repudiation` (accountability-loss variant), one Pattern Category per host agent, mirroring ADR-035 D-4's ML06 two-facet split precedent at the F-7 architectural-tell layer. Architect adjudicates at plan day; alternative is a single-host placement with the unsplit M8 category at whichever agent dominates the empirical mobile architecture under audit.
   - `owasp_references` list extended on the chosen host(s) with `OWASP M8:2024 — Security Misconfiguration`. Existing entries preserved.
   - `## Purpose` paragraph extended with 1–3 lines naming the mobile-misconfiguration surface variant for that host's signal class.
   - Detection Workflow Step 5 references list extended with the new OWASP Mobile + MASTG/MASVS citations.
   - Agent file(s) remain **≤120 lines** per ADR-023 STRIDE-tier cap. PRD-time baselines: `privilege-escalation.md` 52 lines (margin 68 if one category appended); `repudiation.md` 50 lines (margin 70 if one category appended).

**8. Companion catalog edits for M8 host(s)** — `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md` (213 lines) and/or `.claude/skills/tachi-repudiation/references/detection-patterns.md` (148 lines) gain **one or two new Pattern Categories** for M8 facets:
   - **Default plan-day path**: split into two host catalogs:
     - **(privilege-escalation) Pattern Category N+1: Mobile Security Misconfiguration — Privilege-Gain Variant (M8)** — covers exposed debug endpoints in production builds (`adb shell` access points, debug-only Activities exported), default permissive ContentProvider / Service exports without permission scoping, missing app-attestation enabling tampered-binary execution against trusted backend, missing root-detection in security-critical feature gates. Indicators ≥4. Primary sources: `OWASP M8:2024` (primary), `MASTG-PLATFORM` and `MITRE ATT&CK Mobile T1626 — Abuse Elevation Control Mechanism` (related). Mitigations: production-build flag stripping debug code paths, ContentProvider/Activity export scoping with Android signature-level permissions, Play Integrity / DeviceCheck attestation gating, root-detection on security-critical UI flows.
     - **(repudiation) Pattern Category N+1: Mobile Security Misconfiguration — Accountability-Loss Variant (M8)** — covers missing audit logging on security-relevant mobile events (login, money-movement, permission grants), disabled crash reporting in production preventing post-incident root-cause analysis, debug logs leaking sensitive data in production via `Log.d` / `NSLog` not stripped, missing tamper-evident timestamping on audit records that the mobile app emits. Indicators ≥4. Primary sources: `OWASP M8:2024` (primary), `MASTG-PLATFORM` and `MITRE ATT&CK Mobile T1398 — Boot or Logon Initialization Scripts` (related, for boot-time audit gaps). Mitigations: structured audit logging on security-relevant mobile events with server-side persistence, production-build log-statement stripping (ProGuard/R8 rules), tamper-evident timestamping on audit records, crash-reporting enablement with PII redaction.
   - **Alternative single-host path**: One Pattern Category encompassing both variants on whichever agent dominates empirical signal at plan day. Architect adjudicates.

**9. `docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md`** — public per-feature ADR documenting (a) the **canonical Mobile Top 10 sub-pattern → owning-agent mapping table** with explicit M8 split decision (single-host or dual-host) and the per-row signal-class rationale, (b) the Heuristic A enrichment-branch consolidation at four-or-five-agent scope (extending F-3's single-agent, F-5's two-agent, and F-6's three-agent precedents), (c) the additive-only edit discipline conformance per ADR-023 Decision 3, (d) the explicit non-creation of a hypothetical `mobile-platform` agent and the rationale, (e) the no-schema-bump asymmetry to F-1 / F-2 / F-4 and structural symmetry with F-3 (ADR-032), F-5 (ADR-034), and F-6 (ADR-035), (f) the M4 cross-agent boundary clarification between `tampering` Cat 12 (mobile-IPC input validation) and F-1's `output-integrity` agent (LLM-output sanitization) — the disjoint-tells split that prevents duplicate detection on hybrid LLM-plus-mobile architectures, (g) zero-MAESTRO-reference invariant proof on the eight-or-ten enriched files, (h) cross-references to ADR-023 Decision 3 (additive enrichment), ADR-030 Decision 1 (Heuristic A signal-class taxonomy), ADR-032 (single-agent precedent), ADR-034 (two-agent precedent), ADR-035 (three-agent precedent and the forecast for ≥4-agent at the closing forward-scope marker). Authored under the Proposed → Accepted dual-commit pattern. ADR-036 is the next-available number (verified at PRD time: ADR-035 is the highest committed ADR).

**10. Example regeneration on a new `examples/mobile-banking-app/` architecture** — Default plan-day path is **author a new `examples/mobile-banking-app/` architecture** as F-7's mutation target, mirroring F-6's `predictive-ml-app/` precedent. The new example exhibits (a) a mobile client process (Android or iOS) handling user credentials, (b) a credential-handling component using SharedPreferences / NSUserDefaults rather than Keystore/Keychain, (c) a secure-storage data store (encrypted or unencrypted SQLite on device), (d) a mobile-backend API process the client communicates with (with or without certificate pinning), (e) a third-party mobile SDK integration (analytics, payment, crash reporting), (f) at least one exposed debug or admin endpoint demonstrating M8 surface. Effort impact: ~6–8 hours architect/senior-backend-engineer at plan day (slightly larger than F-6's predictive-ml-app/ because mobile architectures need both client-side and backend-side components). SC-12 demonstration target: ≥1 finding per closed Mobile Top 10 item (≥10 findings aggregate across host agents).

The four (or five) enriched agents activate **as they do today** when DFD elements match their existing trigger keywords. The new Pattern Categories fire when the architecture additionally exhibits **mobile-platform indicators** (declared mobile client component, mobile-backend API, secure-storage data store, mobile SDK integration, mobile-IPC pathway, certificate-pinning declaration, biometric/keystore reference, mobile permissions declaration, mobile package-name signal). When no mobile topology is present, the new Categories emit **zero findings** — the existing emission-gate discipline of all four (or five) agents is preserved.

**Three things the solution is deliberately NOT:**

1. It is **not** a new `mobile-platform` agent. The ten Mobile Top 10 items resolve onto four existing signal classes (one per host agent except M8 fanning to two) per Heuristic A. Authoring a new agent would fragment Mobile Top 10 findings across eleven locations and violate Heuristic A consolidation. SDR-001 Decision 4 locked the enrichment-branch rule; F-3 ADR-032 (single-agent), F-5 ADR-034 (two-agent), F-6 ADR-035 (three-agent), and F-7 ADR-036 (four-or-five-agent) execute that rule at progressive scope. F-7 cannot ship as a new agent without re-opening Heuristic A on every prior consolidation.

2. It is **not** a new finding ID prefix. Findings emit on the existing `S-{N}` (spoofing), `T-{N}` (tampering), `I-{N}` (info-disclosure), `E-{N}` (privilege-escalation), and/or `R-{N}` (repudiation) ID schemes — all five prefixes already exist in `schemas/finding.yaml` `id.pattern` regex (PRD-time verification: `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$`, 12 alternation values post-F-4, held through F-5 and F-6 at v1.8 baseline). **No schema bump** — `finding.yaml` stays at v1.8. F-7 is the **fourth BLP-01 detection feature with no schema bump** (after F-3, F-5, F-6) and the **first to skip the bump on a four-or-five-agent enrichment**. ADR-035 closing forward-scope marker explicitly forecast this outcome.

3. It is **not** an orchestrator-dispatch change. All four (or five) host agents (`spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`) are already fully registered in `dispatch-rules.md` and `orchestrator.md`. The existing dispatch paths invoke all five agents for every applicable component without modification. **No `finding-format-shared.md` consumers list edit is needed** — all five agents verified present (PRD-time grep at plan day). **No functional orchestrator/dispatch-rules edit is needed**. **F-7 is the fourth BLP-01 detection feature with zero functional orchestrator-tier touches** (after F-3, F-5, F-6).

### Success Criteria

- **SC-1** — `.claude/agents/tachi/spoofing.md` `owasp_references` list extended to include `OWASP M1:2024 — Improper Credential Usage` and `OWASP M3:2024 — Insecure Authentication/Authorization`; existing entries preserved byte-identically. Agent file line count remains **≤120 lines** (STRIDE tier cap per ADR-023). PRD-time baseline: 51 lines; expected post-edit: 55–60 lines.
- **SC-2** — `.claude/agents/tachi/spoofing.md` `## Purpose` section gains a 1–3 line extension naming the mobile credential storage and mobile session handling surfaces. Pre-existing `## Purpose` prose remains byte-identical (additive, not a rewrite).
- **SC-3** — `.claude/skills/tachi-spoofing/references/detection-patterns.md` (146 lines pre-edit) gains **two new Pattern Categories**: Improper Mobile Credential Usage (M1) and Insecure Mobile Authentication/Authorization (M3). Existing content preserved byte-identically per ADR-023 D3. Each new Category includes (a) ≥4 indicators, (b) at least one worked example grounded in a realistic mobile architecture, (c) at least one OWASP Mobile Top 10:2024 primary citation, (d) at least one MASTG / MASVS related citation.
- **SC-4** — `.claude/agents/tachi/tampering.md` `owasp_references` list extended to include `OWASP M2:2024`, `OWASP M4:2024`, `OWASP M7:2024`. Existing entries (including F-6 ML01:2023) preserved byte-identically. Agent file line count remains **≤120 lines** (STRIDE tier cap per ADR-023). PRD-time baseline: 55 lines; expected post-edit: 60–66 lines.
- **SC-5** — `.claude/agents/tachi/tampering.md` `## Purpose` section gains a 1–3 line extension naming mobile SDK supply-chain integrity, mobile IPC input validation, and mobile binary protections surfaces. Pre-existing `## Purpose` prose (including F-6 extension) remains byte-identical.
- **SC-6** — `.claude/skills/tachi-tampering/references/detection-patterns.md` (221 lines post-F-6) gains **three new Pattern Categories**: Mobile Supply Chain Integrity (M2), Mobile IPC Input Validation (M4), Insufficient Mobile Binary Protections (M7). Existing Categories 1–10 (including F-6 Cat 10) preserved byte-identically per ADR-023 D3. Each new Category includes (a) ≥4 indicators, (b) at least one worked example, (c) at least one OWASP Mobile Top 10:2024 primary citation (M2, M4, or M7 as primary), (d) at least one MASTG / MASVS / MITRE ATT&CK Mobile related citation.
- **SC-7** — `.claude/agents/tachi/info-disclosure.md` `owasp_references` list extended to include `OWASP M5:2024`, `OWASP M6:2024`, `OWASP M9:2024`, `OWASP M10:2024`. Existing entries preserved byte-identically. Agent file line count remains **≤120 lines** (STRIDE tier cap per ADR-023). PRD-time baseline: 54 lines; expected post-edit: 60–66 lines.
- **SC-8** — `.claude/agents/tachi/info-disclosure.md` `## Purpose` section gains a 1–3 line extension naming mobile transport security, mobile privacy controls, mobile secure storage, and mobile cryptography surfaces. Pre-existing `## Purpose` prose remains byte-identical.
- **SC-9** — `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` (192 lines pre-edit) gains **four new Pattern Categories**: Insecure Mobile Communication (M5), Inadequate Mobile Privacy Controls (M6), Insecure Mobile Data Storage (M9), Insufficient Mobile Cryptography (M10). Existing Categories preserved byte-identically per ADR-023 D3. Each new Category includes (a) ≥4 indicators, (b) at least one worked example, (c) at least one OWASP Mobile Top 10:2024 primary citation (M5, M6, M9, or M10 as primary), (d) at least one MASTG / MASVS related citation.
- **SC-10** — `.claude/agents/tachi/privilege-escalation.md` and/or `.claude/agents/tachi/repudiation.md` (M8 host(s) per plan-day decision) `owasp_references` list extended to include `OWASP M8:2024 — Security Misconfiguration`; companion `detection-patterns.md` gains one Pattern Category per host (one in the dual-host path, total of two for M8; one in the single-host path, total of one for M8). Existing entries preserved byte-identically. Agent file line counts remain **≤120 lines** (STRIDE tier cap per ADR-023). Plan-day decision recorded in ADR-036 D-numbered decision and the canonical mapping table.
- **SC-11** — Primary Sources lists in all four (or five) companion files extended with the new OWASP Mobile Top 10:2024 citations applicable to that companion's host agent. Existing Primary Sources entries preserved byte-identically.
- **SC-12** — Agent invocation on the new `examples/mobile-banking-app/` architecture produces **at least 1 new finding per closed Mobile Top 10 item** (≥10 findings aggregate; ≥11 if M8 split across two agents). Findings distribute across host agents as: ≥2 new `S-{N}` from `spoofing` (M1, M3); ≥3 new `T-{N}` from `tampering` (M2, M4, M7); ≥4 new `I-{N}` from `info-disclosure` (M5, M6, M9, M10); ≥1 or 2 new `E-{N}` and/or `R-{N}` from M8 host(s). Each new finding cites the appropriate `OWASP M{N}:2024` primary in its `references:` array.
- **SC-13** — All **6 non-mobile example PDFs** regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. The 6 byte-identity baselines: `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`. Zero-impact-when-absent invariant: those baselines do not exhibit mobile-platform topologies (no mobile client component, no mobile-backend API declaration, no secure-storage data store, no mobile SDK), so the new Pattern Categories emit zero findings, so all downstream artifacts are unchanged. **`agentic-app`**, **`consumer-agent-app`**, and **`predictive-ml-app`** baselines are intentionally **excluded from the byte-identity loop** in `tests/scripts/test_backward_compatibility.py` because they are mutation targets of prior features (F-3 / F-5 for agentic-app; F-4 for consumer-agent-app; F-6 for predictive-ml-app) and are untouched by F-7 absent an explicit mobile signal in those architectures (verified at plan day). **`mobile-banking-app/`** is the new F-7 mutation target; once authored, its baseline is also excluded from the byte-identity loop. **Owner**: SC-13 byte-identity verification (6 baseline regen + grep checks) is explicitly assigned to the `tester` agent (separate from `senior-backend-engineer` who authors the edits) — mirrors F-3 / F-4 / F-5 / F-6 precedent.
- **SC-14** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. Zero new developer dependencies — `pyyaml` and `pytest` already declared.
- **SC-15** — **Schema invariant preserved** — `schemas/finding.yaml` `schema_version` remains **`"1.8"`** (PRD-time verified post-F-6 baseline). `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` — no new prefix; `S`, `T`, `I`, `E`, `R` already enumerated. **F-7 is the fourth BLP-01 detection feature with no schema bump** (after F-3, F-5, F-6) and the first at four-or-five-agent enrichment scope. This outcome was explicitly forecast by ADR-035 closing forward-scope marker.
- **SC-16** — **Zero-edit invariant preserved on every detection-tier file other than the F-7 enrichment targets**. Detection-tier inventory post-F-6: **28 files** (14 host agents + 14 companion catalogs). F-7 follows the F-3 / F-5 / F-6 enrichment branch — modifies 8 files in the **single-host M8 path** (4 host agents + 4 companions = spoofing + tampering + info-disclosure + ONE of {privilege-escalation, repudiation} + their companions) or 10 files in the **dual-host M8 path** (5 host agents + 5 companions = spoofing + tampering + info-disclosure + privilege-escalation + repudiation + their companions). Adds 0 new files. Post-F-7 inventory remains 28. **20 of 28 detection-tier files remain byte-identical in the single-host M8 path** (or **18 of 28** in the dual-host M8 path). Plan-day verification: architect runs grep-checked count and reconciles against this PRD baseline. **No `finding-format-shared.md` consumers list edit is needed**. **No functional orchestrator/dispatch-rules edit is needed**. **F-7 is the first BLP-01 detection feature with four-or-five-agent enrichment scope.**
- **SC-17** — Every emitted Cat-{N+1}+ finding carries the appropriate OWASP Mobile Top 10:2024 ID in its prose-level `references:` array (existing field; verified present in finding YAML schema since v1.0). Each new `S-{N}` finding's `references` array includes `OWASP M1:2024` or `OWASP M3:2024` and where applicable `MASTG-AUTH` / `MASVS-AUTH` (catalog-resolvability verification at plan day per `schemas/taxonomy/owasp.yaml`). Each new `T-{N}` finding's `references` array includes `OWASP M2/M4/M7:2024` and where applicable `MITRE ATT&CK Mobile T1474` or `MASTG-ARCH/CODE/RESILIENCE`. Each new `I-{N}` finding's `references` array includes `OWASP M5/M6/M9/M10:2024` and where applicable `MASTG-NETWORK/PRIVACY/STORAGE/CRYPTO`. Each new `E-{N}` and/or `R-{N}` finding's `references` array includes `OWASP M8:2024` and where applicable `MITRE ATT&CK Mobile T1626` or `T1398`. F-7 does **NOT** extend `source_attribution` populator wiring on the host agents — that scope belongs to F-A3 (deferred per `schemas/finding.yaml` lines 230–238 and ADR-028 D6). **F-A3 dependency direction is one-way (F-7 → F-A3 inheritance); F-7 does not require F-A3 to ship and does not block on it.**
- **SC-18** — **Coverage Matrix transition**: BLP-01 `_internal/strategy/BLP-01-threat-coverage.md` Mobile Top 10 rows transition: **M1, M2, M3, M4, M5, M6, M7, M8, M9, M10 all Planned → Covered** — ten transitions in one feature delivery. F-7 (Feature 237) named as the closure feature for all ten. Coverage milestones panel updates to reflect **OWASP Mobile Top 10:2024 = 10 of 10 Covered**. Combined with post-F-6 milestone of OWASP three-framework total (LLM 10/10 + Agentic 10/10 + ML 10/10 = 30/30), post-F-7 tachi covers **40 of 40 entries across all four top-10 frameworks** — extending the AI security framework family closure to a fourth framework on a non-AI surface.

### Timeline

Target window: **2026-04-29 (Wednesday) → 2026-05-01 (Friday)** with **2026-05-04 (Monday) buffer + 2026-05-05 (Tuesday) reserve**. Calendar verified at PRD time (`cal 4 2026` + `cal 5 2026`): 2026-04-28 = Tuesday (PRD day, today), 2026-04-29 = Wednesday (plan day), 2026-04-30 = Thursday (build Day 1), 2026-05-01 = Friday (build Day 2), 2026-05-04 = Monday (build Day 3 / close-out), 2026-05-05 = Tuesday (buffer / reserve). Plan day shifted to Wednesday 2026-04-29 vs F-6's same-day plan-day cadence because F-7 has wider scope (4-or-5 hosts vs 3) and the M8 split decision needs architect adjudication time on representative mobile architectures.

**Single-envelope sizing** — F-7 is **larger than F-6, the largest BLP-01 enrichment-branch feature** because:
- No new agent file (only additive edits to existing — like F-3, F-5, F-6).
- No new skill directory (only additive edits to existing companions — like F-3, F-5, F-6).
- No schema bump (no new ID prefix — like F-3, F-5, F-6, asymmetric to F-1/F-2/F-4).
- No `finding-format-shared.md` edit (all four-or-five target agents already in consumers list).
- No orchestrator/dispatch-rules edit (all four-or-five agents already fully registered).
- **Four-or-five host agents** vs. F-6's three (33–67% more pattern-authoring surface per file vs F-6).
- **10–11 new Pattern Categories** total across four-or-five files vs. F-6's 7 (43–57% more authoring surface).
- ADR-036 contains the **canonical Mobile Top 10 sub-pattern → owning-agent mapping table** with explicit M8 split decision (single-host or dual-host) and M4-vs-output-integrity disjoint-tells annotation — slightly more ADR-content scope than F-6's ADR-035.
- **New `examples/mobile-banking-app/` example** authoring is required by default (no existing mobile architecture in the example fixture set).
- Heuristic A enrichment-branch is now four-execution-deep validated post-F-7 (F-3 single-agent, F-5 two-agent, F-6 three-agent, F-7 four-or-five-agent) — F-7 doesn't re-adjudicate the rule, only operationalizes it at four-or-five-agent scope.

- **Realistic envelope**: **3.0 working days**, 2.5 days aspirational, 3.5 days conservative. Build effort is +0.5 days over F-6 (which was 2.5 working days) to absorb the additional pattern-authoring surface (10–11 categories vs F-6's 7), the M8 split decision plan-day adjudication, and the new `mobile-banking-app/` example authoring.
- **Buffer**: 2026-05-04 Monday absorbs regeneration friction, ADR-036 Accepted transition, M8 split slip, and any spill from build days. 2026-05-05 Tuesday reserve for unforeseen scope expansion (e.g., MASTG/MASVS reference catalog gaps requiring follow-on schema additions).

**Build Day allocation** (3-day build):

- **Plan Day (Wed 2026-04-29)**: `/aod.spec` → `/aod.project-plan` → `/aod.tasks` chained via `/aod.plan`; Triple Triad sign-off on tasks.md; Architect adjudication on Q1 (M8 split: single-host vs dual-host); Architect adjudication on Q2 (M4 cross-link with `output-integrity` disjoint tells); Architect + senior-backend-engineer co-author `examples/mobile-banking-app/architecture.md` (~6–8 hours).
- **Day 1 (Thu 2026-04-30) AM**: FR-1 + FR-2 (`spoofing.md` + companion: 2 new pattern categories M1 + M3) + **ADR-036 Proposed commit with mapping table populated** (NOT skeleton — Q-numbering and M8 split resolved at plan day so Day 1 AM lands final mapping table).
- **Day 1 (Thu 2026-04-30) PM**: FR-3 + FR-4 (`tampering.md` + companion: 3 new pattern categories M2 + M4 + M7) — densest authoring session; three categories at ~30 lines each plus integration with F-6 Cat 10.
- **Day 2 (Fri 2026-05-01) AM**: FR-5 + FR-6 (`info-disclosure.md` + companion: 4 new pattern categories M5 + M6 + M9 + M10) — second-densest authoring session; four categories at ~30 lines each.
- **Day 2 (Fri 2026-05-01) PM**: FR-7 + FR-8 (M8 host(s): 1 or 2 new pattern categories) + `examples/mobile-banking-app/` initial regen + early-signal byte-identity spot-check on 1–2 baselines (e.g., `web-app` + `maestro-reference`) — pulls verification gate forward to catch regen surprises before Day 3.
- **Day 3 (Mon 2026-05-04) AM**: Full byte-identity verification across all 6 baselines + ADR-036 Accepted transition with SHA fill-in.
- **Day 3 (Mon 2026-05-04) PM**: FR-9 (BLP-01 Coverage Matrix update with ten row transitions) + Triad sign-offs on tasks.md (PM + Architect + Team-Lead) + close-out documentation pass per `/aod.deliver` protocol.

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: `docs/product/01_Product_Vision/product-vision.md`

Tachi's mission is to **automate threat modeling for application architectures** with a focus on AI-system threats that traditional STRIDE-only tooling misses. F-7 closes the **mobile-platform detection gap** — the mobile-client / mobile-backend threat surface (device-local credential handling, certificate pinning, binary protections, mobile IPC, secure storage, mobile cryptography) that sits between classical STRIDE coverage (already in tachi) and the OWASP AI/ML framework family (closed by Tier 1 + F-6). This positions tachi as the only OSS threat-modeling tool with **OWASP Mobile Top 10:2024** structured detection coverage alongside its existing OWASP LLM Top 10, Agentic Top 10, and ML Top 10 coverage — closing the fourth major OWASP framework and extending tachi's reach beyond pure AI/web surfaces to mobile portfolios.

### BLP-01 Tier 2 Fit

**Reference**: `_internal/strategy/BLP-01-threat-coverage.md` §4 Tier 2 Gap Analysis (Predictive ML + Mobile)

F-7 is the **second Tier 2 feature** in the BLP-01 11-feature initiative. Tier 1 (F-1 through F-5) closed the OWASP AI top-10 gap. Tier 2 closes the OWASP ML Top 10 gap (F-6, delivered 2026-04-28 via Feature 232) and the OWASP Mobile Application Security Top 10 gap (F-7); Tier 3 (F-8 through F-11) covers cloud security top-10 and supply-chain refinements. Per BLP-01 §4 Tier 2 Gap Analysis, F-7 enriches four (or five) existing agents at four-or-five-agent fan-out — the largest enrichment-branch scope in BLP-01 to date.

### ADR-036 Lineage

ADR-036 cross-references four prior ADRs that incrementally established the enrichment-branch protocol:
- **ADR-023 Decision 3** (additive-only edit discipline for skill-reference enrichment) — the enabling rule for all four enrichment-branch executions.
- **ADR-030 Decision 1** (Heuristic A signal-class taxonomy) — the same-class consolidation rule that maps ten Mobile Top 10 items onto four existing signal classes (with M8 fanning to two).
- **ADR-032** (F-3 single-agent enrichment precedent for ASI07 / `tool-abuse`) — first execution.
- **ADR-034** (F-5 two-agent enrichment precedent for LLM10 / `denial-of-service` + `model-theft`) — second execution.
- **ADR-035** (F-6 three-agent enrichment precedent for ML01/03/04/06/07/08 / `tampering` + `data-poisoning` + `model-theft`) — third execution; ADR-035 closing forward-scope marker explicitly forecasts F-7 as the four-or-five-agent execution with no schema bump.

ADR-036 establishes the four-or-five-agent execution as the **upper-bound demonstrated scope** for the enrichment-branch protocol; Tier 3 features (F-8 through F-11) may operate at smaller fan-outs depending on signal-class analysis at PRD time.

### Roadmap Fit

**Reference**: `docs/product/03_Product_Roadmap/` (BLP-01 phase milestones)

**Phase**: BLP-01 Tier 2 — closing feature
**Sequencing**: After F-1 (LLM05 closure) → F-2 (LLM09 closure) → F-3 (ASI07 closure) → F-4 (ASI09 closure) → F-5 (LLM10 closure) → F-6 (ML Top 10 closure) → **F-7 (Mobile Top 10 closure)**. Subsequent: F-8 through F-11 (Tier 3 features).
**Dependencies**: F-A1 (taxonomy crosswalk — Mobile Top 10 item IDs in `schemas/taxonomy/owasp.yaml`), F-A2 (`source_attribution` schema field). Both **already delivered** as foundation features (Features 180 + 189). PRD-time verification: M1–M10 entries verified present in `schemas/taxonomy/owasp.yaml` with `full_id: OWASP-MOBILE-2024-M{N}` and `cwe_refs: []`.

---

## 🧑‍💼 Target Users & Personas

**Reference**: `docs/product/01_Product_Vision/target-users.md`

### Primary Persona: Mixed-Portfolio Security Analyst

**Demographics**:
- Role: Application Security Engineer, Mobile Security Engineer, AppSec Architect at a company with both web and mobile products.
- Experience: Familiar with OWASP web and API frameworks; encountering mobile-specific threat modeling for the first time or maturing existing mobile-AppSec practice.
- Goals: Threat-model a mobile-banking app, mobile-IoT companion app, mobile-EHR app, or hybrid web/mobile commerce stack before production; identify mobile-specific defense gaps that web-tier tooling misses.
- Pain Points: Mobile threat modeling requires deep platform knowledge (Android security model, iOS Keychain semantics, certificate pinning mechanics); existing threat-modeling tools focus on web/API surfaces and treat mobile clients as black boxes; bespoke mobile-security tools (MobSF, NowSecure) operate at the binary-analysis layer rather than the architectural-pattern layer.

**Why This Matters to Them**: F-7 surfaces M1–M10 findings in tachi's standard pipeline output (threats.md, risk-scores.md, compensating-controls.md, security-report.pdf) — the analyst gets mobile coverage **without switching tools or adopting a separate mobile-AppSec workflow**. Coverage of credential storage, communication security, data storage, cryptography, binary protections, and mobile IPC means the analyst doesn't have to stitch together insights from MASTG / MASVS docs and traditional STRIDE outputs.

### Secondary Persona: Mobile Application Developer

**Demographics**:
- Role: Mobile Engineer (Android / iOS / React Native / Flutter), Mobile Tech Lead, MobileOps Engineer.
- Experience: Strong mobile-platform background; limited security background; building production mobile apps with regulatory or compliance constraints (PCI-DSS for payment, HIPAA for health, SOC 2 for B2B).
- Goals: Validate that the mobile app they're shipping doesn't have obvious mobile-specific gaps; pass internal security review before App Store / Play Store submission.
- Pain Points: Security tooling treats mobile pipelines as a black box; mobile linting tools focus on code style, not security; existing threat-modeling tools (STRIDE, PASTA) don't have mobile-aware patterns.

**Why This Matters to Them**: F-7's coverage flags structural gaps (no certificate pinning, no Keystore/Keychain for credentials, no FLAG_SECURE on PII screens, no root-detection on payment flows, no signed-SDK policy, no production log-stripping) that the developer can address before App Store / Play Store submission. The pattern categories include named mitigations that map to known mobile-security controls (Android Jetpack Security, iOS Keychain Services, Play Integrity, DeviceCheck, ProGuard/R8, SQLCipher), making the gap-to-control mapping concrete.

### Tertiary Persona: Compliance / Audit Reviewer

**Demographics**:
- Role: SOC 2 / ISO 27001 / PCI-DSS auditor; internal compliance reviewer at a fintech, healthcare, or regulated-industry company with mobile products.
- Experience: Familiar with traditional security frameworks; growing exposure to OWASP Mobile Top 10, MASVS, and platform-specific compliance (PCI-DSS Mobile Application Security Best Practices, HIPAA mobile guidance).
- Goals: Verify that a mobile system has documented threat-model coverage; produce compliance evidence that maps to OWASP Mobile Top 10 and platform-specific controls.
- Pain Points: Mobile systems often lack structured threat-model documentation; ad-hoc mobile security review doesn't produce reproducible evidence; PCI-DSS Mobile guidance requires alignment to OWASP Mobile but tooling doesn't surface it.

**Why This Matters to Them**: tachi's threats.md, risk-scores.md, and security-report.pdf outputs include OWASP Mobile Top 10:2024 references on every emitted finding (per SC-17), giving the auditor a structured trace from architectural pattern → OWASP framework reference → MASTG / MASVS control category → recommended mitigation. The PDF report serves as audit evidence with cross-references to the canonical mobile frameworks.

### Quaternary Persona: Tachi Maintainer

**Demographics**:
- Role: Repo maintainer enforcing Heuristic A consolidation discipline and ADR-023 lean-agent caps.
- Goals: Preserve the single-source-of-truth detection inventory; ensure the enrichment branch operationalizes correctly at four-or-five-agent scope; demonstrate the protocol's stability for Tier 3 feature planning.

**Why This Matters to Them**: F-7 demonstrates the enrichment-branch protocol at four-or-five-agent fan-out — the upper-bound scope before Tier 3 features enter the planning queue. The 18-or-20-of-28 file zero-edit invariant (post-F-7) and the no-schema-bump invariant (fourth execution after F-3, F-5, F-6) are concrete deliverables that prove the protocol scales linearly.

---

## 📖 User Stories

### US-237-1: Mobile Threat Coverage on a Mobile-Banking Architecture

**When** I'm a security analyst running tachi on a mobile-banking application architecture (mobile client + mobile-backend API + secure storage + third-party SDKs + biometric authentication),
**I want to** see new Critical / High findings covering OWASP Mobile Top 10:2024 items M1–M10,
**So I can** identify mobile-specific risks alongside the web-tier and API-tier risks tachi already surfaces — without switching to a separate mobile-AppSec tool.

**Acceptance Criteria**:
- **Given** a mobile-banking architecture with credentials stored in SharedPreferences instead of Android Keystore, **when** tachi runs the `spoofing` agent, **then** at least one new `S-{N}` finding emits citing `OWASP M1:2024 — Improper Credential Usage` with severity ≥ High and mitigation referencing platform-managed Keystore/Keychain.
- **Given** a mobile architecture with no certificate pinning declared in the mobile client, **when** tachi runs the `info-disclosure` agent, **then** at least one new `I-{N}` finding emits citing `OWASP M5:2024 — Insecure Communication` with severity ≥ High and mitigation referencing certificate pinning with backup-pin rotation.
- **Given** a mobile architecture with an unencrypted SQLite database holding PII on the device, **when** tachi runs the `info-disclosure` agent, **then** at least one new `I-{N}` finding emits citing `OWASP M9:2024 — Insecure Data Storage` with severity ≥ High and mitigation referencing SQLCipher / Realm encryption with platform-keyring-derived keys.
- **Given** a mobile architecture with a third-party SDK integrated without checksum verification, **when** tachi runs the `tampering` agent, **then** at least one new `T-{N}` finding emits citing `OWASP M2:2024 — Inadequate Supply Chain Security` with severity ≥ Medium and mitigation referencing SDK signature verification and dependency manifest pinning.
- **Given** a mobile architecture with an exported Activity exposing sensitive functions without permission gating, **when** tachi runs the `tampering` agent, **then** at least one new `T-{N}` finding emits citing `OWASP M4:2024 — Insufficient Input/Output Validation` with severity ≥ Medium and mitigation referencing Intent component routing and ContentProvider permission scoping.
- **Given** a mobile architecture missing biometric step-up on money-movement operations, **when** tachi runs the `spoofing` agent, **then** at least one new `S-{N}` finding emits citing `OWASP M3:2024 — Insecure Authentication/Authorization` with severity ≥ Medium and mitigation referencing biometric step-up on high-risk operations.
- **Given** a mobile architecture with no root-detection in security-critical UI flows and exposed debug endpoints in production, **when** tachi runs the M8 host agent(s) (`privilege-escalation` and/or `repudiation` per plan-day decision), **then** at least one new `E-{N}` and/or `R-{N}` finding emits citing `OWASP M8:2024 — Security Misconfiguration` with severity ≥ Medium and mitigation referencing production-build flag stripping and Play Integrity / DeviceCheck attestation.
- **Given** the BLP-01 Coverage Matrix at `_internal/strategy/BLP-01-threat-coverage.md` §6, **when** F-7 is delivered, **then** all ten Mobile rows (M1–M10) transition from **Planned → Covered**, with F-7 (Feature 237) named as the closure feature.

**Priority**: P1
**Effort**: M

### US-237-2: Four-or-Five-Agent Enrichment Without New Agents, Schema Bumps, or Orchestrator Changes

**When** I'm a tachi maintainer reviewing the F-7 PR diff,
**I want to** see exactly eight or ten material file edits across four-or-five host agents and four-or-five companion files plus one new ADR — and zero edits to schemas, orchestrator dispatch, consumers list, or other detection-tier files,
**So I can** verify that the Heuristic A enrichment-branch protocol scales cleanly to four-or-five-agent fan-out and the lean-agent tier caps are preserved per ADR-023.

**Acceptance Criteria**:
- **Given** the post-F-6 detection-tier inventory of 28 files, **when** I review the F-7 PR, **then** exactly **8 files** (single-host M8 path) **or 10 files** (dual-host M8 path) **are materially modified**: `.claude/agents/tachi/spoofing.md`, `.claude/agents/tachi/tampering.md`, `.claude/agents/tachi/info-disclosure.md`, plus M8 host(s) per plan-day decision, and the matching companions under `.claude/skills/tachi-{spoofing,tampering,info-disclosure,...}/references/`.
- **Given** the line-cap rules in ADR-023 Decision 1, **when** I check the modified agent files post-edit, **then** all four-or-five agents remain ≤ 120 lines (STRIDE tier; PRD baselines 51 + 55 + 54 + 52 + 50, expected post-edit ≤ 60–66 each).
- **Given** the schema invariant for finding IDs, **when** I check `schemas/finding.yaml`, **then** `schema_version` remains `"1.8"` and `id.pattern` regex remains `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\d+$` — no new ID prefix added (F-7 is the fourth no-schema-bump enrichment after F-3, F-5, F-6).
- **Given** the 18-or-20-of-28 file zero-edit invariant on non-target detection-tier files, **when** I run `git diff main HEAD -- '.claude/agents/tachi/' '.claude/skills/tachi-*/references/'`, **then** exactly 8 or 10 files appear in the diff (the F-7 targets) and the other 18 or 20 detection-tier files have zero byte changes.
- **Given** the orchestrator-tier files (`.claude/agents/tachi/orchestrator.md`, `.claude/skills/tachi-orchestration/references/dispatch-rules.md`, `.claude/skills/tachi-orchestration/references/finding-format-shared.md`), **when** I check the F-7 PR diff, **then** zero functional changes appear (annotation-only updates explicitly catalogued and adjudicated by architect at plan day; default is zero edits).
- **Given** the BLP-01 Coverage Matrix ten-row transition, **when** the F-7 PR merges and ADR-036 transitions Proposed → Accepted, **then** the public ADR ships with the canonical 10-or-11-row Mobile Top 10 sub-pattern → owning-agent mapping table and the Heuristic A four-or-five-agent consolidation rationale plus the M4-vs-output-integrity disjoint-tells annotation.

**Priority**: P1
**Effort**: S

### US-237-3: Byte-Identical Regeneration on Non-Mobile Baselines

**When** I'm a tachi adopter running the existing pipeline on an architecture without a mobile-platform topology,
**I want to** see byte-identical output before and after F-7 ships (no spurious new findings, no PDF page-count changes, no SARIF diffs),
**So I can** trust that the enrichment is fully scoped to mobile signals and won't produce false positives on architectures outside the mobile target surface.

**Acceptance Criteria**:
- **Given** the 6 example baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`), **when** I run `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` per ADR-021, **then** the test passes 6/6 byte-identical against `security-report.pdf.baseline` files for all 6 architectures.
- **Given** the mobile-platform emission gate (new Pattern Categories fire only when mobile-platform topology indicators are present), **when** I check threats.md output for the 6 non-mobile baselines, **then** no new mobile-tier findings appear (zero `S-{N}` for M1/M3, zero `T-{N}` for M2/M4/M7, zero `I-{N}` for M5/M6/M9/M10, zero `E-{N}`/`R-{N}` for M8).
- **Given** the new `examples/mobile-banking-app/` example (the F-7 mutation target), **when** I regenerate `mobile-banking-app/` end-to-end, **then** at least 10 new mobile-category findings emit (≥1 per M1–M10), and the regen produces an intentional baseline that is committed as the F-7 mutation-target precedent.
- **Given** the structural changes scope (Python scripts, Typst templates, schema), **when** I review the F-7 PR diff, **then** zero changes appear in `scripts/`, `templates/`, `schemas/finding.yaml`, `schemas/taxonomy/owasp.yaml` (existing M1–M10 entries already present per F-A1 inventory), or any orchestrator dispatch table.

**Priority**: P1
**Effort**: S

---

## ⚙️ Functional Requirements

### FR-1: `.claude/agents/tachi/spoofing.md` — Metadata + Purpose Extension

- **File path**: `.claude/agents/tachi/spoofing.md`
- **Edit posture**: Additive only (per ADR-023 D3). Pre-existing 51 lines preserved byte-identically; expected post-edit count 55–60 lines.
- **Edits**:
  1. `owasp_references` list extended with `OWASP M1:2024 — Improper Credential Usage` and `OWASP M3:2024 — Insecure Authentication/Authorization`. Existing entries preserved.
  2. `## Purpose` paragraph extended with 1–3 lines naming mobile credential storage and mobile session handling surfaces.
  3. Detection Workflow Step 5 references list extended with the new OWASP Mobile + MASTG/MASVS citations.
- **Tier cap**: STRIDE-tier ≤ 120 lines per ADR-023 D1; margin ≥60 lines.

### FR-2: `.claude/skills/tachi-spoofing/references/detection-patterns.md` — Two New Pattern Categories (M1, M3)

- **File path**: `.claude/skills/tachi-spoofing/references/detection-patterns.md`
- **Edit posture**: Additive only. Existing 146 lines preserved byte-identically per ADR-023 D3.
- **Append**:
  - **Pattern Category N+1: Improper Mobile Credential Usage (M1)** — full subsection structure (H2 heading, description, ≥4 indicators, worked example, primary source block citing `OWASP M1:2024` + `MASTG-AUTH`, mitigations naming Keystore/Keychain, biometric-bound key release).
  - **Pattern Category N+2: Insecure Mobile Authentication / Authorization (M3)** — full subsection structure citing `OWASP M3:2024` + `MASTG-AUTH` + `MASVS-AUTH` related; mitigations naming server-side authorization enforcement, certificate pinning, biometric step-up.
  - Primary Sources section additively extended with `OWASP M1:2024` and `OWASP M3:2024`.

### FR-3: `.claude/agents/tachi/tampering.md` — Metadata + Purpose Extension

- **File path**: `.claude/agents/tachi/tampering.md`
- **Edit posture**: Additive only. Pre-existing 55 lines (post-F-6) preserved byte-identically; expected post-edit count 60–66 lines.
- **Edits**:
  1. `owasp_references` list extended with `OWASP M2:2024`, `OWASP M4:2024`, `OWASP M7:2024`. Existing entries (including F-6 ML01:2023 + AML.T0015) preserved.
  2. `## Purpose` paragraph extended with 1–3 lines naming mobile SDK supply-chain integrity, mobile IPC input validation, and mobile binary protections surfaces.
  3. Detection Workflow Step 5 references list extended with the new OWASP Mobile + MASTG/MASVS citations.
- **Tier cap**: STRIDE-tier ≤ 120 lines per ADR-023 D1; margin ≥54 lines.

### FR-4: `.claude/skills/tachi-tampering/references/detection-patterns.md` — Three New Pattern Categories (M2, M4, M7)

- **File path**: `.claude/skills/tachi-tampering/references/detection-patterns.md`
- **Edit posture**: Additive only. Existing 221 lines (post-F-6, including Cat 10 Adversarial Input Manipulation) preserved byte-identically per ADR-023 D3.
- **Append**:
  - **Pattern Category 11: Mobile Supply Chain Integrity (M2)** — full subsection structure citing `OWASP M2:2024` + `MASTG-ARCH` + `MITRE ATT&CK Mobile T1474` related.
  - **Pattern Category 12: Mobile IPC Input Validation (M4)** — full subsection structure citing `OWASP M4:2024` + `MASTG-CODE` + `MASVS-PLATFORM` related; **plus disjoint-tells annotation referencing F-1's `output-integrity` agent boundary** per ADR-036.
  - **Pattern Category 13: Insufficient Mobile Binary Protections (M7)** — full subsection structure citing `OWASP M7:2024` + `MASTG-RESILIENCE` + `MASVS-RESILIENCE` related.
  - Primary Sources section additively extended with `OWASP M2:2024`, `OWASP M4:2024`, `OWASP M7:2024`.

### FR-5: `.claude/agents/tachi/info-disclosure.md` — Metadata + Purpose Extension

- **File path**: `.claude/agents/tachi/info-disclosure.md`
- **Edit posture**: Additive only. Pre-existing 54 lines preserved byte-identically; expected post-edit count 60–66 lines.
- **Edits**:
  1. `owasp_references` list extended with `OWASP M5:2024`, `OWASP M6:2024`, `OWASP M9:2024`, `OWASP M10:2024`. Existing entries preserved.
  2. `## Purpose` paragraph extended with 1–3 lines naming mobile transport security, mobile privacy controls, mobile secure storage, and mobile cryptography surfaces.
  3. Detection Workflow Step 5 references list extended with the new OWASP Mobile + MASTG/MASVS citations.
- **Tier cap**: STRIDE-tier ≤ 120 lines per ADR-023 D1; margin ≥54 lines.

### FR-6: `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` — Four New Pattern Categories (M5, M6, M9, M10)

- **File path**: `.claude/skills/tachi-info-disclosure/references/detection-patterns.md`
- **Edit posture**: Additive only. Existing 192 lines preserved byte-identically per ADR-023 D3.
- **Append**:
  - **Pattern Category N+1: Insecure Mobile Communication (M5)** — full subsection structure citing `OWASP M5:2024` + `MASTG-NETWORK` + `MASVS-NETWORK` related.
  - **Pattern Category N+2: Inadequate Mobile Privacy Controls (M6)** — full subsection structure citing `OWASP M6:2024` + `MASTG-PRIVACY` + `MASVS-PRIVACY` related.
  - **Pattern Category N+3: Insecure Mobile Data Storage (M9)** — full subsection structure citing `OWASP M9:2024` + `MASTG-STORAGE` + `MASVS-STORAGE` related.
  - **Pattern Category N+4: Insufficient Mobile Cryptography (M10)** — full subsection structure citing `OWASP M10:2024` + `MASTG-CRYPTO` + `MASVS-CRYPTO` related.
  - Primary Sources section additively extended with `OWASP M5:2024`, `OWASP M6:2024`, `OWASP M9:2024`, `OWASP M10:2024`.

### FR-7: M8 Host Agent(s) — Metadata + Purpose Extension

- **File path(s)**: `.claude/agents/tachi/privilege-escalation.md` and/or `.claude/agents/tachi/repudiation.md` per plan-day decision (default: dual-host).
- **Edit posture**: Additive only. Pre-existing 52 lines (privilege-escalation) and 50 lines (repudiation) preserved byte-identically; expected post-edit count ≤56 lines each.
- **Edits**:
  1. `owasp_references` list extended with `OWASP M8:2024 — Security Misconfiguration` on the chosen host(s). Existing entries preserved.
  2. `## Purpose` paragraph extended with 1–3 lines naming mobile-misconfiguration surface variant for that host's signal class.
  3. Detection Workflow Step 5 references list extended with the new OWASP Mobile + MASTG/MASVS citations.
- **Tier cap**: STRIDE-tier ≤ 120 lines per ADR-023 D1; margins ≥64 lines (privilege-escalation) and ≥66 lines (repudiation).

### FR-8: M8 Host Companion(s) — One or Two New Pattern Categories

- **File path(s)**: `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md` (213 lines pre-edit) and/or `.claude/skills/tachi-repudiation/references/detection-patterns.md` (148 lines pre-edit) per plan-day decision.
- **Edit posture**: Additive only. Existing content preserved byte-identically per ADR-023 D3.
- **Append (default dual-host path)**:
  - **(privilege-escalation) Pattern Category N+1: Mobile Security Misconfiguration — Privilege-Gain Variant (M8)** — full subsection structure citing `OWASP M8:2024` + `MASTG-PLATFORM` + `MITRE ATT&CK Mobile T1626` related.
  - **(repudiation) Pattern Category N+1: Mobile Security Misconfiguration — Accountability-Loss Variant (M8)** — full subsection structure citing `OWASP M8:2024` + `MASTG-PLATFORM` + `MITRE ATT&CK Mobile T1398` related.
  - Primary Sources sections additively extended on both companions with `OWASP M8:2024`.
- **Alternative single-host path**: One Pattern Category encompassing both variants on the chosen host; architect adjudicates at plan day.

### FR-9: New `examples/mobile-banking-app/` Authoring + Regeneration

- **Plan-day authoring** (Wednesday 2026-04-29): Architect + senior-backend-engineer co-author `examples/mobile-banking-app/architecture.md` exhibiting all six mobile-platform topology indicators: (a) mobile client process (Android or iOS) handling user credentials, (b) credential-handling component using SharedPreferences / NSUserDefaults instead of platform-managed Keystore/Keychain, (c) secure-storage data store (SQLite on device, possibly encrypted), (d) mobile-backend API process the client communicates with (with or without certificate pinning declaration), (e) third-party mobile SDK integration (analytics, payment, crash reporting), (f) at least one exposed debug or admin endpoint demonstrating M8 surface. Effort: ~6–8 hours (architect drafts, senior-backend-engineer reviews/refines).
- **Aggregate target**: ≥10 new Mobile findings (one per M1–M10 closure; ≥11 if M8 splits across two agents in dual-host path).
- **Coverage**: ≥1 new finding from each host agent (`spoofing` for M1+M3, `tampering` for M2+M4+M7, `info-disclosure` for M5+M6+M9+M10, `privilege-escalation` and/or `repudiation` for M8).

### FR-10: ADR-036 Authoring and Lifecycle

- **File path**: `docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md`
- **Authoring lifecycle**: Proposed → Accepted dual-commit pattern per ADR-027 / ADR-032 / ADR-034 / ADR-035 precedent.
- **Mandatory content**:
  1. **Canonical Mobile Top 10 sub-pattern → owning-agent mapping table** (10 or 11 rows): one row per Mobile item, with M8 producing 1 or 2 rows depending on plan-day split decision; per-row signal-class rationale and severity-hint annotation column.
  2. **Heuristic A enrichment-branch consolidation rationale at four-or-five-agent scope** with cross-reference to ADR-030 D1 and worked examples from §11 of GUIDE-threat-coverage-research.
  3. **Additive-only edit discipline conformance** per ADR-023 D3 with grep-checkable preservation evidence on the 8-or-10 modified files.
  4. **Explicit non-creation of `mobile-platform` agent** with rationale (would fragment Mobile Top 10 across eleven locations and violate Heuristic A).
  5. **No-schema-bump symmetry with F-3, F-5, F-6** asymmetry to F-1/F-2/F-4; confirms ADR-035 closing forward-scope marker forecast.
  6. **M4 cross-agent boundary clarification** — disjoint-tells decomposition between `tampering` Cat 12 (mobile-IPC input validation) and F-1's `output-integrity` agent (LLM-output sanitization). Mirrors F-6 ADR-035 D-5 (ML03 vs ML04 disjoint architectural-tells on shared catalog reference) at the F-7 cross-axis layer.
  7. **M8 split decision** — dual-host (default) or single-host with rationale. If dual-host: privilege-escalation owns privilege-gain variant, repudiation owns accountability-loss variant; disjoint architectural-tells per host. If single-host: single category encompassing both variants on chosen host.
  8. **Zero-MAESTRO-reference invariant proof** on the eight-or-ten enriched files (grep-checkable: 0 mentions of MAESTRO Layer N in the modified files post-edit, preserving the architectural-tier separation that ADR-024 established).
  9. **Cross-references to ADR-023 D3, ADR-030 D1, ADR-032, ADR-034, ADR-035** with explicit citation of ADR-035 closing forward-scope marker forecast text.

### FR-11: Coverage Matrix Update in BLP-01

- **File path**: `_internal/strategy/BLP-01-threat-coverage.md` §6 Coverage Matrix
- **Edits**: Ten row transitions: M1, M2, M3, M4, M5, M6, M7, M8, M9, M10 — all Planned → Covered. Closure-feature column populated with "Feature 237 (F-7)" for all ten rows.
- **Coverage milestones panel update**: Reflect OWASP Mobile Top 10:2024 = 10/10 Covered, OWASP four-framework total = 40/40 Covered (with citation of the post-F-7 milestone).

---

## 🚀 Non-Functional Requirements

### Performance Requirements

- **Pipeline latency**: F-7 enrichments add ≤7% wall-clock latency to a tachi pipeline run on a mobile architecture (pattern-loading is bounded; new categories add ≤500 lines aggregate to skill-reference loads — slightly larger than F-6's ≤300 because of higher category count).
- **PDF report regeneration**: F-7 mutation target (`mobile-banking-app/`) produces report in same wall-clock envelope as F-6's regen (≤2 minutes including infographic generation).

### Reliability Requirements

- **Byte-identity preservation**: 6 of 7 example baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) remain byte-identical under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. The `mobile-banking-app/` baseline is intentionally regenerated as the F-7 mutation target. `agentic-app`, `consumer-agent-app`, and `predictive-ml-app/` baselines are excluded from the byte-identity loop because they are mutation targets of prior features (F-3/F-5, F-4, F-6 respectively).
- **Zero false positives on non-mobile architectures**: New Pattern Categories' emission gates (mobile-platform topology indicators) ensure zero finding emission when the architecture lacks mobile signals.
- **Backward compatibility**: F-7 does not modify any external API, schema, or finding format consumed by downstream tools (SARIF consumers, infographic renderer, PDF assembler). All downstream consumers continue to operate without code changes.

### Security Requirements

- **No new attack surface**: F-7 adds detection content only; no new code paths, no new external API endpoints, no new dependency surface.
- **Pattern-content integrity**: Pattern category content is reviewed for accuracy via PR review (architect verifies citation correctness against OWASP Mobile Top 10:2024 source and MASTG/MASVS specifications).

### Maintainability Requirements

- **Tier cap preservation**: All four-or-five modified agent files remain within ADR-023 D1 STRIDE caps (≤ 120 lines, hard ceiling ≤ 180). PRD-time baselines and expected post-edit counts are documented in FR-1, FR-3, FR-5, FR-7.
- **Zero-edit invariant**: 18 or 20 of 28 detection-tier files unchanged post-F-7, preserving the lean-agent inventory discipline established in Feature 082.
- **Heuristic A protocol stability**: Four-execution validation gate (F-3 single-agent, F-5 two-agent, F-6 three-agent, F-7 four-or-five-agent) demonstrates the enrichment branch scales linearly in pattern-authoring surface and ADR-content scope without inflating tier-cap pressure or introducing schema/orchestrator coupling.

---

## 📊 Success Metrics

### Coverage Metrics

- **OWASP Mobile Top 10:2024 coverage**: Pre-F-7 = 0/10 Covered (all ten Planned); Post-F-7 = 10/10 Covered (ten transitions: M1, M2, M3, M4, M5, M6, M7, M8, M9, M10).
- **OWASP four-framework total**: Pre-F-7 = 30/40 Covered (LLM 10/10 + Agentic 10/10 + ML 10/10 + Mobile 0/10); Post-F-7 = 40/40 Covered.
- **BLP-01 features delivered**: Pre-F-7 = 9/11 (Foundation + F-1 through F-6 + F-A1 + F-A2 + F-B); Post-F-7 = 10/11 (only F-8 Web/API Tier 3 remains).
- **Detection-tier inventory**: Pre-F-7 = 28 files; Post-F-7 = 28 files (zero net new — fourth execution of enrichment branch).

### Quality Metrics

- **Pattern category citation rate**: 10 or 11 of 10 or 11 new Pattern Categories carry at least one OWASP Mobile Top 10:2024 primary citation; 10 or 11 of 10 or 11 carry at least one MASTG / MASVS / MITRE ATT&CK Mobile related citation.
- **Indicator density**: Each new Pattern Category specifies ≥4 architectural indicators that drive the finding-emission gate.
- **Mitigation specificity**: Each new Pattern Category names ≥3 specific control mechanisms with platform-specific names where applicable (e.g., Android Keystore, iOS Keychain, SQLCipher, Play Integrity, DeviceCheck, ProGuard/R8, FLAG_SECURE, Android App Links, iOS Universal Links).

### Pattern Validation Metrics

- **Aggregate finding emission on F-7 mutation target**: ≥10 new findings (≥1 per M1–M10) on `examples/mobile-banking-app/`; ≥11 if M8 splits across two agents.
- **Per-host-agent finding emission**: ≥2 new `S-{N}` from `spoofing`, ≥3 new `T-{N}` from `tampering`, ≥4 new `I-{N}` from `info-disclosure`, ≥1 new `E-{N}` and/or `R-{N}` from M8 host(s) on the F-7 mutation target.

### Delivery Metrics

- **Schema bump**: Zero (no new ID prefix; `finding.yaml` stays at v1.8).
- **New runtime dependencies**: Zero.
- **New developer dependencies**: Zero.
- **Files modified**: 8 detection-tier files (single-host M8 path) or 10 detection-tier files (dual-host M8 path) + ADR-036 + BLP-01 strategy doc Coverage Matrix update + new `examples/mobile-banking-app/` example fixture.
- **Backward-compatibility test**: 6/6 byte-identical baselines passing under `SOURCE_DATE_EPOCH=1700000000`.

---

## 🔍 Scope & Boundaries

### In Scope (F-7 / This Release)

**Must Have (P0)**:
- ✅ Two new Pattern Categories in `spoofing` companion covering M1, M3.
- ✅ Three new Pattern Categories in `tampering` companion covering M2, M4, M7.
- ✅ Four new Pattern Categories in `info-disclosure` companion covering M5, M6, M9, M10.
- ✅ One or two new Pattern Categories in M8 host companion(s) covering M8 (single-host or dual-host per plan-day decision).
- ✅ Metadata + Purpose extensions on the four-or-five host agents.
- ✅ ADR-036 authored Proposed → Accepted with canonical Mobile Top 10 sub-pattern → owning-agent mapping table.
- ✅ Coverage Matrix transition for ten rows in BLP-01 strategy doc.
- ✅ Backward-compatibility test passing 6/6 byte-identical on non-mobile baselines.
- ✅ New `examples/mobile-banking-app/` authoring producing ≥10 new Mobile findings.

**Should Have (P1)**:
- 🎯 M8 dual-host split annotated in ADR-036 mapping table with explicit privilege-gain and accountability-loss rows.
- 🎯 MASTG / MASVS cross-references on every applicable Pattern Category.
- 🎯 M4 cross-agent boundary clarification with F-1's `output-integrity` agent in ADR-036.
- 🎯 Heuristic A four-or-five-agent narrative in ADR-036 with worked examples from §11 of GUIDE-threat-coverage-research.

### Out of Scope (Future Phases)

**Could Have (P2)** — Not in F-7:
- 🔮 Mobile Application Security Verification Standard (MASVS) verification levels (L1/L2/R) as a per-finding tag — deferred to a follow-on feature; F-7 cites MASVS control categories as related references only.
- 🔮 Platform-specific (Android-only or iOS-only) detection sub-patterns — F-7 covers cross-platform mobile patterns; deeper platform-specific differentiation is a follow-on.
- 🔮 OWASP Mobile Application Security Testing Guide (MASTG) test-case ID cross-references on a per-finding basis — deferred as a follow-on after MASTG IDs are added to a future taxonomy file.
- 🔮 Hybrid React Native / Flutter / Xamarin specific pattern variants — F-7 covers native Android/iOS patterns; cross-platform framework variants are a follow-on.

**Won't Have** — Explicitly excluded:
- ❌ New `mobile-platform` agent file — violates Heuristic A consolidation per ADR-036 D-numbered decision.
- ❌ Schema bump on `schemas/finding.yaml` — no new ID prefix; S/T/I/E/R already in regex per F-A1.
- ❌ Orchestrator dispatch table edits (functional) — host agents already registered.
- ❌ `finding-format-shared.md` consumers list edit — host agents already in consumers list.
- ❌ Source attribution populator wiring extension — that scope is F-A3.
- ❌ MASTG taxonomy YAML file authoring — F-A1 follow-on scope, not F-7.

### Assumptions

- **A1**: M1–M10 entries are present in `schemas/taxonomy/owasp.yaml` per F-A1 delivery (Feature 180). **VERIFIED at PRD time** via `grep "^- id: M[0-9]\|^- id: M10$" schemas/taxonomy/owasp.yaml` returning all 10 records.
- **A2**: MASTG / MASVS reference categories (e.g., MASTG-AUTH, MASVS-CRYPTO, MASVS-NETWORK) are cited as prose references in finding `mitigation` narratives and pattern-category Primary Source blocks; they do **NOT** require entries in a structured taxonomy YAML file (MASTG IDs are a F-A1 follow-on scope per Issue #186; F-7 cites them as prose only).
- **A3**: MITRE ATT&CK for Mobile entries (T1474, T1626, T1398) are catalog-resolvable per `schemas/taxonomy/mitre-attack.yaml` — PRD-time verification at plan day. If absent, prose-only fallback per F-5 T1496 / F-6 ATLAS-gap precedent.
- **A4**: The post-F-6 detection-tier file count is 28 (verified at PRD time via `find .claude/agents/tachi -name '*.md' | wc -l` + `find .claude/skills/tachi-* -name 'detection-patterns.md' | wc -l`).
- **A5**: A new `examples/mobile-banking-app/` example is authored at plan day rather than grafting mobile signal onto an existing example. Default rationale: empirical grep across existing examples shows zero mobile-platform indicators (no Android / iOS / mobile / SDK / Keystore / Keychain references) — same diagnostic that drove F-6's `predictive-ml-app/` decision.

**Validation Needed at Plan Day**:
- [ ] **A3**: Confirm MITRE ATT&CK Mobile entries (T1474, T1626, T1398) catalog-resolvability.
- [ ] **A5**: Confirm zero mobile-platform indicators across existing examples — empirical grep gate before authoring `mobile-banking-app/`.

### Constraints

**Technical Constraints**:
- ADR-023 D1 tier caps (STRIDE ≤ 120, AI ≤ 150, hard ≤ 180) — non-negotiable; verified margins ≥54 lines on tightest case (`tampering.md`).
- ADR-021 byte-identity invariant on non-mutation baselines — non-negotiable.
- Heuristic A consolidation rule (SDR-001 D4) — non-negotiable; F-7 cannot ship as a new agent without re-opening Heuristic A on every prior consolidation.

**Business Constraints**:
- Timeline: 3 working days (Thu 2026-04-30 → Mon 2026-05-04) + 1 reserve day (Tue 2026-05-05). Plan day Wednesday 2026-04-29 is non-build but includes example authoring (~6–8 hours).
- Resources: standard /aod.build wave allocation (senior-backend-engineer for edits, tester for byte-identity verification, architect for ADR-036 authoring + mobile-banking-app/ co-authoring).

**External Dependencies**:
- F-A1 (taxonomy crosswalk) — **delivered** (Feature 180); M1–M10 entries verified at PRD time.
- F-A2 (`source_attribution` schema field) — **delivered** (Feature 189).

---

## 🛣️ Timeline & Milestones

### Phase Breakdown

**Plan Day** (Wednesday 2026-04-29):
- `/aod.spec` → `/aod.project-plan` → `/aod.tasks` chained via `/aod.plan`
- Triple Triad sign-off on tasks.md
- Architect adjudication on Q1 (M8 split: single-host vs dual-host)
- Architect adjudication on Q2 (M4 cross-link with `output-integrity` disjoint-tells annotation)
- Architect + senior-backend-engineer co-author `examples/mobile-banking-app/architecture.md` (~6–8 hours)

**Build Day 1** (Thursday 2026-04-30):
- AM: FR-1 + FR-2 (`spoofing.md` + companion: 2 new pattern categories M1 + M3) + ADR-036 Proposed commit with mapping table populated.
- PM: FR-3 + FR-4 (`tampering.md` + companion: 3 new pattern categories M2 + M4 + M7).
- **Deliverable**: `spoofing` and `tampering` enrichments complete; ADR-036 Proposed.

**Build Day 2** (Friday 2026-05-01):
- AM: FR-5 + FR-6 (`info-disclosure.md` + companion: 4 new pattern categories M5 + M6 + M9 + M10).
- PM: FR-7 + FR-8 (M8 host(s): 1 or 2 new pattern categories) + `examples/mobile-banking-app/` initial regen + early-signal byte-identity spot-check on 1–2 baselines.
- **Deliverable**: All 10–11 pattern categories complete; mobile-banking-app initial regen; spot-check verification clean.

**Close-Out Day** (Monday 2026-05-04):
- AM: Full byte-identity verification across 6 baselines (FR-11 expanded to all 6).
- AM: ADR-036 Accepted transition with SHA fill-in.
- PM: FR-11 (BLP-01 Coverage Matrix update with ten row transitions).
- PM: `/aod.deliver` close-out + Triad sign-offs on tasks.md.
- **Deliverable**: F-7 fully delivered; PR ready for squash-merge with `feat(237):` Conventional Commit title.

### Key Milestones

| Milestone | Target Date | Owner | Status |
|-----------|-------------|-------|--------|
| PRD Approval | 2026-04-28 | product-manager | 🟡 In Review |
| Spec Complete | 2026-04-29 | architect | 📋 Pending |
| Plan + Tasks Approval | 2026-04-29 | product-manager + architect + team-lead | 📋 Pending |
| `mobile-banking-app/` Authoring | 2026-04-29 | architect + senior-backend-engineer | 📋 Pending |
| Build Day 1 Complete (`spoofing` + `tampering`) | 2026-04-30 | senior-backend-engineer | 📋 Pending |
| Build Day 2 Complete (`info-disclosure` + M8 + mobile-banking-app regen) | 2026-05-01 | senior-backend-engineer + tester | 📋 Pending |
| Byte-identity Verification (6 baselines) | 2026-05-04 | tester | 📋 Pending |
| ADR-036 Accepted | 2026-05-04 | architect | 📋 Pending |
| Coverage Matrix Update | 2026-05-04 | senior-backend-engineer | 📋 Pending |
| Production Deploy / PR Squash-Merge | 2026-05-04 | devops + product-manager | 📋 Pending |
| Reserve Day | 2026-05-05 | — | 📋 Reserved |

Legend: ✅ Complete | 🟢 On Track | 🟡 In Review | 📋 Pending | 🔴 Blocked

---

## ⚠️ Risks & Dependencies

### Technical Risks

**R1: Mobile Mutation Target Authoring** [Probability: HIGH / Impact: Medium]
- **Description**: No existing example exhibits mobile-platform topology (empirical grep across `examples/*/architecture.md` returns zero matches for Android / iOS / mobile / SDK / Keystore / Keychain — same diagnostic that drove F-6's `predictive-ml-app/` decision). New `examples/mobile-banking-app/` example authoring is the **default plan-day path**.
- **Mitigation**: Plan day Wednesday 2026-04-29 architect/senior-backend-engineer co-authors `examples/mobile-banking-app/architecture.md` exhibiting six mobile-platform topology indicators. Effort: ~6–8 hours (architect drafts, senior-backend-engineer reviews/refines). Day 1 AM still lands FR-1 + FR-2 + ADR-036 Proposed as planned.
- **Contingency**: If `mobile-banking-app/` authoring slips beyond plan day, architect downgrades SC-12 to "≥5 new findings (≥1 per host agent on a strawman test fixture authored under `tests/fixtures/`)" — ships F-7 with verification on a synthetic architecture rather than a fully-authored example.

**R2: M8 Split Decision Adjudication Slip** [Probability: Medium / Impact: Medium]
- **Description**: M8 split decision (single-host vs dual-host) requires architect adjudication on representative mobile architectures at plan day. If adjudication slips beyond Wednesday 2026-04-29, Day 1 AM cannot land ADR-036 Proposed with finalized mapping table.
- **Mitigation**: Plan-day adjudication target is end-of-day Wednesday 2026-04-29; PRD recommends dual-host as default to give architect a falsifiable starting position rather than open-ended deliberation. Q1 in Open Questions section enumerates the decision criteria.
- **Contingency**: If architect cannot adjudicate by Day 1 AM, fall back to single-host placement (M8 → privilege-escalation only) and defer dual-host split to a follow-on PR. F-7 ships with single-host M8; dual-host expansion is a no-schema-bump follow-on.

**R3: MITRE ATT&CK Mobile Catalog-Resolvability Gaps** [Probability: Medium / Impact: Low]
- **Description**: One or more of T1474 (Supply Chain Compromise), T1626 (Abuse Elevation Control Mechanism), T1398 (Boot or Logon Initialization Scripts) may be absent from `schemas/taxonomy/mitre-attack.yaml`, requiring prose-only citation in `mitigation` narratives instead of structured `references` array entries (mirrors F-5's T1496 prose-only handling and F-6's 3-of-6 ATLAS prose-only handling).
- **Mitigation**: Architect verifies at plan day; non-catalog entries appear as prose-only citations in pattern-category narratives, not as structured citations. SC-17 acceptance criterion accommodates this.
- **Contingency**: If catalog is missing 2+ entries, architect authorizes a small companion edit to `schemas/taxonomy/mitre-attack.yaml` adding the missing T-records — but this is a F-A1 follow-on, not F-7 scope; F-7 ships with prose-only fallback.

**R4: Four-or-Five-Agent Authoring Surface Schedule Slip** [Probability: Medium / Impact: Medium]
- **Description**: F-7 has 10–11 new pattern categories vs F-6's 7 — 43–57% more authoring surface. Day 1 PM (3 categories on `tampering` companion) and Day 2 AM (4 categories on `info-disclosure` companion) are the densest authoring sessions; if authoring quality slips, Day 2 PM may absorb spillover.
- **Mitigation**: Plan day lands ADR-036 mapping table populated (not skeleton) so Day 1 AM is purely category authoring. Day 2 AM is dedicated to `info-disclosure` authoring with no concurrent ADR work. Buffer day (2026-05-04) used for slip absorption + close-out.
- **Contingency**: If Day 2 PM verification spot-check reveals authoring quality issues, Day 3 AM rolls into category re-authoring rather than verification; full verification pushes to reserve day Tuesday 2026-05-05.

**R5: M4 Cross-Agent Coordination with F-1 `output-integrity`** [Probability: Low / Impact: Medium]
- **Description**: M4 Insufficient Input/Output Validation has potential overlap with F-1's `output-integrity` agent (LLM-output sanitization). Without an explicit boundary, both agents may emit overlapping findings on hybrid LLM-plus-mobile architectures.
- **Mitigation**: ADR-036 includes M4 cross-agent boundary clarification subsection (mirroring F-6 ADR-035 D-5 ML03-vs-ML04 disjoint-tells precedent at the F-7 cross-axis layer): `tampering` Cat 12 owns mobile-IPC-input-side validation (deep-link parameters, Intent extras, URL-scheme parameters); `output-integrity` owns LLM-output-side sanitization (LLM-generated content flowing into browser/SQL/shell sinks). Disjoint indicators ensure no overlap.
- **Contingency**: If overlap detected at FR-9 regen, architect performs a Day 3 AM clarification edit on `tampering` Cat 12 indicators to disambiguate the architectural-tell scope.

**R6: Heuristic A Four-or-Five-Agent Validation Pressure** [Probability: Low / Impact: High]
- **Description**: F-7 is the fourth execution of the Heuristic A enrichment-branch protocol — at four-or-five-agent fan-out, the protocol may surface emergent issues not visible at single-agent (F-3), two-agent (F-5), or three-agent (F-6) scope (e.g., ADR-content scope explosion, mapping-table complexity, cross-agent reference cycles).
- **Mitigation**: ADR-035 closing forward-scope marker explicitly forecast F-7 as a four-or-five-agent execution; F-7 ships under that forecast as the validation. ADR-036 documents any emergent issues for Tier 3 reference.
- **Contingency**: If issues surface that can't be resolved within F-7's envelope, architect authorizes a scope-narrow fallback (e.g., ship 8 of 10 pattern categories with M8 deferred to a follow-on PR), preserving the no-schema-bump and four-or-five-agent-fan-out invariants.

**R7: Backward-Compatibility Baseline Drift** [Probability: Low / Impact: High]
- **Description**: Spurious finding emission on a non-mobile baseline due to overly broad indicator gates on Pattern Categories 11/12/13 (tampering) or new categories on info-disclosure / M8 hosts — could break the byte-identity invariant.
- **Mitigation**: Pattern Category indicator gates reference mobile-platform-specific architectural tells (mobile client component, mobile-backend API declaration, mobile SDK reference, Keystore/Keychain mention, certificate pinning declaration, mobile permissions, package-name signal). Generic indicators (e.g., "API endpoint" or "data store") would be too broad and are explicitly excluded. Day 2 PM early-signal spot-check on 1–2 baselines catches drift before Day 3 full verification.
- **Contingency**: If Day 3 verification reveals drift on any of the 6 baselines, architect performs a Day 3 AM tightening edit on the offending Pattern Category's indicator gate; full verification reruns on the reserve day.

**R8: ADR-036 Content Scope Explosion** [Probability: Low / Impact: Medium]
- **Description**: ADR-036's mapping table is 10 or 11 rows + reference rows (vs F-6's 8 rows); the Heuristic A four-or-five-agent narrative is wider than F-6's three-agent narrative; M8 split decision and M4 cross-agent boundary clarification add complexity.
- **Mitigation**: ADR template enforces Decision-list structure (D1 through D10 mirroring ADR-035); mapping table is bounded at 14 rows max (10–11 closure rows + 3 reference rows). No de facto ADR length cap exists (architect MEDIUM-1 correction in F-6 v2: F-5 ADR-034 = 333 lines, F-3 ADR-032 = 265 lines, F-6 ADR-035 = 319 lines — all shipped without revision); ADR-036 is expected to land in the 350–420 line range.
- **Contingency**: If ADR-036 length becomes unwieldy at architect review, architect splits content between ADR-036 (decision-tier) and a companion `_internal/strategy/F-7-mapping-table.md` (reference-tier); ADR-036 cross-references the companion. Empirical evidence (F-3 + F-5 + F-6 inline tables) suggests this contingency is unlikely to trigger.

### Business Risks

**R9: Coverage Matrix Update Misattribution** [Probability: Low / Impact: Low]
- **Description**: BLP-01 §6 Coverage Matrix ten-row update could over-attribute or under-attribute closure (e.g., crediting F-7 for items already partially Covered).
- **Mitigation**: FR-11 explicitly limits closure-feature column updates to M1–M10 (ten rows; all currently Planned). Reviewer verifies row scope at PR review.

### Dependencies

**Internal Dependencies**:
- **F-A1 (taxonomy crosswalk)**: `schemas/taxonomy/owasp.yaml` includes M1–M10 entries — **VERIFIED at PRD time** (10 of 10 records present with `full_id: OWASP-MOBILE-2024-M{N}`).
- **F-A2 (`source_attribution` schema field)**: Schema 1.6 → 1.7 ships the data-shape contract — **SATISFIED** (Feature 189 delivered 2026-04-17).
- **F-3 (ASI07 enrichment)**: Establishes single-agent enrichment-branch precedent — **SATISFIED** (Feature 219 delivered 2026-04-25).
- **F-5 (LLM10 enrichment)**: Establishes two-agent enrichment-branch precedent — **SATISFIED** (Feature 229 delivered 2026-04-27).
- **F-6 (ML Top 10 enrichment)**: Establishes three-agent enrichment-branch precedent + ADR-035 closing forward-scope marker forecast for F-7 four-or-five-agent execution — **SATISFIED** (Feature 232 delivered 2026-04-28).

**External Dependencies**: None.

**Dependency Graph**:
```
[F-7: Mobile Top 10 Coverage Bundle]
  ├─ Depends on: F-A1 (taxonomy crosswalk) — SATISFIED (M1–M10 verified)
  ├─ Depends on: F-A2 (source_attribution schema) — SATISFIED
  ├─ Depends on: F-3 (single-agent enrichment precedent) — SATISFIED
  ├─ Depends on: F-5 (two-agent enrichment precedent) — SATISFIED
  ├─ Depends on: F-6 (three-agent enrichment precedent + four-or-five-agent forecast) — SATISFIED
  └─ Blocks (precedent-shaping): F-8 (Tier 3 Web/API bundle, scope TBD)
```

---

## ❓ Open Questions

### Product Questions

- [ ] **Q1: M8 split decision (single-host vs dual-host)** — Does M8 Security Misconfiguration produce one Pattern Category on a single host (privilege-escalation OR repudiation) or two Pattern Categories split across both? Default: dual-host (one category per agent with disjoint architectural-tells). Owner: architect — Due: plan day 2026-04-29.
- [ ] **Q2: Mobile-banking-app vs alternative example archetype** — Should the F-7 mutation target be `mobile-banking-app/` (PRD recommendation), or `mobile-iot-companion/`, `mobile-ehr-app/`, or another mobile archetype? Default: mobile-banking-app for breadth (covers credentials, payment, biometrics, secure storage, certificate pinning, all M-items). Owner: product-manager + architect — Due: plan day 2026-04-29.

### Technical Questions

- [ ] **Q3: MITRE ATT&CK Mobile catalog-resolvability for T1474 / T1626 / T1398** — Which entries exist in `schemas/taxonomy/mitre-attack.yaml`? Catalog-resolvable entries appear in `references` array; non-catalog entries appear in `mitigation` prose only. Owner: architect — Due: plan day 2026-04-29.
- [ ] **Q4: MASTG / MASVS reference granularity** — Should pattern categories cite MASTG / MASVS at the **section level** (e.g., MASTG-AUTH, MASVS-CRYPTO) or at the **test-case-ID level** (e.g., MSTG-AUTH-1, MSTG-CRYPTO-1)? Default: section level — preserves consistency with F-6's MASTG-style cross-references and matches the granularity at which the Mobile community typically discusses controls. Test-case-ID granularity is a F-A1 follow-on. Owner: architect — Due: plan day 2026-04-29.
- [ ] **Q5: ADR-036 mapping-table column structure** — should the table have a "severity-hint" column (mirroring ADR-034's 5-row table and ADR-035's 11-row table)? Default: yes, matching ADR-034 / ADR-035 structure for consistency. Owner: architect — Due: plan day 2026-04-29.

### Design Questions

- [ ] **Q6: New `examples/mobile-banking-app/` baseline strategy** — Once authored, should `mobile-banking-app/` be added to `BASELINE_EXAMPLES` for future byte-identity testing (after F-7 ships), or remain excluded as a mutation target until an explicit promotion event? Default: excluded until a future feature promotes it (mirrors F-6's predictive-ml-app/, F-3/F-5's agentic-app, F-4's consumer-agent-app precedent — mutation targets stay excluded). Owner: tester — Due: build day 2026-05-04.

---

## 📚 References

### Product Documentation
- Product Vision: [`docs/product/01_Product_Vision/product-vision.md`](../01_Product_Vision/product-vision.md)
- Roadmap: [`docs/product/03_Product_Roadmap/`](../03_Product_Roadmap/)
- BLP-01 Strategy Doc: [`_internal/strategy/BLP-01-threat-coverage.md`](../../../_internal/strategy/BLP-01-threat-coverage.md) §F-7, §6 Coverage Matrix, §7 Bundling Rule
- GUIDE Threat Coverage Research: [`_internal/strategy/GUIDE-threat-coverage-research.md`](../../../_internal/strategy/GUIDE-threat-coverage-research.md) §4 OWASP Mobile Top 10:2024, §11 Heuristic A signal-class taxonomy (with F-7 worked example)
- SDR-001 Decision 4: [`_internal/strategy/SDR-001-threat-coverage-strategy.md`](../../../_internal/strategy/SDR-001-threat-coverage-strategy.md) (enrichment-branch rule)

### Technical Documentation
- Constitution: [`.aod/memory/constitution.md`](../../../.aod/memory/constitution.md)
- ADR-021: byte-identity invariant under `SOURCE_DATE_EPOCH=1700000000`
- ADR-023 Decision 1 + Decision 3: tier caps and additive-only edit discipline for skill-reference enrichment
- ADR-027: ADR Proposed → Accepted dual-commit pattern
- ADR-028 Decision 6: F-A2 ships data-shape contract; F-A3 ships populator wiring
- ADR-030 Decision 1: Heuristic A signal-class taxonomy in LLM tier
- ADR-032: F-3 single-agent enrichment-branch precedent (ASI07 / `tool-abuse`)
- ADR-034: F-5 two-agent enrichment-branch precedent (LLM10 / `denial-of-service` + `model-theft`)
- ADR-035: F-6 three-agent enrichment-branch precedent (ML01/03/04/06/07/08 / `tampering` + `data-poisoning` + `model-theft`); closing forward-scope marker forecasts F-7 four-or-five-agent execution
- F-082 PRD + ADR: lean-agent skill-references pattern (the enabling structural rule)
- Tachi finding schema: [`schemas/finding.yaml`](../../../schemas/finding.yaml) v1.8 post-F-4 baseline (preserved through F-5, F-6, F-7)
- OWASP taxonomy: [`schemas/taxonomy/owasp.yaml`](../../../schemas/taxonomy/owasp.yaml) M1–M10 entries (per F-A1, verified at PRD time)

### External Resources
- [OWASP Mobile Top 10:2024](https://owasp.org/www-project-mobile-top-10/) — primary source taxonomy
- [OWASP Mobile Application Security Testing Guide (MASTG)](https://mas.owasp.org/MASTG/) — detection-pattern depth for mobile credential handling, binary protection, transport security, secure storage
- [OWASP Mobile Application Security Verification Standard (MASVS)](https://mas.owasp.org/MASVS/) — control-category cross-reference for Mitigation blocks (MASVS-AUTH, MASVS-ARCH, MASVS-RESILIENCE, MASVS-CRYPTO, MASVS-NETWORK, MASVS-STORAGE, MASVS-PRIVACY, MASVS-PLATFORM)
- [MITRE ATT&CK for Mobile](https://attack.mitre.org/matrices/mobile/) — T1474 Supply Chain Compromise, T1626 Abuse Elevation Control Mechanism, T1398 Boot or Logon Initialization Scripts; cross-reference grounding for STRIDE-mobile pattern pairings
- [Android Jetpack Security](https://developer.android.com/jetpack/androidx/releases/security) — EncryptedSharedPreferences, Android Keystore reference for M1, M9, M10 mitigation specificity
- [iOS Keychain Services](https://developer.apple.com/documentation/security/keychain_services) — Keychain reference for M1, M3, M9 mitigation specificity
- [Play Integrity API](https://developer.android.com/google/play/integrity) — Android attestation reference for M8 mitigation specificity
- [DeviceCheck](https://developer.apple.com/documentation/devicecheck) — iOS attestation reference for M8 mitigation specificity

---

## ✅ Approval & Sign-Off

### PRD Review Checklist

**Product Manager** (product-manager):
- [x] Problem statement is clear and user-focused (mobile-platform threat-coverage gap closes mobile detection in tachi).
- [x] User stories have measurable acceptance criteria with specific finding-emission expectations.
- [x] Success metrics are defined and measurable (ten coverage matrix transitions, ≥10 new findings on mutation target, 6/6 byte-identical baselines).
- [x] Scope is realistic for timeline (3 working days + 1 buffer day, sized at +0.5 day over F-6 to absorb wider scope).
- [x] Risks and dependencies identified (R1–R9 with mitigation; F-A1, F-A2, F-3, F-5, F-6 SATISFIED).
- [x] Aligns with product vision (closes fourth major OWASP framework — Mobile Top 10 — alongside LLM, Agentic, ML).

**Architect**:
- [ ] Technical requirements are clear (FR-1 through FR-11 with file paths, edit posture, line-cap verification).
- [ ] Non-functional requirements are realistic (≤7% pipeline latency, byte-identity preservation, tier caps).
- [ ] Dependencies are accurate (F-A1, F-A2 satisfied; F-3, F-5, F-6 establish precedent).
- [ ] Technical risks are identified (R1–R8 cover authoring surface, M8 split, catalog-resolvability, cross-agent coordination, baseline drift).
- [ ] Architecture approach is sound (Heuristic A enrichment-branch at four-or-five-agent fan-out per ADR-035 forecast).

**Engineering Lead** (team-lead):
- [ ] Requirements are implementable (additive edits to 8-or-10 existing files; standard /aod.build wave allocation).
- [ ] Effort estimates are reasonable (3 working days, sized at +0.5 day over F-6's 2.5 days; buffer + reserve days).
- [ ] Team capacity is available (single feature in window; F-8 sequential).
- [ ] Timeline is realistic (Thu–Mon build with Tue reserve; calendar verified `cal 4 2026` + `cal 5 2026`).

### Approval Status

| Role | Name | Status | Date | Comments |
|------|------|--------|------|----------|
| Product Manager | product-manager | ✅ Approved | 2026-04-28 | v2 absorbs architect MEDIUM-1 (SC-16 label inversion fix) + MEDIUM-3 (F-6 issue #232 closed); MEDIUM-2 + team-lead MEDIUM-1/2 deferred to plan-day artifacts |
| Architect | architect | 🟡 Approved with Concerns | 2026-04-28 | 0 BLOCKING / 0 HIGH / 3 MEDIUM / 4 LOW; Heuristic A four-or-five-agent protocol compliance FULL; full review at `.aod/results/architect-prd-237.md` |
| Engineering Lead | team-lead | 🟡 Approved with Concerns | 2026-04-28 | 0 BLOCKING / 0 HIGH / 2 MEDIUM / 3 LOW; calendar verified; dependencies satisfied (F-6 #232 closed at PRD time); sizing defensible at +0.5 day over F-6; full review at `.aod/results/team-lead-prd-237.md` |

Legend: ✅ Approved | 🟡 Approved with Comments | ❌ Rejected | 📋 Pending

### Definition of Done

1. ✅ `spoofing.md` `owasp_references` extended with OWASP M1:2024 + M3:2024 (additive); existing entries preserved byte-identically.
2. ✅ `spoofing.md` `## Purpose` extended with mobile credential storage and mobile session handling surfaces (additive); pre-existing prose preserved.
3. ✅ `spoofing` companion gains 2 new Pattern Categories (M1, M3); existing 146 lines preserved byte-identically.
4. ✅ `tampering.md` `owasp_references` extended with OWASP M2/M4/M7:2024 (additive); existing entries (including F-6 ML01:2023) preserved byte-identically.
5. ✅ `tampering.md` `## Purpose` extended with mobile SDK supply-chain, mobile IPC, mobile binary protections surfaces (additive); pre-existing prose preserved.
6. ✅ `tampering` companion gains Pattern Categories 11 (Mobile Supply Chain), 12 (Mobile IPC Input Validation), 13 (Insufficient Mobile Binary Protections); existing 221 lines (post-F-6) preserved byte-identically.
7. ✅ `info-disclosure.md` `owasp_references` extended with OWASP M5/M6/M9/M10:2024 (additive); existing entries preserved byte-identically.
8. ✅ `info-disclosure.md` `## Purpose` extended with mobile transport security, mobile privacy, mobile data storage, mobile cryptography surfaces (additive); pre-existing prose preserved.
9. ✅ `info-disclosure` companion gains 4 new Pattern Categories (M5, M6, M9, M10); existing 192 lines preserved byte-identically.
10. ✅ M8 host(s) (`privilege-escalation` and/or `repudiation`) gain `OWASP M8:2024` in `owasp_references` and 1 or 2 new Pattern Categories per plan-day decision; existing entries preserved byte-identically.
11. ✅ ADR-036 committed with Status: Accepted; canonical 10-or-11-row mapping table populated; Heuristic A four-or-five-agent narrative; M4 cross-agent boundary clarification with F-1's `output-integrity`; M8 split decision recorded; cross-references to ADR-023 D3, ADR-030 D1, ADR-032, ADR-034, ADR-035 (with explicit citation of ADR-035 closing forward-scope marker).
12. ✅ All 6 non-mobile example baselines pass byte-identity verification under `SOURCE_DATE_EPOCH=1700000000` (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference). Owner: tester.
13. ✅ New `examples/mobile-banking-app/` example authored and regenerated with ≥10 new Mobile findings (≥1 per M1–M10); intentional baseline created.
14. ✅ BLP-01 Coverage Matrix ten-row update: M1, M2, M3, M4, M5, M6, M7, M8, M9, M10 all Planned → Covered, with Feature 237 (F-7) named as closure feature for all ten.
15. ✅ Schema invariant: `schemas/finding.yaml` `schema_version` remains `"1.8"`; `id.pattern` regex unchanged. F-7 is the fourth no-schema-bump enrichment after F-3, F-5, F-6.
16. ✅ 18-or-20-of-28 file zero-edit invariant verified on the non-target detection-tier files; 8 or 10 F-7 targets are the only files with material changes.
17. ✅ Triad sign-off recorded on `tasks.md` (PM + Architect + Team-Lead).
18. ✅ PR #NNN squash-merged with `feat(237):` Conventional Commit title per `.claude/rules/git-workflow.md` two-step Pre-merge + Post-merge enforcement; release-please PR opened within ~30s of merge.

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-28 | product-manager | Initial PRD draft for F-7 Mobile Top 10 Coverage Bundle (Tier 2 second feature; four-or-five-agent enrichment per ADR-035 closing forward-scope marker forecast). Submitted to parallel Architect + Team-Lead review. |
| 2.0 | 2026-04-28 | product-manager | v2 absorbs architect MEDIUM-1 (SC-16 inverted dual/single-host labels corrected — single-host = 20 of 28 zero-edit, dual-host = 18 of 28 zero-edit) and architect MEDIUM-3 (F-6 issue #232 closed at PRD time via `gh issue close 232` citing PR #235 squash-merge commit `e325375`). All three Triad sign-offs recorded: PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS. Architect MEDIUM-2 (ADR-036 9-vs-10-decision structure with Pattern Category Disambiguation as discrete D-numbered decision) and team-lead MEDIUM-1/2 (plan-day overload via parallel mobile-banking-app authoring track; Day 2 AM throughput via FR-6 4-subtask split) deferred to plan-day spec/plan/tasks artifacts per architect + team-lead explicit guidance. PRD ready for /aod.plan. |
