# PRD Index

**Last Updated**: 2026-05-08 (F-4 Claude Permissions Baseline #277 PRD APPROVED — BLP-02 Wave 4 PRD authored & sign-offs landed (Triad triple sign-off: PM ✓, Architect ⚠ APPROVED_WITH_CONCERNS v1.1 11-of-11 v1.0 items resolved, Team-Lead ⚠ APPROVED_WITH_CONCERNS v1.0 5 advisories all /aod.spec/tasks-time refinements); PRD scope: curated `.claude/settings.json` baseline (~80 LOC after Cat-1 dedup; categorized read-only / local-state / destructive deny+ask / network host-allowlist with 19 domains spanning GitHub/Anthropic/OWASP/MITRE/NIST), `docs/standards/CLAUDE_PERMISSIONS.md` (~250 LOC self-contained policy decision log), ADR-041 (~100 LOC, 6 alternatives-considered including PreToolUse hooks and managed-settings layer), CHANGELOG entry; 14 mandatory ACs + 2 nice-to-have; cross-list `deny → ask → allow` precedence honored honestly with two worked examples; Bash pattern fragility / process-wrapper bypass via npx-docker-devbox-mise / read-only built-in shadow risks documented (R-8, R-9, R-10); ~8-9h active envelope / next-day wall-clock target; trigger same as F-3 (Daniel Wood LinkedIn 2026-05-02 enterprise-developer-environment posture); ICE 22 (I:8 C:7 E:7); ADR-041 reserved per Issue #277 §Detail. Prior: F-3 SECURITY.md and Private Disclosure Channel #272 DELIVERED 2026-05-08 — BLP-02 Wave 3 closed (3/5 features); SECURITY.md restructured to GitHub-canonical 5-section format (Supported Versions / Reporting a Vulnerability / What to expect / Scope / Out-of-scope, 51 LOC); GitHub Private Vulnerability Reporting toggle enabled (manual repo-settings); README.md `## Community` one-line SECURITY.md pointer; closes TACHI-VULN-05abc41ad4cc (INFO, A05 Security Misconfiguration); PR #273 squash-merged as `7b1cc53` on main; release-please PR #274 `chore(main): release 4.33.0`. Prior: F-2 Source-Pattern Hardening #256 DELIVERED 2026-05-05 — BLP-02 Wave 2 complete; 5 /security vuln_ids closed; canonical `aod_template_load_kv_file` primitive; ADR-040 Accepted; PR #257 squash-merged. Prior: F-250 Adversarial Unit Extraction Hot-Fix DELIVERED 2026-05-04. Prior: F-248 Substitution Surface Hardening DELIVERED 2026-05-04 — BLP-02 Wave 1.)
**Legend**: ✓=APPROVED, ⚠=APPROVED_WITH_CONCERNS, 🔄=CHANGES_REQUESTED, ⛔=BLOCKED, ⚠⚡=OVERRIDDEN


| # | Feature | PM | Architect | Team-Lead | Status | Date |
|---|---------|----|-----------|-----------| -------|------|
| 277 | [F-4 Claude Permissions Baseline (BLP-02 Wave 4)](277-claude-permissions-baseline-2026-05-08.md) | ✓ | ⚠ | ⚠ | Approved | 2026-05-08 |
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
