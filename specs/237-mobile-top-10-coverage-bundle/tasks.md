---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-29
    status: APPROVED_WITH_CONCERNS
    notes: "Post-build T073 (2026-04-29): 17/17 FRs + 20/20 SCs + 3/3 P1 US scenarios PASS (T054-T058 + T066 + T070 + T071 verify; 16 mobile-tier findings on mobile-banking-app regen; OWASP four-framework 40/40). Code-review HIGH-1 (19 broken /2024-risks/ URLs) + MEDIUM-1 (mitre-atlas/mitre-attack mislabel x2) FIXED INLINE at Wave 5.2 commit 428f89b. 3 MEDIUM + 2 LOW new post-build concerns deferred to T077 retrospective. Plan-time 2 MEDIUM + 4 LOW absorbed inline as planned. APPROVED_WITH_CONCERNS for /aod.deliver close-out. Plan-time review: .aod/results/product-manager-tasks-237.md. Post-build review: .aod/results/product-manager-tasks-237-postbuild.md."
  architect_signoff:
    agent: architect
    date: 2026-04-29
    status: APPROVED_WITH_CONCERNS
    notes: "Post-build T073 (2026-04-29): 0 BLOCKING / 0 HIGH / 2 MEDIUM / 2 LOW new post-build concerns (separate from plan-time 0/0/2/4 baseline). All 14 architect criteria substantively PASS post-build. ADR-036's 10 D-numbered Decisions all operationalized. Heuristic A four-or-five-agent enrichment-branch fourth execution confirmed without schema bump (finding.yaml 1.8 unchanged; fulfills ADR-035 closing forward-scope marker forecast). 22-file zero-edit invariant preserved; 6/6 byte-identity baselines green at T066 + re-verified T070 post-HIGH-1/MEDIUM-1 polish. M8 dual-host disjoint-tells (D-4) operationalized; M4 cross-axis with F-1 output-integrity (D-5) cited 3x in tampering Cat 12. Plan-time MEDIUM-1 (T069 verify-before-apply math) absorbed correctly: actual frozenset = 5 pre-edit, +4 → 9 post-edit. Code-reviewer T071 HIGH-1 + MEDIUM-1 fixed inline at commit 428f89b; MEDIUM-2/3/4 + LOW-1/2 deferred to T077 retrospective. APPROVED_WITH_CONCERNS for /aod.deliver close-out. Plan-time review: .aod/results/architect-tasks-237.md. Post-build review: .aod/results/architect-tasks-237-postbuild.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-29
    status: APPROVED_WITH_CONCERNS
    notes: "Post-build T073 (2026-04-29): 0 BLOCKING / 0 HIGH / 1 MEDIUM / 1 LOW new post-build concerns. 3.0-day envelope collapsed to ~19hr wall-clock (Tue 2026-04-28 14:32 → Wed 2026-04-29 09:34) — reserve day Tue 2026-05-05 untouched; close-out Mon 2026-05-04 likely advances to same-day Wed 2026-04-29 PM if /aod.deliver runs cleanly. 0 rollbacks invoked across T-NN-1/2/3 + M5-1/M6-1/M9-1/M10-1 sub-checkpoints. All agent loading within plan targets (senior-backend-engineer ~70%, architect ~25%, tester ~25%, code-reviewer 1 task, PM+team-lead sign-off only). Plan-time MEDIUM-1 + MEDIUM-2 absorbed favorably (Wave 0.0/0.1 mobile-banking-app authoring + Wave 3.x 4-subtask split). Wave 4.2 direct-sub-agent-invocation pattern (bypassing orchestrator context-saturation) codify as F-8 precedent at T077 retrospective. T074/T076/T077/T078 scheduled in Wave 5.5. APPROVED_WITH_CONCERNS for /aod.deliver close-out. Plan-time review: .aod/results/team-lead-tasks-237.md. Post-build review: .aod/results/team-lead-tasks-237-postbuild.md."
---

# Tasks: Mobile Top 10 Coverage Bundle (F-7 / Feature 237)

**Input**: Design documents from `/specs/237-mobile-top-10-coverage-bundle/`
**Prerequisites**: spec.md (PM APPROVED), plan.md (PM + Architect APPROVED_WITH_CONCERNS), research.md, data-model.md, contracts/finding-contract.md, quickstart.md

**Tests**: REQUIRED per Constitution VI (Testing Excellence) — F-7 ships with new structural-diff + line-count + MAESTRO grep + Pattern Category Disambiguation header presence (5 dual-host) + references-array fixture tests + ATT&CK Mobile catalog-resolvability gap test at `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py`. Backward-compatibility byte-identity test at `tests/scripts/test_backward_compatibility.py` runs as gate (additive infrastructure update: `DETECTION_AGENT_PATHS` 8 → 3 dual-host; `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` 5 → 9 dual-host; `mobile-banking-app` added to mutation-target exclusion list).

**Organization**: Tasks are grouped by user story (US-1 / US-2 / US-3 from spec.md) to enable independent implementation and testing of each. The three P1 stories are operationalized through 22 sequential waves (0.0 / 0.1 / 1.0 / 1.1 / 2.0 / 2.1 / 2.2 / 2.3 / 3.0 / 3.1 / 3.2 / 3.3 / 3.4 / 4.0 / 4.0b / 4.1 / 4.2 / 5.0 / 5.1 / 5.2 / 5.3 / 5.4 / 5.5 / 5.6) with explicit owner assignments + reserve day reserved.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 / US2 / US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project** (tachi methodology toolkit): `.claude/agents/tachi/`, `.claude/skills/tachi-*/references/`, `docs/architecture/02_ADRs/`, `tests/scripts/`, `examples/`, `specs/`, `_internal/strategy/`
- All paths are absolute from repo root `/Users/david/Projects/tachi/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prerequisites already satisfied at PRD/spec/plan time; this phase is a verification gate before Wave 0.0 begins on PRD-day evening (Tue 2026-04-28 PM).

- [X] T001 Verify all 10 baseline files match expected line counts: `wc -l .claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md .claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md` returns exactly 51 / 55 / 54 / 52 / 50 / 146 / 221 / 192 / 213 / 148
- [X] T002 Verify schema invariant: `grep -E '^schema_version:|^\s+pattern:' schemas/finding.yaml` returns `schema_version: "1.8"` + `pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"` unchanged
- [X] T003 Verify M1-M10 catalog-resolvability: `grep -c "^- id: M[0-9]" schemas/taxonomy/owasp.yaml` returns 10 (verified at PRD/spec/plan time)
- [X] T004 Verify ATT&CK Mobile catalog gap (Q3 plan-time RESOLVED): `for t in T1474 T1626 T1398; do grep -c "^- id: $t" schemas/taxonomy/mitre-attack.yaml; done` returns 0/0/0 (3 of 3 absent — ALL prose-only at worst-case scale; mirrors F-5 1-of-1 + F-6 3-of-6 ATLAS-gap precedent)
- [X] T005 Verify ADR-036 is next-available: `ls docs/architecture/02_ADRs/ADR-03*` shows ADR-035 highest existing
- [X] T006 Verify zero MAESTRO references in all 10 target files: `grep -i 'maestro' .claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md .claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md` returns no matches
- [X] T007 Verify all 5 host agents present in `finding-format-shared.md` consumers list: `grep -E '(spoofing|tampering|info-disclosure|privilege-escalation|repudiation)' .claude/skills/tachi-shared/references/finding-format-shared.md` returns ≥5 matches
- [X] T008 Verify zero structural mobile-platform indicators on existing examples (Q2 grounding): `grep -i 'android\|ios\|mobile\|keystore\|keychain\|sharedpref\|nsuser' examples/*/architecture.md` returns only the incidental match in `microservices/architecture.md` ("End-user browser or mobile app" generic External Entity descriptor — NOT structural). Confirms `examples/mobile-banking-app/` authoring is the default plan-day path.

---

## Phase 2: Foundational — Wave 0.0 + Wave 0.1 + Wave 1.0 + Wave 1.1 (PRD-day Evening + Plan-day Blocking Prerequisites)

**Purpose**: Mobile-banking-app skeleton (PRD-day evening per team-lead MEDIUM-1) → mobile-banking-app full draft (plan-day AM-early) → architect re-verification → ADR-036 Proposed commit + spoofing host enrichment (Wave 1.1). MUST complete before Wave 2.x can begin.

**CRITICAL**: No tampering or info-disclosure or M8 host authoring can begin until Wave 1.1 lands.

### Wave 0.0 — `examples/mobile-banking-app/` Skeleton Authoring (PRD-day evening Tuesday 2026-04-28 PM, ~2-3 hours per team-lead MEDIUM-1 plan-time RESOLVED)

- [X] T009 Architect drafts `examples/mobile-banking-app/architecture.md` skeleton (~80-120 lines) covering 5 of 6 mobile-platform topology indicators: (a) mobile client process (Android, fictional WellnessBank app), (b) credential-handling component using SharedPreferences, (c) secure-storage data store (SQLite on device), (d) mobile-backend API process the client communicates with, (e) third-party mobile SDK integration (analytics + payment). 6th indicator (exposed debug endpoint) added in Wave 0.1 full-draft pass. Architecture covers fictional mobile-banking application (clearly-fictional scenario per Constitution V Privacy)

### Wave 0.1 — `examples/mobile-banking-app/` Full Draft Completion + ADR-036 Proposed (Plan-day AM-early Wednesday 2026-04-29, ~4-5 hours)

- [X] T010 Architect + senior-backend-engineer co-author `examples/mobile-banking-app/architecture.md` full draft completion (~180-220 lines total) — extend skeleton with 6th indicator (exposed debug endpoint demonstrating M8 surface), normalize component naming, add data flows declaring certificate-pinning absence, add explicit clauses naming the absent controls (no Keystore/Keychain reference, no FLAG_SECURE, no SQLCipher, no root-detection, no certificate pinning, no signed-SDK policy)
- [X] T011 [P] Author placeholder `examples/mobile-banking-app/README.md` documenting the example as F-7 mutation target (excluded from `test_backward_compatibility.py` byte-identity loop per Q6 plan-time RESOLVED + FR-10)

### Wave 1.0 — Architect Re-Verification + ADR-036 Proposed Commit (Wed 2026-04-29 AM-mid, 30-60 min)

- [X] T012 Architect re-verifies all baseline assumptions: line counts (51/55/54/52/50 + 146/221/192/213/148), schema invariant (1.8 + id.pattern unchanged), catalog-resolvability (M1-M10 = 10/10; T1474/T1626/T1398 = 0/0/0), ADR-036 next-available, zero MAESTRO refs, consumer-list presence. Confirm Heuristic A protocol distinctness intact at four-or-five-agent scope per ADR-035 closing forward-scope marker forecast.
- [X] T013 Author ADR-036 Proposed at `docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md` (~370-420 lines) with **10 numbered Decisions** per architect MEDIUM-2 plan-time RESOLVED 10-decision structure: D-1 Heuristic A enrichment at four-or-five-agent scope (5 host agents in dual-host M8 path; 4 in single-host fallback; mobile-platform agent NOT created); D-2 additive-only edit discipline (ADR-023 D3); D-3 canonical 11-row sub-pattern → owning-agent mapping table with severity-hint annotation column populated COMPLETE per Q5 plan-time RESOLVED YES (10 closure rows + reference rows; M8 produces 2 rows in dual-host path); D-4 M8 dual-host disjoint architectural-tells (privilege-escalation Cat N+1 = privilege-gain variant; repudiation Cat N+1 = accountability-loss variant; mirrors ADR-035 D-4 ML06 two-facet precedent); D-5 M4 cross-agent boundary clarification with F-1 `output-integrity` (tampering Cat 12 owns mobile-IPC-input-side; output-integrity owns LLM-output-side; disjoint architectural-tells prevent duplicate emission on hybrid LLM+mobile architectures; mirrors ADR-035 D-5 ML03 vs ML04 disjoint-tells precedent at F-7 cross-axis layer); D-6 no schema bump (fourth no-bump enrichment after F-3/F-5/F-6; first at four-or-five-agent scope; fulfills ADR-035 closing forward-scope marker forecast); D-7 no consumers-list edit + ATT&CK Mobile catalog gap codification (T1474/T1626/T1398 prose-only at 3-of-3 worst-case scale per F-A2 referential-integrity contract); D-8 no functional orchestrator/dispatch edit; D-9 Pattern Category Disambiguation requirement on 5 companions in dual-host path (4 in single-host fallback) — mirrors F-3 ADR-032 D7 + F-5 ADR-034 D7 + F-6 ADR-035 D-9 precedent at four-or-five-agent scale; D-10 no source_attribution populator wiring extension (F-A3 deferral). Cross-references: ADR-021, ADR-023, ADR-027, ADR-028, ADR-030 D1, ADR-031 D8 (asymmetry — F-7 does NOT invoke), ADR-032, ADR-034, ADR-035 closing forward-scope marker forecast (with explicit citation of forecast text). Revision History with provisional Proposed date 2026-04-29; SHA-fill placeholder for post-merge. Public-only governance per Option C.

### Wave 1.1 — spoofing Edits + Cat N+1/N+2 + Disambiguation + Fixtures (parallel, Wed 2026-04-29 AM-late)

- [X] T014 [US1] Edit `.claude/agents/tachi/spoofing.md` Edit 1: extend metadata YAML `owasp_references` with `"OWASP M1:2024 — Improper Credential Usage"` and `"OWASP M3:2024 — Insecure Authentication/Authorization"` appended; pre-existing entries byte-identical (FR-1)
- [X] T015 [US1] Edit `.claude/agents/tachi/spoofing.md` Edit 2: extend `## Purpose` section with 1–3 line additive append naming the mobile credential storage and mobile session handling surfaces alongside existing identity-spoofing surface; pre-existing prose byte-identical (FR-2)
- [X] T016 [US1] Edit `.claude/agents/tachi/spoofing.md` Edit 3: extend Detection Workflow Step 5 references list with `OWASP M1:2024, OWASP M3:2024, MASTG-AUTH, MASVS-AUTH` exemplar mention; existing references byte-identical (FR-2). Verify post-edit line count ≤120 (target 55-60)
- [X] T017 [US1] Edit `.claude/skills/tachi-spoofing/references/detection-patterns.md`: append **Pattern Category N+1 — Improper Mobile Credential Usage (M1)** after current last category (~line 146) with primary OWASP M1:2024, MASTG-AUTH + MASVS-CRYPTO in mitigation prose at section-level granularity (Q4 plan-time RESOLVED); ≥4 indicators (target 6: mobile client component declared + credentials in SharedPreferences/NSUserDefaults/plaintext SQLite/app-bundled config + no platform-managed Keystore/Keychain reference + hardcoded API keys/secrets in mobile binary + no biometric-bound key release + no credential rotation policy); ≥1 worked example (mobile-banking app persisting login credentials in SharedPreferences with `MODE_PRIVATE` rather than EncryptedSharedPreferences); named mobile-specific mitigations (platform-managed secure storage Android Keystore + iOS Keychain, credential rotation, no hardcoded secrets in shipped binaries, biometric-bound key release for sensitive operations) (FR-3 part 1)
- [X] T018 [US1] Edit `.claude/skills/tachi-spoofing/references/detection-patterns.md`: append **Pattern Category N+2 — Insecure Mobile Authentication / Authorization (M3)** after Cat N+1 with primary OWASP M3:2024, MASTG-AUTH + MASVS-AUTH in mitigation prose; ≥4 indicators (target 6: mobile client component declared + bypassed certificate pinning/pinning-only-on-specific-domains + broken or absent JWT validation + weak refresh-token handling + missing step-up authentication + client-side authorization decisions not re-validated); ≥1 worked example (mobile-banking app missing biometric step-up on money-movement + certificate pinning enabled only on production domain leaving staging exposed); named mitigations (server-side authorization enforcement, certificate pinning with backup-pin rotation, refresh-token binding to device fingerprint, biometric step-up on high-risk operations) (FR-3 part 2)
- [X] T019 [US2] Edit `.claude/skills/tachi-spoofing/references/detection-patterns.md`: append **Pattern Category Disambiguation** subsection after Cat N+2 explicitly drawing the boundary between Cat 1–N (existing identity/credential signal class — generic web/API authentication-bypass, credential-stuffing) and Cat N+1/N+2 (mobile-specific credential storage and mobile-specific authentication/authorization). Same architecture (hybrid web+mobile) may legitimately surface both pre-existing and Cat N+1/N+2 findings without duplication (ADR-036 D-9 / FR-3)
- [X] T020 [US1] Edit `.claude/skills/tachi-spoofing/references/detection-patterns.md`: append Primary Sources extension with `OWASP M1:2024 — Improper Credential Usage`, `OWASP M3:2024 — Insecure Authentication/Authorization` (FR-3 / SC-11)
- [X] T021 [P] [US1] Author spoofing Cat N+1 fixture finding at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_n_plus_1_spoofing_mobile_credential_finding.yaml` per `contracts/finding-contract.md` Cat N+1 (S) shape — including `references: ["OWASP M1:2024 — Improper Credential Usage"]`
- [X] T022 [P] [US1] Author spoofing Cat N+2 fixture finding at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_n_plus_2_spoofing_mobile_authentication_finding.yaml` per `contracts/finding-contract.md` Cat N+2 (S) shape — including `references: ["OWASP M3:2024 — Insecure Authentication/Authorization"]`

**Checkpoint**: ADR-036 Proposed committed with 11-row mapping table populated COMPLETE; `spoofing.md` 3 additive edits applied (≤120 lines verified); spoofing companion Cat N+1 + Cat N+2 + Pattern Category Disambiguation + Primary Sources extension applied; 2 fixtures authored. **Wave 2 can now start.**

---

## Phase 3: User Story 1 — Mobile Threat Coverage on a Mobile-Banking Architecture (Priority: P1) MVP

**Goal**: Surface findings covering the full OWASP Mobile Top 10:2024 surface (M1 through M10) through 4 (single-host M8) or 5 (dual-host M8 default) existing host agents on the new `mobile-banking-app/` architecture.

**Independent Test**: Given the new `mobile-banking-app/` architecture exhibiting all 6 mobile-platform topology indicators, running `/tachi.threat-model` emits ≥2 new `S-{N}` (Cat N+1/N+2 M1/M3), ≥3 new `T-{N}` (Cat 11/12/13 M2/M4/M7), ≥4 new `I-{N}` (Cat N+1/N+2/N+3/N+4 M5/M6/M9/M10), ≥1 new `E-{N}` (M8 privilege-gain variant), ≥1 new `R-{N}` (M8 accountability-loss variant) — aggregate ≥10 (single-host) or ≥11 (dual-host) Mobile findings across 10 closed Mobile Top 10 items.

### Wave 2 — tampering Edits + Cat 11/12/13 (Wed 2026-04-29 PM)

**Note**: Per F-6 Wave 2.1/2.2/2.3 precedent, Wave 2 is broken into three sequential category-by-category checkpoints (T-NN-1 / T-NN-2 / T-NN-3) at ~75-90 minutes each with rollback capability.

- [X] T023 [US1] Edit `.claude/agents/tachi/tampering.md` Edit 1: extend metadata YAML `owasp_references` with 3-line append: `"OWASP M2:2024 — Inadequate Supply Chain Security"`, `"OWASP M4:2024 — Insufficient Input/Output Validation"`, `"OWASP M7:2024 — Insufficient Binary Protections"`; pre-existing entries (including F-6 ML01:2023 + AML.T0015) byte-identical (FR-4 part 1)
- [X] T024 [US1] Edit `.claude/agents/tachi/tampering.md` Edit 2: extend `## Purpose` section with 1–3 line additive append naming the mobile SDK supply-chain integrity, mobile IPC input validation, and mobile binary protections surfaces alongside existing data-tampering surface and F-6 predictive-ML adversarial-input surface; pre-existing prose byte-identical (FR-4 part 2)
- [X] T025 [US1] Edit `.claude/agents/tachi/tampering.md` Edit 3: extend Detection Workflow Step 5 references list with `OWASP M2/M4/M7:2024, MASTG-ARCH/CODE/RESILIENCE, MASVS-PLATFORM/RESILIENCE` exemplar mention; T1474 named in prose only; existing references byte-identical. Verify post-edit line count ≤120 (target 60-66) (FR-4 part 3)
- [X] T026 [US1] Wave 2.1 / **CHECKPOINT T-NN-1**: Edit `.claude/skills/tachi-tampering/references/detection-patterns.md` PART 1 of 3 — append **Pattern Category 11 — Mobile Supply Chain Integrity (M2)** after F-6 Cat 10 with primary OWASP M2:2024, MASTG-ARCH + MITRE ATT&CK Mobile T1474 in mitigation prose only (catalog-absent per Q3 RESOLVED); ≥4 indicators (target 7: third-party mobile SDK integration declared + no checksum verification + no signed-artifact policy + sideloaded APK distribution + missing app-store provenance review + CocoaPods/Gradle/SPM unsigned sources + missing reproducible-build enforcement); ≥1 worked example (mobile-banking app integrating third-party analytics SDK pulled via Gradle from private Maven repo without checksum verification); named mitigations (SDK signature verification, dependency manifest pinning with reproducible builds, app-store-only distribution, supplier-provenance review gate before SDK adoption). **Self-review checkpoint**: re-read Cat 11 for indicator/example/citation/mitigation discipline before proceeding to T-NN-2 (FR-5 part 1)
- [X] T027 [US1] Wave 2.2 / **CHECKPOINT T-NN-2**: Edit `.claude/skills/tachi-tampering/references/detection-patterns.md` PART 2 of 3 — append **Pattern Category 12 — Mobile IPC Input Validation (M4)** after Cat 11 with primary OWASP M4:2024, MASTG-CODE + MASVS-PLATFORM in mitigation prose; **with explicit disjoint-tells annotation referencing F-1 `output-integrity` agent boundary per ADR-036 D-5**: tampering Cat 12 owns mobile-IPC-input-side validation; output-integrity owns LLM-output-side sanitization; ≥4 indicators (target 7: Android Activity/Service/BroadcastReceiver with `android:exported="true"` and no permission gating + iOS URL-scheme declaration with no parameter validation + deep-link handler reaching trusted operations without re-validation + exported ContentProvider with no permission scoping + pasteboard-injection paths into shared-clipboard handlers + missing Android App Links/iOS Universal Links claim verification); ≥1 worked example (mobile-banking app exporting `MoneyTransferActivity` without permission gating, accepting Intent extras `recipient_account` and `amount` directly into transfer logic without re-authentication); named mitigations (explicit Intent component routing, URL-scheme allowlist with parameter validation, deep-link claim verification Android App Links / iOS Universal Links, ContentProvider permission scoping with signature-level Android permissions). **Self-review checkpoint**: re-read Cat 12 for discipline + verify disjoint-tells annotation reference to F-1 boundary present (FR-5 part 2)
- [X] T028 [US1] Wave 2.3 / **CHECKPOINT T-NN-3**: Edit `.claude/skills/tachi-tampering/references/detection-patterns.md` PART 3 of 3 — append **Pattern Category 13 — Insufficient Mobile Binary Protections (M7)** after Cat 12 with primary OWASP M7:2024, MASTG-RESILIENCE + MASVS-RESILIENCE in mitigation prose; ≥4 indicators (target 6: mobile client production build declared + no root/jailbreak detection in security-critical features + no anti-tampering stubs RASP/integrity self-checks + no code obfuscation no ProGuard/R8 rules on Android no bitcode + symbol-stripping on iOS + debug symbols in shipped binaries + no emulator-detection on fraud-sensitive flows); ≥1 worked example (mobile-banking app shipping production builds with debug symbols and no root-detection on the money-transfer flow); named mitigations (root/jailbreak detection with policy-based response, RASP integration with attestation, ProGuard/R8 obfuscation on Android, bitcode + symbol-stripping on iOS, emulator-detection on payment and KYC flows). **Self-review checkpoint**: re-read Cat 13 for discipline. Apply Pattern Category Disambiguation subsection (Cat 11/12/13 vs Cat 1-9 generic + Cat 10 F-6 ML01; Cat 12 cross-link to F-1 output-integrity boundary explicitly named per ADR-036 D-5); apply Primary Sources extension with M2:2024 + M4:2024 + M7:2024 (FR-5 part 3 + FR-5 Disambiguation + SC-11)
- [X] T029 [P] [US1] Author tampering Cat 11 fixture at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_11_tampering_mobile_supply_chain_finding.yaml` (`references: ["OWASP M2:2024 — Inadequate Supply Chain Security"]`; T1474 prose-only)
- [X] T030 [P] [US1] Author tampering Cat 12 fixture at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_12_tampering_mobile_ipc_finding.yaml` (`references: ["OWASP M4:2024 — Insufficient Input/Output Validation"]`; with disjoint-tells annotation in description)
- [X] T031 [P] [US1] Author tampering Cat 13 fixture at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_13_tampering_mobile_binary_protections_finding.yaml` (`references: ["OWASP M7:2024 — Insufficient Binary Protections"]`)

**Checkpoint**: Wave 2 complete. tampering enrichment authored (221 → ~315-345 lines); line count verified ≤120 on agent (55 → 60-66); 3 fixtures authored; Pattern Category Disambiguation subsection appended.

### Wave 3 — info-disclosure Edits + Cat N+1/N+2/N+3/N+4 (Thu 2026-04-30 AM)

**Note**: Per team-lead MEDIUM-2 plan-time RESOLVED, Wave 3 FR-7 is split into FOUR sequential sub-task checkpoints (M5-1 / M6-1 / M9-1 / M10-1) at ~75-90 minutes each with rollback capability — mirrors F-6 Wave 2.x precedent at 4-cat scale.

- [X] T032 [US1] Edit `.claude/agents/tachi/info-disclosure.md` Edit 1: extend metadata YAML `owasp_references` with 4-line append: `"OWASP M5:2024 — Insecure Communication"`, `"OWASP M6:2024 — Inadequate Privacy Controls"`, `"OWASP M9:2024 — Insecure Data Storage"`, `"OWASP M10:2024 — Insufficient Cryptography"`; pre-existing entries byte-identical (FR-6 part 1)
- [X] T033 [US1] Edit `.claude/agents/tachi/info-disclosure.md` Edit 2: extend `## Purpose` section with 1–3 line additive append naming the mobile transport security, mobile privacy controls, mobile secure storage, and mobile cryptography surfaces alongside existing confidentiality-leakage surface; pre-existing prose byte-identical (FR-6 part 2)
- [X] T034 [US1] Edit `.claude/agents/tachi/info-disclosure.md` Edit 3: extend Detection Workflow Step 5 references list with `OWASP M5/M6/M9/M10:2024, MASTG-NETWORK/PRIVACY/STORAGE/CRYPTO, MASVS-NETWORK/PRIVACY/STORAGE/CRYPTO` exemplar mention; existing references byte-identical. Verify post-edit line count ≤120 (target 60-66) (FR-6 part 3)
- [X] T035 [US1] Wave 3.1 / **TEAM-LEAD MEDIUM-2 SUB-CHECKPOINT M5-1**: Edit `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` PART 1 of 4 — append **Pattern Category N+1 — Insecure Mobile Communication (M5)** after current last category (~line 192) with primary OWASP M5:2024, MASTG-NETWORK + MASVS-NETWORK in mitigation prose at section-level granularity (Q4); ≥4 indicators (target 6: mobile client to mobile-backend Data Flow declared + cleartext HTTP traffic enabled (no `usesCleartextTraffic="false"` on Android, no `NSAppTransportSecurity` exception audit on iOS) + no TLS certificate pinning + HTTP-to-HTTPS downgrade attack path + weak TLS cipher acceptance + missing HSTS-equivalent enforcement at app-level); ≥1 worked example (mobile-banking app's network security config allows cleartext traffic to staging endpoints + missing certificate pinning on production endpoints); named mitigations (cleartext-traffic prohibition in network security config, certificate pinning with backup-pin rotation, TLS 1.3 with strict cipher allowlist, HSTS-equivalent enforcement at app-level). **Self-review checkpoint**: re-read Cat N+1 for indicator/example/citation/mitigation discipline before proceeding to M6-1 (FR-7 part 1)
- [X] T036 [US1] Wave 3.2 / **SUB-CHECKPOINT M6-1**: Edit `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` PART 2 of 4 — append **Pattern Category N+2 — Inadequate Mobile Privacy Controls (M6)** after Cat N+1 with primary OWASP M6:2024, MASTG-PRIVACY + MASVS-PRIVACY in mitigation prose; ≥4 indicators (target 6: mobile client component declared + PII/PHI persisted in device-local caches without TTL expiry + telemetry/analytics SDKs collecting personal data without disclosure or consent gating + clipboard exposure on sensitive fields + screenshot leakage on sensitive screens (no FLAG_SECURE on Android, no equivalent on iOS) + over-broad permission requests on first launch); ≥1 worked example (mobile-banking app caching account-balance data without TTL + missing FLAG_SECURE on the transaction-history screen); named mitigations (data-minimization on caches with TTL enforcement, consent-gated telemetry with opt-out, FLAG_SECURE / equivalent screenshot prevention on PII screens, just-in-time permission prompts with graceful denial paths). **Self-review checkpoint**: re-read Cat N+2 for discipline before proceeding to M9-1 (FR-7 part 2)
- [X] T037 [US1] Wave 3.3 / **SUB-CHECKPOINT M9-1**: Edit `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` PART 3 of 4 — append **Pattern Category N+3 — Insecure Mobile Data Storage (M9)** after Cat N+2 with primary OWASP M9:2024, MASTG-STORAGE + MASVS-STORAGE in mitigation prose; ≥4 indicators (target 6: mobile client component declared + unencrypted SQLite/Realm/Room database on device + unencrypted KeyValue store SharedPreferences/NSUserDefaults plaintext + cloud-backup leakage iCloud/Google Drive backup including sensitive app data without exclusion + external SD-card writes for sensitive files + world-readable file permissions on Android internal storage); ≥1 worked example (mobile-banking app storing transaction history in unencrypted SQLite without `allowBackup="false"` excluding it from Google Drive backup); named mitigations (SQLCipher / Realm encryption with platform-keyring-derived keys, EncryptedSharedPreferences Android Jetpack / Keychain-stored secrets iOS, `allowBackup="false"` on Android with sensitive data partitioning, internal-storage-only writes for sensitive files). **Self-review checkpoint**: re-read Cat N+3 for discipline before proceeding to M10-1 (FR-7 part 3)
- [X] T038 [US1] Wave 3.4 / **SUB-CHECKPOINT M10-1**: Edit `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` PART 4 of 4 — append **Pattern Category N+4 — Insufficient Mobile Cryptography (M10)** after Cat N+3 with primary OWASP M10:2024, MASTG-CRYPTO + MASVS-CRYPTO in mitigation prose; ≥4 indicators (target 6: mobile client component declared + weak key derivation on user PINs (low PBKDF2 iteration counts, no salting, no per-device entropy) + custom-rolled crypto algorithms in mobile binaries + hardcoded symmetric keys in shipped binaries + insecure PRNG seeding `java.util.Random` for security purposes + deprecated cipher suites DES/RC4/MD5/SHA1 for sensitive operations); ≥1 worked example (mobile-banking app deriving encryption keys from a 4-digit PIN with PBKDF2 iteration count of 1000 and no salting); named mitigations (platform-provided key derivation Argon2id/scrypt/PBKDF2 with ≥600k iterations, platform crypto APIs only with no custom algorithms, key derivation from platform-keyring-bound material, SecureRandom for all cryptographic randomness, AES-GCM and SHA-256+ as the minimum baseline). **Self-review checkpoint**: re-read Cat N+4 for discipline. Apply Pattern Category Disambiguation subsection (Cat N+1/N+2/N+3/N+4 vs Cat 1-N existing); apply Primary Sources extension with M5:2024 + M6:2024 + M9:2024 + M10:2024 (FR-7 part 4 + FR-7 Disambiguation + SC-11)
- [X] T039 [P] [US1] Author info-disclosure Cat N+1 fixture at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_n_plus_1_info_disclosure_mobile_communication_finding.yaml` (`references: ["OWASP M5:2024 — Insecure Communication"]`)
- [X] T040 [P] [US1] Author info-disclosure Cat N+2 fixture at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_n_plus_2_info_disclosure_mobile_privacy_finding.yaml` (`references: ["OWASP M6:2024 — Inadequate Privacy Controls"]`)
- [X] T041 [P] [US1] Author info-disclosure Cat N+3 fixture at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_n_plus_3_info_disclosure_mobile_data_storage_finding.yaml` (`references: ["OWASP M9:2024 — Insecure Data Storage"]`)
- [X] T042 [P] [US1] Author info-disclosure Cat N+4 fixture at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_n_plus_4_info_disclosure_mobile_cryptography_finding.yaml` (`references: ["OWASP M10:2024 — Insufficient Cryptography"]`)

**Checkpoint**: Wave 3 complete. info-disclosure enrichment authored (192 → ~315-345 lines); line count verified ≤120 on agent (54 → 60-66); 4 fixtures authored; Pattern Category Disambiguation subsection appended.

### Wave 4 — M8 Dual-Host (privilege-escalation + repudiation) Edits + Pattern Categories (Thu 2026-04-30 PM, dual-host per Q1 plan-time RESOLVED)

- [X] T043 [US1] Wave 4.0 PART A — privilege-escalation: Edit `.claude/agents/tachi/privilege-escalation.md` Edit 1: extend metadata YAML `owasp_references` with 1-line append: `"OWASP M8:2024 — Security Misconfiguration"`; pre-existing entries byte-identical (FR-8 part 1, dual-host)
- [X] T044 [US1] Wave 4.0 PART A — privilege-escalation: Edit `.claude/agents/tachi/privilege-escalation.md` Edit 2: extend `## Purpose` section with 1–3 line additive append naming the mobile security misconfiguration privilege-gain variant surface (exposed debug endpoints, default permissive ContentProvider/Service exports, missing app-attestation, missing root-detection on security-critical features) alongside existing broken-access-control / IDOR / role-escalation surfaces; pre-existing prose byte-identical (FR-8 part 2, dual-host)
- [X] T045 [US1] Wave 4.0 PART A — privilege-escalation: Edit `.claude/agents/tachi/privilege-escalation.md` Edit 3: extend Detection Workflow Step 5 references list with `OWASP M8:2024, MASTG-PLATFORM, MASVS-PLATFORM` exemplar mention; T1626 named in prose only; existing references byte-identical. Verify post-edit line count ≤120 (target 56-58) (FR-8 part 3, dual-host)
- [X] T046 [US1] Wave 4.0 PART A — privilege-escalation companion: Edit `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md`: append **Pattern Category N+1 — Mobile Security Misconfiguration: Privilege-Gain Variant (M8)** after current last category (~line 213) with primary OWASP M8:2024, MASTG-PLATFORM + MITRE ATT&CK Mobile T1626 in mitigation prose only (catalog-absent per Q3 RESOLVED); ≥4 indicators (target 6: mobile client production build declared + exposed debug endpoints `adb shell` access points / debug-only Activities exported + default permissive ContentProvider/Service exports without permission scoping + missing app-attestation Play Integrity/DeviceCheck enabling tampered-binary execution + missing root-detection in security-critical feature gates + missing certificate-pinning enforcement on debug builds shipped to production); ≥1 worked example (mobile-banking app's production build retaining debug-only Activity exposing internal database state via `adb shell am start` because debug guard removed during signing); named mitigations (production-build flag stripping debug code paths, ContentProvider/Activity export scoping with Android signature-level permissions, Play Integrity / DeviceCheck attestation gating, root-detection on security-critical UI flows). Apply Pattern Category Disambiguation subsection (Cat N+1 M8 privilege-gain variant vs Cat 1-N pre-existing broken-access-control/IDOR/role-escalation per ADR-036 D-9); Primary Sources extension with M8:2024 (FR-9 dual-host part A + ADR-036 D-9 + SC-11)
- [X] T047 [US1] Wave 4.0b PART B — repudiation: Edit `.claude/agents/tachi/repudiation.md` Edit 1: extend metadata YAML `owasp_references` with 1-line append: `"OWASP M8:2024 — Security Misconfiguration"`; pre-existing entries byte-identical (FR-8 part 1, dual-host)
- [X] T048 [US1] Wave 4.0b PART B — repudiation: Edit `.claude/agents/tachi/repudiation.md` Edit 2: extend `## Purpose` section with 1–3 line additive append naming the mobile security misconfiguration accountability-loss variant surface (missing audit logging on security-relevant events, disabled crash reporting in production, debug logs leaking sensitive data via Log.d/NSLog, missing tamper-evident timestamping) alongside existing missing-audit-trail / log-tampering surfaces; pre-existing prose byte-identical (FR-8 part 2, dual-host)
- [X] T049 [US1] Wave 4.0b PART B — repudiation: Edit `.claude/agents/tachi/repudiation.md` Edit 3: extend Detection Workflow Step 5 references list with `OWASP M8:2024, MASTG-PLATFORM, MASVS-PLATFORM` exemplar mention; T1398 named in prose only; existing references byte-identical. Verify post-edit line count ≤120 (target 54-56) (FR-8 part 3, dual-host)
- [X] T050 [US1] Wave 4.0b PART B — repudiation companion: Edit `.claude/skills/tachi-repudiation/references/detection-patterns.md`: append **Pattern Category N+1 — Mobile Security Misconfiguration: Accountability-Loss Variant (M8)** after current last category (~line 148) with primary OWASP M8:2024, MASTG-PLATFORM + MITRE ATT&CK Mobile T1398 in mitigation prose only (catalog-absent per Q3 RESOLVED); ≥4 indicators (target 6: mobile client component declared + missing audit logging on security-relevant mobile events login/money-movement/permission grants + disabled crash reporting in production + debug logs leaking sensitive data via `Log.d`/`NSLog` not stripped + missing tamper-evident timestamping on audit records the mobile app emits + missing log-integrity verification at backend ingestion gate); ≥1 worked example (mobile-banking app's production build retaining `Log.d("auth", "user=" + username + " token=" + token)` statements stripped only in obfuscation pass that wasn't applied to release config); named mitigations (structured audit logging on security-relevant mobile events with server-side persistence, production-build log-statement stripping ProGuard/R8 rules, tamper-evident timestamping on audit records, crash-reporting enablement with PII redaction). Apply Pattern Category Disambiguation subsection (Cat N+1 M8 accountability-loss variant vs Cat 1-N pre-existing missing-audit-trail/log-tampering per ADR-036 D-9); Primary Sources extension with M8:2024 (FR-9 dual-host part B + ADR-036 D-9 + SC-11)
- [X] T051 [US1] Architect integration walkthrough: re-read M8 dual-host disjoint-tells decision per ADR-036 D-4 against the two new Pattern Categories; confirm privilege-gain variant (Cat N+1 in privilege-escalation) and accountability-loss variant (Cat N+1 in repudiation) have disjoint architectural-tells with no overlap; same architecture exhibiting both variants may legitimately surface both findings without duplication
- [X] T052 [P] [US1] Author privilege-escalation M8 fixture at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_n_plus_1_privilege_escalation_mobile_misconfig_priv_gain_finding.yaml` (`references: ["OWASP M8:2024 — Security Misconfiguration"]`; T1626 prose-only)
- [X] T053 [P] [US1] Author repudiation M8 fixture at `tests/scripts/fixtures/mobile_top_10_coverage_bundle/valid_category_n_plus_1_repudiation_mobile_misconfig_accountability_loss_finding.yaml` (`references: ["OWASP M8:2024 — Security Misconfiguration"]`; T1398 prose-only)

**Checkpoint**: Wave 4 complete. M8 dual-host enrichment authored (privilege-escalation 213 → ~245-260 lines + repudiation 148 → ~180-195 lines); line counts verified ≤120 on both agents (52 → 56-58 + 50 → 54-56); 2 fixtures authored; Pattern Category Disambiguation subsections appended on both companions.

---

## Phase 4: User Story 2 — Four-or-Five-Agent Enrichment Without Architectural Surface Expansion (Priority: P1)

**Goal**: PR diff shows exactly 10 file edits + ADR-036 (dual-host path); 18 detection-tier files unchanged; schema invariant preserved; Pattern Category Disambiguation present on all 5 companions; M8 dual-host + M4 cross-agent boundary decisions in ADR-036.

**Independent Test**: `git diff --name-only main HEAD -- '.claude/agents/tachi/' '.claude/skills/tachi-*/references/'` returns exactly 10 files (dual-host); `git diff main HEAD -- schemas/finding.yaml` is empty; `grep -c "Pattern Category Disambiguation" .claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md` returns 1/1/1/1/1 (5 total dual-host).

### Wave 1.0 + Wave 1.1 (already covered T013 ADR-036 above)

ADR-036 D-numbered decisions are authored at T013 — Wave 1.0 fully operationalizes US-2's ADR deliverables:
- D-1 Heuristic A four-or-five-agent (architect MEDIUM-2 plan-time RESOLVED 10-decision structure)
- D-2 Additive-only edit discipline
- D-3 Canonical 11-row mapping table with severity-hint column (Q5 RESOLVED YES)
- D-4 M8 dual-host disjoint architectural-tells (Q1 RESOLVED dual-host)
- D-5 M4 cross-agent boundary clarification with F-1 output-integrity
- D-6 No schema bump (fourth no-bump enrichment; ADR-035 closing forward-scope marker forecast fulfilled)
- D-7 No consumers-list edit + ATT&CK Mobile catalog gap (Q3 RESOLVED 3-of-3 prose-only)
- D-8 No functional orchestrator/dispatch edit
- D-9 Pattern Category Disambiguation requirement on 5 companions (dual-host) — mirrors F-3/F-5/F-6 precedent
- D-10 No source_attribution wiring

### Wave 4-end verification of US-2 invariants (Thu 2026-04-30 PM late, after Wave 4.0/4.0b completion)

- [X] T054 [US2] Verify schema invariant gate (FR-13 / SC-15): `git diff main HEAD -- schemas/finding.yaml` is empty (zero lines)
- [X] T055 [US2] Verify 18-file zero-edit invariant (FR-14 / SC-16): `git diff --name-only main HEAD -- '.claude/agents/tachi/' '.claude/skills/tachi-*/references/'` returns exactly the 10 F-7 targets (dual-host); `git diff main HEAD -- '.claude/agents/tachi/orchestrator.md' '.claude/agents/tachi/output-integrity.md' '.claude/agents/tachi/misinformation.md' '.claude/agents/tachi/tool-abuse.md' '.claude/agents/tachi/human-trust-exploitation.md' '.claude/agents/tachi/denial-of-service.md' '.claude/agents/tachi/data-poisoning.md' '.claude/agents/tachi/model-theft.md' '.claude/agents/tachi/prompt-injection.md' '.claude/agents/tachi/agent-autonomy.md'` is empty
- [X] T056 [US2] Verify orchestrator + consumers list zero functional edit (FR-14 / SC-16): `git diff main HEAD -- .claude/skills/tachi-shared/references/finding-format-shared.md .claude/agents/tachi/orchestrator.md .claude/skills/tachi-orchestration/references/dispatch-rules.md` is empty
- [X] T057 [US2] Verify Pattern Category Disambiguation header presence on all 5 companions (ADR-036 D-9 dual-host): `grep -c "Pattern Category Disambiguation" .claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md` returns 1/1/1/1/1 (5 total)
- [X] T058 [US2] Verify zero MAESTRO references in all 10 enriched files (post-edit grep): `grep -i 'maestro' .claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md .claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md` returns 0 matches

**Checkpoint**: US-2 invariants verified. All structural enforceable invariants green.

---

## Phase 5: User Story 3 — Byte-Identical Regeneration on Non-Mobile Baselines + New `mobile-banking-app/` Mutation Target (Priority: P1)

**Goal**: 6 non-mobile baselines regenerate byte-identically; new `mobile-banking-app/` regenerates with ≥10 (single-host) or ≥11 (dual-host) new Mobile findings; agentic-app + consumer-agent-app + predictive-ml-app zero-touch.

**Independent Test**: `pytest tests/scripts/test_backward_compatibility.py -k "byte_identical" -v` passes 6/6; `examples/mobile-banking-app/` regen yields ≥10 new Mobile findings (≥1 per M1-M10).

### Wave 4.1 — Tester Early-Signal Spot-Check (parallel with Wave 4.0/4.0b; Thu 2026-04-30 PM)

- [X] T059 [P] [US3] Tester (per FR-15 separation-of-duties): early-signal byte-identity spot-check on `examples/web-app/` — regenerate via pipeline under `SOURCE_DATE_EPOCH=1700000000`; verify `diff -q examples/web-app/sample-report/security-report.pdf examples/web-app/sample-report/security-report.pdf.baseline` returns identical
- [X] T060 [P] [US3] Tester: early-signal byte-identity spot-check on `examples/maestro-reference/` — regenerate via pipeline; verify byte-identical against baseline

### Wave 4.2 — `mobile-banking-app/` End-to-End Regeneration (Thu 2026-04-30 PM late)

- [X] T061 [US3] Regenerate `examples/mobile-banking-app/` end-to-end via pipeline: `cd examples/mobile-banking-app && SOURCE_DATE_EPOCH=1700000000 /tachi.threat-model && SOURCE_DATE_EPOCH=1700000000 /tachi.risk-score && SOURCE_DATE_EPOCH=1700000000 /tachi.compensating-controls && SOURCE_DATE_EPOCH=1700000000 /tachi.infographic all && SOURCE_DATE_EPOCH=1700000000 /tachi.security-report` (FR-10)
- [X] T062 [US3] Verify aggregate ≥10 (single-host) or ≥11 (dual-host) new Mobile findings on `mobile-banking-app/`: ≥2 new `S-{N}` (Cat N+1/N+2 M1/M3) + ≥3 new `T-{N}` (Cat 11/12/13 M2/M4/M7) + ≥4 new `I-{N}` (Cat N+1/N+2/N+3/N+4 M5/M6/M9/M10) + ≥1 new `E-{N}` (M8 privilege-gain) + ≥1 new `R-{N}` (M8 accountability-loss) covering 10 closed Mobile Top 10 items (SC-12)
- [X] T063 [US3] Verify references-array carries OWASP Mobile primaries: `grep -E "OWASP M[0-9]+:2024" examples/mobile-banking-app/sample-report/threats.md` returns ≥10 distinct citations across the 10 closed M-items (SC-17)
- [X] T064 [US3] Verify ATT&CK Mobile catalog gap codification: `grep -E "T1474|T1626|T1398" examples/mobile-banking-app/sample-report/threats.md` returns matches in mitigation prose ONLY (NOT in `references:` arrays — ADR-036 D-7 prose-only fallback per Q3 RESOLVED)
- [X] T065 [US3] Commit `examples/mobile-banking-app/sample-report/security-report.pdf.baseline` as F-7 mutation target baseline (excluded from byte-identity loop in `test_backward_compatibility.py` per Q6 plan-time RESOLVED + FR-10; mirrors agentic-app + consumer-agent-app + predictive-ml-app precedent)

**Checkpoint**: Wave 4 complete. `mobile-banking-app/` regenerates with ≥10 new Mobile findings; tester spot-check confirms 2 of 6 baselines byte-identical (early signal).

### Wave 5.0 — Tester Full 6-Baseline Byte-Identity Verification (Fri 2026-05-01 AM-1)

**Note**: Per F-6 Wave 5.0/5.1 split precedent, Day 3 AM is split into AM-1 (tester) + AM-2 (architect) so the two activities don't share a single slot owner.

- [X] T066 [US3] **Wave 5.0 (AM-1)**: Tester runs full byte-identity verification across all 6 baselines under `SOURCE_DATE_EPOCH=1700000000` per ADR-021: `pytest tests/scripts/test_backward_compatibility.py -k "byte_identical" -v` returns 6/6 passing for `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference` (SC-13)

### Wave 5.1 — Architect ADR-036 Accepted Transition (parallel with Wave 5.0; Fri 2026-05-01 AM-2)

- [X] T067 [US2] **Wave 5.1 (AM-2)**: Architect transitions ADR-036 Proposed → Accepted at `docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md` Status field; Revision History gains "Accepted: 2026-05-01" line with provisional date (post-merge SHA fill at T078 below per F-1/F-2/F-3/F-4/F-5/F-6 precedent — placeholder SHA strategy = Option B keep `Status: Proposed` until PR squash-merge, atomic transition + SHA fill at T078)

### Wave 5.2 — Test Infrastructure + Enrichment Test Suite (Fri 2026-05-01 AM)

- [X] T068 [P] [US1] Author new `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py` (~500-600 lines) with tests: (a) line-count caps on all 5 host agents (≤120 STRIDE); (b) structural-diff byte-identity on Cat 1-N pre-existing in all 5 companions per ADR-023 D3; (c) MAESTRO grep returning 0 matches on all 10 enriched files; (d) Pattern Category Disambiguation header presence test (5 matches across 5 companions in dual-host path; 4 in single-host fallback); (e) references-array fixture validation for all 10 fixtures (Cat N+1/N+2 S + Cat 11/12/13 T + Cat N+1/N+2/N+3/N+4 I + M8 E + M8 R); (f) ATT&CK Mobile catalog-resolvability gap test asserting T1474/T1626/T1398 NOT in any references array (prose-only); (g) MANDATORY Read directive presence on all 5 host agents
- [X] T069 [P] [US1] Modify `tests/scripts/test_backward_compatibility.py` infrastructure: `DETECTION_AGENT_PATHS` removes 4 NEW F-7 hosts (`spoofing.md` + `info-disclosure.md` + `privilege-escalation.md` + `repudiation.md` — `tampering.md` already removed by F-6, so post-F-6 baseline = 8 entries; F-7 removes 4 → final = 4 dual-host path; in single-host fallback removes 3 → final = 5); `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset adds 4 NEW hosts (`tachi-spoofing` + `tachi-info-disclosure` + `tachi-privilege-escalation` + `tachi-repudiation` companions — `tachi-tampering` already from F-6); post-F-6 baseline frozenset count varies (architect MEDIUM-1 absorption: verify actual count via grep before applying delta — F-6 retrospective at T059 noted documentation discrepancy precedent of off-by-2 between asserted "5→7" and actual "3→5"; F-7 implementation MUST verify actual count first, then apply delta of +4 dual-host or +3 single-host); add `mobile-banking-app` to mutation-target exclusion list (alongside `agentic-app`, `consumer-agent-app`, `predictive-ml-app`)
- [X] T070 [US1] Run all tests: `pytest tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py tests/scripts/test_backward_compatibility.py -v` returns all green
- [X] T071 [US1] Code-review pass on all 10 file edits + ADR-036 + new example architecture (cross-reference completeness, ADR-036 D-numbered decisions complete, Pattern Category content quality on all 11 categories — 10 closure + Disambiguation subsections)

**Checkpoint**: Wave 5 AM complete. 6 baselines byte-identical (per tester per FR-15); ADR-036 Accepted (provisional date); new test file + infrastructure update green; code-review pass green.

---

## Phase 6: Wave 5.3 — Coverage Matrix Ten-Row Update (Fri 2026-05-01 PM)

**Goal**: BLP-01 strategy doc reflects ten row transitions + coverage milestone update.

- [X] T072 [US1] Update `_internal/strategy/BLP-01-threat-coverage.md` §6 Coverage Matrix: M1, M2, M3, M4, M5, M6, M7, M8, M9, M10 — all Planned → Covered. Closure-feature column populated with "Feature 237 (F-7)" for all 10 rows. Coverage milestones panel updated to OWASP Mobile Top 10:2024 = 10/10 Covered + OWASP four-framework total = 40/40 (combined post-F-6 OWASP three-framework = 30/30 + Mobile 10/10). Single commit per F-3/F-4/F-5/F-6 precedent (FR-12)

**Checkpoint**: Coverage Matrix ten-row transition committed.

---

## Phase 7: Wave 5.4–5.5 — Triple Sign-Off + Close-Out + Delivery Retrospective (Mon 2026-05-04 primary close-out per +0.5 day envelope vs F-6)

**Goal**: tasks.md triple sign-off, `/aod.deliver` close-out with `feat(237):` Conventional Commits PR title + post-merge release-please verification, delivery retrospective filed.

- [X] T073 [US1] PM, Architect, Team-Lead apply triple sign-off on tasks.md per `/aod.tasks` triple-sign-off protocol — frontmatter `triad.{pm,architect,techlead}_signoff` populated
- [ ] T074 [US1] Pre-merge: verify PR title is Conventional-Commit-formatted (`gh pr view 238 --json title --jq .title` returns `feat(237): Mobile Top 10 Coverage Bundle` or similar `feat(237):` prefix ≤70 chars); if non-conventional, retitle via `gh pr edit 238 --title "feat(237): Mobile Top 10 Coverage Bundle"` per `.claude/rules/git-workflow.md` Pre-merge enforcement
- [ ] T075 [US1] `/aod.deliver` close-out: squash-merge PR #238 via `gh pr merge 238 --squash`; pull main; commit final state
- [ ] T076 [US1] Post-merge: verify release-please PR opens within ~30s via `gh pr list --state open --search "release-please" --limit 3`; if empty, push empty release-marker commit `git commit --allow-empty -m "feat(237): Mobile Top 10 Coverage Bundle — release marker"` + `git push origin main` per F-212 incident precedent
- [ ] T077 [US1] Author delivery retrospective at `specs/237-mobile-top-10-coverage-bundle/delivery.md` (~180-220 lines) capturing: actual vs estimated effort; **fourth execution of Heuristic A enrichment branch at four-or-five-agent scope** lessons (precedent for F-8 Tier 3); M8 dual-host disjoint-tells coordination lessons (architect MEDIUM-2 absorbed at ADR-036 D-4); M4 cross-agent boundary with F-1 output-integrity coordination lessons (absorbed at ADR-036 D-5); Pattern Category Disambiguation lessons across 5 companions (architect MEDIUM-2 absorbed at ADR-036 D-9); team-lead MEDIUM-1 PRD-day evening + plan-day full-draft mobile-banking-app authoring track efficacy (Wave 0.0 + 0.1 sequencing); team-lead MEDIUM-2 Wave 3.x 4-subtask split efficacy (M5-1/M6-1/M9-1/M10-1 sequential rollback capability); ATT&CK Mobile catalog gap propagation handling (3 of 3 prose-only at worst-case scale); byte-identity preservation evidence (FR-15 grep proofs across 6 baselines + new `mobile-banking-app/` ≥10-or-11 findings); canonical 11-row mapping table audit-deliverable lessons; ADR-036 Accepted-commit SHA-fill execution; any deviations from PRD timeline or scope
- [ ] T078 [US1] Post-merge ADR-036 SHA fill: capture squash-merge SHA via `git rev-parse HEAD` and update ADR-036 Revision History line "Accepted: 2026-05-04 (squash commit: <SHA>)"; commit `docs(237): ADR-036 Accepted — post-merge SHA fill`

**Checkpoint**: F-7 delivered. PR squash-merged with `feat(237):` title; release-please confirmed firing; delivery retrospective filed; ADR-036 SHA filled.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Optional final polish that affects multiple user stories.

- [ ] T079 [P] Update `CLAUDE.md` Recent Changes section with F-7 (Feature 237) entry: fourth execution of Heuristic A enrichment branch at four-or-five-agent scope; ADR-036 lineage; 6/6 byte-identical baselines; OWASP Mobile Top 10 = 10/10 + 40/40 four-framework milestone; BLP-01 10/11 features delivered post-F-7
- [ ] T080 [P] Update memory file `~/.claude/projects/-Users-david-Projects-tachi/memory/project_blp01_threat_coverage.md` with F-7 delivery state per CLAUDE.md auto-memory convention; status now 10/11 delivered; OWASP four-framework total 40/40; first four-or-five-agent enrichment-branch execution; M8 dual-host pattern catalogue
- [ ] T081 [P] Run `/aod.deliver 237` close-out flow if not already run during T075; verify all DoD bullets green (line-count caps on 5 agents, byte-identity 6/6, mobile-banking-app baseline, Coverage Matrix ten-row transition, ADR-036 Accepted, schema invariant, Pattern Category Disambiguation 5/5 dual-host, zero MAESTRO refs, PR title Conventional Commit, release-please fired)
- [ ] T082 [P] Optional reserve-day-only tasks (Tue 2026-05-05 if Mon 2026-05-04 close-out residual capacity insufficient): delivery retrospective filing fallback; M8 fall-back to single-host if architect adjudication issues surface during Wave 4.0/4.0b (defer M8 dual-host to follow-on PR; spec OoS-equivalent); reduced 8-of-10 categories shipping if R6 emergent-issue at four-or-five-agent scope triggers

**Checkpoint**: F-7 fully delivered. All Triad sign-offs recorded. All artifacts in place. BLP-01 progress: 10/11 features delivered (only F-8 Web/API Tier 3 remains).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 → Phase 2**: Setup verifications must pass before Wave 0.0 starts (PRD-day evening Tue)
- **Phase 2 Wave 0.0 → Wave 0.1**: Skeleton drafted before plan-day full-draft completion
- **Phase 2 Wave 0.1 → Wave 1.0/1.1**: Mobile-banking-app full draft + ADR-036 Proposed before pattern-catalog authoring
- **Phase 2 Wave 1.1 → Phase 3 Wave 2**: spoofing edits complete before tampering edits
- **Phase 3 Wave 2 → Wave 3**: tampering edits + Cat 11/12/13 + Disambiguation complete before info-disclosure edits
- **Phase 3 Wave 3 → Wave 4**: info-disclosure edits + 4 sub-tasks (M5-1/M6-1/M9-1/M10-1) + Disambiguation complete before M8 dual-host edits
- **Phase 3 Wave 4 → Phase 4 verification**: All 10 file edits + Pattern Category Disambiguation on 5 companions complete before US-2 invariant verification
- **Phase 5 Wave 4.x → Wave 5.0**: Spot-check signal informs Day 3 AM full verification scope
- **Phase 5 Wave 5.0 → Wave 5.1**: Strongly parallel — different owners (tester vs architect)
- **Phase 5 Wave 5.0/5.1 → Wave 5.2**: Both AM activities complete before test infrastructure work
- **Phase 5 Wave 5.2 → Phase 6**: Full byte-identity 6/6 + ADR-036 Accepted + tests green before Coverage Matrix update (FR-12 single commit)
- **Phase 6 → Phase 7**: Coverage Matrix transition committed before triple sign-off + close-out

### Wave Gate Points

| Gate | Wave | Owner | Decision |
|------|------|-------|----------|
| Wave 0.0 → Wave 0.1 | architect | Mobile-banking-app skeleton exhibits 5 of 6 indicators? Confirm before plan-day AM full draft. |
| Wave 0.1 → Wave 1.0 | architect | Mobile-banking-app architecture exhibits all 6 indicators? Confirm before architect re-verification. |
| Wave 1.0 → Wave 1.1 | architect | All baseline assumptions re-verified? Heuristic A protocol intact at four-or-five-agent scope? Confirm before pattern-catalog authoring. |
| Wave 1.1 → Wave 2 | senior-backend-engineer | spoofing edits + Cat N+1/N+2 + Disambiguation byte-identity-clean? ADR-036 Proposed committed with mapping table populated COMPLETE (NOT skeleton)? |
| Wave 2 → Wave 3 | senior-backend-engineer | All 3 category-by-category checkpoints (T-NN-1/2/3) completed cleanly? Wave 2.1, 2.2, 2.3 each self-reviewed? |
| Wave 3 → Wave 4 | senior-backend-engineer + team-lead MEDIUM-2 | All 4 sub-task checkpoints (M5-1/M6-1/M9-1/M10-1) completed cleanly? Wave 3.1, 3.2, 3.3, 3.4 each self-reviewed? |
| Wave 4.0 → Wave 4.0b | architect | privilege-escalation M8 privilege-gain variant byte-identity-clean? |
| Wave 4.0b → Wave 4.1/4.2 | architect | repudiation M8 accountability-loss variant byte-identity-clean? Disjoint-tells with privilege-escalation Cat verified? |
| Wave 4.2 → Wave 5.0 | senior-backend-engineer + tester | mobile-banking-app regen yields ≥10 (single-host) or ≥11 (dual-host) new Mobile findings? Tester engaged for early-signal spot-check? |
| Wave 4.1 → Wave 5.0 | tester | Spot-check on 2 baselines green? |
| Wave 5.0 → Wave 5.1 | tester (parallel architect) | Full 6-baseline verification 6/6? (Wave 5.1 Architect Accepted-transition runs in parallel) |
| Wave 5.0/5.1 → Wave 5.2 | tester + architect | Both AM activities complete? |
| Wave 5.2 → Wave 5.3 | senior-backend-engineer + code-reviewer | All tests + code-review green? |
| Wave 5.3 → Wave 5.4 | senior-backend-engineer | Coverage Matrix committed? |
| Wave 5.4 → Wave 5.5 | PM + Architect + Team-Lead | Triple sign-off recorded on tasks.md? |
| Wave 5.5 → Wave 5.6 (reserve) | senior-backend-engineer + architect | Pre-merge title verified + post-merge release-please fired + retrospective filed? |

### Parallel Opportunities

- **Wave 1.1 parallel**: T013 (ADR-036) + T014 (spoofing Edit 1) + T021/T022 (spoofing fixtures) — three different files, no inter-task dependencies
- **Wave 2.x sequential**: T026 (T-NN-1 Cat 11) → T027 (T-NN-2 Cat 12) → T028 (T-NN-3 Cat 13) — single file (tampering companion) requires sequential checkpoints per F-6 precedent; T029-T031 fixtures parallel after Wave 2.3
- **Wave 3.x sequential**: T035 (M5-1) → T036 (M6-1) → T037 (M9-1) → T038 (M10-1) — single file (info-disclosure companion) requires sequential sub-checkpoints per team-lead MEDIUM-2; T039-T042 fixtures parallel after Wave 3.4
- **Wave 4.0 + 4.0b sequential**: T043-T046 (privilege-escalation) → T047-T050 (repudiation) — different files but coordinated dual-host sequencing
- **Wave 4.1 + 4.0/4.0b/4.2 weakly parallel**: tester spot-check (T059/T060) and senior-backend-engineer regen (T061-T065) — tester can begin spot-check on 1–2 baselines before mobile-banking-app regen completes
- **Wave 5.0 + 5.1 strongly parallel**: tester full 6-baseline verification (T066) + architect ADR-036 Accepted transition (T067) — different owners, different files, fully parallel per F-6 Wave 5.0/5.1 precedent
- **Wave 5.2 parallel**: T068 (new test file) + T069 (test infra modify) — different files

### Critical Path

T009 (mobile-banking-app skeleton PRD-day) → T010 (mobile-banking-app full draft) → T012 (architect re-verification) → T013 (ADR-036 Proposed) → T014-T020 (spoofing enrichment) → T023-T028 (tampering enrichment, sequential T-NN-1/2/3) → T032-T038 (info-disclosure enrichment, sequential M5-1/M6-1/M9-1/M10-1) → T043-T050 (M8 dual-host enrichment) → T061-T065 (mobile-banking-app regen) → T066 (full byte-identity verification) → T067 (ADR-036 Accepted) → T072 (Coverage Matrix) → T073-T076 (close-out + release-please) → T077 (delivery retrospective)

---

## Implementation Strategy

### MVP Path (Baseline — 3.0-day envelope per PRD §Timeline)

**PRD-day Evening (Tue 2026-04-28 PM)** — Wave 0.0
- T009 mobile-banking-app skeleton (~2-3 hr per team-lead MEDIUM-1)

**Plan-day AM-early (Wed 2026-04-29 AM-early)** — Wave 0.1
- T010 mobile-banking-app full draft (~4-5 hr; architect + senior-backend-engineer co-authoring)
- T011 README placeholder

**Plan-day AM-mid (Wed 2026-04-29 AM-mid)** — Wave 1.0
- T012 architect re-verification (15-30 min)
- T013 ADR-036 Proposed authored (10-decision structure with mapping table populated COMPLETE)

**Plan-day AM-late (Wed 2026-04-29 AM-late)** — Wave 1.1
- T014-T022 spoofing enrichment (parallel) + 2 fixtures

**Plan-day PM (Wed 2026-04-29 PM)** — Wave 2 (densest authoring slot per F-6 Wave 2.x precedent)
- T023-T025 tampering agent metadata
- T026 (T-NN-1: Cat 11) → T027 (T-NN-2: Cat 12 with disjoint-tells) → T028 (T-NN-3: Cat 13) — three sequential ~75-90-min checkpoints
- T029-T031 fixtures parallel

**Build Day 1 AM (Thu 2026-04-30 AM)** — Wave 3 (4-subtask split per team-lead MEDIUM-2)
- T032-T034 info-disclosure agent metadata
- T035 (M5-1: Cat N+1) → T036 (M6-1: Cat N+2) → T037 (M9-1: Cat N+3) → T038 (M10-1: Cat N+4) — four sequential ~75-90-min sub-checkpoints
- T039-T042 fixtures parallel

**Build Day 1 PM (Thu 2026-04-30 PM)** — Wave 4 (M8 dual-host) + 4.1 + 4.2
- T043-T046 privilege-escalation M8 enrichment (Wave 4.0 PART A)
- T047-T050 repudiation M8 enrichment (Wave 4.0b PART B)
- T051 architect integration walkthrough M8 dual-host disjoint-tells verification
- T052-T053 fixtures parallel
- T059-T060 tester early-signal spot-check (parallel with regen)
- T061-T065 mobile-banking-app regen

**Build Day 2 AM (Fri 2026-05-01 AM)** — Wave 5.0 + 5.1 + 5.2 (strong parallel per F-6 precedent)
- T054-T058 US-2 invariant verification (Wave 4-end gate)
- T066 tester full 6-baseline verification (AM-1)
- T067 architect ADR-036 Accepted (AM-2; parallel)
- T068-T071 test infrastructure + tests + code-review

**Build Day 2 PM (Fri 2026-05-01 PM)** — Wave 5.3 + 5.4
- T072 Coverage Matrix ten-row transition (single commit)
- T073 triple sign-off

**Close-Out Day (Mon 2026-05-04)** — Wave 5.5 primary close-out per +0.5 day envelope vs F-6
- T074 pre-merge title verification
- T075 squash-merge
- T076 post-merge release-please verification
- T077 delivery retrospective
- T078 ADR-036 SHA fill

**Reserve Day (Tue 2026-05-05)** — Reserved for slip absorption
- Priority order: (1) Day 1/2 slip absorption; (2) M8 fall-back to single-host if architect adjudication issues surface during Wave 4.0/4.0b (defer M8 dual-host to follow-on PR); (3) Reduced 8-of-10 categories shipping if R6 emergent-issue triggers; (4) post-merge ADR-036 SHA fill + release-please verification
- T082 reserve-day-only tasks if triggered

### Escalation Paths

- **R1 (mobile-banking-app authoring slip)**: PRD-day evening skeleton (T009) + plan-day full draft (T010); if slips, downgrade SC-12 to ≥5 findings on synthetic test fixture under `tests/fixtures/` (PRD R1 contingency). Reserve day absorbs.
- **R2 (M8 split adjudication slip)**: If architect cannot adjudicate dual-host vs single-host at plan day, fall back to single-host placement (M8 → privilege-escalation only); F-7 ships with single-host M8 + 8 file edits; dual-host expansion becomes follow-on no-schema-bump PR. PRD R2 + plan Wave 5.6 reserve.
- **R4 (Wave 2/Wave 3 authoring quality slip)**: Sequential checkpoint pattern (T-NN-1/2/3 + M5-1/M6-1/M9-1/M10-1) provides ~75-90-min rollback capability. If quality slip on any sub-checkpoint, halt before next and re-author.
- **R6 (Heuristic A 4-or-5-agent emergent issues)**: If R6 triggers at Day 2 AM, ship 8 of 10 categories closing M1+M2+M3+M4+M5+M6+M7 + one M-item from M8/M9/M10 deferred to follow-on PR per spec OoS / plan Wave 5.6 reserve.
- **R7 (baseline drift)**: Day 1 PM early-signal spot-check (T059/T060) catches drift before Day 2 full verification. If drift detected, tighten indicator gate on offending Pattern Category at Day 2 AM; full verification reruns on reserve day.
- **R3 (ATT&CK Mobile catalog gap propagation 3-of-3 worst-case)**: Already absorbed at PRD/spec/plan time (Q3 RESOLVED: T1474/T1626/T1398 ALL prose-only). No mid-build escalation expected.
- **release-please skip post-merge**: Push empty `feat(237):` release-marker commit per F-212 incident precedent (T076).

---

## Notes

- All paths absolute from repo root `/Users/david/Projects/tachi/`
- Single-engineer fan-out across four-or-five agents (Wave 1.1 + Wave 2 + Wave 3 + Wave 4.0 + Wave 4.0b sequential) prevents authoring quality risk from concurrent multi-agent edits
- Wave 4.1 + 4.0/4.0b/4.2 weak parallelism (tester + senior-backend-engineer) and Wave 5.0 + 5.1 strong parallelism (tester + architect) are explicit team-lead recommendations per F-6 Wave 4.1 + 5.0/5.1 precedent
- Test infrastructure update (T069) is the **fifth BLP-01 detection feature to extend `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS`** (after F-3 single-host + F-5 two-host + F-6 two-host extension); F-7 adds 4 more hosts (spoofing + info-disclosure + privilege-escalation + repudiation; tampering already from F-6) to extend the frozenset to 9 entries dual-host (8 single-host fallback)
- Schema `finding.yaml` v1.8 unchanged — F-7 is the fourth no-schema-bump enrichment after F-3 + F-5 + F-6 per ADR-035 closing forward-scope marker forecast (fulfilled)
- 18-of-28 (dual-host) or 20-of-28 (single-host) file zero-edit invariant covers other detection agents + companion `detection-patterns.md` files; F-6's `tampering.md` becomes part of F-7's enriched 5 (extends F-6's enrichment); F-5's `denial-of-service.md` and `model-theft.md` are zero-touch in F-7
- Conventional Commits PR title `feat(237): Mobile Top 10 Coverage Bundle` (≤70 chars) enforced at draft PR (already at #238) + pre-merge re-verify + post-merge release-please verification per `.claude/rules/git-workflow.md` two-step Pre-merge + Post-merge enforcement
- ATT&CK Mobile catalog gap codified at ADR-036 D-7 (Q3 plan-time RESOLVED): T1474/T1626/T1398 are NOT catalog-resolvable per `schemas/taxonomy/mitre-attack.yaml`; appear in mitigation prose only at 3-of-3 worst-case scale; mirrors F-5 1-of-1 + F-6 3-of-6 ATLAS-gap precedent
- Architect MEDIUM-2 deferred from PRD plan-time RESOLVED: ADR-036 ships with **10-decision structure** (D-1 through D-10) mirroring ADR-035 D-9 Pattern Category Disambiguation precedent; discrete D-9 codifies disambiguation requirement on 5 companions in dual-host path
- Team-lead MEDIUM-1 deferred from PRD plan-time RESOLVED: PRD-day evening skeleton (Wave 0.0) + plan-day full draft (Wave 0.1) parallel mobile-banking-app authoring track reduces architect Wed AM critical-path load from 12-14 hrs to ~4-5 hrs
- Team-lead MEDIUM-2 deferred from PRD plan-time RESOLVED: FR-7 split into 4 sequential sub-task checkpoints (M5-1/M6-1/M9-1/M10-1) at ~75-90 min each with rollback capability mirrors F-6 Wave 2.x precedent at 4-cat scale
