---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-28
    status: APPROVED_WITH_CONCERNS
    notes: "Counts: 0 BLOCKING / 0 HIGH / 2 MEDIUM / 4 LOW. Plan operationalizes 17/17 FRs + 20/20 SCs + 3/3 P1 stories + 9/9 Q-decision/MEDIUM deferrals (Q1 dual-host M8, Q2 mobile-banking-app, Q3 prose-only RESOLVED at spec time, Q4 section-level, Q5 severity-hint YES, Q6 excluded mutation target; architect MEDIUM-2 → 10-decision ADR-036 structure; team-lead MEDIUM-1 → Wave 0.0 PRD-evening skeleton + Wave 0.1 plan-day full draft; team-lead MEDIUM-2 → FR-7 4-subtask split Wave 3.1/3.2/3.3/3.4). Won't-Have exclusions preserved (no new agent, no schema bump, no orchestrator/dispatch edits, no consumers-list edit, no source_attribution wiring, no MASTG taxonomy YAML). 3-day envelope (Wed plan + Thu/Fri build + Mon close-out + Tue reserve) honored. Coverage Matrix ten-row update Wave 5.3 single-commit per F-3/F-4/F-5/F-6 precedent. Mutation-target authoring track feasible at parallel skeleton/full-draft cadence. ADR-036 audit deliverable adequately scoped at 10-decision structure with 10-or-11-row mapping table including severity-hint column. MEDIUM-1 (Day-labelling drift PRD vs plan Wave-day) + MEDIUM-2 (Wave 5.4 Triple Triad sign-off positioning) absorbable at tasks.md layer. LOW-1/2/3/4 cosmetic. Ready for /aod.tasks. Full review: .aod/results/product-manager-plan-237.md."
  architect_signoff:
    agent: architect
    date: 2026-04-28
    status: APPROVED_WITH_CONCERNS
    notes: "Counts: 0 BLOCKING / 0 HIGH / 2 MEDIUM / 4 LOW. Plan technically sound at four-or-five-agent scope. Heuristic A protocol compliance FULL: ADR-023 D3 additive-only edit discipline preserved across 10 dual-host (or 8 single-host) target files; ADR-030 D1 signal-class taxonomy correctly applied (S/T/I + E/R = 5 prefix families, all already enumerated in id.pattern regex); ADR-035 closing forward-scope marker forecast (F-7 four-or-five-agent execution with no schema bump) FULFILLED. Schema invariant verified: finding.yaml v1.8 unchanged, id.pattern unchanged. ADR-036 mapping table completeness verified at plan layer: 10-or-11 closure rows + reference rows + severity-hint annotation column (Q5 RESOLVED YES) + M4 cross-agent boundary annotation with F-1 output-integrity (D-5) + Heuristic A four-or-five-agent consolidation rationale. ADR-036 D-numbered structure: 10-decision per architect MEDIUM-2 plan-time RESOLVED (mirrors ADR-035 D-9 Pattern Category Disambiguation precedent). M8 split decision (Q1) plan-time RESOLVED dual-host with disjoint architectural-tells (privilege-escalation = privilege-gain variant; repudiation = accountability-loss variant). MITRE ATT&CK Mobile catalog gap (Q3) ALL 3 of 3 prose-only at worst-case scale (T1474/T1626/T1398 absent per grep); ADR-036 D-7 codifies. Tier cap preservation verified: all 5 host agents within ≤120 STRIDE cap (margins ≥54 lines on tightest case). 18-or-20-of-28 file zero-edit invariant correctly scoped. Test infrastructure scope (Wave 5.2) complete: test_backward_compatibility.py infrastructure update + new test_mobile_top_10_coverage_bundle_enrichment.py with structural-diff + line-count + MAESTRO grep + Pattern Category Disambiguation header presence (5 matches dual-host) + references-array fixtures + ATT&CK Mobile catalog-resolvability gap test. Wave 0.0/0.1 mobile-banking-app authoring track feasible. Wave 3.x 4-subtask split (M5/M6/M9/M10 ~75-90 min each) absorbs team-lead MEDIUM-2 throughput asymmetry. M4 cross-agent boundary D-5 disjoint-tells annotation prevents duplicate emission on hybrid LLM+mobile architectures. Constitution Check 10/10 PASS; gate verdict: no violations. MEDIUM-1 (DETECTION_AGENT_PATHS off-by-one math: post-F-6 baseline 8 → 3 dual-host or 8 → 4 single-host depending on path; plan currently states 8→3) + MEDIUM-2 (ADR-036 D-7 prose-only codification conflated with consumers-list-edit decision; should be split into two D-numbered decisions or absorbed into D-3 mapping table footnote) absorbable at Wave 1.0 ADR-036 finalization + Wave 5.2 test infrastructure authoring. LOW-1/2/3/4 cosmetic. Architect APPROVES_WITH_CONCERNS for /aod.tasks. Full review: .aod/results/architect-plan-237.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Mobile Top 10 Coverage Bundle (OWASP Mobile Application Security Top 10:2024)

**Branch**: `237-mobile-top-10-coverage-bundle` | **Date**: 2026-04-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/237-mobile-top-10-coverage-bundle/spec.md`
**PRD**: [docs/product/02_PRD/237-mobile-top-10-coverage-bundle-2026-04-28.md](../../docs/product/02_PRD/237-mobile-top-10-coverage-bundle-2026-04-28.md)
**BLP-01 Phase**: Tier 2 F-7 — second Tier 2 closure feature; **fourth execution** of the Heuristic A **enrichment** branch (after F-3 single-agent, F-5 two-agent, F-6 three-agent), **first at four-or-five-agent scope**; closes M1–M10 Planned → Covered, completing OWASP Mobile Top 10:2024 = 10/10 milestone (combined post-F-6 OWASP three-framework total = 30/30: post-F-7 = 40/40 across all four top-10 frameworks)

## Summary

Enrich four (Q1 default) or five (Q1 dual-host fallback) existing host threat agents — `spoofing` (STRIDE-tier), `tampering` (STRIDE-tier; previously enriched by F-6 Cat 10), `info-disclosure` (STRIDE-tier), plus **M8 host(s)** `privilege-escalation` and/or `repudiation` (STRIDE-tier per Q1 default = dual-host) — to close 10 OWASP Mobile Top 10:2024 detection gaps via Heuristic A consolidation at **four-or-five-agent scope**. **No new agent files, no new skill directories, no schema bump, no consumers-list edit, no functional orchestrator/dispatch edit, no `source_attribution` populator wiring extension.** Net change is **purely additive** to 8 (single-host M8 path) or 10 (dual-host M8 path) existing files plus one new ADR-036 plus one new mutation-target example: (1) `spoofing.md` metadata `owasp_references += [OWASP M1:2024, OWASP M3:2024]`, `## Purpose` 1–3 line extension, Detection Workflow Step 5 references += new Mobile/MASTG/MASVS exemplar mention; (2) `tachi-spoofing/references/detection-patterns.md` appends Pattern Category N+1 (Improper Mobile Credential Usage M1) + Cat N+2 (Insecure Mobile Authentication/Authorization M3) after current last category + Pattern Category Disambiguation subsection + Primary Sources extension; (3) `tampering.md` metadata `owasp_references += [OWASP M2:2024, M4:2024, M7:2024]`, `## Purpose` extension, Step 5 references extension; (4) `tachi-tampering/references/detection-patterns.md` appends Cat 11 (Mobile Supply Chain Integrity M2) + Cat 12 (Mobile IPC Input Validation M4 with disjoint-tells annotation referencing F-1 `output-integrity` boundary) + Cat 13 (Insufficient Mobile Binary Protections M7) after F-6's Cat 10 + Pattern Category Disambiguation subsection + Primary Sources extension; (5) `info-disclosure.md` metadata `owasp_references += [OWASP M5:2024, M6:2024, M9:2024, M10:2024]`, `## Purpose` extension, Step 5 references extension; (6) `tachi-info-disclosure/references/detection-patterns.md` appends Cat N+1 (Insecure Mobile Communication M5) + Cat N+2 (Inadequate Mobile Privacy Controls M6) + Cat N+3 (Insecure Mobile Data Storage M9) + Cat N+4 (Insufficient Mobile Cryptography M10) + Pattern Category Disambiguation subsection + Primary Sources extension; (7) M8 host(s) per **Q1 plan-time decision: DUAL-HOST**: `privilege-escalation.md` + `repudiation.md` metadata `owasp_references += [OWASP M8:2024]`, `## Purpose` extension, Step 5 references extension; (8) M8 companion(s): `tachi-privilege-escalation/references/detection-patterns.md` appends Cat N+1 (Mobile Security Misconfiguration — Privilege-Gain Variant M8) + Pattern Category Disambiguation + Primary Sources extension; `tachi-repudiation/references/detection-patterns.md` appends Cat N+1 (Mobile Security Misconfiguration — Accountability-Loss Variant M8) + Pattern Category Disambiguation + Primary Sources extension; (9) public ADR-036 documenting the Heuristic A enrichment pattern at four-or-five-agent scope as operational precedent (Proposed → Accepted dual-commit per ADR-027/032/034/035 lineage); (10) new `examples/mobile-banking-app/architecture.md` mutation target. Findings emit with existing `S-{N}` prefix (spoofing), `T-{N}` prefix (tampering), `I-{N}` prefix (info-disclosure), `E-{N}` prefix (privilege-escalation), `R-{N}` prefix (repudiation) — all 5 already present in `id.pattern` regex post-F-4; each new finding cites the appropriate `OWASP M{N}:2024` primary in its prose-level `references:` array (existing finding-YAML field since v1.0; F-7 does NOT extend `source_attribution` populator wiring — that scope belongs to F-A3).

**Architectural approach**: Apply ADR-023 Decision 3 additive-only edit discipline. Existing prose in all four-or-five agent `.md` files' `## Purpose` sections + companion sections (Cat 1–N pre-existing in each catalog) + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries) sections remain **byte-identical** pre/post edit (grep-checkable). Architect MEDIUM-2 (ADR-036 9-vs-10 decision structure with Pattern Category Disambiguation as discrete D-numbered decision) absorbed into ADR-036 D-numbered decisions (**plan-time decision: 10-DECISION STRUCTURE** mirroring ADR-035 D-9 precedent). Team-lead MEDIUM-1 (plan-day overload mitigation — architect-critical-path 12-14 hrs Wed) absorbed via Wave 0.0 PRD-day evening parallel skeleton drafting + Wave 0.1 plan-day mobile-banking-app authoring track. Team-lead MEDIUM-2 (Day 2 AM throughput asymmetry — info-disclosure 4 cats = +33% vs F-6 densest) absorbed via FR-7 task split into 4 sequential sub-task checkpoints (M5/M6/M9/M10 each at ~75-90 min with rollback capability per F-6 Wave 2.1/2.2/2.3 precedent). Q1 plan-time RESOLVED: **DUAL-HOST** for M8 (architect adjudication: privilege-escalation owns privilege-gain variant; repudiation owns accountability-loss variant; mirrors ADR-035 D-4 ML06 two-facet precedent at the F-7 architectural-tell layer). Q3 plan-time RESOLVED at spec authoring time: 0 of 3 MITRE ATT&CK Mobile entries (T1474/T1626/T1398) catalog-resolvable; ALL prose-only at 3-of-3 scale (worst case in BLP-01; mirrors F-5 T1496 + F-6 3-of-6 ATLAS-gap precedent). Q4 plan-time RESOLVED: section-level granularity (MASTG-AUTH, MASVS-CRYPTO etc.); test-case-ID granularity is F-A1 follow-on. Q5 plan-time RESOLVED: YES, severity-hint column (parity with ADR-034 5-row + ADR-035 11-row precedent). Q6 plan-time RESOLVED: `mobile-banking-app/` excluded from `BASELINE_EXAMPLES` byte-identity loop (mirrors `agentic-app`, `consumer-agent-app`, `predictive-ml-app/` precedent). Q2 plan-time RESOLVED: `mobile-banking-app/` archetype confirmed (covers credentials, payment, biometrics, secure storage, certificate pinning across all M-items). The enriched agents activate as they do today on Process / Data Store / Data Flow / External Entity components matching existing trigger keywords; new Pattern Categories fire only on architectures additionally exhibiting **mobile-platform topology indicators** (the mobile-platform topology gate ensures byte-identity on the 6 non-mobile baselines).

**Touch points**: 0 new agent files, 0 new skill directories, 0 schema edits, 0 functional dispatch edits, 0 consumers-list edits, 0 `source_attribution` populator wiring extensions, 0 new runtime dependencies. **10 additive file edits in dual-host M8 path** (5 host agents + 5 companions) **OR 8 in single-host fallback** (4 host agents + 4 companions) + **1 new ADR** (ADR-036 with 10-or-11-row mapping table + M8 split decision + M4 cross-agent boundary + 10-decision structure) + **1 new example architecture** (`examples/mobile-banking-app/architecture.md` Q2 RESOLVED) + **1 example regeneration** (`mobile-banking-app/`) + **0 cosmetic annotation edits** (default-NO; all five host agents already fully registered). **F-7 surface is 43-57% larger than F-6's pattern-authoring surface (10-11 categories vs F-6's 7) and exercises four-or-five-agent fan-out (vs F-6's three). Realistic envelope: 3.0 working days.**

## Technical Context

**Language/Version**: Markdown + YAML + Python 3.11 (existing — stdlib + `pyyaml`); agent and skill content files, not executable code
**Primary Dependencies**: `pyyaml` (runtime, already declared), `pytest` (dev-only, already declared per Feature 128 precedent); **no new runtime or dev dependencies**
**Storage**: File-based; reads `schemas/finding.yaml` (v1.8, **no edit**), `schemas/taxonomy/{owasp,mitre-atlas,mitre-attack}.yaml` (F-A1 catalogs, read-only for `references` validation); writes only to `.claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md` (5 files dual-host path), `.claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md` (5 files dual-host path), `docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md`, `examples/mobile-banking-app/` (Q2 RESOLVED — new architecture authoring at plan day Wed 2026-04-29 with Wave 0.0 PRD-day evening skeleton draft per team-lead MEDIUM-1)
**Testing**: pytest (existing harness at `tests/scripts/`) + backward-compatibility test `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 — **6 non-mobile baselines** byte-identity gate (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`); structural-diff tests on Cat 1–N pre-existing byte-identity in all five companions; line-count tests on `spoofing.md` (≤120) + `tampering.md` (≤120) + `info-disclosure.md` (≤120) + `privilege-escalation.md` (≤120) + `repudiation.md` (≤120); MAESTRO grep tests on all ten enriched files (5 hosts + 5 companions in dual-host path); references-array assertion tests on Cat N+1/N+2 (S) + Cat 11/12/13 (T) + Cat N+1/N+2/N+3/N+4 (I) + M8 Cat (E) + M8 Cat (R) fixture findings (catalog-resolvable: M1-M10 OWASP Mobile + section-level MASTG/MASVS prose; all 3 MITRE ATT&CK Mobile entries T1474/T1626/T1398 prose-only)
**Target Platform**: Command-line Python tooling (macOS/Linux/WSL); orchestrator + threat agents invoked via `/tachi.threat-model` Claude command; PDF rendering via Typst + Mermaid CLI (unchanged)
**Project Type**: Single project (methodology toolkit — agents + skills + schemas + templates in a unified repo); no frontend/backend split
**Performance Goals**: Agent invocation latency unchanged. Ten or eleven new Pattern Categories add O(10-11 additional pattern matches across four-or-five host dispatches); aggregate ≤500 lines added across companion files; empirical impact <3ms per architecture file. ≤7% pipeline wall-clock latency on a mobile architecture (SC-19).
**Constraints**: (a) SC-3 byte-identity on Cat 1–N pre-existing (spoofing companion 146 lines pre-edit) is a BLOCKER; (b) SC-6 byte-identity on Cat 1–10 pre-existing (tampering companion 221 lines post-F-6) is a BLOCKER; (c) SC-9 byte-identity on Cat 1–N pre-existing (info-disclosure companion 192 lines) is a BLOCKER; (d) SC-10 byte-identity on Cat 1–N pre-existing (privilege-escalation 213 + repudiation 148 companions) is a BLOCKER; (e) SC-13 byte-identity on **6 non-mobile example PDFs** under `SOURCE_DATE_EPOCH=1700000000` is a BLOCKER; (f) SC-1/4/7/10 line-count cap ≤120 on all five enriched STRIDE agents (PRD/plan-time baselines 51/55/54/52/50; expected post-edit ≤66 each; minimum margin ≥54 lines on tightest case) is a BLOCKER; (g) SC-16 zero-edit invariant on every detection-tier file other than the F-7 enrichment targets is a BLOCKER (post-F-6 inventory: 28 detection-tier files; F-7 edits 8 single-host path or 10 dual-host path; remaining 20 or 18 stay byte-identical); (h) SC-15 schema invariant — `schemas/finding.yaml` `schema_version` MUST remain `"1.8"` (BLOCKER); (i) SC-17 `references:` array must include the appropriate Mobile primary on every emitted new finding (BLOCKER); MITRE ATT&CK Mobile entries (T1474/T1626/T1398) appear in mitigation prose only (BLOCKER — NOT in `references` array); (j) Zero MAESTRO references in all 8 or 10 enriched files (grep-auditable, BLOCKER); (k) FR-15 mobile-platform topology gate (correctness BLOCKER) — all 10-or-11 new Pattern Categories emit zero findings on architectures lacking mobile-platform indicators; (l) Pattern Category Disambiguation subsection on each companion (4 instances single-host, 5 instances dual-host total) per ADR-036 D-9 is a BLOCKER mirroring ADR-035 D-9 precedent
**Scale/Scope**: 0 new agent files; 0 new skill directories; 8 or 10 file edits (~5 lines additive on each STRIDE agent file: 51→55-60 / 55→60-66 / 54→60-66 / 52→56-58 / 50→54-56; ~50-60 lines additive on spoofing companion (Cat N+1 + N+2 + Disambiguation + Primary Sources); ~90-100 lines additive on tampering companion (Cat 11 + 12 + 13 + Disambiguation + Primary Sources); ~120-140 lines additive on info-disclosure companion (Cat N+1 + N+2 + N+3 + N+4 + Disambiguation + 4 Primary Sources entries); ~30-35 lines additive on privilege-escalation companion (M8 Cat N+1 privilege-gain variant + Disambiguation + Primary Sources); ~30-35 lines additive on repudiation companion (M8 Cat N+1 accountability-loss variant + Disambiguation + Primary Sources)); 10 or 11 new Pattern Categories total (Cat N+1/N+2 in spoofing; Cat 11/12/13 in tampering; Cat N+1/N+2/N+3/N+4 in info-disclosure; Cat N+1 in privilege-escalation; Cat N+1 in repudiation) with ≥4 indicators each, ≥1 worked example each, named mobile-specific mitigations; 1 new ADR (~370-420 lines including 10-or-11-row mapping table + M8 split decision + M4 cross-agent boundary + 10 numbered Decisions); 1 new example architecture (`mobile-banking-app/architecture.md` ~180-220 lines authored across PRD-day evening skeleton + plan-day Wed full draft) + 1 example regeneration. **Edit surface is between F-6 (three-agent enrichment, 2.5d, 7 categories) and a hypothetical full new-agent feature (3.5d). Realistic envelope: 3.0 working days.**

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.aod/memory/constitution.md`:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | All 10-or-11 Pattern Categories detect generic mobile-platform signal classes; no hardcoded project-type assumptions; works on any architecture exhibiting mobile-platform topology indicators (mobile client component, Keystore/Keychain mention, certificate pinning declaration, mobile SDK reference, mobile permissions, package-name signal, ContentProvider/Activity export declaration) |
| II. API-First Design | N/A | No REST/GraphQL surface; threat agents are content files consumed by the orchestrator at invocation time |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Mobile-platform topology gate (FR-15 spec / FR-016-equivalent at plan layer) ensures byte-identity on 6 non-mobile baselines. Schema unchanged; existing `S-{N}` / `T-{N}` / `I-{N}` / `E-{N}` / `R-{N}` findings remain valid. Local `.aod/` workflows unaffected. **No schema bump means even the schema-version-pinning surface is byte-identical** — F-7 is the fourth BLP-01 detection feature with zero schema-tier impact (after F-3 + F-5 + F-6) and the first at four-or-five-agent enrichment scope. ADR-035 closing forward-scope marker forecast fulfilled. |
| IV. Concurrency & Data Integrity | N/A | F-7 is single-invocation content authoring; no concurrent state |
| V. Privacy & Data Isolation | PASS | Worked examples use clearly-fictional scenarios (mobile-banking app handling fake credentials in SharedPreferences, mobile architecture without certificate pinning, mobile app with unencrypted SQLite holding fictional PII, mobile architecture with hypothetical exported Activity); no PII, no adopter data, no network calls by the agent |
| VI. Testing Excellence (MANDATORY) | PASS | Structural-diff tests on Cat 1–N (S) + Cat 1–10 (T) + Cat 1–N (I) + Cat 1–N (E) + Cat 1–N (R) byte-identity; line-count tests on all five agent files; MAESTRO grep test on all 8 or 10 enriched files; references-array assertion tests for Cat N+1/N+2 (S) + Cat 11/12/13 (T) + Cat N+1/N+2/N+3/N+4 (I) + M8 Cat (E) + M8 Cat (R) fixture findings; backward-compat byte-identity gate on 6 non-mobile baselines (per FR-15: explicit `tester` agent ownership separate from `senior-backend-engineer` per F-3/F-4/F-5/F-6 separation-of-duties precedent); Pattern Category Disambiguation header presence test (4 matches single-host, 5 matches dual-host expected per ADR-036 D-9 + plan-time Q1 dual-host decision) |
| VII. Definition of Done (NON-NEGOTIABLE) | PASS | Spec-defined SCs (SC-1 through SC-20) map to grep-checkable / wc-checkable / byte-identity predicates. SC-3 + SC-6 + SC-9 + SC-10 + SC-13 + SC-15 + SC-16 + SC-17 are BLOCKER-level gates. Delivery retrospective at /aod.deliver close-out per FR-26-equivalent. Release-please post-merge gate via `/aod.deliver` two-step Pre-merge + Post-merge enforcement per `.claude/rules/git-workflow.md` |
| VIII. Product-Spec Alignment | PASS | Approved PRD 237 v2 exists (PM APPROVED; Architect APPROVED_WITH_CONCERNS — 0 BLOCKING / 0 HIGH / 3 MEDIUM (1 absorbed in v2, 2 deferred to plan day) / 4 LOW; Team-Lead APPROVED_WITH_CONCERNS — 0 BLOCKING / 0 HIGH / 2 MEDIUM-deferred / 3 LOW); spec.md has PM APPROVED sign-off (0 BLOCKING / 0 HIGH / 2 MEDIUM (style/scope clarification) / 3 LOW) |
| IX. Git Workflow | PASS | Feature branch `237-mobile-top-10-coverage-bundle` created; draft PR #238 opened with `feat(237):` Conventional Commits title at plan stage; no main commits; ADR-036 Proposed → Accepted dual-commit pattern. R12 release-please mitigation enforced via two-step Pre-merge + Post-merge per `.claude/rules/git-workflow.md` (F-212 incident precedent). |
| X. Zero-Edit Invariant (ADR-023 lineage) | PASS | SC-16 explicit; 18-or-20-of-28 file invariant covers 9 or 10 other host agents + 9 or 10 other companion `detection-patterns.md` files (post-F-6 inventory: 28 detection-tier files; F-7 edits 8 single-host or 10 dual-host; remaining 20 or 18 stay byte-identical). FR-14 enforces zero edit to `finding-format-shared.md` consumers list. FR-14 enforces zero functional edit to orchestrator dispatch tier (no cosmetic annotation defaults — all 4 or 5 host agents already registered). FR-13 enforces zero `source_attribution` populator wiring extension on host agents (deferred to F-A3). |

**Gate verdict**: No violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/237-mobile-top-10-coverage-bundle/
├── plan.md                  # This file (/aod.project-plan output)
├── research.md              # Phase 0 output (populated by /aod.spec)
├── data-model.md            # Phase 1 output — Pattern Category N+1/N+2 (S) + 11/12/13 (T) + N+1/N+2/N+3/N+4 (I) + M8 (E) + M8 (R) shape + mobile-platform topology gate + finding shape
├── contracts/
│   └── finding-contract.md  # Finding IR contract for Cat N+1/N+2 S-{N}, Cat 11/12/13 T-{N}, Cat N+1/N+2/N+3/N+4 I-{N}, M8 E-{N}, M8 R-{N} findings (references-array + mitigation rules + prose-only ATT&CK Mobile)
├── quickstart.md            # Phase 1 output — verification walkthrough
├── checklists/
│   └── requirements.md      # Spec quality checklist (PM-validated)
├── spec.md                  # PM-approved spec
└── tasks.md                 # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
tachi/
├── .claude/
│   ├── agents/
│   │   └── tachi/
│   │       ├── spoofing.md                                  # MODIFY (additive; 3 small edits) — 51 → 55-60 lines
│   │       ├── tampering.md                                 # MODIFY (additive; 3 small edits) — 55 → 60-66 lines
│   │       ├── info-disclosure.md                           # MODIFY (additive; 3 small edits) — 54 → 60-66 lines
│   │       ├── privilege-escalation.md                      # MODIFY (additive; 3 small edits, dual-host M8) — 52 → 56-58 lines
│   │       ├── repudiation.md                               # MODIFY (additive; 3 small edits, dual-host M8) — 50 → 54-56 lines
│   │       ├── orchestrator.md                              # UNCHANGED (zero functional edit; all 5 agents already registered)
│   │       ├── output-integrity.md                          # UNCHANGED (18-or-20-file invariant; F-1 host)
│   │       ├── misinformation.md                            # UNCHANGED (18-or-20-file invariant; F-2 host)
│   │       ├── tool-abuse.md                                # UNCHANGED (18-or-20-file invariant; F-3 host)
│   │       ├── human-trust-exploitation.md                  # UNCHANGED (18-or-20-file invariant; F-4 host)
│   │       ├── denial-of-service.md                         # UNCHANGED (18-or-20-file invariant; F-5 host)
│   │       ├── data-poisoning.md                            # UNCHANGED (18-or-20-file invariant; F-6 host)
│   │       ├── model-theft.md                               # UNCHANGED (18-or-20-file invariant; F-5 + F-6 host)
│   │       ├── prompt-injection.md / agent-autonomy.md      # UNCHANGED (18-or-20-file invariant)
│   │       ├── risk-scorer.md                               # UNCHANGED (infrastructure-tier invariant)
│   │       ├── control-analyzer.md                          # UNCHANGED
│   │       ├── threat-report.md                             # UNCHANGED
│   │       ├── threat-infographic.md                        # UNCHANGED
│   │       └── report-assembler.md                          # UNCHANGED
│   │
│   └── skills/
│       ├── tachi-spoofing/
│       │   └── references/
│       │       └── detection-patterns.md                    # MODIFY (additive; appends Cat N+1 + N+2 + Pattern Category Disambiguation + Primary Sources extension) — 146 → ~200-220 lines
│       │
│       ├── tachi-tampering/
│       │   └── references/
│       │       └── detection-patterns.md                    # MODIFY (additive; appends Cat 11 + 12 + 13 + Pattern Category Disambiguation + Primary Sources extension) — 221 → ~315-345 lines
│       │
│       ├── tachi-info-disclosure/
│       │   └── references/
│       │       └── detection-patterns.md                    # MODIFY (additive; appends Cat N+1 + N+2 + N+3 + N+4 + Pattern Category Disambiguation + 4 Primary Sources entries) — 192 → ~315-345 lines
│       │
│       ├── tachi-privilege-escalation/
│       │   └── references/
│       │       └── detection-patterns.md                    # MODIFY (additive, dual-host M8; appends Cat N+1 privilege-gain variant + Pattern Category Disambiguation + Primary Sources extension) — 213 → ~245-260 lines
│       │
│       ├── tachi-repudiation/
│       │   └── references/
│       │       └── detection-patterns.md                    # MODIFY (additive, dual-host M8; appends Cat N+1 accountability-loss variant + Pattern Category Disambiguation + Primary Sources extension) — 148 → ~180-195 lines
│       │
│       ├── tachi-orchestration/
│       │   └── references/
│       │       └── dispatch-rules.md                        # UNCHANGED (all 5 host agents already registered; no cosmetic annotation defaults)
│       │
│       ├── tachi-shared/
│       │   └── references/
│       │       └── finding-format-shared.md                 # UNCHANGED (spoofing, tampering, info-disclosure, privilege-escalation, repudiation all in consumers list — verified at PRD time + plan time)
│       │
│       ├── tachi-output-integrity/                          # UNCHANGED (18-or-20-file invariant; F-1's companion — but referenced from F-7 tampering Cat 12 disjoint-tells annotation)
│       ├── tachi-misinformation/                            # UNCHANGED (18-or-20-file invariant; F-2's companion)
│       ├── tachi-tool-abuse/                                # UNCHANGED (18-or-20-file invariant; F-3 host companion)
│       ├── tachi-human-trust-exploitation/                  # UNCHANGED (18-or-20-file invariant; F-4's companion)
│       ├── tachi-denial-of-service/                         # UNCHANGED (18-or-20-file invariant; F-5 host companion)
│       ├── tachi-data-poisoning/                            # UNCHANGED (18-or-20-file invariant; F-6 host companion)
│       ├── tachi-model-theft/                               # UNCHANGED (18-or-20-file invariant; F-5/F-6 host companion)
│       └── tachi-{2 other detection skills}/                # UNCHANGED (18-or-20-file invariant)
│
├── schemas/
│   ├── finding.yaml                                         # UNCHANGED — schema_version stays "1.8"; id.pattern unchanged
│   └── taxonomy/                                            # UNCHANGED — read-only source for references validation
│       ├── owasp.yaml                                       # M1-M10 entries present (PRD/plan-time verified; 10 entries via grep)
│       ├── mitre-atlas.yaml                                 # N/A for F-7 (Mobile is ATT&CK Mobile, not ATLAS)
│       └── mitre-attack.yaml                                # T1474 + T1626 + T1398 entries **ABSENT** (PRD/plan-time grep-verified zero hits) — all 3 named in mitigation prose only on Cat 11 (T) + M8 Cat (E) + M8 Cat (R)
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-036-mobile-top-10-coverage-bundle.md     # NEW — Proposed → Accepted dual-commit (PRD/plan-time verified next-available; ADR-035 highest existing)
│
├── tests/
│   └── scripts/
│       ├── test_mobile_top_10_coverage_bundle_enrichment.py # NEW — structural-diff tests on Cat 1–N pre-existing byte-identity in all 5 companions + line-count tests on all 5 agents + MAESTRO grep tests on all 10 files + Pattern Category Disambiguation header presence test (4 matches single-host, 5 matches dual-host) + references-array assertion fixtures for Cat N+1/N+2 (S) + Cat 11/12/13 (T) + Cat N+1/N+2/N+3/N+4 (I) + M8 Cat (E) + M8 Cat (R) + ATT&CK-Mobile catalog-resolvability gap test (T1474/T1626/T1398 prose-only)
│       ├── test_backward_compatibility.py                   # MODIFY (additive infrastructure update) — `DETECTION_AGENT_PATHS` removes 5 enriched hosts (8 → 3 entries in dual-host path; 8 → 4 in single-host path); `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset adds spoofing + tampering [already present from F-6] + info-disclosure + privilege-escalation + repudiation companions (5 → 9 in dual-host path; 5 → 8 in single-host path); 6-baseline byte-identity loop unchanged; mobile-banking-app added to mutation-target exclusion list alongside agentic-app + consumer-agent-app + predictive-ml-app
│       └── fixtures/
│           └── mobile_top_10_coverage_bundle/               # NEW — fixture findings (10 in dual-host path, 9 in single-host path; one per closed M-item)
│               ├── valid_category_n_plus_1_spoofing_mobile_credential_finding.yaml      # S-{N} M1
│               ├── valid_category_n_plus_2_spoofing_mobile_authentication_finding.yaml  # S-{N} M3
│               ├── valid_category_11_tampering_mobile_supply_chain_finding.yaml         # T-{N} M2
│               ├── valid_category_12_tampering_mobile_ipc_finding.yaml                  # T-{N} M4 (with disjoint-tells annotation reference)
│               ├── valid_category_13_tampering_mobile_binary_protections_finding.yaml   # T-{N} M7
│               ├── valid_category_n_plus_1_info_disclosure_mobile_communication_finding.yaml  # I-{N} M5
│               ├── valid_category_n_plus_2_info_disclosure_mobile_privacy_finding.yaml         # I-{N} M6
│               ├── valid_category_n_plus_3_info_disclosure_mobile_data_storage_finding.yaml    # I-{N} M9
│               ├── valid_category_n_plus_4_info_disclosure_mobile_cryptography_finding.yaml    # I-{N} M10
│               ├── valid_category_n_plus_1_privilege_escalation_mobile_misconfig_priv_gain_finding.yaml  # E-{N} M8 privilege-gain variant (dual-host)
│               └── valid_category_n_plus_1_repudiation_mobile_misconfig_accountability_loss_finding.yaml  # R-{N} M8 accountability-loss variant (dual-host)
│
├── examples/
│   ├── web-app / microservices / ascii-web-api / mermaid-agentic-app / free-text-microservice / maestro-reference/  # UNCHANGED (SC-13 baselines; non-mobile — zero new findings)
│   ├── agentic-app/                                         # UNCHANGED (F-3 + F-5 mutation target — F-7 zero-touch)
│   ├── consumer-agent-app/                                  # UNCHANGED (F-4 mutation target — F-7 zero-touch)
│   ├── predictive-ml-app/                                   # UNCHANGED (F-6 mutation target — F-7 zero-touch)
│   └── mobile-banking-app/                                  # NEW — F-7 mutation target; PRD-day evening (Tue 2026-04-28 PM) ~2-3hr skeleton draft per team-lead MEDIUM-1 + plan-day (Wed 2026-04-29) ~4-5 hr full draft completion by architect + senior-backend-engineer co-authoring; ~180-220 lines architecture.md exhibiting all 6 mobile-platform topology indicators (mobile client process Android or iOS handling user credentials, credential-handling component using SharedPreferences/NSUserDefaults, secure-storage data store SQLite on device, mobile-backend API process with or without certificate pinning, third-party mobile SDK integration analytics/payment/crash-reporting, exposed debug/admin endpoint demonstrating M8 surface); baseline excluded from `test_backward_compatibility.py` byte-identity loop per Q6 plan-time decision (mirrors agentic-app + consumer-agent-app + predictive-ml-app precedent)
│
└── scripts/
    └── tachi_parsers.py                                     # UNCHANGED (validate references field — no F-7 changes; F-A3 will own source_attribution populator wiring later)
```

**Structure Decision**: Single-project layout (existing tachi repo structure). **Zero new top-level directories**. All changes confined to `.claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md`, `.claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md`, `docs/architecture/02_ADRs/`, `tests/scripts/`, `examples/mobile-banking-app/` (new). F-7 follows Feature 082 (lean-agent refactor) + ADR-023 (additive-only shared-reference edits) + Feature 142 (multi-agent component types) + F-1 + F-2 + F-3 + F-4 + F-5 + F-6 precedents. **F-7 is the first BLP-01 feature to exercise ADR-023 Decision 3 at four-or-five-agent scope simultaneously** — the eight-or-ten-file additive surface across four-or-five host-agent + companion pairs.

## System Design

### Components

**Modified components (additive edits only — F-7-owned)**:

1. **`spoofing` Threat Agent** (`.claude/agents/tachi/spoofing.md`)
   - **Edit 1** (two-line additive): metadata YAML `owasp_references` list extended with `"OWASP M1:2024 — Improper Credential Usage"` and `"OWASP M3:2024 — Insecure Authentication/Authorization"` appended. Pre-existing entries byte-identical.
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the mobile credential storage and mobile session handling surfaces alongside existing identity-spoofing surface — preserves existing `## Purpose` prose byte-identical
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing references-mention extended with `OWASP M1:2024, OWASP M3:2024, MASTG-AUTH, MASVS-AUTH` exemplar mention
   - Line count: ≤120 (STRIDE tier cap per ADR-023); PRD/plan-time baseline 51; expected post-edit 55-60
   - Five-section canonical layout, single `**MANDATORY**: Read` directive, zero MAESTRO references — all preserved

2. **`tampering` Threat Agent** (`.claude/agents/tachi/tampering.md`)
   - **Edit 1** (three-line additive): metadata YAML `owasp_references` list extended with `"OWASP M2:2024 — Inadequate Supply Chain Security"`, `"OWASP M4:2024 — Insufficient Input/Output Validation"`, `"OWASP M7:2024 — Insufficient Binary Protections"` appended. Pre-existing entries (including F-6 ML01:2023 + AML.T0015) byte-identical.
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the mobile SDK supply-chain integrity, mobile IPC input validation, and mobile binary protections surfaces alongside existing data-tampering surface and F-6 predictive-ML adversarial-input surface — preserves existing `## Purpose` prose byte-identical
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing references-mention extended with `OWASP M2/M4/M7:2024, MASTG-ARCH/CODE/RESILIENCE, MASVS-PLATFORM/RESILIENCE` exemplar mention; T1474 named in prose only
   - Line count: ≤120 (STRIDE tier cap per ADR-023); baseline 55; expected post-edit 60-66
   - Zero MAESTRO references preserved

3. **`info-disclosure` Threat Agent** (`.claude/agents/tachi/info-disclosure.md`)
   - **Edit 1** (four-line additive): metadata YAML `owasp_references` list extended with `"OWASP M5:2024 — Insecure Communication"`, `"OWASP M6:2024 — Inadequate Privacy Controls"`, `"OWASP M9:2024 — Insecure Data Storage"`, `"OWASP M10:2024 — Insufficient Cryptography"` appended. Pre-existing entries byte-identical.
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the mobile transport security, mobile privacy controls, mobile secure storage, and mobile cryptography surfaces alongside existing confidentiality-leakage surface — preserves existing `## Purpose` prose byte-identical
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing references-mention extended with `OWASP M5/M6/M9/M10:2024, MASTG-NETWORK/PRIVACY/STORAGE/CRYPTO, MASVS-NETWORK/PRIVACY/STORAGE/CRYPTO` exemplar mention
   - Line count: ≤120 (STRIDE tier cap per ADR-023); baseline 54; expected post-edit 60-66
   - Zero MAESTRO references preserved

4. **`privilege-escalation` Threat Agent** (`.claude/agents/tachi/privilege-escalation.md`) — **dual-host M8 path per Q1 plan-time decision**
   - **Edit 1** (one-line additive): metadata YAML `owasp_references` list extended with `"OWASP M8:2024 — Security Misconfiguration"` appended. Pre-existing entries byte-identical.
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the mobile security misconfiguration privilege-gain variant surface (exposed debug endpoints, default permissive ContentProvider/Service exports, missing app-attestation, missing root-detection on security-critical features) alongside existing broken-access-control / IDOR / role-escalation surfaces — preserves existing `## Purpose` prose byte-identical
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing references-mention extended with `OWASP M8:2024, MASTG-PLATFORM, MASVS-PLATFORM` exemplar mention; T1626 named in prose only
   - Line count: ≤120 (STRIDE tier cap per ADR-023); baseline 52; expected post-edit 56-58
   - Zero MAESTRO references preserved

5. **`repudiation` Threat Agent** (`.claude/agents/tachi/repudiation.md`) — **dual-host M8 path per Q1 plan-time decision**
   - **Edit 1** (one-line additive): metadata YAML `owasp_references` list extended with `"OWASP M8:2024 — Security Misconfiguration"` appended. Pre-existing entries byte-identical.
   - **Edit 2** (1–3 line additive append within `## Purpose` section): name the mobile security misconfiguration accountability-loss variant surface (missing audit logging on security-relevant events, disabled crash reporting in production, debug logs leaking sensitive data via Log.d/NSLog, missing tamper-evident timestamping) alongside existing missing-audit-trail / log-tampering surfaces — preserves existing `## Purpose` prose byte-identical
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing references-mention extended with `OWASP M8:2024, MASTG-PLATFORM, MASVS-PLATFORM` exemplar mention; T1398 named in prose only
   - Line count: ≤120 (STRIDE tier cap per ADR-023); baseline 50; expected post-edit 54-56
   - Zero MAESTRO references preserved

6. **spoofing Pattern Catalog** (`.claude/skills/tachi-spoofing/references/detection-patterns.md`)
   - **Edit 1** (additive append after current last category, ~line 146): **Pattern Category N+1 — Improper Mobile Credential Usage (M1)** with primary OWASP M1:2024, related MASTG-AUTH + MASVS-CRYPTO (named in mitigation prose at section-level granularity per Q4 plan-time decision); ≥4 indicators (target 5) covering credentials persisted in SharedPreferences (Android) / NSUserDefaults (iOS) / plaintext SQLite / app-bundled config files instead of platform-managed Keystore/Keychain, hardcoded API keys / secrets in mobile binaries, credential leakage via clipboard / debug logs / backup archives, missing biometric-bound key release for sensitive operations, missing credential rotation; ≥1 worked example (mobile-banking app persisting login credentials in SharedPreferences with `MODE_PRIVATE` rather than Android Keystore-protected EncryptedSharedPreferences); named mobile-specific mitigations distinct from generic spoofing controls (platform-managed secure storage Android Keystore + iOS Keychain, credential rotation, no hardcoded secrets in shipped binaries, biometric-bound key release for sensitive operations)
   - **Edit 2** (additive append after Cat N+1): **Pattern Category N+2 — Insecure Mobile Authentication / Authorization (M3)** with primary OWASP M3:2024, related MASTG-AUTH + MASVS-AUTH (named in mitigation prose); ≥4 indicators (target 5) covering bypassed certificate pinning / pinning-only-on-specific-domains, broken or absent JWT validation in mobile clients (no signature verification, no `iss` / `aud` / `exp` checks), weak refresh-token handling (long-lived tokens not bound to device), missing step-up authentication for sensitive operations (e.g., money movement, profile changes), client-side authorization decisions that the server doesn't re-validate; ≥1 worked example (mobile-banking app missing biometric step-up on money-movement operations + certificate pinning enabled only on production domain leaving staging exposed); named mitigations (server-side authorization enforcement, certificate pinning with backup-pin rotation, refresh-token binding to device fingerprint, biometric step-up on high-risk operations)
   - **Edit 3** (additive Pattern Category Disambiguation subsection per ADR-036 D-9): explicit non-overlap carve between **spoofing Cat 1–N** (existing identity/credential signal class — generic web/API authentication-bypass, credential-stuffing) and **Cat N+1 / N+2** (mobile-specific credential storage and mobile-specific authentication/authorization). Same architecture (hybrid web+mobile) may legitimately surface both pre-existing and Cat N+1/N+2 findings without duplication.
   - **Edit 4** (additive list extension on `## Primary Sources`): append `OWASP M1:2024 — Improper Credential Usage`, `OWASP M3:2024 — Insecure Authentication/Authorization`
   - Pre-existing Cat 1–N + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries) remain byte-identical pre/post edit per ADR-023 Decision 3 (BLOCKER per SC-3)

7. **tampering Pattern Catalog** (`.claude/skills/tachi-tampering/references/detection-patterns.md`)
   - **Edit 1** (additive append after F-6 Cat 10, ~line 221): **Pattern Category 11 — Mobile Supply Chain Integrity (M2)** with primary OWASP M2:2024, related MASTG-ARCH + MITRE ATT&CK Mobile T1474 (named in mitigation prose only — NOT catalog-resolvable per Q3); ≥4 indicators (target 5) covering third-party mobile SDKs and libraries integrated without checksum verification or signed-artifact policy, sideloaded APK distribution paths bypassing app-store review, CocoaPods / Gradle / Swift Package Manager dependencies pulled from unsigned sources, missing app-store provenance review on production releases, missing reproducible-build enforcement; ≥1 worked example (mobile-banking app integrating a third-party analytics SDK pulled directly via Gradle from a private Maven repo without checksum verification or signed-artifact policy); named mitigations (SDK signature verification, dependency manifest pinning with reproducible builds, app-store-only distribution, supplier-provenance review gate before SDK adoption)
   - **Edit 2** (additive append after Cat 11): **Pattern Category 12 — Mobile IPC Input Validation (M4)** with primary OWASP M4:2024, related MASTG-CODE + MASVS-PLATFORM (mitigation prose); **with explicit disjoint-tells annotation referencing F-1 `output-integrity` agent boundary per ADR-036 D-5**: tampering Cat 12 owns mobile-IPC-input-side validation (deep-link parameters, Intent extras, URL-scheme parameters, exported ContentProvider gates); `output-integrity` owns LLM-output-side sanitization (LLM-generated content flowing into browser/SQL/shell sinks). Disjoint architectural-tells prevent duplicate emission on hybrid LLM-plus-mobile architectures; ≥4 indicators (target 5) covering Android Intent injection on exposed Activity / Service / BroadcastReceiver, iOS URL-scheme injection on `application(_:open:options:)`, deep-link parameter tampering reaching trusted operations without re-validation, exported ContentProvider with no permission gates, pasteboard-injection paths into shared-clipboard handlers; ≥1 worked example (mobile-banking app exporting a `MoneyTransferActivity` without permission gating, accepting Intent extras `recipient_account` and `amount` directly into transfer logic without re-authentication); named mitigations (explicit Intent component routing, URL-scheme allowlist with parameter validation, deep-link claim verification Android App Links / iOS Universal Links, ContentProvider permission scoping with signature-level Android permissions)
   - **Edit 3** (additive append after Cat 12): **Pattern Category 13 — Insufficient Mobile Binary Protections (M7)** with primary OWASP M7:2024, related MASTG-RESILIENCE + MASVS-RESILIENCE (mitigation prose); ≥4 indicators (target 5) covering missing root/jailbreak detection in security-critical features (banking, payment, regulated content), missing anti-tampering stubs (RASP, integrity self-checks), missing code obfuscation on production builds, debug symbols in shipped binaries, missing emulator-detection on fraud-sensitive flows; ≥1 worked example (mobile-banking app shipping production builds with debug symbols and no root-detection on the money-transfer flow); named mitigations (root/jailbreak detection with policy-based response, RASP integration with attestation, ProGuard/R8 obfuscation on Android, bitcode + symbol-stripping on iOS, emulator-detection on payment and KYC flows)
   - **Edit 4** (additive Pattern Category Disambiguation subsection per ADR-036 D-9): explicit non-overlap carve between **tampering Cat 1–9** (pre-existing data-tampering / supply-chain integrity / injection / deserialization / etc.) and **Cat 10** (F-6 Adversarial Input Manipulation Predictive ML) and **Cat 11/12/13** (mobile-specific). Cat 12 cross-link to F-1 `output-integrity` boundary explicitly named per ADR-036 D-5. Same architecture (e.g., LLM-fronted mobile app) may legitimately surface Cat 1–9 + Cat 10 + Cat 11/12/13 + `output-integrity` findings without overlap.
   - **Edit 5** (additive list extension on `## Primary Sources`): append `OWASP M2:2024 — Inadequate Supply Chain Security`, `OWASP M4:2024 — Insufficient Input/Output Validation`, `OWASP M7:2024 — Insufficient Binary Protections`
   - Pre-existing Cat 1–10 (post-F-6 baseline) + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries including F-6 ML01:2023) remain byte-identical pre/post edit per ADR-023 Decision 3 (BLOCKER per SC-6)

8. **info-disclosure Pattern Catalog** (`.claude/skills/tachi-info-disclosure/references/detection-patterns.md`)
   - **Edit 1** (additive append after current last category, ~line 192): **Pattern Category N+1 — Insecure Mobile Communication (M5)** with primary OWASP M5:2024, related MASTG-NETWORK + MASVS-NETWORK (mitigation prose); ≥4 indicators (target 5) covering cleartext HTTP traffic from mobile clients (no `usesCleartextTraffic="false"` on Android, no `NSAppTransportSecurity` exception audit on iOS), missing TLS certificate pinning enabling MITM via root-CA installation or rogue Wi-Fi, downgrade attacks via HTTP-to-HTTPS redirect handling, weak TLS cipher acceptance on mobile clients, missing HSTS-equivalent enforcement at app-level; ≥1 worked example (mobile-banking app's network security config allows cleartext traffic to staging endpoints + missing certificate pinning on production endpoints); named mitigations (cleartext-traffic prohibition in network security config, certificate pinning with backup-pin rotation, TLS 1.3 with strict cipher allowlist, HSTS-equivalent enforcement at app-level)
   - **Edit 2** (additive append after Cat N+1): **Pattern Category N+2 — Inadequate Mobile Privacy Controls (M6)** with primary OWASP M6:2024, related MASTG-PRIVACY + MASVS-PRIVACY (mitigation prose); ≥4 indicators (target 5) covering PII / PHI persisted in device-local caches without expiry, telemetry / analytics SDKs collecting personal data without disclosure or consent gating, clipboard exposure on sensitive fields (passwords, PII), screenshot leakage on sensitive screens (no FLAG_SECURE on Android, no equivalent screenshot prevention on iOS), over-broad permission requests on first launch; ≥1 worked example (mobile-banking app caching account-balance data without TTL + missing FLAG_SECURE on the transaction-history screen); named mitigations (data-minimization on caches with TTL enforcement, consent-gated telemetry with opt-out, FLAG_SECURE / equivalent screenshot prevention on PII screens, just-in-time permission prompts with graceful denial paths)
   - **Edit 3** (additive append after Cat N+2): **Pattern Category N+3 — Insecure Mobile Data Storage (M9)** with primary OWASP M9:2024, related MASTG-STORAGE + MASVS-STORAGE (mitigation prose); ≥4 indicators (target 5) covering unencrypted SQLite / Realm / Room databases on device, unencrypted KeyValue stores (SharedPreferences plaintext, NSUserDefaults plaintext), cloud-backup leakage (iCloud / Google-Drive backup including sensitive app data without exclusion), external SD-card writes for sensitive files, world-readable file permissions on Android internal storage; ≥1 worked example (mobile-banking app storing transaction history in unencrypted SQLite without `allowBackup="false"` excluding it from Google Drive backup); named mitigations (SQLCipher / Realm encryption with platform-keyring-derived keys, EncryptedSharedPreferences Android Jetpack / Keychain-stored secrets iOS, `allowBackup="false"` on Android with sensitive data partitioning, internal-storage-only writes for sensitive files)
   - **Edit 4** (additive append after Cat N+3): **Pattern Category N+4 — Insufficient Mobile Cryptography (M10)** with primary OWASP M10:2024, related MASTG-CRYPTO + MASVS-CRYPTO (mitigation prose); ≥4 indicators (target 5) covering weak key derivation on user PINs (low PBKDF2 iteration counts, no salting, no per-device entropy), custom-rolled crypto algorithms in mobile binaries, hardcoded symmetric keys in shipped binaries, insecure PRNG seeding (e.g., `java.util.Random` for security purposes), deprecated cipher suites (DES, RC4, MD5, SHA1) for sensitive operations; ≥1 worked example (mobile-banking app deriving encryption keys from a 4-digit PIN with PBKDF2 iteration count of 1000 and no salting); named mitigations (platform-provided key derivation Argon2id / scrypt / PBKDF2 with ≥600k iterations, platform crypto APIs only with no custom algorithms, key derivation from platform-keyring-bound material, SecureRandom for all cryptographic randomness, AES-GCM and SHA-256+ as the minimum baseline)
   - **Edit 5** (additive Pattern Category Disambiguation subsection per ADR-036 D-9): explicit non-overlap carve between **info-disclosure Cat 1–N** (pre-existing confidentiality-leakage signal class — error-message exposure, excessive API responses, side-channel leakage) and **Cat N+1/N+2/N+3/N+4** (mobile-specific transport / privacy / storage / cryptography). Same architecture may legitimately surface both pre-existing and Cat N+1/N+2/N+3/N+4 findings on different DFD elements (e.g., backend API error-message exposure surfacing pre-existing Cat finding + mobile client cleartext traffic surfacing Cat N+1).
   - **Edit 6** (additive list extension on `## Primary Sources`): append `OWASP M5:2024 — Insecure Communication`, `OWASP M6:2024 — Inadequate Privacy Controls`, `OWASP M9:2024 — Insecure Data Storage`, `OWASP M10:2024 — Insufficient Cryptography`
   - Pre-existing Cat 1–N + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries) remain byte-identical pre/post edit per ADR-023 Decision 3 (BLOCKER per SC-9)

9. **privilege-escalation Pattern Catalog** (`.claude/skills/tachi-privilege-escalation/references/detection-patterns.md`) — **dual-host M8 path per Q1 plan-time decision**
   - **Edit 1** (additive append after current last category, ~line 213): **Pattern Category N+1 — Mobile Security Misconfiguration: Privilege-Gain Variant (M8)** with primary OWASP M8:2024, related MASTG-PLATFORM + MITRE ATT&CK Mobile T1626 (named in mitigation prose only — NOT catalog-resolvable per Q3); ≥4 indicators (target 5) covering exposed debug endpoints in production builds (`adb shell` access points, debug-only Activities exported), default permissive ContentProvider / Service exports without permission scoping, missing app-attestation enabling tampered-binary execution against trusted backend, missing root-detection in security-critical feature gates, missing certificate-pinning enforcement on debug builds shipped to production; ≥1 worked example (mobile-banking app's production build retaining a debug-only Activity exposing internal database state via `adb shell am start` because debug guard removed during signing); named mitigations (production-build flag stripping debug code paths, ContentProvider/Activity export scoping with Android signature-level permissions, Play Integrity / DeviceCheck attestation gating, root-detection on security-critical UI flows)
   - **Edit 2** (additive Pattern Category Disambiguation subsection per ADR-036 D-9): explicit non-overlap carve between **privilege-escalation Cat 1–N** (pre-existing broken-access-control / IDOR / role-escalation / multi-tenancy boundary violations) and **Cat N+1** (mobile-specific misconfiguration enabling privilege gain). Same architecture (mobile + backend) may legitimately surface both pre-existing IDOR findings on backend API + Cat N+1 finding on mobile client misconfiguration.
   - **Edit 3** (additive list extension on `## Primary Sources`): append `OWASP M8:2024 — Security Misconfiguration`
   - Pre-existing Cat 1–N + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries) remain byte-identical pre/post edit per ADR-023 Decision 3 (BLOCKER per SC-10)

10. **repudiation Pattern Catalog** (`.claude/skills/tachi-repudiation/references/detection-patterns.md`) — **dual-host M8 path per Q1 plan-time decision**
    - **Edit 1** (additive append after current last category, ~line 148): **Pattern Category N+1 — Mobile Security Misconfiguration: Accountability-Loss Variant (M8)** with primary OWASP M8:2024, related MASTG-PLATFORM + MITRE ATT&CK Mobile T1398 (named in mitigation prose only — NOT catalog-resolvable per Q3); ≥4 indicators (target 5) covering missing audit logging on security-relevant mobile events (login, money-movement, permission grants), disabled crash reporting in production preventing post-incident root-cause analysis, debug logs leaking sensitive data in production via `Log.d` / `NSLog` not stripped, missing tamper-evident timestamping on audit records that the mobile app emits, missing log-integrity verification at backend ingestion gate; ≥1 worked example (mobile-banking app's production build retaining `Log.d("auth", "user=" + username + " token=" + token)` statements stripped only in obfuscation pass that wasn't applied to release config); named mitigations (structured audit logging on security-relevant mobile events with server-side persistence, production-build log-statement stripping ProGuard/R8 rules, tamper-evident timestamping on audit records, crash-reporting enablement with PII redaction)
    - **Edit 2** (additive Pattern Category Disambiguation subsection per ADR-036 D-9): explicit non-overlap carve between **repudiation Cat 1–N** (pre-existing missing-audit-trail / log-tampering / timestamp-manipulation) and **Cat N+1** (mobile-specific misconfiguration enabling accountability loss). Same architecture (mobile + backend) may legitimately surface both pre-existing log-tampering findings on backend audit pipeline + Cat N+1 finding on mobile client misconfiguration.
    - **Edit 3** (additive list extension on `## Primary Sources`): append `OWASP M8:2024 — Security Misconfiguration`
    - Pre-existing Cat 1–N + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` + `## Primary Sources` (existing entries) remain byte-identical pre/post edit per ADR-023 Decision 3 (BLOCKER per SC-10)

11. **Public Per-Feature ADR** (`docs/architecture/02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md`)
    - Proposed → Accepted dual-commit (ADR-027/032/034/035 precedent)
    - **10 numbered Decisions** in body (architect MEDIUM-2 plan-time RESOLVED: 10-decision structure mirroring ADR-035 D-9 Pattern Category Disambiguation precedent):
      - **Decision 1**: Heuristic A enrichment vs. new agents at **four-or-five-agent scope** — signal-class identity rationale (M1 + M3 → spoofing identity/credential sub-class; M2 + M4 + M7 → tampering data-integrity / supply-chain / binary-integrity sub-class; M5 + M6 + M9 + M10 → info-disclosure confidentiality sub-class; M8 dual-host: privilege-gain variant → privilege-escalation broken-access-control sub-class; accountability-loss variant → repudiation missing-audit-trail sub-class). One hypothetical new agent (`mobile-platform`) explicitly NOT created.
      - **Decision 2**: Additive-only edit discipline per ADR-023 Decision 3 with byte-identity proof on Cat 1–N pre-existing in all five companions
      - **Decision 3**: **Canonical 10-or-11-row Mobile Top 10 sub-pattern → owning-agent mapping table with severity-hint annotation column** (Q5 plan-time RESOLVED: YES, parity with ADR-034 + ADR-035; the audit deliverable). Closure rows: (a) M1 improper credential usage → spoofing Cat N+1 (severity HIGH default per banking/credentials sensitivity); (b) M2 inadequate supply chain security → tampering Cat 11 (HIGH default); (c) M3 insecure authentication/authorization → spoofing Cat N+2 (HIGH default); (d) M4 insufficient input/output validation → tampering Cat 12 (MEDIUM-HIGH default); (e) M5 insecure communication → info-disclosure Cat N+1 (HIGH default); (f) M6 inadequate privacy controls → info-disclosure Cat N+2 (MEDIUM default); (g) M7 insufficient binary protections → tampering Cat 13 (MEDIUM default); (h) M8 security misconfiguration: privilege-gain variant → privilege-escalation Cat N+1 (HIGH default per dual-host) + accountability-loss variant → repudiation Cat N+1 (MEDIUM default per dual-host); (i) M9 insecure data storage → info-disclosure Cat N+3 (HIGH default); (j) M10 insufficient cryptography → info-disclosure Cat N+4 (HIGH default). Reference rows: (k) ADR-023 D3 enabling rule; (l) ADR-030 D1 Heuristic A; (m) ADR-035 closing forward-scope marker forecast (verified fulfilled).
      - **Decision 4**: **M8 dual-host disjoint architectural-tells decision** (Q1 plan-time RESOLVED: dual-host): privilege-escalation Cat N+1 owns privilege-gain variant (exposed debug endpoints, ContentProvider/Service export gaps, missing app-attestation, missing root-detection); repudiation Cat N+1 owns accountability-loss variant (missing audit logging, disabled crash reporting, debug-log leakage, missing tamper-evident timestamping). Same architecture exhibiting both variants may legitimately surface both findings without duplication. Mirrors ADR-035 D-4 ML06 two-facet precedent at the F-7 architectural-tell layer.
      - **Decision 5**: **M4 cross-agent boundary clarification with F-1 `output-integrity`** (Q2 plan-time RESOLVED): tampering Cat 12 owns mobile-IPC-input-side validation (deep-link parameters, Intent extras, URL-scheme parameters, exported ContentProvider gates, pasteboard-injection paths); F-1's `output-integrity` agent owns LLM-output-side sanitization (LLM-generated content flowing into browser/SQL/shell sinks). Disjoint architectural-tells prevent duplicate emission on hybrid LLM-plus-mobile architectures. Mirrors ADR-035 D-5 ML03 vs ML04 disjoint-tells precedent at the F-7 cross-axis layer.
      - **Decision 6**: No schema bump — reuses S-{N} / T-{N} / I-{N} / E-{N} / R-{N} prefixes; structurally symmetric with F-3 (ADR-032 lines 84+182 forecast), F-5 (ADR-034 lines 192–204 forecast), F-6 (ADR-035 lines 84+182 forecast). **Fourth BLP-01 detection feature with no schema bump after F-3 + F-5 + F-6; first at four-or-five-agent enrichment scope.** Asymmetric to F-1/F-2/F-4 (which all bumped schema). Fulfills ADR-035 closing forward-scope marker explicit forecast.
      - **Decision 7**: No consumers-list edit — `spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation` all already in `finding-format-shared.md` consumers list (PRD/plan-time verified). MITRE ATT&CK Mobile catalog gap codified per F-A2 referential-integrity contract: T1474/T1626/T1398 are NOT catalog-resolvable per `schemas/taxonomy/mitre-attack.yaml` (Q3 plan-time grep-verified zero hits, 3-of-3 prose-only at worst-case scale; mirrors F-5 T1496 + F-6 3-of-6 ATLAS precedent).
      - **Decision 8**: No functional orchestrator/dispatch-rules edit — all 4-or-5 host agents already fully registered. No cosmetic annotation defaults.
      - **Decision 9**: **Pattern Category Disambiguation requirement on four or five companions** (architect MEDIUM-2 RESOLVED): spoofing disambiguates Cat N+1/N+2 from Cat 1–N; tampering disambiguates Cat 11/12/13 from Cat 1–9 (existing) + Cat 10 (F-6); info-disclosure disambiguates Cat N+1/N+2/N+3/N+4 from Cat 1–N; privilege-escalation disambiguates Cat N+1 from Cat 1–N (dual-host); repudiation disambiguates Cat N+1 from Cat 1–N (dual-host). Total 5 disambiguation subsections in dual-host path (4 in single-host fallback). Mirrors F-3 ADR-032 D7 + F-5 ADR-034 D7 + F-6 ADR-035 D-9 precedent at four-or-five-agent scale.
      - **Decision 10**: No `source_attribution` populator wiring extension on host agents — deferred to F-A3; F-7 cites Mobile Top 10 references in prose-level `references:` array only; F-A3 inheritance one-way
      - (Optional Decision 11): Public ADR omits commercial framing per SDR-001 Option C
    - Cross-references: ADR-021 (byte-identity baseline harness), ADR-023 (lean+skill-references pattern, additive-only edits Decision 3), ADR-027 (Proposed → Accepted dual-commit pattern), ADR-028 (source attribution schema extension + Decision 6 F-A3 deferral), ADR-030 Decision 1 (signal-class taxonomy in LLM tier; same rule applied at STRIDE tier in F-7), ADR-031 Decision 8 (regex-alternation minor-bump rule as the **asymmetry** F-7 does NOT invoke — fourth no-bump enrichment), ADR-032 (first enrichment-branch execution at single-agent scope), ADR-034 (second enrichment-branch execution at two-agent scope), ADR-035 (third enrichment-branch execution at three-agent scope; **explicit cross-reference to closing forward-scope marker forecast** that F-7 will land at four-or-five-agent scope with no schema bump — fulfilled)
    - Detection Calibration Note: clarifies structural-absence detection style consistent with F-1 / F-2 / F-4 / F-5 / F-6 absence-style; acceptable FP risk on architectures with implicit-but-undeclared mobile-platform controls per existing tachi convention
    - Zero-MAESTRO-reference invariant: ADR-036 itself contains zero MAESTRO references in Decision sections (mirrors agent file invariant per ADR-023 Decision 2)
    - Revision History table tracking Proposed → Accepted dates; post-merge SHA fill recording squash commit

### Data Flow

Given a DFD architecture description, the orchestrator dispatches `spoofing` **as it does today** when any DFD `External Entity`, `Process`, or `Data Flow` element matches existing spoofing trigger keywords AND `tampering` when any `Process`, `Data Store`, or `Data Flow` matches existing tampering trigger keywords AND `info-disclosure` when any `Process`, `Data Store`, or `Data Flow` matches existing info-disclosure trigger keywords AND `privilege-escalation` when any `Process` matches existing privilege-escalation trigger keywords AND `repudiation` when any `External Entity` or `Process` matches existing repudiation trigger keywords. Each agent reads its companion `detection-patterns.md` via the existing single `**MANDATORY**: Read` directive, evaluates pattern categories on each dispatched component, and emits zero or more findings. The new Pattern Categories (Cat N+1/N+2 in spoofing; Cat 11/12/13 in tampering; Cat N+1/N+2/N+3/N+4 in info-disclosure; M8 Cat in privilege-escalation; M8 Cat in repudiation) enforce the **mobile-platform topology gate** (FR-15 spec): findings emit only when the architecture additionally exhibits mobile-platform indicators (declared mobile client component Android/iOS, mobile-backend API process, secure-storage data store, mobile SDK integration declaration, certificate-pinning declaration, Keystore/Keychain mention, biometric reference, mobile permissions declaration, package-name signal, ContentProvider/Activity export declaration). Cat 12 (tampering, mobile IPC) emits independently from F-1's `output-integrity` agent — same architecture (LLM-fronted mobile app) may surface both Cat 12 and `output-integrity` findings without duplication per ADR-036 D-5 disjoint architectural-tells. M8 dual-host emission: privilege-escalation Cat N+1 (privilege-gain variant) and repudiation Cat N+1 (accountability-loss variant) are emitted independently when the architecture exhibits both variants per ADR-036 D-4 disjoint architectural-tells. Findings flow through orchestrator Phase 3, Phase 4 (referential validation reads `references` array — no F-7 changes; F-A3 will own `source_attribution` populator wiring later), and Phase 5 (deduplication) **identically** to existing S-{N}, T-{N}, I-{N}, E-{N}, R-{N} findings. No consumer-tier changes required. Report-tier rendering (`threat-report.md`, `threats.md`) groups all `S-{N}` findings cohesively in `category: spoofing` section, all `T-{N}` findings cohesively in `category: tampering` section, all `I-{N}` findings cohesively in `category: info-disclosure` section, all `E-{N}` findings cohesively in `category: privilege-escalation` section, all `R-{N}` findings cohesively in `category: repudiation` section — single-namespace ID space per agent, sequential numbering across all categories.

### Tech Stack

- **Agent / skill files**: Markdown + YAML (ADR-023 lean-agent + additive-only shared-reference pattern)
- **Schema**: `schemas/finding.yaml` v1.8 — **unchanged** (S, T, I, E, R prefixes already enumerated; F-7 reuses all five)
- **Taxonomy catalogs**: `schemas/taxonomy/{owasp,mitre-attack}.yaml` (F-A1, unchanged) — consumed read-only for `references` validation. M1-M10 catalog-resolvable; **T1474, T1626, T1398 ALL ABSENT** (Q3 plan-time grep-verified; named in mitigation prose only); MASTG/MASVS catalog files do NOT exist (F-A1 follow-on scope per spec OoS) — section-level citations appear in mitigation prose only.
- **Orchestrator dispatch**: `.claude/agents/tachi/orchestrator.md` + `.claude/skills/tachi-orchestration/references/dispatch-rules.md` — **unchanged** (all 4 or 5 host agents already fully registered)
- **Parser**: `scripts/tachi_parsers.py` (unchanged — `references` field validation already in place; F-A3 will own `source_attribution` populator wiring later)
- **Test harness**: pytest + `tests/scripts/test_backward_compatibility.py` (modified additively — `DETECTION_AGENT_PATHS` removes 5 enriched hosts (8 → 3 entries dual-host path); `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` adds 4 new entries (5 → 9 dual-host path; tampering already present from F-6); 6-baseline byte-identity loop unchanged thanks to mobile-platform topology gate ensuring zero impact on non-mobile baselines; mobile-banking-app added to mutation-target exclusion list) + new `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py` (structural-diff + line-count + MAESTRO grep + Pattern Category Disambiguation header presence test 5 matches dual-host + references-array assertion fixtures for 10 finding fixtures + ATT&CK-Mobile catalog-resolvability gap test)
- **Example regeneration pipeline**: `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` (existing pipeline, unchanged)
- **Typst templates**: no edits — PDF renderer reads `threats.md` / `risk-scores.md` / `compensating-controls.md` and existing pipeline artifacts auto-render post-regeneration
- **ADR dual-commit**: standard Proposed → Accepted lifecycle via `gh pr` + squash merge (ADR-027/032/034/035 precedent)
- **New example architecture**: `examples/mobile-banking-app/architecture.md` authored across PRD-day evening skeleton (~2-3 hr per team-lead MEDIUM-1 mitigation) + plan-day Wed (~4-5 hr full draft completion) by architect + senior-backend-engineer co-authoring; exhibits all 6 mobile-platform topology indicators

## Phase 0: Research

**Status**: Populated by `/aod.spec` at [research.md](./research.md). Key grounding facts re-confirmed at plan time (2026-04-28):

- `.claude/agents/tachi/spoofing.md` is **51 lines** (PRD/spec/plan-time verified; expected post-edit 55-60 lines)
- `.claude/agents/tachi/tampering.md` is **55 lines** post-F-6 (PRD/spec/plan-time verified; existing `owasp_references` includes F-6 ML01:2023 + AML.T0015 — F-7 appends OWASP M2/M4/M7:2024, 3-line append; expected post-edit 60-66 lines)
- `.claude/agents/tachi/info-disclosure.md` is **54 lines** (PRD/spec/plan-time verified; expected post-edit 60-66 lines)
- `.claude/agents/tachi/privilege-escalation.md` is **52 lines** (PRD/spec/plan-time verified; expected post-edit 56-58 lines in dual-host M8 path)
- `.claude/agents/tachi/repudiation.md` is **50 lines** (PRD/spec/plan-time verified; expected post-edit 54-56 lines in dual-host M8 path)
- `.claude/skills/tachi-spoofing/references/detection-patterns.md` is **146 lines** (PRD/spec/plan-time verified) with Cat 1–N + Overview + Targeted DFD Element Types + Trigger Keywords + Primary Sources
- `.claude/skills/tachi-tampering/references/detection-patterns.md` is **221 lines** post-F-6 (PRD/spec/plan-time verified) with Cat 1–10 + structural sections including F-6 Cat 10 Adversarial Input Manipulation
- `.claude/skills/tachi-info-disclosure/references/detection-patterns.md` is **192 lines** (PRD/spec/plan-time verified) with Cat 1–N + structural sections
- `.claude/skills/tachi-privilege-escalation/references/detection-patterns.md` is **213 lines** (PRD/spec/plan-time verified) with Cat 1–N + structural sections
- `.claude/skills/tachi-repudiation/references/detection-patterns.md` is **148 lines** (PRD/spec/plan-time verified) with Cat 1–N + structural sections
- `schemas/finding.yaml:13` `schema_version: "1.8"` (post-F-6; F-7 does NOT bump)
- `schemas/finding.yaml` `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$"` — `S`, `T`, `R`, `I`, `E` already enumerated; F-7 reuses all five
- `schemas/taxonomy/owasp.yaml` contains **M1-M10** records (10 entries plan-time-verified via grep)
- `schemas/taxonomy/mitre-attack.yaml` catalog-resolvability for ATT&CK Mobile entries:
  - **T1474** (Supply Chain Compromise — Mobile): **ABSENT** — named in Cat 11 (T) mitigation prose only
  - **T1626** (Abuse Elevation Control Mechanism — Mobile): **ABSENT** — named in M8 Cat (E) privilege-gain variant mitigation prose only
  - **T1398** (Boot or Logon Initialization Scripts — Mobile): **ABSENT** — named in M8 Cat (R) accountability-loss variant mitigation prose only
  - **All 3 of 3 prose-only** at the worst-case scale of any BLP-01 enrichment feature (compare F-5 1-of-1 T1496 prose-only; F-6 3-of-6 ATLAS prose-only)
- MASTG/MASVS section-level citations (e.g., MASTG-AUTH, MASVS-CRYPTO) appear in mitigation prose only at section-level granularity per Q4 plan-time decision; test-case-ID granularity (MSTG-AUTH-1, MSTG-CRYPTO-1) is F-A1 follow-on scope (no MASTG taxonomy YAML exists yet)
- `.claude/skills/tachi-shared/references/finding-format-shared.md` consumers list contains all 5 host agents (PRD/spec/plan-time verified — no edits needed)
- `.claude/skills/tachi-orchestration/references/dispatch-rules.md` references all 5 host agents at multiple callsites (no functional dispatch edit needed; no cosmetic annotation defaults)
- ADR-036 does NOT yet exist (PRD/spec/plan-time verified next-available ADR number; ADR-035 is highest existing per `ls docs/architecture/02_ADRs/`)
- 0 MAESTRO references in all 10 target files (PRD/spec/plan-time grep-verified)
- F-1, F-2, F-3, F-4, F-5, F-6 ADRs (ADR-030, ADR-031, ADR-032, ADR-033, ADR-034, ADR-035) all Accepted; F-7 ADR-036 cross-references ADR-030 D1, ADR-031 D8 (asymmetry — F-7 does NOT invoke), ADR-032 (single-agent precedent), ADR-034 (two-agent precedent), ADR-035 (three-agent precedent + closing forward-scope marker forecast)
- Empirical mobile-signal grep across `examples/*/architecture.md`: only 1 incidental match in `microservices/architecture.md` ("End-user browser or mobile app" generic External Entity descriptor — NOT a structural mobile-platform topology indicator). Zero structural mobile-platform components across all 7 existing examples. New `examples/mobile-banking-app/` authoring is the default plan-day path (Q2 RESOLVED).

**Open research items resolved at PRD/spec time** (not re-litigated during /aod.project-plan):
- **Q1**: M8 split (single-host vs dual-host) — RESOLVED at plan time: **DUAL-HOST**. Architect adjudication on representative mobile architectures: privilege-escalation owns privilege-gain variant; repudiation owns accountability-loss variant; mirrors ADR-035 D-4 ML06 two-facet precedent.
- **Q2**: Mutation-target archetype — RESOLVED at PRD time: `mobile-banking-app` (covers credentials, payment, biometrics, secure storage, certificate pinning across all M-items). Authoring track per team-lead MEDIUM-1: PRD-day evening (Tue 2026-04-28 PM) ~2-3 hr skeleton + plan-day Wed (~4-5 hr full draft).
- **Q3**: MITRE ATT&CK Mobile catalog-resolvability for T1474/T1626/T1398 — RESOLVED at spec time via grep on `schemas/taxonomy/mitre-attack.yaml`: **0 of 3 catalog-resolvable**; ALL 3 prose-only at worst-case scale (3-of-3). The 3 absent entries appear in mitigation prose only at greater scale than F-6's 3-of-6 prose-only. Catalog augmentation deferred to F-A1 follow-on per spec OoS.
- **Q4**: MASTG/MASVS reference granularity — RESOLVED at plan time: **section-level** (e.g., `MASTG-AUTH`, `MASVS-CRYPTO`). Test-case-ID granularity (`MSTG-AUTH-1`) is F-A1 follow-on scope after MASTG taxonomy YAML is added.
- **Q5**: ADR-036 mapping-table column structure — RESOLVED at plan time: **YES**, severity-hint column (parity with ADR-034 5-row + ADR-035 11-row precedent for cross-feature comparability).
- **Q6**: `mobile-banking-app/` post-F-7 baseline strategy — RESOLVED at plan time: **EXCLUDED** from `BASELINE_EXAMPLES` byte-identity loop (mirrors `agentic-app`, `consumer-agent-app`, `predictive-ml-app/` precedent — mutation targets stay excluded until explicit promotion event).
- **Architect MEDIUM-2** (ADR-036 9-vs-10 decision structure) — RESOLVED at plan time: **10-DECISION STRUCTURE** mirroring ADR-035 D-9 Pattern Category Disambiguation precedent. Discrete D-9 codifies disambiguation requirement on 4 (single-host) or 5 (dual-host) companions.
- **Team-Lead MEDIUM-1** (plan-day overload mitigation — architect-critical-path 12-14 hrs Wed) — RESOLVED at plan time: **PRD-day evening skeleton (Wave 0.0)** + **plan-day full draft (Wave 0.1)** parallel mobile-banking-app authoring track; Day 1 AM cleanup if skeleton-quality issues surface.
- **Team-Lead MEDIUM-2** (Day 2 AM throughput asymmetry — info-disclosure 4 cats) — RESOLVED at plan time: **FR-7 task split into 4 sequential sub-task checkpoints** (M5 / M6 / M9 / M10 each at ~75-90 min with rollback capability). Mirrors F-6 Wave 2.1/2.2/2.3 precedent at 4-cat scale.

## Phase 1: Design & Contracts

**Prerequisites**: research.md populated (Phase 0 complete)

### Finding IR Contract (`contracts/finding-contract.md`)

**Purpose**: Document the shape of Cat N+1/N+2 `S-{N}` findings (spoofing), Cat 11/12/13 `T-{N}` findings (tampering), Cat N+1/N+2/N+3/N+4 `I-{N}` findings (info-disclosure), M8 Cat `E-{N}` findings (privilege-escalation), and M8 Cat `R-{N}` findings (repudiation) emitted by the enriched agents, including `references` array invariants, mitigation-text rules (with prose-only handling for non-catalog-resolvable ATT&CK Mobile entries), and mobile-platform topology gate. See [contracts/finding-contract.md](./contracts/finding-contract.md) for full contract.

**Contract summary (spoofing Cat N+1 / N+2)**:

```yaml
id: "S-{N}"                           # existing prefix (no schema bump in F-7); single-namespace across Cat 1–N+2
category: "spoofing"                  # existing enum value — unchanged
title: "{Cat N+1: Improper Mobile Credential Usage | Cat N+2: Insecure Mobile Authentication/Authorization}: {short_summary}"
severity: "medium" | "high"           # OWASP 3×3 matrix; Cat N+1 default HIGH (banking/credentials); Cat N+2 default MEDIUM-HIGH
component: "{DFD External Entity | Process — mobile client | mobile-backend API | secure storage}"
description: "{2-4 sentence threat description distinguishing mobile-specific credential storage / mobile session handling from generic web/API authentication-bypass}"
mitigation: "{mobile-specific control mechanisms — Android Keystore + iOS Keychain, biometric step-up, certificate pinning with backup-pin rotation. MASTG-AUTH, MASVS-AUTH cited at section-level granularity in prose}"
references:
  - "OWASP M1:2024 — Improper Credential Usage"  # Cat N+1 REQUIRED
  - "OWASP M3:2024 — Insecure Authentication/Authorization"  # Cat N+2 REQUIRED
  # MASTG-AUTH / MASVS-AUTH cited in mitigation prose at section-level granularity (Q4); not in references array (no MASTG taxonomy YAML)
```

**Contract summary (tampering Cat 11 / 12 / 13)**:

```yaml
id: "T-{N}"                           # existing prefix; single-namespace across Cat 1–13
category: "tampering"                 # existing enum value — unchanged
title: "{Cat 11: Mobile Supply Chain Integrity | Cat 12: Mobile IPC Input Validation | Cat 13: Insufficient Mobile Binary Protections}: {short_summary}"
severity: "medium" | "high"           # Cat 11 default HIGH (supply-chain integrity); Cat 12 default MEDIUM-HIGH (depends on Activity sensitivity); Cat 13 default MEDIUM (binary-protection signal)
component: "{DFD Process | Data Store — mobile SDK / mobile client / mobile-backend API}"
description: "{2-4 sentence threat description; Cat 12 includes disjoint-tells annotation referencing F-1 output-integrity boundary per ADR-036 D-5}"
mitigation: "{mobile-specific control mechanisms — SDK signature verification, Intent component routing, ProGuard/R8 obfuscation, RASP. MASTG-ARCH/CODE/RESILIENCE, MASVS-PLATFORM/RESILIENCE cited at section-level granularity in prose. T1474 / T1626 / T1398 named in prose only — NOT in references}"
references:
  - "OWASP M2:2024 — Inadequate Supply Chain Security"  # Cat 11 REQUIRED
  - "OWASP M4:2024 — Insufficient Input/Output Validation"  # Cat 12 REQUIRED
  - "OWASP M7:2024 — Insufficient Binary Protections"  # Cat 13 REQUIRED
  # MITRE ATT&CK Mobile T1474 named in Cat 11 mitigation prose only — NOT in references (catalog-absent)
```

**Contract summary (info-disclosure Cat N+1 / N+2 / N+3 / N+4)**:

```yaml
id: "I-{N}"                           # existing prefix; single-namespace across Cat 1–N+4
category: "info-disclosure"           # existing enum value — unchanged
title: "{Cat N+1: Insecure Mobile Communication | Cat N+2: Inadequate Mobile Privacy Controls | Cat N+3: Insecure Mobile Data Storage | Cat N+4: Insufficient Mobile Cryptography}: {short_summary}"
severity: "medium" | "high"           # Cat N+1/N+3/N+4 default HIGH; Cat N+2 default MEDIUM
component: "{DFD Process | Data Flow | Data Store — mobile client / mobile-backend API / device-local storage}"
description: "{2-4 sentence threat description}"
mitigation: "{mobile-specific control mechanisms — certificate pinning + TLS 1.3, FLAG_SECURE, SQLCipher, EncryptedSharedPreferences, AES-GCM. MASTG-NETWORK/PRIVACY/STORAGE/CRYPTO, MASVS-NETWORK/PRIVACY/STORAGE/CRYPTO cited at section-level granularity in prose}"
references:
  - "OWASP M5:2024 — Insecure Communication"  # Cat N+1 REQUIRED
  - "OWASP M6:2024 — Inadequate Privacy Controls"  # Cat N+2 REQUIRED
  - "OWASP M9:2024 — Insecure Data Storage"  # Cat N+3 REQUIRED
  - "OWASP M10:2024 — Insufficient Cryptography"  # Cat N+4 REQUIRED
```

**Contract summary (privilege-escalation M8 Cat — dual-host privilege-gain variant)**:

```yaml
id: "E-{N}"                           # existing prefix; single-namespace across Cat 1–N+1
category: "privilege-escalation"      # existing enum value — unchanged
title: "Mobile Security Misconfiguration — Privilege-Gain Variant: {short_summary}"
severity: "medium" | "high"           # default HIGH (privilege-gain implication)
component: "{DFD Process — mobile client | mobile-backend API}"
description: "{2-4 sentence threat description distinguishing mobile-misconfiguration privilege-gain from generic broken-access-control / IDOR; references ADR-036 D-4 dual-host disjoint-tells with repudiation Cat M8}"
mitigation: "{mobile-specific control mechanisms — production-build flag stripping, ContentProvider/Activity export scoping with signature-level permissions, Play Integrity / DeviceCheck attestation, root-detection on security-critical UI. MASTG-PLATFORM, MASVS-PLATFORM cited in prose. T1626 named in prose only — NOT in references}"
references:
  - "OWASP M8:2024 — Security Misconfiguration"  # REQUIRED
  # MITRE ATT&CK Mobile T1626 named in mitigation prose only — NOT in references (catalog-absent)
```

**Contract summary (repudiation M8 Cat — dual-host accountability-loss variant)**:

```yaml
id: "R-{N}"                           # existing prefix; single-namespace across Cat 1–N+1
category: "repudiation"               # existing enum value — unchanged
title: "Mobile Security Misconfiguration — Accountability-Loss Variant: {short_summary}"
severity: "medium" | "high"           # default MEDIUM (audit-loss implication)
component: "{DFD External Entity | Process — mobile client | mobile-backend audit pipeline}"
description: "{2-4 sentence threat description distinguishing mobile-misconfiguration accountability-loss from generic missing-audit-trail / log-tampering; references ADR-036 D-4 dual-host disjoint-tells with privilege-escalation Cat M8}"
mitigation: "{mobile-specific control mechanisms — structured audit logging on security-relevant mobile events, production-build log-statement stripping ProGuard/R8 rules, tamper-evident timestamping, crash-reporting with PII redaction. MASTG-PLATFORM, MASVS-PLATFORM cited in prose. T1398 named in prose only — NOT in references}"
references:
  - "OWASP M8:2024 — Security Misconfiguration"  # REQUIRED
  # MITRE ATT&CK Mobile T1398 named in mitigation prose only — NOT in references (catalog-absent)
```

**Mobile-platform topology gate** (FR-15 enforcement contract): every Cat N+1/N+2 (S) + Cat 11/12/13 (T) + Cat N+1/N+2/N+3/N+4 (I) + M8 Cat (E) + M8 Cat (R) finding emits ONLY when the architecture additionally exhibits ≥4 mobile-platform structural indicators from the named set: declared mobile client component (Android or iOS Process), credential-handling component (SharedPreferences / NSUserDefaults / Keystore / Keychain mention), secure-storage data store (SQLite on device, Realm, Room, EncryptedSharedPreferences), mobile-backend API process the client communicates with (with or without certificate pinning declaration), third-party mobile SDK integration (analytics / payment / crash-reporting / advertising), exposed debug or admin endpoint (M8 surface), mobile permissions declaration (camera / location / contacts / etc.), package-name signal (com.example.app / com.bank.mobile), ContentProvider/Activity export declaration. Architectures lacking ≥4 mobile-platform structural indicators emit zero new findings (BLOCKER per FR-15 + SC-13 byte-identity preservation).

### Data Model (`data-model.md`)

**Purpose**: Document the architectural-tell indicators that drive Cat N+1/N+2 (S) + Cat 11/12/13 (T) + Cat N+1/N+2/N+3/N+4 (I) + M8 Cat (E) + M8 Cat (R) emission. See [data-model.md](./data-model.md).

**Pattern Category N+1 (spoofing) — Improper Mobile Credential Usage indicators**:
- Mobile client component (Android / iOS Process) declared
- Credentials persisted in SharedPreferences / NSUserDefaults / plaintext SQLite / app-bundled config files
- No platform-managed Keystore (Android) / Keychain (iOS) reference
- Hardcoded API keys / secrets in mobile binary (production build)
- No biometric-bound key release for sensitive operations
- No credential rotation policy

**Pattern Category N+2 (spoofing) — Insecure Mobile Authentication/Authorization indicators**:
- Mobile client component declared
- Bypassed certificate pinning / pinning enabled only on production domain
- Broken or absent JWT validation (no signature, no `iss`/`aud`/`exp` checks)
- Weak refresh-token handling (long-lived, not bound to device)
- Missing step-up authentication for high-risk operations (money movement, profile changes)
- Client-side authorization decisions not re-validated server-side

**Pattern Category 11 (tampering) — Mobile Supply Chain Integrity indicators**:
- Third-party mobile SDK / library integration declared
- No checksum verification on SDK artifacts
- No signed-artifact policy
- Sideloaded APK distribution path declared
- Missing app-store provenance review
- CocoaPods / Gradle / SPM dependencies from unsigned sources
- Missing reproducible-build enforcement

**Pattern Category 12 (tampering) — Mobile IPC Input Validation indicators**:
- Android Activity / Service / BroadcastReceiver with `android:exported="true"` and no permission gating
- iOS URL-scheme declaration with no parameter validation
- Deep-link handler reaching trusted operations (auth, payment, profile) without re-validation
- Exported ContentProvider with no permission scoping
- Pasteboard-injection paths into shared-clipboard handlers
- Missing Android App Links / iOS Universal Links claim verification
- **Disjoint-tells from F-1 `output-integrity`**: F-7 Cat 12 fires on mobile-IPC-input-side; output-integrity fires on LLM-output-side flowing into browser/SQL/shell sinks

**Pattern Category 13 (tampering) — Insufficient Mobile Binary Protections indicators**:
- Mobile client production build declared
- No root/jailbreak detection in security-critical features (banking, payment, regulated content)
- No anti-tampering stubs (RASP, integrity self-checks)
- No code obfuscation (no ProGuard/R8 rules on Android, no bitcode + symbol-stripping on iOS)
- Debug symbols in shipped binaries
- No emulator-detection on fraud-sensitive flows

**Pattern Category N+1 (info-disclosure) — Insecure Mobile Communication indicators**:
- Mobile client to mobile-backend Data Flow declared
- Cleartext HTTP traffic enabled (no `usesCleartextTraffic="false"` on Android, no NSAppTransportSecurity exception audit on iOS)
- No TLS certificate pinning
- HTTP-to-HTTPS downgrade attack path
- Weak TLS cipher acceptance
- Missing HSTS-equivalent enforcement at app-level

**Pattern Category N+2 (info-disclosure) — Inadequate Mobile Privacy Controls indicators**:
- Mobile client component declared
- PII / PHI persisted in device-local caches without TTL expiry
- Telemetry / analytics SDKs collecting personal data without disclosure or consent gating
- Clipboard exposure on sensitive fields (passwords, PII)
- Screenshot leakage on sensitive screens (no FLAG_SECURE on Android, no equivalent on iOS)
- Over-broad permission requests on first launch (camera + location + contacts + etc.)

**Pattern Category N+3 (info-disclosure) — Insecure Mobile Data Storage indicators**:
- Mobile client component declared
- Unencrypted SQLite / Realm / Room database on device
- Unencrypted KeyValue store (SharedPreferences plaintext, NSUserDefaults plaintext)
- Cloud-backup leakage (iCloud / Google Drive backup including sensitive app data without exclusion)
- External SD-card writes for sensitive files
- World-readable file permissions on Android internal storage

**Pattern Category N+4 (info-disclosure) — Insufficient Mobile Cryptography indicators**:
- Mobile client component declared
- Weak key derivation on user PINs (low PBKDF2 iteration counts, no salting, no per-device entropy)
- Custom-rolled crypto algorithms in mobile binaries
- Hardcoded symmetric keys in shipped binaries
- Insecure PRNG seeding (`java.util.Random` for security purposes)
- Deprecated cipher suites (DES, RC4, MD5, SHA1) for sensitive operations

**M8 Pattern Category (privilege-escalation) — Mobile Security Misconfiguration: Privilege-Gain Variant indicators**:
- Mobile client production build declared
- Exposed debug endpoints (`adb shell` access points, debug-only Activities exported)
- Default permissive ContentProvider / Service exports without permission scoping
- Missing app-attestation (Play Integrity / DeviceCheck) enabling tampered-binary execution
- Missing root-detection in security-critical feature gates
- Missing certificate-pinning enforcement on debug builds shipped to production

**M8 Pattern Category (repudiation) — Mobile Security Misconfiguration: Accountability-Loss Variant indicators**:
- Mobile client component declared
- Missing audit logging on security-relevant mobile events (login, money-movement, permission grants)
- Disabled crash reporting in production preventing post-incident root-cause analysis
- Debug logs leaking sensitive data via `Log.d` / `NSLog` not stripped in production
- Missing tamper-evident timestamping on audit records the mobile app emits
- Missing log-integrity verification at backend ingestion gate

### Quickstart (`quickstart.md`)

**Purpose**: Walk through verifying F-7 enrichment on the new `examples/mobile-banking-app/` architecture and confirming byte-identity on the 6 non-mobile baselines. See [quickstart.md](./quickstart.md).

**Verification flow**:

1. **PRD-day evening** (Tuesday 2026-04-28 PM, ~2-3 hr per team-lead MEDIUM-1): Architect drafts `examples/mobile-banking-app/architecture.md` skeleton (mobile client + secure storage + mobile-backend API + 1 third-party SDK + 1 exposed debug endpoint = 5 of 6 indicators).
2. **Plan day** (Wednesday 2026-04-29, ~4-5 hr): Architect + senior-backend-engineer co-author full draft (~180-220 lines) + populate ADR-036 mapping table COMPLETE (10 closure rows + reference rows + severity-hint column) per Q5 plan-time decision.
3. **Wave 1.0** (Wed 2026-04-29 AM, parallel with mobile-banking-app full draft): ADR-036 Proposed commit with 10-row mapping table populated COMPLETE (NOT skeleton); 10 numbered Decisions per architect MEDIUM-2 plan-time RESOLVED 10-decision structure.
4. **Wave 1.1** (Wed 2026-04-29 AM-late): Land FR-1 + FR-2 + FR-3 (`spoofing.md` + companion: 2 new pattern categories Cat N+1 M1 + Cat N+2 M3 + Pattern Category Disambiguation + Primary Sources). Spoofing enrichment complete.
5. **Wave 2.0** (Wed 2026-04-29 PM): FR-4 (`tampering.md` 3 small additive edits — 55 → 60-66 lines).
6. **Wave 2.1 / 2.2 / 2.3** (Wed 2026-04-29 PM, T-NN-1 / T-NN-2 / T-NN-3 sequential checkpoints per F-6 Wave 2.x precedent): FR-5 PART 1 (Cat 11 M2) → FR-5 PART 2 (Cat 12 M4 with disjoint-tells annotation) → FR-5 PART 3 (Cat 13 M7) + Pattern Category Disambiguation + 3 Primary Sources entries. Tampering enrichment complete (221 → ~315-345 lines).
7. **Wave 3.0** (Thu 2026-04-30 AM): FR-6 (`info-disclosure.md` 3 small additive edits — 54 → 60-66 lines).
8. **Wave 3.1 / 3.2 / 3.3 / 3.4** (Thu 2026-04-30 AM, M5 / M6 / M9 / M10 sequential sub-task checkpoints per team-lead MEDIUM-2 plan-time RESOLVED ~75-90 min each): FR-7 PART 1 (Cat N+1 M5) → FR-7 PART 2 (Cat N+2 M6) → FR-7 PART 3 (Cat N+3 M9) → FR-7 PART 4 (Cat N+4 M10) + Pattern Category Disambiguation + 4 Primary Sources entries. Info-disclosure enrichment complete (192 → ~315-345 lines).
9. **Wave 4.0** (Thu 2026-04-30 PM, dual-host M8 path — TWO sub-tasks): FR-8 PART 1 + FR-9 PART 1 (`privilege-escalation.md` + companion: 1 new pattern category M8 privilege-gain variant + Pattern Category Disambiguation + Primary Sources). FR-8 PART 2 + FR-9 PART 2 (`repudiation.md` + companion: 1 new pattern category M8 accountability-loss variant + Pattern Category Disambiguation + Primary Sources). M8 dual-host enrichment complete.
10. **Wave 4.1** (Thu 2026-04-30 PM, weakly parallel with Wave 4.0): Tester engages for early-signal byte-identity spot-check on 1–2 baselines (e.g., `web-app` + `maestro-reference` recommended) per FR-15 separation-of-duties.
11. **Wave 4.2** (Thu 2026-04-30 PM late): `examples/mobile-banking-app/` end-to-end regen via `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report`. Verify ≥10 new Mobile findings (≥1 per M1–M10; ≥11 in dual-host path with M8 split).
12. **Wave 5.0** (Fri 2026-05-01 AM-1): Tester runs full byte-identity verification across 6 baselines under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 + SC-13.
13. **Wave 5.1** (Fri 2026-05-01 AM-2, strongly parallel with 5.0 per F-6 Wave 5.0/5.1 split precedent): Architect transitions ADR-036 Proposed → Accepted with post-merge SHA fill (provisional date pre-merge; final SHA post-merge).
14. **Wave 5.2** (Fri 2026-05-01 AM): Senior-backend-engineer authors `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py` + modifies `test_backward_compatibility.py` infrastructure (`DETECTION_AGENT_PATHS` 8 → 3; `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` 5 → 9 in dual-host path; mobile-banking-app added to mutation-target exclusion list).
15. **Wave 5.3** (Fri 2026-05-01 PM): FR-12 BLP-01 Coverage Matrix ten-row update (M1–M10 Planned → Covered, F-7 closure-feature column populated; coverage milestones panel update to 40/40 four-framework total) — single commit per F-3/F-4/F-5/F-6 precedent.
16. **Wave 5.4** (Fri 2026-05-01 PM): Triple Triad sign-offs on tasks.md per `/aod.tasks` (PM + Architect + Team-Lead).
17. **Wave 5.5** (Mon 2026-05-04, primary close-out target — F-7 envelope is +0.5 day vs F-6): `/aod.deliver` close-out: pre-merge title verification + squash-merge with `feat(237):` Conventional Commits title + post-merge release-please verification + delivery retrospective filing.
18. **Wave 5.6** (Tue 2026-05-05 reserve): Buffer / slip absorption / R5 contingency invocation if triggered.

**Verification gates**:

- `wc -l .claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md` — all 5 within tier cap ≤120
- `git diff main HEAD -- '.claude/agents/tachi/' '.claude/skills/tachi-*/references/'` — exactly 10 files in diff (dual-host path) or 8 (single-host fallback)
- `grep -i 'maestro' .claude/agents/tachi/{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}.md .claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md` — 0 matches
- `grep -c "## Pattern Category Disambiguation" .claude/skills/tachi-{spoofing,tampering,info-disclosure,privilege-escalation,repudiation}/references/detection-patterns.md` — 5 matches dual-host (4 single-host fallback)
- `grep -E '^schema_version:' schemas/finding.yaml` — `"1.8"` (SC-15)
- `grep -E '^\s+pattern:' schemas/finding.yaml` — `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$` unchanged (SC-15)
- `pytest tests/scripts/test_backward_compatibility.py -k "byte_identity" -v` — 6/6 passing (SC-13)
- `pytest tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py -v` — all enrichment tests passing
- `git diff main HEAD -- examples/mobile-banking-app/sample-report/security-report.pdf.baseline` — present (new mutation target baseline)
- `git diff main HEAD -- examples/agentic-app/ examples/consumer-agent-app/ examples/predictive-ml-app/` — empty (prior mutation targets zero-touch)

### Wave Allocation

| Wave | Day/Slot | Owner | Task | Cumulative State |
|------|----------|-------|------|------------------|
| 0.0 | Tue 2026-04-28 PM | architect | New `examples/mobile-banking-app/architecture.md` skeleton drafting (~2-3 hr per team-lead MEDIUM-1; covers 5 of 6 indicators) | Skeleton ready |
| 0.1 | Wed 2026-04-29 AM-early | architect + senior-backend-engineer | `examples/mobile-banking-app/architecture.md` full draft completion (~4-5 hr; 6 of 6 indicators; ~180-220 lines); ADR-036 Proposed commit with 10-row mapping table populated COMPLETE (NOT skeleton) — 10 numbered Decisions per architect MEDIUM-2 plan-time 10-decision structure | New mutation target ready + ADR-036 Proposed |
| 1.0 | Wed 2026-04-29 AM-mid | architect | ADR-036 Proposed commit finalization (cross-references to ADR-023 D3 + ADR-027 + ADR-030 D1 + ADR-031 D8 asymmetry + ADR-032 + ADR-034 + ADR-035 closing forward-scope marker forecast text quoted) | ADR-036 Proposed |
| 1.1 | Wed 2026-04-29 AM-late | senior-backend-engineer | FR-1 + FR-2 + FR-3: `spoofing.md` 3 small additive edits (owasp_references, Purpose, Step 5) — 51 → 55-60 lines; FR-3: `tachi-spoofing` companion Cat N+1 M1 + Cat N+2 M3 + Pattern Category Disambiguation + Primary Sources extension — 146 → ~200-220 lines | spoofing enrichment complete |
| 2.0 | Wed 2026-04-29 PM | senior-backend-engineer | FR-4: `tampering.md` 3 small additive edits (owasp_references 3-line, Purpose, Step 5) — 55 → 60-66 lines | tampering agent metadata complete |
| 2.1 | Wed 2026-04-29 PM | senior-backend-engineer | FR-5 PART 1 + checkpoint T-NN-1: Cat 11 (Mobile Supply Chain Integrity M2) land + self-review (~30 lines) | tampering Cat 11 complete |
| 2.2 | Wed 2026-04-29 PM | senior-backend-engineer | FR-5 PART 2 + checkpoint T-NN-2: Cat 12 (Mobile IPC Input Validation M4) land + disjoint-tells annotation reference to F-1 output-integrity per ADR-036 D-5 + self-review (~30 lines) | tampering Cat 12 complete |
| 2.3 | Wed 2026-04-29 PM | senior-backend-engineer | FR-5 PART 3 + checkpoint T-NN-3: Cat 13 (Insufficient Mobile Binary Protections M7) land + self-review (~30 lines) + Pattern Category Disambiguation subsection + 3 Primary Sources entries | tampering enrichment complete (221 → ~315-345 lines) |
| 3.0 | Thu 2026-04-30 AM-early | senior-backend-engineer | FR-6: `info-disclosure.md` 3 small additive edits (owasp_references 4-line, Purpose, Step 5) — 54 → 60-66 lines | info-disclosure agent metadata complete |
| 3.1 | Thu 2026-04-30 AM | senior-backend-engineer | FR-7 PART 1 + team-lead MEDIUM-2 sub-checkpoint M5-1: Cat N+1 (Insecure Mobile Communication M5) land + self-review (~30 lines, ~75-90 min) | info-disclosure Cat N+1 complete |
| 3.2 | Thu 2026-04-30 AM | senior-backend-engineer | FR-7 PART 2 + sub-checkpoint M6-1: Cat N+2 (Inadequate Mobile Privacy Controls M6) land + self-review (~30 lines, ~75-90 min) | info-disclosure Cat N+2 complete |
| 3.3 | Thu 2026-04-30 AM-mid | senior-backend-engineer | FR-7 PART 3 + sub-checkpoint M9-1: Cat N+3 (Insecure Mobile Data Storage M9) land + self-review (~30 lines, ~75-90 min) | info-disclosure Cat N+3 complete |
| 3.4 | Thu 2026-04-30 AM-late | senior-backend-engineer | FR-7 PART 4 + sub-checkpoint M10-1: Cat N+4 (Insufficient Mobile Cryptography M10) land + self-review (~30 lines, ~75-90 min) + Pattern Category Disambiguation subsection + 4 Primary Sources entries | info-disclosure enrichment complete (192 → ~315-345 lines) |
| 4.0 | Thu 2026-04-30 PM | senior-backend-engineer | FR-8 PART 1 + FR-9 PART 1 (dual-host): `privilege-escalation.md` 3 small additive edits (owasp_references 1-line, Purpose, Step 5) — 52 → 56-58 lines; companion Cat N+1 M8 privilege-gain variant + Pattern Category Disambiguation + Primary Sources extension — 213 → ~245-260 lines | privilege-escalation M8 enrichment complete |
| 4.0b | Thu 2026-04-30 PM | senior-backend-engineer | FR-8 PART 2 + FR-9 PART 2 (dual-host): `repudiation.md` 3 small additive edits (owasp_references 1-line, Purpose, Step 5) — 50 → 54-56 lines; companion Cat N+1 M8 accountability-loss variant + Pattern Category Disambiguation + Primary Sources extension — 148 → ~180-195 lines | repudiation M8 enrichment complete |
| 4.1 | Thu 2026-04-30 PM | tester (per FR-15 separation-of-duties) | Early-signal byte-identity spot-check on 1–2 baselines (`web-app` + `maestro-reference` recommended) | Early-signal spot-check passed |
| 4.2 | Thu 2026-04-30 PM late | senior-backend-engineer | `examples/mobile-banking-app/` end-to-end regen: `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` | mobile-banking-app baseline + all artifacts |
| 5.0 | Fri 2026-05-01 AM-1 | tester (per FR-15) | Full byte-identity verification across 6 baselines under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 | SC-13 verified 6/6 |
| 5.1 | Fri 2026-05-01 AM-2 | architect | ADR-036 Accepted transition + post-merge SHA fill (provisional date pre-merge; final SHA post-merge) | ADR-036 Accepted |
| 5.2 | Fri 2026-05-01 AM | senior-backend-engineer | FR-17: New test file `tests/scripts/test_mobile_top_10_coverage_bundle_enrichment.py` with structural-diff + line-count + MAESTRO grep + Pattern Category Disambiguation header presence (5 matches dual-host) + references-array fixtures (10 fixtures dual-host: Cat N+1/N+2 S + Cat 11/12/13 T + Cat N+1/N+2/N+3/N+4 I + M8 E + M8 R) + ATT&CK Mobile catalog-resolvability gap test (T1474/T1626/T1398 prose-only); FR-16: modify `test_backward_compatibility.py` infrastructure (`DETECTION_AGENT_PATHS` 8 → 3 dual-host; `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` 5 → 9 dual-host) | Test infrastructure complete |
| 5.3 | Fri 2026-05-01 PM | senior-backend-engineer | FR-12: BLP-01 Coverage Matrix ten-row update (M1, M2, M3, M4, M5, M6, M7, M8, M9, M10 Planned → Covered, F-7 closure-feature column populated; coverage milestones panel update to OWASP four-framework 40/40) — single commit per F-3/F-4/F-5/F-6 precedent | Coverage Matrix transitioned |
| 5.4 | Fri 2026-05-01 PM | product-manager + architect + team-lead | Triple Triad sign-offs on tasks.md per `/aod.tasks` | Triple sign-off recorded |
| 5.5 | Mon 2026-05-04 (primary close-out per +0.5 day envelope vs F-6) | senior-backend-engineer + architect | `/aod.deliver` close-out: pre-merge title verification + squash-merge with `feat(237):` Conventional Commits title + post-merge release-please verification + delivery retrospective filing | F-7 delivered |
| 5.6 (reserve) | Tue 2026-05-05 | — | Slip absorption / regen friction / delivery retrospective filing fallback / R5 contingency invocation if triggered (M8 fall-back to single-host if architect MEDIUM-2 issues surface; OR reduced 8-of-10 categories with M8 deferred) | Reserve reserved |

**Wave parallelism notes**: Wave 0.0 (skeleton draft Tue evening) is parallel with PRD-day governance (already complete). Wave 0.1 (full draft Wed AM-early) and Wave 1.0 (ADR-036 Proposed) are weakly parallel — architect drives both. Wave 1.1 + Wave 2.x + Wave 3.x + Wave 4.x are sequential (single-engineer fan-out — five agents in one half-day each would risk authoring quality; team-lead MEDIUM-2 enforces sub-task split on info-disclosure). Wave 4.1 (tester spot-check) is weakly parallel with Wave 4.0/4.0b/4.2. Wave 5.0 (full verification) and Wave 5.1 (ADR-036 SHA fill) are strongly parallel per F-6 Wave 5.0/5.1 split precedent.

**Buffer-day priority order** (per team-lead recommendations): (1) Day 2 / Day 3 slip absorption; (2) M8 fall-back to single-host if architect adjudication issues surface during Wave 4.0/4.0b; (3) Reduced 8-of-10 categories shipping if R6 emergent-issue at four-or-five-agent scope triggers (defer M8 dual-host to follow-on PR); (4) post-merge ADR-036 SHA fill + `/aod.deliver` execution + release-please PR verification.

## Complexity Tracking

*No Constitution Check violations. No Complexity Tracking entries required.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | (none) | (none) |

---

## Plan-Day Architect Decisions Summary

For traceability and reviewer cross-reference, the architect plan-day decisions resolved during /aod.project-plan:

| Decision | Default | Plan-Time Decision | Rationale |
|----------|---------|---------------------|-----------|
| Q1 (M8 split: single-host vs dual-host) | dual-host | **DUAL-HOST** | privilege-escalation owns privilege-gain variant; repudiation owns accountability-loss variant — disjoint architectural-tells per ADR-036 D-4. Mirrors ADR-035 D-4 ML06 two-facet precedent at F-7 architectural-tell layer. |
| Q2 (mutation-target archetype: mobile-banking-app vs alternatives) | mobile-banking-app | **MOBILE-BANKING-APP** | Covers credentials, payment, biometrics, secure storage, certificate pinning across all M1–M10 items. |
| Q3 (MITRE ATT&CK Mobile catalog-resolvability for 3 entries) | RESOLVED at spec time | **0 of 3 catalog-resolvable** (T1474, T1626, T1398 ALL absent); 3 of 3 prose-only | Empirical grep on `schemas/taxonomy/mitre-attack.yaml` returns zero hits. Worst-case scale (3-of-3) at any BLP-01 enrichment feature; mirrors F-5 1-of-1 + F-6 3-of-6 prose-only precedent. ADR-036 D-7 codifies. |
| Q4 (MASTG/MASVS reference granularity: section-level vs test-case-ID) | section-level | **SECTION-LEVEL** | Test-case-ID granularity (MSTG-AUTH-1) is F-A1 follow-on after MASTG taxonomy YAML is added. F-7 cites at MASTG-AUTH / MASVS-CRYPTO etc. |
| Q5 (ADR-036 mapping-table column structure: severity-hint column) | YES | **YES** | Parity with ADR-034 5-row + ADR-035 11-row precedent for cross-feature comparability. |
| Q6 (mobile-banking-app post-F-7 baseline strategy) | excluded mutation target | **EXCLUDED** | Mirrors agentic-app + consumer-agent-app + predictive-ml-app precedent — mutation targets stay excluded until explicit promotion event. |
| Architect MEDIUM-2 (ADR-036 9-vs-10 decision structure) | DEFERRED to plan day | **10-DECISION STRUCTURE** with discrete D-9 Pattern Category Disambiguation | Mirrors ADR-035 D-9 precedent. D-9 codifies disambiguation requirement on 4 (single-host) or 5 (dual-host) companions. |
| Team-Lead MEDIUM-1 (plan-day overload mitigation — architect-critical-path 12-14 hrs Wed) | DEFERRED to plan day | **PRD-day evening skeleton (Wave 0.0) + plan-day full draft (Wave 0.1)** parallel mobile-banking-app authoring track | Reduces architect Wed AM load from 12-14 hrs to ~4-5 hrs full-draft + ADR finalization. |
| Team-Lead MEDIUM-2 (Day 2 AM throughput — info-disclosure 4 cats = +33% vs F-6 densest) | DEFERRED to tasks.md | **WAVE 3.1 / 3.2 / 3.3 / 3.4** (M5-1 / M6-1 / M9-1 / M10-1) | Four sequential ~75-90-minute checkpoints with rollback capability. Mirrors F-6 Wave 2.1/2.2/2.3 precedent at 4-cat scale. |
| Team-Lead LOW-1 (Day 3 AM split between Wave 5.0 tester + Wave 5.1 architect) | DEFERRED to tasks.md | **ENCODED** as Wave 5.0 + Wave 5.1 strongly parallel | Two activities don't share single slot owner. Mirrors F-6 Wave 5.0/5.1 precedent. |
