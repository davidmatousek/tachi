# Institutional Knowledge - tachi

**Project**: tachi - Automated threat modeling toolkit extending STRIDE with AI-specific threat agents for agentic applications
**Purpose**: Capture learnings, patterns, and solutions to prevent repeated mistakes
**Created**: {{PROJECT_START_DATE}}
**Last Updated**: 2026-04-08

**Entry Count**: 23 / 20 (KB System Upgrade triggers at 20 — schedule review)
**Last Review**: 2026-03-30
**Status**: ✅ Manual mode (file-based)

---

## Overview

This file stores institutional knowledge for tachi development. It's used by:
- `kb-create` skill - Add new learnings
- `kb-query` skill - Search existing patterns
- `root-cause-analyzer` skill - Document root causes

### When to Upgrade to KB System

**Trigger Conditions** (upgrade when ANY is true):
- Entry count reaches **20**
- File size exceeds **2,000 lines**
- Search takes **>5 minutes** (currently <5 seconds with Cmd+F)
- Major project milestone complete

**Current Status**: Manual file working well. No upgrade needed yet.
**Next Review**: When entry count reaches 15

---

## Patterns

### PAT-001: Wave-Based Parallelism for Content-Heavy Features

**Date**: 2026-03-21
**Feature**: 001 — Project Skeleton & Interface Contract
**Category**: Process / Execution Strategy

**Context**: Feature 001 required 33 tasks producing 119 files (all markdown + YAML, zero runtime code). Tasks were organized into 6 execution waves with parallel markers `[P]` on independent tasks.

**Pattern**: Group tasks into waves by dependency order, mark independent tasks with `[P]`, and execute each wave with maximum parallelism. Content-only features (markdown/YAML) have high parallelism potential because most files have no cross-dependencies until a verification phase.

**Result**: 33 tasks completed in a single session. Wave 3 achieved maximum parallelism with 15 simultaneous tasks across 3 independent user stories. The Team-Lead's 3-4 hour estimate held because parallel execution compressed wall-clock time.

**When to Apply**: Any feature where deliverables are independent files (agent prompts, schemas, documentation, templates). Less applicable to features with runtime code where compilation order and test dependencies constrain parallelism.

**Quality Score**: 8/10

### PAT-002: Parallel Agent Validation Across User Stories

**Date**: 2026-03-22
**Feature**: 005 — STRIDE Threat Agents
**Category**: Process / Execution Strategy

**Context**: Feature 005 required validating 6 STRIDE threat agents across 5 user stories (41 tasks). User stories 1–3 each targeted 2 agents independently (Spoofing+Tampering, Repudiation+InfoDisclosure, DoS+PrivilegeEscalation), while US4 and US5 handled cross-agent consistency and end-to-end integration.

**Pattern**: When a feature produces multiple independent domain artifacts (e.g., 6 agents), organize user stories so each story validates a subset of artifacts in isolation. This enables Wave 3 (the implementation-heavy wave) to run 3 parallel tracks — one per user story. Cross-cutting concerns (consistency, integration) come in later waves after individual artifacts are validated.

**Result**: 41 tasks completed in ~1 day. Wave 3 achieved 3-way parallelism across US1/US2/US3 with zero cross-dependencies. US4 (cross-agent consistency) and US5 (integration) ran sequentially afterward but were lightweight because individual agent quality was already validated.

**When to Apply**: Any feature where multiple peer artifacts (agents, schemas, templates) need creation and validation. Structure user stories around artifact subsets, not phases. Less applicable when artifacts have tight cross-dependencies that prevent independent validation.

**Quality Score**: 8/10

### PAT-003: Phased Delivery with Per-Story Checkpoints

**Date**: 2026-03-22
**Feature**: 010 — Deduplication & Risk Rating
**Category**: Process / Delivery Strategy

**Context**: Feature 010 required 24 tasks across 3 user stories (correlation detection, deduplicated counts, risk calibration) plus setup and polish phases. Each user story had clear input/output boundaries and an independent validation test.

**Pattern**: Structure implementation into phases aligned with user stories, each ending with a validation checkpoint. Phase 1 (Setup) establishes shared foundations. Phases 2-4 implement one user story each with an independent test. Phase 5 (Polish) handles cross-cutting concerns. This creates natural pause points where partial delivery already provides value — e.g., correlation detection (US-1) is useful even without deduplicated counts (US-2).

**Result**: 24 tasks completed same-day. Each phase checkpoint confirmed correctness before building on it. US-3 (risk calibration) was independent of US-1/US-2, enabling parallel development. The phased approach also made the tasks.md easier for reviewers to validate — each phase was self-contained with clear success criteria.

**When to Apply**: Any feature with multiple user stories where each story has independent validation criteria. Structure phases around stories, not technical layers. Less applicable when user stories are tightly coupled and cannot be validated independently.

**Quality Score**: 8/10

---

### PAT-004: SARIF 2.1.0 Maps Naturally to STRIDE Threat Models

**Date**: 2026-03-22
**Context**: Delivery retrospective for Feature 012 — SARIF Output Generation. Estimated: 1-2 days, Actual: 1 day.

**Problem**:
Needed to convert STRIDE + AI threat model findings into SARIF 2.1.0 format for CI/CD pipeline integration (GitHub Code Scanning, Azure DevOps).

**Solution**:
The STRIDE category-to-rule mapping and severity-to-CVSS alignment translate directly into SARIF's `reportingDescriptor` and `result` objects. A well-defined intermediate representation (finding IR with category, severity, component, mitigation) makes the SARIF mapping mechanical. Correlated findings map to `relatedLocations`, component context maps to `logicalLocations`, and deterministic fingerprints enable stable tracking across runs.

**Why This Matters**:
Captured during structured delivery retrospective. Smooth sailing — everything went roughly as planned. When the IR is well-structured, adding new output formats is straightforward prompt engineering with no schema friction.

**When to Apply**: Any future output format additions (e.g., CycloneDX, CSAF). Design the IR first, then map to the target schema. The IR-to-format mapping should be mechanical, not creative.

**Tags**: #retrospective #delivery #architecture #pattern

**Quality Score**: 7/10

---

### PAT-005: Spec-First Architecture Enables Clean External API Degradation

**Date**: 2026-03-23
**Feature**: 018 — Threat Infographic Agent
**Category**: Architecture / Graceful Degradation

**Context**: Feature 018 introduced tachi's first external API dependency (Gemini image generation). The team needed to integrate an optional external service without compromising the local-first, zero-dependency pipeline.

**Pattern**: Design the specification as the primary deliverable and the external API output (image) as best-effort. The spec is always produced locally; the image is only attempted when the API key is present. Six failure conditions (missing key, rate limit, timeout, content policy, missing input, empty model) all resolve the same way: save the spec, log the reason, continue the pipeline.

**Result**: The infographic agent produces a useful deliverable (spec) in all conditions. The Gemini API is purely additive — its absence is invisible to the pipeline. Triple opt-out (flag, env var, config) gives users control at every level.

**When to Apply**: Any feature that integrates an external API where the API output is valuable but not essential. Design the local artifact first, make the API call optional, and ensure all failure modes produce the local artifact. This pattern preserves tachi's local-first principle.

**Tags**: #retrospective #delivery #architecture #pattern #graceful-degradation

**Quality Score**: 8/10

---

### PAT-006: Post-Pipeline Enrichment via Schema-Driven Scoring

**Date**: 2026-03-27
**Feature**: 035 — Quantitative Risk Scoring
**Category**: Architecture / Pipeline Extension

**Context**: Feature 035 needed to add quantitative risk scoring to the existing `/tachi.threat-model` pipeline without modifying the threat agents or their output. The scoring agent consumes threat model output (threats.md or threats.sarif) and produces enriched output (risk-scores.md and risk-scores.sarif).

**Pattern**: Design post-pipeline enrichment as a separate command and agent that reads existing output and produces new artifacts. Use a dedicated schema (risk-scoring.yaml) to define scoring dimensions, weights, and severity bands — making the scoring methodology configurable and transparent. The enrichment agent references the existing finding schema via an optional extension block, preserving backward compatibility. SARIF fingerprints and taxonomies are preserved from source to enriched output for tracking continuity.

**Result**: 29 tasks completed same-day across 9 phases. The scoring agent operates independently of threat agents — no modifications to existing commands, agents, or schemas were needed (only an optional extension reference added to finding.yaml). Dual-format output reused the established SARIF generation pattern (PAT-004), and the weighted composite formula with severity band mapping made scoring reproducible (+/- 0.5 tolerance).

**When to Apply**: Any feature that enriches existing pipeline output with new dimensions (e.g., compensating controls, compliance mapping, cost estimation). Design as a separate command consuming existing output, use a dedicated schema for the enrichment logic, and preserve source identifiers for traceability. Avoid modifying upstream agents or schemas — extend via optional references.

**Tags**: #retrospective #delivery #architecture #pattern #pipeline-extension

**Quality Score**: 8/10

---

### PAT-007: Chained Pipeline Enrichment Validates Schema-Driven Extension Pattern

**Date**: 2026-03-28
**Feature**: 036 — Compensating Controls Analysis
**Category**: Architecture / Pipeline Extension

**Context**: Feature 036 added the third stage to tachi's threat analysis pipeline (`/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls`). It consumes risk-scores output and produces compensating-controls output with control detection, effectiveness classification, recommendations, and residual risk — extending the same schema-driven enrichment approach from PAT-006.

**Pattern**: Successive pipeline stages can chain reliably when each stage follows the same contract: consume prior stage's dual output (MD + SARIF), extend via a dedicated schema (compensating-controls.yaml extending risk-scoring.yaml), and produce new dual output. The 6-phase agent design (parse → discover → detect → classify → recommend → output) decomposed cleanly because each phase has well-defined inputs and outputs. The 8 STRIDE + 2 AI control detection categories mapped directly to the existing threat taxonomy, requiring no upstream schema modifications.

**Result**: 21 tasks completed in ~1 day across 6 waves. Smooth execution — the pipeline extension pattern from Feature 035 transferred directly. Schema extension (rather than modification) preserved backward compatibility. The coverage matrix and residual risk calculation were straightforward because the finding IR already carried all necessary fields from upstream stages.

**When to Apply**: When adding successive enrichment stages to an existing pipeline. If the previous stage validated the schema-driven extension pattern, subsequent stages can follow the same template with high confidence. The key enabler is a well-structured finding IR that carries forward all fields needed by downstream stages.

**Tags**: #retrospective #delivery #architecture #pattern #pipeline-extension

**Quality Score**: 8/10

---

### PAT-008: Well-Structured Specs with Atomic Tasks Enable Same-Day Delivery

**Date**: 2026-03-28
**Feature**: 039 — Standalone /tachi.infographic Command
**Category**: Process / Delivery Velocity

**Context**: Feature 039 decoupled infographic generation from the `/tachi.threat-model` pipeline into a standalone `/tachi.infographic` command. The change touched 32 files across 5 platform adapters, required dual-path data extraction logic, and removed Phase 6 from the orchestrator — all delivered same-day with 30 tasks across 5 user stories.

**Pattern**: When specifications decompose cleanly into atomic, independently testable tasks with clear acceptance criteria, same-day delivery is achievable even for cross-cutting changes touching 30+ files. The key enablers are: (1) each task maps to a single file or a single logical change, (2) adapter mirror tasks (T017-T027) follow a repeatable pattern from the primary implementation, and (3) validation tasks (T028-T030) are defined upfront so testing is not an afterthought.

**Result**: 30 tasks completed same-day. Zero blockers, zero rework. The adapter matrix (5 platforms × 2 agents + 1 command + orchestrator changes) was the largest surface area, but systematic mirror tasks made it mechanical rather than complex. Clean same-day delivery from spec to merged PR.

**When to Apply**: When planning features that are primarily command reorganization or pipeline restructuring (not greenfield architecture). If the change follows established patterns and the adapter matrix is well-understood, invest in atomic task decomposition — the upfront planning cost pays back in execution speed and zero-defect delivery.

**Tags**: #retrospective #delivery #process #velocity #same-day

**Quality Score**: 8/10

---

### PAT-009: Documentation Features Require Source Material Audit Before Writing

**Date**: 2026-03-28
**Feature**: 045 — End-to-End tachi Instruction Manual
**Category**: Process / Documentation

**Context**: Feature 045 created a comprehensive developer guide covering tachi's 4-command threat modeling pipeline. During implementation, existing source documentation (command specs, interface contracts) was found to be incomplete — requiring additional research to fill gaps before guide content could be written accurately.

**Pattern**: For documentation-heavy features, always run a source material audit in Phase 1 that explicitly reads every file the guide will reference and flags gaps. The research.md output should note not just what was found, but what was missing or ambiguous. This prevents mid-implementation surprises where writers discover they cannot document behavior that was never specified.

**Result**: 31 tasks completed same-day despite the incomplete source material. The mandatory read-first phase (T001-T006) caught the gaps early enough that they could be resolved during writing rather than causing rework.

**When to Apply**: Any feature where the primary deliverable is documentation that references existing command specs, API contracts, or architecture docs. Budget extra time for source material gaps — they are the norm, not the exception.

**Tags**: #retrospective #documentation #process #source-material

**Quality Score**: 7/10

---

### KB-010: Docs-Only Prompt Engineering Features Deliver in a Single Session

**Date**: 2026-03-28
**Feature**: 048 — Infographic Tiered Pipeline Auto-Detection & Residual Risk
**Category**: Process / Velocity

**Context**: Feature 048 extended the `/tachi.infographic` command with three-tier data source detection and residual risk extraction. All 27 tasks edited markdown prompt files (`.claude/commands/tachi.infographic.md` and `.claude/agents/tachi/threat-infographic.md`) — zero application code. The feature was designed, planned, built, and delivered in a single session.

**Pattern**: Features that modify only agent prompts and command files (no application code, no tests, no infrastructure) can complete the full AOD lifecycle in one session. The absence of build/test/deploy cycles eliminates the usual bottlenecks. Same-day delivery is achievable when: (1) all changes are markdown/YAML, (2) validation is manual walkthrough, and (3) the feature extends existing patterns rather than creating new ones.

**Result**: 27 tasks completed same-day. PRD → spec → plan → tasks → build → deliver all in one session. No surprises or blockers.

**When to Apply**: When scoping features that modify agent prompts, command orchestration, or documentation only. Set expectations for single-session delivery and avoid over-engineering the task breakdown.

**Tags**: #retrospective #velocity #prompt-engineering #process

**Quality Score**: 7/10

---

### PAT-011: 9-Section Template Pattern Enables Predictable Infographic Extension

**Date**: 2026-03-28
**Feature**: 053 — Risk Reduction Funnel
**Category**: Architecture / Template Extensibility

**Context**: Feature 053 added a third infographic template (risk-funnel) to the existing baseball-card and system-architecture templates. The 9-section template pattern (frontmatter, ASCII layout, style table, color palette, typography, zone specs, Gemini prompt, API config, accessibility) established by the first two templates made adding the third straightforward and predictable.

**Pattern**: The 9-section template pattern provides a stable contract for infographic templates. Each new template follows the same structure, making it possible to add new visualization types without modifying the agent's core logic — only the template file and registry entries change. The pattern also enables same-day delivery because the author knows exactly which sections to fill and can reuse established style conventions (dark theme, severity colors, Gemini prompt format).

**Result**: 24 tasks completed same-day. Template, agent, and command updates followed a predictable path with no architectural surprises. Graceful degradation (4-tier, 3-tier, 1-tier) added naturally through the Section 5 data extraction pattern.

**When to Apply**: When designing extensible template systems. Establish a numbered-section contract early (ideally with the first 2 templates), then each subsequent template becomes a fill-in-the-blanks exercise. The contract should cover layout, styling, data mapping, and external API integration.

**Tags**: #retrospective #architecture #pattern #template-extensibility

**Quality Score**: 7/10

---

### PAT-012: Docs-Only Template Features Complete Faster Than Estimated

**Source**: Feature 054 — Security Assessment PDF Booklet (Retrospective, 2026-03-28)

**Pattern**: Features that consist entirely of documentation, templates, and agent/command definitions (no application code, no tests, no runtime dependencies) consistently complete in 1 session vs. 3-4 session estimates. The absence of compilation, test suites, and integration debugging eliminates the typical implementation friction.

**Evidence**: Feature 054 estimated 3-4 sessions (team-lead assessment based on 34 tasks across 4 waves). Actual: 1 session. Feature 048 (infographic tiered pipeline) and Feature 053 (risk funnel template) showed similar compression. KB-010 documented a single prior instance; this entry upgrades it to a confirmed pattern with Feature 054 as third data point.

**When to Apply**: When estimating timelines for features that produce only markdown, YAML, or Typst files with no runtime code. Reduce estimates by 50-70% from standard task-count-based projections. The key indicator is "no test suite required" — if the feature needs manual PDF/output review rather than automated tests, it's in this category.

**Tags**: #retrospective #estimation #pattern #docs-only

**Quality Score**: 8/10

---

### PAT-013: Typst Template Modularity Requires Hub-First Architecture

**Source**: Feature 060 — Professional PDF Security Assessment Report (Retrospective, 2026-03-29)

**Pattern**: When building modular Typst template systems, the theme token layer (colors, fonts, spacing) and shared utility layer (reusable functions) must be fully stabilized before individual page templates are authored. Attempting to build page templates in parallel with the theme system leads to inconsistent token usage and repeated rework as the shared API changes.

**Evidence**: Feature 060 required 5 implementation waves with Wave 1 dedicated entirely to theme.typ + shared.typ foundation before any new pages could begin. The spec explicitly marked Wave 1 as "CRITICAL: No user story work can begin until this phase is complete." Getting the import chain right (main.typ → theme → shared → pages) required iteration on the module boundary design.

**When to Apply**: When designing multi-file Typst template systems with shared theming. Allocate a dedicated foundation phase for the theme token system and shared utilities. Only begin page-level work after the import chain and token API are frozen. This mirrors the hub-and-spoke content model from the knowledge system stack conventions.

**Tags**: #retrospective #architecture #typst #template-design

**Quality Score**: 7/10

---

### PAT-014: Precision Data Extraction Requires Scripts, Not LLM Parsing

**Source**: Feature 067 — Deterministic Report Data Extraction (Retrospective, 2026-03-30)

**Pattern**: When extracting structured data from known, stable formats (markdown tables, YAML frontmatter) for report generation, deterministic script-based parsing (regex, line splitting) must be used instead of LLM-based parsing. LLM parsing introduces non-determinism — identical inputs produce different severity counts, scope data counts, and recommendation text across runs. This makes the output unsuitable for compliance, audit trails, or executive communication where reproducibility is required.

**Evidence**: Feature 067 replaced inline LLM parsing in the report-assembler agent with a Python script (`scripts/extract-report-data.py`). The LLM-based approach produced 4 different severity distributions from 4 runs on identical input. The script produces byte-identical output every time. The script uses only Python stdlib (regex, argparse, pathlib) — zero external dependencies.

**When to Apply**: Any time structured data must be extracted from known formats and the output must be reproducible. If the format is stable and documented, script it. Reserve LLM-based extraction for unstructured or highly variable formats where exact reproduction is not required.

**Tags**: #retrospective #architecture #data-extraction #determinism #reporting

**Quality Score**: 9/10

---

### PAT-015: Determinism by Design — Explicit Choices at Every Level

**Source**: Feature 071 — Deterministic Infographic Extraction (Retrospective, 2026-03-30)

**Pattern**: Byte-identical output from identical input requires explicit design choices at every level of data processing: `json.dumps(sort_keys=True)` for key ordering, deterministic tie-breaking rules (composite score descending, threat ID ascending), Largest Remainder Method for percentage rounding (guarantees integer percentages sum to 100%), and stable sort algorithms for all collections. Determinism cannot be retrofitted — it must be a first-class design constraint from the start.

**Evidence**: Feature 071 built `scripts/extract-infographic-data.py` with determinism as a foundational requirement across 46 tasks. Every computation — severity percentages, heat map ordering, top-N finding selection, component risk weights — required an explicit deterministic strategy. The Largest Remainder Method was surfaced during the research phase as superior to naive `round()` which silently drops or adds percentage points. Pre-spec research directly improved the technical approach.

**When to Apply**: Any time output must be reproducible across runs for compliance, audit, or trust reasons. Design determinism into the data model and algorithms from the start. Document tie-breaking rules in the spec. Use research phases to find mathematically sound approaches (like LRM) rather than naive implementations.

**Tags**: #retrospective #architecture #determinism #data-extraction #infographic

**Quality Score**: 8/10

---

### PAT-016: On-Demand Skill Extraction for Agent Complexity Management

**Added**: 2026-03-31
**Source**: Feature 075 retrospective
**Category**: Architecture Pattern

**Pattern**: When agent prompt files exceed tier caps (Leaf ≤300, Report ≤800, Methodology ≤1,000 lines), extract domain knowledge (schemas, lookup tables, dispatch rules, scoring formulas) into dedicated skill directories with a tiered loading structure: SKILL.md (Level 2 overview + loading table) and references/ subdirectory (Level 3 on-demand files). Agents retain workflow logic and load domain knowledge via Read tool only when needed per ADR-002. This pattern reduced three methodology agents from 1,300–2,000 lines to under 1,000 lines each while maintaining identical pipeline output.

**Evidence**: Feature 075 extracted domain knowledge from orchestrator (2,000→769 lines), risk-scorer (1,419→994 lines), and control-analyzer (1,367→935 lines) into three skills: tachi-orchestration, tachi-risk-scoring, tachi-control-analysis. Pipeline regression test confirmed identical threat detection, risk scoring, and control coverage. The extraction was clean because domain knowledge (reference data) and workflow logic (agent behavior) have natural separation boundaries.

**When to Apply**: When any agent exceeds its tier line cap and the excess is reference data rather than workflow logic. The key indicator is content that agents consult but don't modify — schemas, lookup tables, scoring formulas, detection patterns. If the content drives conditional behavior, it belongs in the agent; if it's consulted as reference, it belongs in a skill.

**Tags**: #retrospective #architecture #skill-extraction #agent-design #on-demand-loading

**Quality Score**: 9/10

---

### PAT-017: Output Template Parity Requires Dedicated Validation Tasks

**Date**: 2026-04-01
**Feature**: 074 — Baseline-Aware Pipeline
**Category**: Process / Quality Assurance

**Context**: Feature 074 extended three output template pairs (threats.md/.sarif, risk-scores.md/.sarif, compensating-controls.md/.sarif) with baseline-aware sections — delta status columns, frontmatter blocks, and SARIF baselineState properties. During final validation, code review found 2 critical parity issues: the output-schemas.md checklist was missing the new baseline fields, and compensating-controls.md table columns didn't match the updated schema.

**Pattern**: When a feature modifies YAML schemas that have corresponding output templates (both .md and .sarif), template parity validation must be an explicit checkpoint task — not deferred to final validation. Each schema change should trigger a paired template review: (1) does the .md template include all new schema fields in its table columns, (2) does the .sarif template include corresponding properties, and (3) does the output-schemas.md checklist reflect the additions. Template parity checks should be built into phase checkpoints, not discovered at the end.

**Result**: The 2 critical parity issues were caught in final validation and fixed before merge. However, catching them earlier (at the Phase 1 checkpoint after schema extensions) would have prevented the code review round-trip. Future features touching schemas should add a "template parity audit" task at the end of each schema-modifying phase.

**When to Apply**: Any feature that extends or modifies YAML schemas with downstream output templates. Add explicit template parity tasks after schema modification phases. The key indicator is multiple representation formats of the same data model — if a field exists in a schema, it must exist in every template that renders that schema.

**Tags**: #retrospective #quality #template-parity #schemas

**Quality Score**: 8/10

---

### PAT-018: Prototype-First Gates Prevent Rework at Scale

**Date**: 2026-04-02
**Feature**: 078 — Agent Context Optimization
**Category**: Process / Risk Mitigation

**Context**: Feature 078 restructured 6 tachi agents from monolithic prompts (650-1,286 lines) to lean definitions (~150-180 lines) with on-demand skill references. The plan included a P0 prototype gate: restructure the risk-scorer agent first, validate the pattern works end-to-end, then scale to the remaining 5 agents.

**Pattern**: When applying a structural pattern change across multiple similar components, implement one component first as a prototype with an explicit validation gate before proceeding. The P0 gate on risk-scorer caught issues with reference file granularity and Read instruction formatting that would have required rework across all 6 agents if discovered later. The gate added ~2 hours but prevented an estimated 4-6 hours of rework at scale.

**Result**: P0 checkpoint was APPROVED_WITH_CONCERNS (non-blocking). Issues caught: reference file organization needed finer granularity than initially planned, and agent Read instructions needed explicit file path patterns. These learnings were applied cleanly to all subsequent agents (orchestrator, control-analyzer, report-assembler, threat-report, threat-infographic), resulting in P2 checkpoint APPROVED with 0 findings.

**When to Apply**: Any feature that applies the same structural change to 3+ similar components. The prototype gate is most valuable when the pattern involves new architectural concepts (like the lean agent + skill reference pattern) where the first implementation reveals design assumptions that need adjustment.

**Tags**: #retrospective #process #prototype-gate #agent-restructuring #risk-mitigation

**Quality Score**: 9/10

---

### PAT-019: Manifest-Driven Scripts Complete Faster Than Estimated

**Date**: 2026-04-06
**Feature**: 066 — Install Script and Version Tagging
**Category**: Process / Estimation

**Context**: Feature 066 replaced 6+ manual `cp -r` commands with a single `scripts/install.sh` that parses a machine-parseable manifest section in `INSTALL_MANIFEST.md`. The PRD estimated 7-10 hours; team-lead estimated 6.25 hours with parallelism. Implementation completed in a single session.

**Pattern**: When distributable paths are pre-defined in a parseable manifest and the spec contains exhaustive acceptance criteria with concrete Given/When/Then scenarios, bash script implementation becomes a translation exercise rather than a design exercise. Each acceptance scenario maps directly to a function or code block, eliminating ambiguity during coding.

**Result**: 19/20 tasks completed in a single session (T018 deferred by design — post-merge git tag). All 4 architect checkpoints passed. The spec's 7 success criteria and 5 edge cases provided complete coverage without any mid-implementation design decisions.

**When to Apply**: Any automation feature where (a) the input data is already structured (manifest, config, schema), (b) the spec enumerates all edge cases with concrete scenarios, and (c) the tool has no external dependencies beyond standard Unix tools. Less applicable to features requiring iterative design discovery or external API integration.

**Tags**: #retrospective #process #estimation #bash #manifest-driven #translation-not-design

**Quality Score**: 8/10

---

### KB-020: Config-Only Features Map Cleanly to AOD Lifecycle

**Date**: 2026-04-06
**Category**: Process
**Source**: Feature 086 retrospective
**Severity**: Informational

**Problem**: Uncertainty about whether the full AOD lifecycle (Discover → Define → Plan → Build → Deliver) is proportionate for features that produce only configuration files (no application code).

**Root Cause**: The lifecycle stages are process-agnostic — they govern what/why/how decisions, not code volume. A 3-file CI/CD feature benefits from the same governance gates as a 50-file application feature.

**Solution**: Feature 086 (3 YAML/JSON config files) completed the full lifecycle in a single session. Governance caught scope alignment (PRD 066 deferred this explicitly), verified install.sh compatibility, and produced a clean 3-wave build. The overhead was minimal and the traceability was valuable.

**Result**: Full lifecycle completed in one session. All Triad gates passed on first attempt. The key insight is that "small scope" doesn't mean "skip governance" — it means governance is fast.

**When to Apply**: Any feature where deliverables are configuration files, GitHub Actions workflows, or infrastructure-as-code with no application logic. The Plan stage may skip data-model.md and contracts/, but spec/plan/tasks still add value.

**Tags**: #retrospective #process #cicd #configuration #governance

**Quality Score**: 7/10

---

### KB-021: Taxonomy Overlay Features Propagate Smoothly Through Finding IR

**Date**: 2026-04-08
**Category**: Architecture
**Source**: Feature 084 retrospective
**Severity**: Informational

**Problem**: Uncertainty about whether adding a new classification dimension (MAESTRO layers) to the existing pipeline would require significant refactoring of downstream agents and output formats.

**Root Cause**: The finding IR was designed with optional extensible fields, and downstream agents already follow a passive propagation pattern — they include whatever fields exist in the finding without gating on them. This architecture makes taxonomy overlays a natural fit.

**Solution**: Feature 084 added `maestro_layer` as an optional field in the finding schema, classified components in Phase 1 via keyword matching, and let the field flow passively to all downstream outputs. No agent detection logic, scoring formulas, or dispatch rules required changes. All 22 tasks completed in 2 days across 5 waves.

**Result**: Implementation was smoother and faster than the 2-3 day estimate. The keyword-based classification achieved 95.2% accuracy on existing examples. Example regeneration validated the full pipeline end-to-end in a single pass.

**When to Apply**: Any future feature that adds a classification dimension to findings (e.g., compliance framework mapping, kill-chain phase tagging). Follow the same pattern: define taxonomy in shared reference, classify in Phase 1, extend schema with optional field, let downstream agents propagate passively.

**Tags**: #retrospective #architecture #taxonomy #pipeline #maestro

**Quality Score**: 8/10

---

### KB-022: Existing Template Patterns Accelerate New Template Development

**Date**: 2026-04-08
**Category**: Architecture
**Source**: Feature 091 retrospective
**Severity**: Informational

**Problem**: Estimating effort for new infographic templates and PDF report pages when extending an established pattern.

**Root Cause**: The infographic template system (mandatory sections: layout, style, color palette, typography, zone specs, prompt template, API config, accessibility) and the Typst single-export-function pattern provide strong structural constraints. When new templates follow existing patterns, the creative design space is limited to data mapping and visual layout — not system architecture.

**Solution**: Feature 091 added two new infographic templates (maestro-stack, maestro-heatmap), one new Typst page (maestro-findings), and extended two extraction scripts. All 25 tasks completed in a single session (estimated 3 days, actual <1 day). The 3-wave parallel strategy after the foundational extraction phase maximized throughput.

**Result**: Implementation was significantly faster than estimated. No surprises. The extraction script extension (MAESTRO data parsing) was the most code-intensive part, but followed established patterns from Feature 071.

**When to Apply**: Future infographic templates or PDF report pages that follow existing patterns. Estimate aggressively — the template architecture absorbs complexity. Reserve longer estimates for templates that require novel extraction logic or visual formats.

**Tags**: #retrospective #architecture #templates #infographics #estimation

**Quality Score**: 7/10

---

### KB-023: Centralized Parser Module Enables Same-Day Cross-Cutting Propagation

**Date**: 2026-04-08
**Category**: Architecture
**Source**: Feature 104 retrospective
**Severity**: Informational

**Problem**: Need to propagate baseline delta annotations (NEW, UNCHANGED, UPDATED, RESOLVED) through all downstream pipeline consumers (threat-report, infographic, PDF report) without modifying each consumer's parsing logic independently.

**Root Cause**: The shared parser module (`tachi_parsers.py`) serves as the single extraction point for all downstream scripts. Adding new fields to shared parser functions automatically makes them available to both `extract-report-data.py` and `extract-infographic-data.py`, which in turn feed agent prompts and report assembly.

**Solution**: Feature 104 added 2 new parser functions (`parse_baseline_frontmatter()`, `parse_resolved_findings()`) and extended 1 existing function (`parse_threats_findings()`) in the shared parser. Both extraction scripts consumed the new fields without needing independent parsing logic. Agent instructions and command files received delta context through the existing data flow — no new plumbing required. All 18 tasks completed same-day across 5 waves.

**Result**: Cross-cutting propagation through 10 files completed in a single session. The centralized parser pattern (established in Feature 067, PAT-014) proved its value as an architectural multiplier — one change point propagated to all consumers. Backward compatibility was maintained via presence checks (fields are only included when baseline data exists).

**When to Apply**: Any future feature that adds new data fields to the pipeline. Always add extraction logic to `tachi_parsers.py` first, then let downstream scripts consume via the shared API. Avoid adding field-specific parsing to individual extraction scripts — the shared parser is the single source of truth for data extraction.

**Tags**: #retrospective #architecture #parser #pipeline #centralized-extraction

**Quality Score**: 8/10

---

## Bug Fixes

*No entries yet. Use `/kb-create` to add the first bug fix.*
