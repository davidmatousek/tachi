# PRD Index

**Last Updated**: 2026-06-10 (PRD 184 APPROVED — NIST AI 600-1 GAI Risk Taxonomy Addition / Surface C Transcription (BLP-05 Wave 2, F-A1.1 follow-on to F-180, Issue #184): add `schemas/taxonomy/nist-ai-600-1.yaml` as the **8th catalog** (12 GAI Risk records §§2.1–2.12, quoted-string ids, shared DOI URL), expand the frozen `taxonomy` enum **7→8** via the integrity test’s hardcoded gates (ADR-027 Decision 3 extension recorded as a Revision History entry + Decision 3 annotation per the OQ-3 ruling — no standalone ADR), correct the F-180 FR-022 direction (`tachi-stride-ai-category → nist-ai-600-1`), transcribe the **15 verbatim Surface C Overlap edges** (`primary`/`high`, citation to `nist-ai-rmf-mapping.md`, Architect-verified 1:1 against the table), and **remove the 16 surviving wrong-direction drift edges** (define-stage finding **C-e**: T029’s Option (d) MIX normalized rather than removed them — verified live at HEAD by YAML parse; FR-7 PM ruling Option A completes the standing T027 removal directive with Constitution III disclosure) — crosswalk lands at **541 primary / 37 related / 0 superseded = 578 edges** (≥500 floor holds with 41 headroom). Five issue-body corrections (C-a–C-e) verified against the live repo (test NOT generic — CATALOG_FILENAMES + TAXONOMY_ENUM hardcoded; 5-field record shape with `cwe_refs: []`; separate `_sort_key_section` + new elif per OQ-1/TL-C4, `_sort_key_nist` byte-untouched per the M1×C4 re-review ruling; both Gap rows omitted per OQ-2 — §2.6 is endpoint-less and §2.9×Spoofing would be the crosswalk’s first-ever `low` edge; stale "8 of 11" reference prose routes to a one-line ADR-025 amendment note at delivery per OQ-4/FR-024). Serialize vs #185 (crosswalk/README/CHANGELOG are shared surfaces); `docs/architecture/01_system_design/README.md` exempt from the stale-count sweep (init.sh baseline-fixture coupling, Architect C2); interpreter pin `/usr/bin/python3`; effort 0.75–1.25 d (realistic ~1.0 incl. FR-7, expect same-day per #186/#182 anchors). Triad triple sign-off: PM ✓ APPROVED (author; v1.1 carries the FR-022 direction re-sign + FR-7 ruling), Architect ⚠ APPROVED_WITH_CONCERNS (bounded re-review after v1.0 CHANGES_REQUESTED C1/C2+M1–M3; FR-7 16-edge list verified 1:1; M1×C4 docstring ruling folded at v1.2), Team-Lead ⚠ APPROVED_WITH_CONCERNS (5 advisory concerns folded; W0–W4 single-engineer + checkpoint-gates plan, ~12–14 tasks). Next: `/aod.plan`.)
**Legend**: ✓=APPROVED, ⚠=APPROVED_WITH_CONCERNS, 🔄=CHANGES_REQUESTED, ⛔=BLOCKED, ⚠⚡=OVERRIDDEN


| # | Feature | PM | Architect | Team-Lead | Status | Date |
|---|---------|----|-----------|-----------| -------|------|
| 184 | [F-A1.1 follow-on: NIST AI 600-1 GAI Risk Taxonomy — Surface C Transcription (BLP-05 Wave 2)](184-nist-ai-600-1-surface-c-transcription-2026-06-10.md) ([Issue #184](https://github.com/davidmatousek/tachi/issues/184)) | ✓ | ⚠ | ⚠ | Approved | 2026-06-10 |
| 182 | [F-A1 follow-on: Crosswalk `related` + `superseded` Edge Expansion (BLP-05 Wave 3)](182-crosswalk-related-superseded-edges-2026-06-07.md) ([PR #323](https://github.com/davidmatousek/tachi/pull/323)) · [spec](../../../specs/182-crosswalk-related-superseded-edges/spec.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-06-07 |
| 186 | [F-A1.3 MITRE ATT&CK + ATLAS Catalog Expansion (BLP-05 Wave 2)](186-mitre-catalog-expansion-2026-06-07.md) ([PR #321](https://github.com/davidmatousek/tachi/pull/321)) · [spec](../../../specs/186-mitre-catalog-expansion/spec.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-06-07 |
| 311 | [F-1 MAESTRO Matrix Model B: Clean vs n/a (BLP-05 Wave 1)](311-maestro-matrix-model-b-clean-vs-na-2026-06-03.md) ([PR #318](https://github.com/davidmatousek/tachi/pull/318)) · [spec](../../../specs/311-maestro-matrix-model-b-clean-vs-na/spec.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-06-04 |
| 315 | [F-315 MAESTRO Output Completeness (Round 2): Infographic + CI Durability (US-1 carved → #311)](315-maestro-output-completeness-round-2-2026-06-02.md) ([PR #316](https://github.com/davidmatousek/tachi/pull/316)) · [spec](../../../specs/315-maestro-output-completeness-round-2/spec.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-06-03 |
| 098 | [F-4 MAESTRO 7-Layer Output Polish (BLP-04 Wave 4 — closes BLP-04 4/4)](098-maestro-7-layer-output-polish-2026-06-01.md) ([PR #310](https://github.com/davidmatousek/tachi/pull/310)) · [spec](../../../specs/098-maestro-7-layer/spec.md) | ✓ | ✓ | ⚠ | Delivered | 2026-06-02 |
| 305 | [F-3 Adoption Signal Capture (BLP-04 Wave 3)](305-adoption-signal-capture-2026-06-01.md) ([PR #306](https://github.com/davidmatousek/tachi/pull/306)) | ⚠ | ⚠ | ⚠ | Delivered (MVP; post-merge tail pending) | 2026-06-01 |
| 302 | [F-2 (F-260b) Asset-Tag Output Wiring (BLP-04 Wave 2)](302-asset-tag-output-wiring-2026-05-30.md) ([PR #303](https://github.com/davidmatousek/tachi/pull/303)) | ⚠ | ⚠ | ⚠ | Delivered | 2026-06-01 |
| 296 | [F-1 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1)](296-50-50-owasp-coverage-distribution-launch-2026-05-28.md) ([Issue #296](https://github.com/davidmatousek/tachi/issues/296)) | ⚠ | ⚠ | ⚠ | Approved | 2026-05-28 |
| 292 | [F-292 Output-Integrity Cross-Sink Refinement (community-feedback, follow-on to F-1)](292-output-integrity-cross-sink-refinement-2026-05-14.md) ([PR #293](https://github.com/davidmatousek/tachi/pull/293)) | ✓ | ⚠ | ⚠ | Delivered | 2026-05-14 |
| 282 | [F-5 Pre-commit Secret-Scanning Defaults (BLP-02 Wave 4+ — closes BLP-02 5/5)](282-pre-commit-secret-scanning-defaults-2026-05-09.md) ([PR #283](https://github.com/davidmatousek/tachi/pull/283)) | ✓ | ⚠ | ⚠ | Delivered | 2026-05-10 |
| 277 | [F-4 Claude Permissions Baseline (BLP-02 Wave 4)](277-claude-permissions-baseline-2026-05-08.md) ([PR #278](https://github.com/davidmatousek/tachi/pull/278)) | ✓ | ⚠ | ⚠ | Delivered | 2026-05-09 |
| 272 | [F-3 SECURITY.md and Private Disclosure Channel (BLP-02 Wave 3)](272-security-md-disclosure-2026-05-08.md) ([PR #273](https://github.com/davidmatousek/tachi/pull/273)) | ✓ | ⚠ | ⚠ | Delivered | 2026-05-08 |
| 256 | [F-2 Source-Pattern Hardening (BLP-02 Wave 2)](256-source-pattern-hardening-2026-05-04.md) ([PR #257](https://github.com/davidmatousek/tachi/pull/257)) | ✓ | ✓ | ⚠ | Delivered | 2026-05-05 |
| 250 | [Adversarial Unit Extraction Hot-Fix (BLP-02 follow-up)](250-adversarial-unit-extraction-hotfix-2026-05-04.md) ([PR #253](https://github.com/davidmatousek/tachi/pull/253)) | ✓ | ⚠ | ⚠ | Delivered | 2026-05-04 |
| 248 | [F-1 Substitution Surface Hardening (BLP-02 Wave 1)](248-substitution-surface-hardening-2026-05-03.md) ([PR #249](https://github.com/davidmatousek/tachi/pull/249)) | ✓ | ⚠ | ⚠ | Delivered | 2026-05-04 |
| 241 | [F-8 + F-A3 Web/API Coverage Attestation + Populator Wiring [Tier 3]](241-web-api-coverage-attestation-2026-04-29.md) ([PR #242](https://github.com/davidmatousek/tachi/pull/242)) | ✓ | ⚠ | ⚠ | Delivered | 2026-05-01 |
| 237 | [F-7 Mobile Top 10 Coverage Bundle [Tier 2]](237-mobile-top-10-coverage-bundle-2026-04-28.md) ([PR #238](https://github.com/davidmatousek/tachi/pull/238)) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-29 |
| 232 | [F-6 ML Top 10 Coverage Bundle [Tier 2]](232-ml-top-10-coverage-bundle-2026-04-27.md) ([PR #235](https://github.com/davidmatousek/tachi/pull/235)) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-28 |
| 229 | [F-5 LLM10 Unbounded Consumption Verification](229-llm10-unbounded-consumption-verification-2026-04-27.md) ([PR #230](https://github.com/davidmatousek/tachi/pull/230)) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-27 |
| 224 | [F-4 ASI09 Human-Agent Trust Exploitation](224-trust-exploitation-threat-agent-2026-04-26.md) ([PR #225](https://github.com/davidmatousek/tachi/pull/225)) | ✓ | ✓ | ⚠ | Delivered | 2026-04-27 |
| 219 | [F-3 ASI07 Insecure Inter-Agent Communication](219-asi07-tool-abuse-enrichment-2026-04-25.md) ([PR #220](https://github.com/davidmatousek/tachi/pull/220)) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-26 |
| 212 | [Improve Executive-Architecture Infographic](212-improve-executive-architecture-infographic-2026-04-24.md) ([PR #213](https://github.com/davidmatousek/tachi/pull/213)) | ⚠ | ⚠ | ⚠ | Delivered | 2026-04-25 |
| 206 | [F-2 Misinformation Threat Agent (LLM09)](206-misinformation-threat-agent-2026-04-23.md) ([PR #207](https://github.com/davidmatousek/tachi/pull/207)) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-24 |
| 201 | [F-1 Output Integrity Threat Agent (LLM05)](201-output-integrity-threat-agent-2026-04-18.md) ([PR #202](https://github.com/davidmatousek/tachi/pull/202)) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-19 |
| 194 | [F-B Coverage Attestation Report Section](194-coverage-attestation-report-section-2026-04-18.md) ([PR #195](https://github.com/davidmatousek/tachi/pull/195)) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-18 |
| 189 | [F-A2 Source Attribution Schema Extension](189-source-attribution-schema-extension-2026-04-17.md) ([PR #190](https://github.com/davidmatousek/tachi/pull/190)) | ⚠ | ✓ | ⚠ | Delivered | 2026-04-17 |
| 180 | [F-A1 Taxonomy Crosswalk Collection](180-taxonomy-crosswalk-collection-2026-04-17.md) ([PR #181](https://github.com/davidmatousek/tachi/pull/181)) | ⚠ | ⚠ | ⚠ | Delivered | 2026-04-17 |
| 145 | [MAESTRO Canonical Worked Example: Multi-Agent Reference Architecture](145-maestro-canonical-worked-example-2026-04-16.md) ([PR #175](https://github.com/davidmatousek/tachi/pull/175)) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-17 |
| 142 | [MAESTRO Phase 3: Agentic Threat Pattern Expansion](142-maestro-agentic-pattern-expansion-2026-04-16.md) ([PR #172](https://github.com/davidmatousek/tachi/pull/172)) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-16 |
| 144 | [MAESTRO Companion: NIST AI RMF Integration Evaluation ADR](144-nist-ai-rmf-evaluation-adr-2026-04-15.md) ([PR #169](https://github.com/davidmatousek/tachi/pull/169)) | ⚠ | ⚠ | ⚠ | Delivered | 2026-04-16 |
| 143 | [MAESTRO Phase 4: OWASP AIVSS Evaluation ADR](143-maestro-aivss-evaluation-adr-2026-04-14.md) | ⚠ | ⚠ | ⚠ | Delivered | 2026-04-15 |
| 129 | [Attack Tree Delta Sub-Agent](129-attack-tree-delta-sub-agent-2026-04-13.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-14 |
| 141 | [MAESTRO Phase 2: Cross-Layer Attack Chains](141-maestro-cross-layer-attack-chains-2026-04-12.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-12 |
| 082 | [Threat Agent Skill References](082-threat-agent-skill-references-2026-04-11.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-11 |
| 130 | [Fix Attack Path Mermaid Rendering](130-fix-attack-path-mermaid-rendering-2026-04-11.md) | ✓ | ✓ | ✓ | Delivered | 2026-04-11 |
| 136 | [MAESTRO Canonical Layer Correctness Fix](136-maestro-canonical-layer-correctness-fix-2026-04-10.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-10 |
| 128 | [Executive Threat Architecture Infographic](128-executive-threat-architecture-2026-04-09.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-10 |
| 120 | [Architecture Lifecycle Command](120-architecture-lifecycle-command-2026-04-09.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-09 |
| 121 | [Rename Tachi Commands to tachi.* Namespace](121-rename-tachi-commands-to-namespace-2026-04-09.md) | ✓ | ⚠ | ⚠ | Delivered | 2026-04-09 |
| 112 | [Attack Path Pages in Security Report PDF](112-attack-path-pages-in-pdf-2026-04-09.md) | ✓ | ✓ | ✓ | Delivered | 2026-04-09 |
| 104 | [Downstream Baseline Propagation](104-downstream-baseline-propagation-2026-04-08.md) | ✓ | ✓ | ✓ | Delivered | 2026-04-08 |
| 091 | [MAESTRO Infographic Templates and PDF Report Section](091-maestro-infographic-templates-and-pdf-report-section-2026-04-08.md) | ✓ | ✓ | ✓ | Delivered | 2026-04-08 |
| 084 | [MAESTRO Layer Mapping](084-maestro-layer-mapping-2026-04-07.md) | ✓ | ✓ | ✓ | Delivered | 2026-04-08 |
| 086 | [Automated Release Tagging via GitHub Actions](086-automated-release-tagging-via-github-actions-2026-04-06.md) | ✓ | ✓ | ✓ | Delivered | 2026-04-06 |
| 066 | [Install Script and Version Tagging](066-install-script-and-version-tagging-2026-04-06.md) | ✓ | ✓ | ✓ | Delivered | 2026-04-06 |
| 078 | [Agent Context Optimization](078-agent-context-optimization-2026-04-01.md) | ✓ | ✓ | ✓ | Delivered | 2026-04-02 |
| 074 | [Baseline-Aware Pipeline](074-baseline-aware-pipeline-2026-03-31.md) | ✓ | ✓ | ✓ | Delivered | 2026-04-01 |
| 075 | [Tachi Agent Best Practices](075-tachi-agent-best-practices-2026-03-31.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-31 |
| 071 | [Deterministic Infographic Extraction](071-deterministic-infographic-extraction-2026-03-30.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-30 |
| 067 | [Deterministic Report Data Extraction](067-deterministic-report-data-extraction-2026-03-30.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-30 |
| 060 | [Professional PDF Security Report Branding](060-professional-pdf-security-report-branding-2026-03-29.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-29 |
| 054 | [Security Assessment PDF Booklet](054-security-assessment-pdf-booklet-2026-03-28.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-28 |
| 053 | [Risk Reduction Funnel](053-risk-reduction-funnel-2026-03-28.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-28 |
| 048 | [Infographic Tiered Detection & Residual Risk](048-infographic-tiered-detection-residual-risk-2026-03-28.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-28 |
| 045 | [Instruction Manual](045-instruction-manual-2026-03-28.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-28 |
| 039 | [Standalone /tachi.infographic Command](039-standalone-infographic-command-2026-03-28.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-28 |
| 036 | [Compensating Controls](036-compensating-controls-2026-03-27.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-28 |
| 035 | [Quantitative Risk Scoring](035-quantitative-risk-scoring-2026-03-27.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-27 |
| 029 | [Agent Refactoring: Right-Size](029-agent-refactoring-right-size-2026-03-25.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-25 |
| 024 | [Example Threat Models](024-example-threat-models-2026-03-23.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-23 |
| 021 | [Platform Adapters](021-platform-adapters-2026-03-23.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-23 |
| 018 | [Threat Infographic Agent](018-threat-infographic-agent-2026-03-23.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-23 |
| 015 | [Threat Report Agent & Attack Trees](015-threat-report-agent-attack-trees-2026-03-23.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-23 |
| 012 | [SARIF Output Generation](012-sarif-output-generation-2026-03-22.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-22 |
| 010 | [Deduplication & Risk Rating](010-deduplication-risk-rating-2026-03-22.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-22 |
| 007 | [AI Threat Agents](007-ai-threat-agents-2026-03-22.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-22 |
| 005 | [STRIDE Threat Agents](005-stride-threat-agents-2026-03-21.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-22 |
| 003 | [Orchestrator Agent](003-orchestrator-agent-2026-03-21.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-21 |
| 001 | [Project Skeleton & Interface Contract](001-project-skeleton-interface-contract-2026-03-21.md) | ✓ | ✓ | ✓ | Delivered | 2026-03-21 |
| 000 | [Example Feature](000-example-feature.md) | — | — | — | Template | — |
