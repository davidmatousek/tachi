# Research Summary: F-7 Mobile Top 10 Coverage Bundle

**Feature**: 237-mobile-top-10-coverage-bundle
**Date**: 2026-04-28
**Phase**: BLP-01 Tier 2 — second feature

---

## Knowledge Base Findings

**Heuristic A enrichment-branch protocol** (CLAUDE.md "Recent Changes" + memory `project_blp01_threat_coverage`):
- F-3 (#219, ASI07/`tool-abuse`): single-agent precedent — ADR-032 — established "additive-only edits to existing agent + companion catalog" pattern.
- F-5 (#229, LLM10/DoS+model-theft): two-agent precedent — ADR-034 — first multi-host application; `Q1 SPLIT` cross-agent vector decomposition (availability vs economic damage).
- F-6 (#232, ML01/03/04/06/07/08 across `tampering`+`data-poisoning`+`model-theft`): three-agent precedent — ADR-035 — `Q-decision plan-day` model; ML06 corpus-side vs artifact-side cross-host decomposition; ATLAS-catalog gap propagation rule (3 of 6 prose-only).
- F-7 (this feature): four-or-five-agent execution — ADR-036 forecast at ADR-035 closing forward-scope marker.

**Key lessons reused**:
- Plan-day Q-decisions populated at PRD time, not skeleton — Day 1 AM lands ADR Proposed with mapping table populated (not blank), preventing Day 1 stall (F-6 lesson).
- MITRE catalog gaps handled as prose-only in `mitigation` narratives, NOT in structured `references` array (F-5 T1496 + F-6 ATLAS-gap precedent).
- Mutation-target example authored at plan day (~6–8 hr architect+SBE co-authoring) when no existing example exhibits the target topology (F-6 `predictive-ml-app/` lesson).
- Tester owns SC-13 byte-identity verification (NOT senior-backend-engineer who authors edits) — separation-of-duties precedent from F-3/F-4/F-5/F-6.

**KB references not surfaced**: no prior mobile-platform threat-modeling features in tachi history; F-7 is the first.

---

## Codebase Analysis

**PRD-time baselines verified** (line counts match PRD §FR-1, FR-3, FR-5, FR-7 exactly):

| File | Lines | Tier Cap | Margin |
|------|-------|----------|--------|
| `.claude/agents/tachi/spoofing.md` | 51 | ≤120 STRIDE | ≥69 |
| `.claude/agents/tachi/tampering.md` | 55 | ≤120 STRIDE | ≥65 |
| `.claude/agents/tachi/info-disclosure.md` | 54 | ≤120 STRIDE | ≥66 |
| `.claude/agents/tachi/privilege-escalation.md` | 52 | ≤120 STRIDE | ≥68 |
| `.claude/agents/tachi/repudiation.md` | 50 | ≤120 STRIDE | ≥70 |
| `.claude/skills/tachi-spoofing/references/detection-patterns.md` | 146 | none | — |
| `.claude/skills/tachi-tampering/references/detection-patterns.md` | 221 | none | — |
| `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` | 192 | none | — |
| `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md` | 213 | none | — |
| `.claude/skills/tachi-repudiation/references/detection-patterns.md` | 148 | none | — |

**Schema baseline**:
- `schemas/finding.yaml` `schema_version: "1.8"` confirmed.
- `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"` — `S`, `T`, `I`, `E`, `R` all present; **no new prefix needed for F-7**.

**Patterns to follow** (precedent ADRs verified to exist):
- `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md` — single-agent template.
- `docs/architecture/02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md` — two-agent template.
- `docs/architecture/02_ADRs/ADR-035-ml-top-10-coverage-bundle.md` — three-agent template (immediate predecessor; ADR-036 mirrors structure).

**Companion-catalog Pattern Category structure** (from F-6 `tampering` Cat 10):
- H2 heading naming the category and primary OWASP item.
- Description paragraph (1–3 lines).
- ≥4 architectural indicators (bullet list).
- ≥1 worked example grounded in realistic architecture.
- Primary Sources block: OWASP primary citation + ≥1 related citation (MASTG/MASVS/MITRE).
- Mitigations list: ≥3 specific control mechanisms.

---

## Architecture Constraints

**Non-negotiable invariants** (from `.aod/memory/constitution.md` + ADR set):

1. **ADR-023 D1 tier caps**: STRIDE-tier agents ≤120 lines (hard ≤180). All five candidate hosts have ≥65-line margin even after expected 5-line edits.
2. **ADR-023 D3 additive-only edit discipline**: existing content byte-identical pre/post edit; new content appended only.
3. **ADR-021 byte-identity invariant**: 6 non-mutation baselines must regen byte-identically under `SOURCE_DATE_EPOCH=1700000000`.
4. **Heuristic A consolidation rule (SDR-001 D4)**: same-class threats share agent; new agent only when signal class is new. M1–M10 resolve onto 4 existing signal classes (S/T/I + E or R), not a new class.
5. **ADR-027 Proposed → Accepted dual-commit pattern**: ADR-036 lands Proposed at Day 1 AM, Accepted at close-out with squash-merge SHA fill-in.
6. **Lean-agent inventory discipline (Feature 082 pattern)**: 28 detection-tier files post-F-6; F-7 modifies 8 (single-host M8) or 10 (dual-host M8); 0 net new.

**Validated assumptions**:
- **A1 verified**: `grep "^- id: M[0-9]" schemas/taxonomy/owasp.yaml` returns M1–M10 (10 of 10 records).
- **A3 partially false → prose-only fallback applies**: `grep "T1474|T1626|T1398" schemas/taxonomy/mitre-attack.yaml` returns **zero matches**. All three MITRE ATT&CK Mobile entries cited in the PRD are NOT catalog-resolvable. Fallback per F-5 (T1496 prose-only) + F-6 (3 of 6 ATLAS prose-only). Findings cite these in `mitigation` narratives only, not in `references` array.
- **A5 verified**: empirical grep across `examples/*/architecture.md` for `android|ios|mobile|keystore|keychain|sharedpref|nsuser` returns one incidental match in `microservices/architecture.md` (line: "End-user browser or mobile app" — generic external-entity descriptor, NOT a mobile-platform topology indicator). Zero structural mobile-platform components across all 7 existing examples. New `examples/mobile-banking-app/` authoring is the default plan-day path.

**Dependencies satisfied**:
- F-A1 (#180) — taxonomy crosswalk — CLOSED.
- F-A2 (#189) — `source_attribution` schema field — CLOSED.
- F-3 (#219), F-5 (#229), F-6 (#232) — enrichment-branch precedents — all CLOSED.

---

## Industry Research

**OWASP Mobile Top 10:2024** (primary source):
- M1 Improper Credential Usage — credential storage/transmission/handling failures.
- M2 Inadequate Supply Chain Security — third-party SDK trust failures.
- M3 Insecure Authentication/Authorization — mobile-client auth/session weaknesses.
- M4 Insufficient Input/Output Validation — mobile IPC/intent/URL-scheme injection.
- M5 Insecure Communication — cleartext, missing TLS pinning, weak ciphers.
- M6 Inadequate Privacy Controls — PII leakage via clipboard/screenshots/cache.
- M7 Insufficient Binary Protections — root/jailbreak detection, RASP, obfuscation.
- M8 Security Misconfiguration — exposed debug endpoints, default permissions, missing attestation.
- M9 Insecure Data Storage — unencrypted SQLite, exposed backups, world-readable files.
- M10 Insufficient Cryptography — weak KDF, custom crypto, hardcoded keys, insecure PRNG.

**MASTG / MASVS cross-references** (related, prose-cited at section-level granularity per Q4 default):
- MASTG-AUTH, MASTG-NETWORK, MASTG-STORAGE, MASTG-CRYPTO, MASTG-CODE, MASTG-RESILIENCE, MASTG-PLATFORM, MASTG-PRIVACY, MASTG-ARCH.
- MASVS-AUTH, MASVS-NETWORK, MASVS-STORAGE, MASVS-CRYPTO, MASVS-CODE, MASVS-RESILIENCE, MASVS-PLATFORM, MASVS-PRIVACY.

**MITRE ATT&CK for Mobile** (catalog-resolvability gap; all prose-only per A3 verification):
- T1474 Supply Chain Compromise — M2 reference.
- T1626 Abuse Elevation Control Mechanism — M8 privilege-gain variant reference.
- T1398 Boot or Logon Initialization Scripts — M8 accountability-loss variant reference.

**Platform-specific control terminology** (named in mitigation blocks for specificity per Quality Metrics):
- Android: Keystore, EncryptedSharedPreferences, Play Integrity API, FLAG_SECURE, ProGuard/R8, Android App Links, Network Security Config.
- iOS: Keychain Services, DeviceCheck, NSAppTransportSecurity, Universal Links, bitcode, symbol-stripping.
- Cross-platform: SQLCipher, Realm encryption, certificate pinning with backup-pin rotation.

---

## Recommendations for Spec

1. **Translate PRD §User Stories US-237-1/2/3 directly** into spec User Stories with priority P1/P1/P1 — all three independently testable (mobile-banking finding emission, file-edit invariant verification, byte-identity regen on non-mobile baselines).
2. **FR-1 through FR-11** map directly from PRD; spec preserves the file-path + edit-posture + tier-cap structure since this is a documentation-pattern enrichment, not application code.
3. **Defer 6 plan-day decisions to plan.md / tasks.md** (do NOT resolve in spec): Q1 M8 split, Q2 mobile-banking-app archetype confirmation, Q3 MITRE catalog-resolvability (already empirically resolved as prose-only), Q4 MASTG/MASVS section-level granularity (PRD default), Q5 ADR-036 severity-hint column (PRD default = yes), Q6 mobile-banking-app baseline strategy (default = excluded mutation target).
4. **No NEEDS CLARIFICATION markers** — PRD provides comprehensive context; plan-day Q-decisions are explicit deferrals, not ambiguities.
5. **Edge cases section** must cover: non-mobile architecture emission (zero new findings), MITRE ATT&CK Mobile catalog gap (prose-only), M8 split fall-back to single-host on adjudication slip, hybrid web+mobile architecture (F-1 output-integrity vs `tampering` Cat 12 disjoint-tells boundary).
6. **Success Criteria SC-1 through SC-18 from PRD** map 1:1 into spec Success Criteria — all measurable, all verifiable without implementation details.
7. **Key Entities section** lists: Pattern Category (data structure), Detection Agent (already-existing artifact extended additively), Companion Catalog (already-existing artifact extended additively), Architectural Indicator (gates finding emission), ADR-036 (governance artifact).
