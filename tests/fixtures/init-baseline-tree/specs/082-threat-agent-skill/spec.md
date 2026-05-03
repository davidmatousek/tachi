---
prd_reference: docs/product/02_PRD/082-threat-agent-skill-references-2026-04-11.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-11
    status: APPROVED_WITH_CONCERNS
    notes: "Spec 082 faithfully represents PRD 082. All 19 deferred concerns (architect 11 + team-lead 8) verified resolved via 8/8 FR/SC spot-checks. Zero [NEEDS CLARIFICATION] markers. All 14 SC measurable, 6/6 PRD success metrics (M1-M6) mapped. 4 LOW-severity non-blocking items: cosmetic Q3/Q4/Q5 traceability + FR-13 formatting + agentic-app JPEG coordination. Full review: .aod/results/product-manager-spec.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Threat Agent Skill References — Externalize Detection Knowledge for All 11 Threat Agents

**Feature Branch**: `082-threat-agent-skill`
**Created**: 2026-04-11
**Status**: Draft
**Input**: PRD 082 — Threat Agent Skill References (approved 2026-04-11 with 11 architect + 8 team-lead non-blocking concerns deferred to spec)

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — STRIDE Agent Skill References (Priority: P1)

A developer runs `/tachi.threat-model` on a traditional 3-tier web application. Each of the 6 STRIDE agents (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) loads its detection patterns from a companion skill reference directory instead of embedding them inline. The resulting `threats.md` is equivalent to the current output in finding count and severity distribution on the 6 example architectures — with zero regression on any example.

**Why this priority**: STRIDE agents are the most mature detection tier with the tightest inline ceiling (113-141 lines each). This story demonstrates the refactor works on well-understood territory before AI agents. Shipping STRIDE-only is the fallback if Phase 2 discovers the pattern doesn't generalize to AI agents (PRD R5 contingency, natural fracture at STRIDE/AI boundary).

**Independent Test**: After extraction, open any STRIDE agent file and verify (a) it contains a `## Skill References` table, (b) it contains a `## Detection Workflow` section with one `**MANDATORY**: Read` directive loading the agent's detection patterns at invocation start, (c) the agent file is ≤120 lines, (d) running `/tachi.threat-model` on `examples/web-app/` produces a `threats.md` with finding count ≥ baseline and equivalent severity distribution.

**Acceptance Scenarios**:

1. **Given** any STRIDE agent file, **When** a contributor opens it, **Then** it contains a `## Skill References` table with at least one detection pattern reference path and at least one shared reference path (e.g., `severity-bands-shared.md` or `finding-format-shared.md`).
2. **Given** the spoofing agent, **When** it runs against a component during threat analysis, **Then** it reads `.claude/skills/tachi-spoofing/references/detection-patterns.md` via a single `**MANDATORY**: Read` directive at the start of detection.
3. **Given** the 6 STRIDE agents post-refactor, **When** a reviewer diffs `threats.md` output on the `web-app` example against the pre-refactor baseline, **Then** finding count is equal or higher, severity distribution is within ±1 per level, and no existing finding has been dropped.
4. **Given** each STRIDE agent file, **When** measured with `wc -l`, **Then** it is ≤120 lines (hard ceiling 180, stretch ≤90).

---

### User Story 2 — AI Threat Agent Skill References (Priority: P1)

A developer runs `/tachi.threat-model` on an agentic AI application (the `mermaid-agentic-app` or `agentic-app` example). Each of the 5 AI-specific agents (prompt-injection, data-poisoning, model-theft, tool-abuse, agent-autonomy) loads its detection patterns from a companion skill reference directory. The agentic-app example surfaces equivalent or additional findings — including at least one new finding category enabled by the enriched detection patterns (MITRE ATLAS agent-specific techniques AML.T0058-T0062 added Oct 2025, OWASP LLM Top 10 v2025 categories, OWASP AI Exchange).

**Why this priority**: AI agents are the core differentiator for tachi's "threat modeling toolkit for agentic AI" positioning. They're also the largest agents (167-201 lines) and hit the inline ceiling hardest. Enrichment here matters most because the AI threat landscape evolves rapidly (ATLAS Oct 2025 additions post-date the current inline patterns).

**Independent Test**: Open any AI agent file post-refactor and verify (a) it contains a `## Skill References` table pointing to a companion skill directory, (b) the agent file is ≤150 lines, (c) running `/tachi.threat-model` on `examples/agentic-app/` produces a `threats.md` where the AI-category finding count is equal or higher than baseline, (d) at least one finding in the enriched agentic-app output cites a primary source not in the pre-refactor baseline (e.g., OWASP LLM v2025, ATLAS AML.T0058+, NIST AI 600-1).

**Acceptance Scenarios**:

1. **Given** any AI agent file, **When** a contributor opens it, **Then** it contains a `## Skill References` table with a path under `.claude/skills/tachi-<agent-name>/references/`.
2. **Given** the prompt-injection agent, **When** it runs against an LLM-integrated component, **Then** it reads its enriched detection pattern reference file (containing the pre-refactor inline patterns plus ≥2 new enriched categories, OR 0 if enrichment was de-scoped for that specific agent during Phase 2e — see Requirement 7).
3. **Given** the 5 AI agents post-refactor, **When** a reviewer diffs `threats.md` on `agentic-app`, **Then** finding count is equal or higher AND at least one AI-category finding cites a primary source (OWASP LLM v2025, OWASP AI Exchange, MITRE ATLAS ≥v5.1, or NIST AI 600-1) that was not cited in the pre-refactor baseline.
4. **Given** each AI agent file, **When** measured with `wc -l`, **Then** it is ≤150 lines (hard ceiling 180, stretch ≤130).

---

### User Story 3 — Shared Reference Deduplication with Additive-Only Edits (Priority: P1)

The OWASP 3×3 risk matrix currently appears as an identical 9-row table in 11 threat agent files (≈110 duplicated lines). After the refactor, the matrix lives in exactly one shared reference file (`severity-bands-shared.md` or `finding-format-shared.md`, whichever is appropriate per content orientation). Threat agents Read the shared reference via `**MANDATORY**: Read` directives. Edits to shared references are **additive-only** — no existing content that infrastructure agents already consume is modified in place. When a contributor grep-searches for the OWASP 3×3 matrix across the repository, they find it in exactly one shared reference file.

**Why this priority**: Shared reference deduplication is what makes the refactor durable. Without it, future contributors will re-duplicate content and the architecture will drift back toward the pre-refactor state. Additive-only discipline protects the 6 infrastructure agents (orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) that already consume these shared references in production — a breaking edit to a shared reference could silently regress the entire pipeline.

**Independent Test**: Run `grep -rn "OWASP 3×3"` (and equivalent patterns for STRIDE category names) across the repository. The OWASP 3×3 matrix must appear in exactly one `.claude/skills/tachi-shared/references/` file. All 11 threat agents and any other consumer must reach it via a Read directive. No threat agent file contains the matrix inline.

**Acceptance Scenarios**:

1. **Given** the 11 threat agents post-refactor, **When** a reviewer grep-searches for any OWASP 3×3 matrix row, **Then** every match is inside `.claude/skills/tachi-shared/references/` — not inside any `.claude/agents/tachi/*.md` file.
2. **Given** any threat agent needing the finding template, **When** it generates a finding, **Then** it has Read `finding-format-shared.md` via a `**MANDATORY**: Read` directive and uses its producer-oriented construction guidance (added in Phase 2c).
3. **Given** the 6 infrastructure agents (orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler), **When** they run pre-refactor vs. post-refactor on the 6 example architectures, **Then** their content-level output is unchanged (re-baseline of 5 byte-deterministic PDFs is expected — see Requirement 17).
4. **Given** any existing shared reference file, **When** a reviewer diffs pre/post content, **Then** existing sections are byte-identical (no modifications) and any new sections are clearly additive (new `## ` headings appended).

---

### User Story 4 — Prototype-First Validation Gate with Sub-Phasing (Priority: P1)

Before touching 9 of the 11 agents, the team extracts spoofing (STRIDE) and prompt-injection (AI) first in a prototype phase. The prototype runs in two sub-phases: **Phase 1a** extracts the architectural refactor *without* adding new detection patterns (regression-only check); **Phase 1b** then adds the enrichment. Phase 1 passes only after both sub-phases pass concrete, measurable criteria reviewed by architect + team-lead. A failing Phase 1b enrichment can be reverted independently from a passing Phase 1a refactor. If Phase 1 fails after a maximum of 2 iterations, the feature is escalated for PRD re-scoping — default fallback is shipping STRIDE-only (Phase 2a) and deferring AI agents to a follow-up PRD 083.

**Why this priority**: The prototype-first gate is the real risk mitigation for R1 (pattern mismatch), R2 (enrichment noise), and the sibling-variant framing decision. Feature 078's T014 gate found a real clamping bug AND surfaced an intentional behavioral improvement — this pattern is proven to catch issues that would cost 4-6 hours to fix at scale. Sub-phasing lets the team separate "does the architectural surface work?" from "do the new patterns help?", which are two independent questions the current PRD bundles.

**Independent Test**: After Phase 1a completes, run the full pipeline on all 6 examples and diff `threats.md` against baseline; expect ZERO new findings (refactor should be transparent). After Phase 1b completes, re-run the pipeline; expect ≥1 new finding on the prototype agent's example surface (demonstrating enrichment actually adds coverage). Both sub-phase gates must be reviewed by architect + team-lead before Phase 2 begins.

**Acceptance Scenarios**:

1. **Given** Phase 1a (refactor-only), **When** the pipeline runs on all 6 examples, **Then** `threats.md` is equivalent to baseline in finding count per category (±0 — no new findings from refactor alone).
2. **Given** Phase 1b (refactor + enrichment), **When** the pipeline runs on the prototype agents' example surface, **Then** at least 1 new finding emerges from each enriched agent's new pattern categories, cited to primary sources.
3. **Given** Phase 1 results, **When** team-lead + architect review them, **Then** Phase 2 only starts on explicit joint approval; a failing sub-phase blocks rollout without blocking the other sub-phase's progress.
4. **Given** a Phase 1 gate failure, **When** 2 iterations have been attempted without passing, **Then** the feature is escalated for PRD re-scoping — the default fallback is shipping STRIDE-only (6 agents) and creating PRD 083 to handle the 5 AI agents.
5. **Given** the sibling-variant decision (methodology / phase-gated vs. detection / single-point load), **When** Phase 1 completes, **Then** the load-shape variant used by detection agents is documented in ADR-023 before Phase 2 begins (exit criterion E-4).

---

### User Story 5 — Detection Coverage Enrichment with Aggregate Floor (Priority: P2)

During extraction, each agent's detection pattern reference file is enriched with additional categories drawn from primary sources (OWASP Top 10, OWASP LLM Top 10 v2025, OWASP AI Exchange, MITRE ATT&CK, MITRE ATLAS v5.1+, CWE Top 25 2024, NIST AI 600-1). The enrichment target is **aggregate**: ≥22 new pattern categories across all 11 agents collectively, not ≥2 per agent individually. Some agents may receive 5+ enriched categories while others receive 0 — enrichment is explicitly de-scopable per agent on the critical path.

**Why this priority**: P2 rather than P1 because the architectural refactor (User Stories 1-4) is the non-negotiable outcome. Enrichment is an opportunistic bonus during the extraction window — deferring it risks never doing it at all (the inline patterns have gone untouched for multiple release cycles), but it must not block the refactor from shipping. The aggregate floor (≥22) is protected; the per-agent floor is negotiable.

**Independent Test**: After all 11 agents are extracted, tally the new pattern categories added across all 11 reference files. Verify aggregate total is ≥22. Have security-analyst review the enriched patterns for (a) primary source citation, (b) taxonomy correctness, (c) false-positive risk. Any pattern that fails security review is removed from its reference file without blocking the architectural refactor.

**Acceptance Scenarios**:

1. **Given** the 11 detection pattern reference files post-refactor, **When** a reviewer tallies new pattern categories added (not in pre-refactor inline versions), **Then** the aggregate total is ≥22.
2. **Given** each new pattern category, **When** a security-analyst reviews the reference file, **Then** the category cites at least one primary source (OWASP/CWE/MITRE ATT&CK/MITRE ATLAS/NIST AI RMF/NIST AI 600-1) with a canonical URL or identifier.
3. **Given** a pattern category that security-analyst flags as speculative or a false-positive risk, **When** review completes, **Then** the category is removed from the reference file (enrichment is reverted for that pattern) without affecting the architectural refactor.
4. **Given** an agent where enrichment is de-scoped on the critical path (e.g., research time inflated), **When** the agent is extracted, **Then** the agent still ships with its pre-refactor patterns intact in the reference file (architectural refactor succeeds even with 0 enrichment).

---

### Edge Cases

- **What happens when a shared reference file is missing or malformed at agent load time?** Per Principle VIII (Observability) and ADR-022 (fail-loud CLI prerequisites), the agent must produce a clear, actionable error message naming the missing file path. No silent fallback. The orchestrator surfaces this as a pipeline error, not as zero findings.
- **How does the system handle a threat agent that is refactored but its detection pattern reference file has not been created yet?** The agent fails to load (broken `**MANDATORY**: Read` directive). This is a build-time error, caught by validation tests, not a runtime degradation.
- **What happens if Phase 2 parallel extraction waves both try to edit the same shared reference file?** Shared reference consolidation is **serialized** in Phase 2c (single-writer wave, 1-2 hours). Per-agent skill directory work parallelizes; shared reference edits do not. This is a process constraint, not a technical one.
- **What happens if the enriched detection patterns introduce noisy findings on example architectures?** R2 mitigation: security-analyst reviews each enriched reference file in Phase 2e before Phase 3 validation. Specific enriched patterns can be reverted per-pattern without reverting the architectural refactor for that agent.
- **What happens if shared-reference edits (additive-only) flow through to the report pipeline and diff the 5 byte-deterministic PDFs?** R6 mitigation: re-baselining the 5 PDFs is an **expected Phase 3 outcome**, not an incident. The process is identical to Feature 136's `maestro-layers-shared.md` re-baseline — `SOURCE_DATE_EPOCH=1700000000` per ADR-021 produces new byte-identical baselines committed alongside the refactor.
- **What happens if a Phase 2 wave discovers that one specific agent doesn't fit the pattern?** Per-agent commit discipline (Requirement 15) means any single agent can be reverted independently. The 8 other extractions + Phase 1 prototype still ship; the 1 problematic agent is deferred to a follow-up.
- **What happens if a contributor accidentally adds MAESTRO references to a threat agent during the refactor?** Code review must reject this. The spec forbids it (FR-9). MAESTRO inheritance runs orchestrator-side in Phase 3 Table Assembly; threat agents are MAESTRO-agnostic and must stay that way.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-1 — Sibling-variant lean pattern**: Each threat agent MUST be restructured as a **sibling variant** of the lean + skill references pattern, distinct from the methodology / phase-gated variant used by control-analyzer. Detection agents MUST have a single `**MANDATORY**: Read` load point at the start of a `## Detection Workflow` section (not multiple phase-gated loads). The section name MUST be `## Detection Workflow`, not `## Phase Workflow`, to avoid implying multi-phase structure the agent does not have.

- **FR-2 — Skill References table**: Each threat agent MUST contain a `## Skill References` table immediately after its `## Purpose` section. The table MUST list at least one detection pattern reference (under `.claude/skills/tachi-<agent-name>/references/`) and at least one shared reference (under `.claude/skills/tachi-shared/references/`). Each row MUST specify file path, load-when semantics (always/conditional), and purpose.

- **FR-3 — Companion skill directory per agent**: Each of the 11 threat agents MUST have a companion skill directory at `.claude/skills/tachi-<agent-name>/references/` (no tier prefix — e.g., `tachi-spoofing/`, not `tachi-stride-spoofing/`). Each directory MUST contain at least a `detection-patterns.md` reference file. Directories named per the existing `tachi-*` convention.

- **FR-4 — Detection reference files are self-documenting**: Each `detection-patterns.md` (and any sibling reference file in the agent's skill directory) MUST be independently readable — a contributor reading the reference file without the parent agent MUST be able to learn what the threat category means, what patterns are being detected, and why each pattern matters. The reference file is the primary documentation surface for the threat category.

- **FR-5 — Shared reference consolidation is additive-only**: Shared reference files in `.claude/skills/tachi-shared/references/` MUST NOT have existing content modified or removed during this refactor. New content for threat agents MUST be added as new sections (new `## ` headings) appended to existing files, OR placed in new shared reference files. Specifically, `finding-format-shared.md` MUST gain a new `## For Threat Agents (Producers)` section with finding-construction guidance (resolving the consumer/producer orientation gap flagged by architect).

- **FR-6 — Shared reference audit before consolidation**: Before Phase 2c shared-reference consolidation begins, a spec task MUST verify content-orientation of each existing shared reference file. The audit task MUST produce a report naming any file whose current content is consumer-oriented (written for orchestrator/risk-scorer validation) and MUST specify the additive producer section to append.

- **FR-7 — Aggregate enrichment floor**: The 11 enriched detection reference files collectively MUST contain at least 22 new pattern categories that were not in the pre-refactor inline versions. Per-agent enrichment is explicitly de-scopable on the critical path — some agents may receive 5+ enriched categories while others receive 0. Each new category MUST cite at least one primary source from the approved source set.

- **FR-8 — Primary source citation for all new categories**: Every new detection pattern category added during enrichment MUST cite at least one of: OWASP Top 10 (2021 or later), OWASP LLM Top 10 (v2025 or later), OWASP AI Exchange, MITRE ATT&CK (v15+), MITRE ATLAS (v5.1 Nov 2025 or later), CWE Top 25 (2024 or later), NIST AI 600-1 (July 2024 or later). NIST AI 600-1 is acceptable for risk-framing context but NOT as a sole detection-signature source (use as supporting citation, not primary).

- **FR-9 — Threat agents remain MAESTRO-agnostic**: The refactor MUST NOT add any MAESTRO layer references, frontmatter fields, inline tables, or skill reference directives to any of the 11 threat agents. MAESTRO layer inheritance runs entirely orchestrator-side in Phase 3 Table Assembly (STRIDE and AI paths), as verified during architect review. A contributor who tries to externalize MAESTRO logic into a threat agent reference file during this refactor MUST have the change rejected in code review.

- **FR-10 — Tier-specific line count ceilings**: Each STRIDE agent file MUST be ≤120 lines (stretch target ≤90). Each AI agent file MUST be ≤150 lines (stretch target ≤130). Hard ceiling for any threat agent MUST be 180 lines. Enforcement is via `wc -l` check in validation phase.

- **FR-11 — `model:` frontmatter field preserved**: All 11 threat agents already have `model: sonnet` set in their YAML frontmatter today (verified during research). The refactor MUST preserve this field on every agent file. No agent may lose its `model:` declaration during extraction.

- **FR-12 — Prototype-first gate with sub-phasing**: Phase 1 MUST extract exactly 2 agents (spoofing from STRIDE, prompt-injection from AI) in two sub-phases: (a) Phase 1a does refactor-only extraction with zero new detection patterns; (b) Phase 1b adds enrichment patterns. Each sub-phase MUST pass measurable criteria reviewed by architect + team-lead before the next sub-phase begins. Phase 2 MUST NOT begin until both Phase 1a AND Phase 1b have passed.

- **FR-13 — Phase 1 exit criteria (measurable)**: Phase 1 gate MUST check, on all 6 example architectures: (a) finding count per category within ±2, (b) severity distribution within ±1 per level, (c) SARIF result count within ±2, (d) line count targets per FR-10, (e) at least 1 new finding surfaces from Phase 1b enrichment on the prototype agents' example surface (ensures enrichment is not theater), (f) sibling-variant load-shape documented in ADR-023 (exit criterion E-4). Max 2 gate iterations before escalation to PRD re-scoping.

- **FR-14 — Phase 2c serialization for shared-reference consolidation**: Shared reference edits in `.claude/skills/tachi-shared/references/` MUST be performed by a single writer in a dedicated serial wave (Phase 2c). Per-agent extraction work parallelizes; shared reference consolidation does not. If two parallel Phase 2a/2b tracks discover content that belongs in a shared reference, they MUST flag it but NOT modify the shared reference file; Phase 2c consolidates all flagged content.

- **FR-15 — Per-agent commit discipline**: Each of the 11 agent extractions MUST be a separate commit (or a self-contained set of commits scoped to one agent). Shared reference edits in Phase 2c MUST be a separate commit. This enables per-agent revert if Phase 2 or Phase 3 surfaces an issue with one specific agent without reverting the entire refactor.

- **FR-16 — ADR-023 created during spec or Phase 1**: An architectural decision record MUST be created at `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` documenting: (a) detection agents use a sibling variant of the lean + skill references pattern with single-point load semantics, (b) MAESTRO inheritance is orchestrator-owned and must not leak into threat agents, (c) shared reference edits are additive-only as a default posture, (d) finding-format-shared.md has a consumer audience (orchestrator/risk-scorer validation) and a producer audience (threat agents construction) with separate sections. ADR-023 MUST be created by end of Phase 1b at latest; earlier (during spec phase or Phase 1a) is preferred.

- **FR-17 — Byte-deterministic PDF re-baseline in Phase 3**: The 5 byte-deterministic PDFs (web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice — agentic-app is not byte-deterministic per Feature 128 convention) MUST be re-generated with `SOURCE_DATE_EPOCH=1700000000` per ADR-021 after shared reference consolidation completes. Re-baselining is an **expected Phase 3 outcome**, not an incident. The process mirrors Feature 136's `maestro-layers-shared.md` re-baseline. New baselines MUST be committed in the same PR as the refactor.

- **FR-18 — Zero regression gate (content-level, not byte-level)**: On each of the 6 example architectures, the pre-refactor `threats.md` and post-refactor `threats.md` MUST have equivalent content: finding count per category within ±2, severity distribution within ±1 per level, no existing finding dropped (new findings from enrichment are allowed). This is a content-level check on parsed findings, not a byte diff — the refactor moves content around, so byte-level equality is not expected.

- **FR-19 — Cross-agent coverage overlap audit**: After Phase 2 completes, an architect-led audit (Phase 2d) MUST identify detection categories that appear in 2+ threat agents (e.g., credential theft could be owned by spoofing, privilege-escalation, or both) and assign a single canonical owner for each overlapping category. The audit produces a short report documenting ownership assignments. This prevents drift back toward duplication after the refactor.

- **FR-20 — Security-analyst enrichment review (Phase 2e)**: Before Phase 3 validation begins, a dedicated Phase 2e wave MUST have security-analyst review each enriched reference file for: (a) primary source citation correctness, (b) taxonomy alignment with source intent (e.g., CWE-918 is SSRF, not SSRF-adjacent), (c) false-positive risk, (d) speculative patterns that should be removed. Security-analyst may reject specific patterns; those are reverted without affecting the architectural refactor.

### Key Entities

- **Threat Agent File**: A markdown file at `.claude/agents/tachi/<name>.md` containing YAML frontmatter (`model: sonnet`), metadata block, purpose, `## Skill References` table, `## Detection Workflow` with a single `**MANDATORY**: Read` directive, and minimal inline orchestration. Post-refactor shape is ≤120 lines (STRIDE) or ≤150 lines (AI). Attributes: `name` (spoofing, tampering, …), `category` (stride/ai), `companion_skill_directory` path, `pre_refactor_lines`, `post_refactor_lines`, `enrichment_count` (new pattern categories added).

- **Companion Skill Directory**: A directory at `.claude/skills/tachi-<agent-name>/references/` containing reference files consumed only by the corresponding threat agent. Attributes: `directory_path`, `reference_files[]`, `total_lines`, `parent_agent_name`.

- **Detection Pattern Reference File**: A markdown file (typically `detection-patterns.md`) inside a companion skill directory containing externalized inline patterns plus enrichment. Attributes: `file_path`, `pattern_categories[]`, `primary_source_citations[]`, `enrichment_count`, `is_self_documenting` (boolean).

- **Shared Reference File**: A markdown file at `.claude/skills/tachi-shared/references/<name>.md` consumed by multiple agents. Existing files: severity-bands-shared, finding-format-shared, stride-categories-shared, maestro-layers-shared. Attributes: `file_path`, `consumers[]` (frontmatter-declared), `actual_readers[]` (verified via grep), `content_orientation` (consumer/producer/both), `edit_policy` (additive-only).

- **Phase 1 Gate Result**: A structured gate outcome per sub-phase (1a, 1b) containing: `finding_count_delta[]`, `severity_delta[]`, `sarif_count_delta`, `line_count_per_agent[]`, `new_findings_from_enrichment[]` (Phase 1b only), `adr_023_status`, `gate_decision` (pass/fail), `iteration_count`. Max iterations before escalation: 2.

- **Enrichment Category**: A new detection pattern category added to a reference file during enrichment. Attributes: `agent_name`, `category_name`, `primary_source` (OWASP/CWE/MITRE ATT&CK/MITRE ATLAS/NIST), `citation_url`, `is_de_scoped` (boolean — set if the category was removed during Phase 2e security review).

- **ADR-023**: The architectural decision record at `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` documenting the detection-variant pattern. Status: `Draft` during Phase 1, `Accepted` after Phase 1 gate passes.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 — Architectural consistency**: 11 of 11 threat agents (100%) contain a `## Skill References` table, a `## Detection Workflow` section, and a single `**MANDATORY**: Read` directive at detection start. Verification: `grep -l "## Skill References" .claude/agents/tachi/*.md` returns 11 matches (currently 0).

- **SC-002 — Tier-specific line count targets met**: All 6 STRIDE agent files measure ≤120 lines via `wc -l`; all 5 AI agent files measure ≤150 lines; no threat agent exceeds 180 lines. Stretch: STRIDE ≤90, AI ≤130 (nice-to-have, not required).

- **SC-003 — Companion skill directories exist**: 11 of 11 directories exist at `.claude/skills/tachi-<agent-name>/references/` (matching the existing `tachi-control-analysis/` naming convention — no tier prefix). Each contains at least 1 reference file. Verification: `ls .claude/skills/tachi-{spoofing,tampering,…}/references/` returns files for all 11.

- **SC-004 — Shared reference deduplication verified**: Running `grep -rn "OWASP 3×3" .claude/` returns matches only in `.claude/skills/tachi-shared/references/` — not in any `.claude/agents/tachi/*.md` file. The OWASP 3×3 risk matrix appears in exactly one canonical location.

- **SC-005 — Zero content-level regression on 6 examples**: Running `/tachi.threat-model` on all 6 example architectures pre-refactor vs. post-refactor produces `threats.md` with finding count per category within ±2, severity distribution within ±1 per level, and no existing findings dropped. Byte-level equivalence of PDFs is NOT required (re-baseline is expected, per SC-008).

- **SC-006 — Aggregate enrichment floor met**: The 11 enriched detection reference files collectively contain ≥22 new pattern categories that were not in pre-refactor inline versions. Per-agent distribution may vary (some agents may have 0, others 5+). Verification: tally maintained in `specs/082-*/enrichment-tally.md` during Phase 2.

- **SC-007 — Primary source citations present**: 100% of new pattern categories cite at least one primary source (OWASP/CWE/MITRE ATT&CK/MITRE ATLAS/NIST AI RMF/NIST AI 600-1) with canonical URL or identifier. Verified by security-analyst in Phase 2e review.

- **SC-008 — Byte-deterministic PDFs re-baselined successfully**: After shared reference consolidation, the 5 byte-deterministic example PDFs (all examples except agentic-app) are regenerated with `SOURCE_DATE_EPOCH=1700000000` and commit cleanly — diff sizes match the expected scope (shared reference content propagation). If regeneration diff exceeds the expected scope, R6 contingency activates (roll back shared ref consolidation and use threat-only shared files).

- **SC-009 — ADR-023 created and accepted**: `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` exists, is referenced from the updated tech stack docs, and status is `Accepted` by end of Phase 1.

- **SC-010 — MAESTRO boundary preserved**: Running `grep -l "maestro\|MAESTRO" .claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}.md` returns **zero matches** post-refactor (same as pre-refactor). MAESTRO inheritance logic is not duplicated into threat agents.

- **SC-011 — Per-agent revert capability demonstrated**: Every agent extraction has its own commit (or commit cluster) in the Phase 2 PR history. A reviewer inspecting `git log --oneline` for the refactor PR sees at least 11 agent-specific commit messages identifiable by the agent name.

- **SC-012 — Infrastructure agent output unchanged at content level**: The 6 infrastructure agents (orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) produce equivalent content-level output pre/post refactor. Shared reference edits are additive-only; infrastructure agent findings, risk scores, control mappings, and narrative reports are unchanged except for any intentional re-baselining required by SC-008.

- **SC-013 — Phase 1 prototype catches issues at 2-agent surface**: If Phase 1 surfaces a pattern-fit issue (R1) or enrichment noise (R2), the issue is caught BEFORE Phase 2 extraction begins, limiting blast radius to 2 agents. Measurement: any architectural re-scope event during the refactor is traceable to Phase 1 gate findings, not to Phase 2 discoveries.

- **SC-014 — No runtime dependency additions**: `scripts/*.py` remains stdlib-only per PRD 128 convention. No new Python packages, Node packages, or CLI tools are added. Verification: no new entries in any package manifest; `pyproject.toml` unchanged except for version/metadata.

---

## Assumptions

- **A1 — Control-analyzer pattern is sibling-compatible**: The control-analyzer lean + skill references pattern maps onto detection agents as a **sibling variant** (single-point load, not phase-gated). This is validated in Phase 1 prototype. If Phase 1 reveals the pattern does not generalize, fallback is to ship STRIDE-only and create PRD 083 for AI agents (natural fracture point at STRIDE/AI boundary, confirmed by line-count tiers: STRIDE 113-141 lines, AI 167-201 lines).
- **A2 — Existing shared references are the right consolidation target**: The 4 existing files in `tachi-shared/references/` (severity-bands, finding-format, stride-categories, maestro-layers) are sufficient for cross-agent deduplication. No new shared reference files are needed. If Phase 2c discovers content that doesn't fit any existing shared file, it goes into a new file in the same directory (not in a new top-level skill).
- **A3 — Primary source availability for enrichment**: OWASP, CWE, MITRE ATT&CK, MITRE ATLAS, NIST AI RMF, NIST AI 600-1 collectively contain ≥22 new pattern categories that extend beyond the pre-refactor inline vocabulary. Web-researcher confirmed (research.md §3.3) the feasible ceiling is ~33+, well above the target.
- **A4 — The 6 example architectures are sufficient regression surface for architectural refactor**: They were sufficient for PRDs 029, 075, 078, 084, 091, 104, 128, 136. They are expected to be sufficient for the structural refactor in PRD 082. Architect noted that these examples validate **structural** regression (SC-005), not **enrichment coverage** — enrichment validation is source-citation-based per FR-8, not example-triggered.
- **A5 — MAESTRO inheritance remains orchestrator-side**: Orchestrator Phase 3 Table Assembly continues to attach `maestro_layer` to findings based on the Phase 1 component inventory. Threat agents continue to produce findings without `maestro_layer`. The refactor does not change this.
- **A6 — R2 enrichment noise is bounded by security-analyst review**: Enriched patterns may produce false positives on some example architectures, but Phase 2e security-analyst review catches speculative or noisy patterns before Phase 3 validation. Rollback is per-pattern, not per-agent.
- **A7 — R6 re-baseline is mechanical**: The 5 byte-deterministic PDFs can be regenerated successfully with `SOURCE_DATE_EPOCH=1700000000` after shared reference edits. This is the same pattern as Feature 136 (`maestro-layers-shared.md` re-baseline), which succeeded without incident.

**Validation needed** (tracked in checklist):
- [ ] A1 validated in Phase 1 prototype (sibling-variant pattern generalizes to both spoofing AND prompt-injection without forcing)
- [ ] A3 validated by security-analyst in Phase 2e (primary source citations are correct and taxonomically aligned)

---

## Constraints

**Technical Constraints**:
- **C1 — No new runtime dependencies**: `scripts/*.py` remains stdlib-only per PRD 128 convention (no new Python packages, no new Node packages, no new CLI tools).
- **C2 — No agent invocation interface changes**: Orchestrator's dispatch logic (in `tachi-orchestration/references/dispatch-rules.md`) is unchanged. The interface between orchestrator and each threat agent remains byte-identical.
- **C3 — Reference files are markdown**: All reference files use markdown format, not YAML or JSON, to match the existing `.claude/skills/tachi-*` convention.
- **C4 — SOURCE_DATE_EPOCH byte-determinism**: The 5 non-agentic example PDFs must regenerate to new byte-deterministic baselines under `SOURCE_DATE_EPOCH=1700000000` per ADR-021. Baselines are committed to the repo alongside the refactor.
- **C5 — Schema version stays 1.3**: `schemas/finding.yaml` is unchanged. No new fields, no renamed enums, no structural changes.
- **C6 — One directory per agent**: Each of the 11 agents gets its own `.claude/skills/tachi-<agent-name>/` directory (FR-3). Content that doesn't fit there goes into `tachi-shared/references/`, not into new multi-agent top-level skills.

**Process Constraints**:
- **C7 — Prototype-first gate is a hard requirement**: Phase 2 does not begin without explicit team-lead + architect approval of Phase 1a AND Phase 1b results. Max 2 gate iterations before escalation to PRD re-scoping.
- **C8 — Per-agent commit discipline**: Each agent extraction is an atomic, independently reviewable unit of work (one commit or one commit cluster per agent). Shared reference edits in Phase 2c are a separate commit.
- **C9 — Additive-only shared reference edits**: Existing content in `.claude/skills/tachi-shared/references/` files MUST NOT be modified. New content is appended as new sections. Escalation path: if existing content must change, create a new file alongside.
- **C10 — Parallel-wave constraints**: Per-agent extraction parallelizes (Phase 2a STRIDE, Phase 2b AI). Shared reference consolidation does NOT parallelize (Phase 2c serial single-writer). Cross-agent overlap audit does NOT parallelize (Phase 2d).

---

## Out of Scope

- **Automated test suite for detection pattern coverage**: No pytest or equivalent tests exist for threat agents today. Adding a detection-pattern coverage test suite is deferred to a future PRD.
- **MAESTRO-aware detection pattern tagging**: Tagging enriched patterns with MAESTRO layers (enabling MAESTRO-stratified detection) is deferred. Threat agents remain MAESTRO-agnostic per FR-9.
- **Schema validation for detection pattern files**: No YAML schema enforcing required fields per pattern. Reference files remain plain markdown.
- **New threat categories beyond the 11 existing agents**: No new STRIDE letter, no new AI threat category. The 11-agent taxonomy is stable.
- **Orchestrator dispatch rule changes**: Orchestrator continues to call the same 11 agents via the same dispatch logic.
- **Baseline-aware delta logic changes**: PRD 104 delta propagation is unchanged.
- **Finding output format changes**: Finding schema v1.3 is unchanged. Producer/consumer contract unchanged.
- **New example architectures to exercise enriched patterns**: Adding an industry-vertical example (healthcare PHI, financial PCI) is a follow-up PRD if enrichment quality is in doubt.

---

## Open Questions

- [x] **Q1** (from PRD Q1, deferred to spec): Should enriched detection patterns cover specific industry verticals? **Resolved**: OPPORTUNISTIC only. If a primary source naturally includes an industry-specific pattern, enrichment may include it. The aggregate floor (≥22 categories) is protected regardless; industry-vertical coverage is not a separate mandate.
- [x] **Q2** (from PRD Q2): Line target realism. **Resolved by FR-10**: tier-specific targets (STRIDE ≤120, AI ≤150, hard ceiling 180, stretch STRIDE ≤90 / AI ≤130).
- [x] **Q6** (from PRD Q6): Primary sources for enrichment. **Resolved by research.md §3 and FR-8**: OWASP Top 10, OWASP LLM Top 10 v2025, OWASP AI Exchange, MITRE ATT&CK v15+, MITRE ATLAS v5.1+ (Oct 2025 agent techniques AML.T0058-T0062), CWE Top 25 2024, NIST AI RMF + AI 600-1.
- [x] **Q7** (from PRD Q7): AI agent example findings placement. **Resolved**: IN-AGENT for Phase 1 prototype. If file size exceeds the tier target in FR-10, Phase 1b revisits the decision.

---

## Dependencies

**Internal Dependencies**:
- **`tachi-shared/references/` skill directory**: Already in active production use by 6 infrastructure agents. MUST NOT break during consolidation (additive-only edits per C9).
- **`tachi-control-analysis/` skill directory**: Used as a reference implementation for the lean + skill references pattern (methodology variant). No changes needed; only imitation.
- **6 example architectures**: Regression test surface. MUST remain stable; no architecture changes during this refactor.
- **`specs/078-agent-context-optimization/`**: Predecessor feature. T014 prototype gate pattern, phase wave structure, and `wc -l` validation commands are reused.
- **ADR-021**: SOURCE_DATE_EPOCH=1700000000 for byte-determinism. R6 mitigation depends on this ADR being valid.
- **Feature 136 precedent**: `maestro-layers-shared.md` re-baseline process. Re-used verbatim for R6.

**External Dependencies**:
- **None** — this refactor has no external integrations. Primary sources (OWASP, CWE, MITRE ATT&CK, ATLAS, NIST) are referenced by URL in reference files, not fetched at runtime.

**Dependency Graph**:
```
PRD 082 (this feature)
  ├── Depends on: Control-analyzer pattern (proven in PRD 075)
  ├── Depends on: Shared references infrastructure (proven in PRDs 075, 078)
  ├── Depends on: ADR-021 determinism (for R6 re-baseline)
  ├── Depends on: Feature 136 re-baseline precedent
  ├── Depends on: Feature 078 T014 gate pattern (for Phase 1)
  └── Blocks: None (future threat detection enrichment becomes easier;
              PRD 083 exists only if Phase 1 fails and STRIDE-only fallback triggers)
```

---

## Implementation Sequencing (informational)

*Detailed task breakdown belongs in `tasks.md`. This section captures sequence-critical dependencies discovered in research and review.*

### Phase 0 (pre-prototype preparation)

1. Web-researcher produces per-agent enrichment briefs from approved primary sources (FR-8) — identifies which new categories each agent should consider.
2. Architect creates draft ADR-023 documenting the sibling-variant pattern decision (FR-16).
3. Pre-refactor baseline capture: run pipeline on all 6 example architectures, commit `threats.md` baselines for regression comparison.

### Phase 1 (prototype, 5-8 hours, per team-lead widening)

1. **Phase 1a — refactor-only**: Extract spoofing + prompt-injection to lean agents + companion skill directories with pre-refactor patterns verbatim (NO new categories). Re-run pipeline on all 6 examples. Gate: FR-18 content-level regression passes with ±0 new findings.
2. **Phase 1b — enrichment**: Add ≥2 new categories to each prototype agent's reference file, citing primary sources (FR-8). Re-run pipeline. Gate: FR-13 exit criteria met; at least 1 new finding surfaces from enrichment.
3. **Phase 1 combined gate**: team-lead + architect review; explicit joint approval required before Phase 2. Max 2 iterations before escalation.

### Phase 2 (rollout, 14-20 hours)

- **Phase 2a — STRIDE extraction** (parallel, 3 tracks max): tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation
- **Phase 2b — AI extraction** (parallel, 3 tracks max): data-poisoning, model-theft, tool-abuse, agent-autonomy
- **Phase 2c — Shared reference consolidation** (SERIAL single-writer, 1-2h): Update `finding-format-shared.md` with `## For Threat Agents (Producers)` section; update any other shared refs via additive-only edits
- **Phase 2d — Cross-agent overlap audit** (serial, architect-led, 1h): identify overlapping categories across agents, assign canonical owners (FR-19)
- **Phase 2e — Security-analyst enrichment review** (serial, 1-2h): verify primary sources, taxonomy, false-positive risk (FR-20)

### Phase 3 (validation, 4-6 hours)

1. Full regression on all 6 example architectures (FR-18, SC-005)
2. Cross-agent grep audit for duplications (SC-004)
3. Byte-deterministic PDF re-baseline with `SOURCE_DATE_EPOCH=1700000000` (FR-17, SC-008)
4. Documentation sync: `docs/architecture/00_Tech_Stack/README.md` agent inventory; ADR-023 status → Accepted
5. CHANGELOG entry (release-please handles version bump)

### Agent assignments (per team-lead §3 expanded milestone table)

- **senior-backend-engineer**: Phase 1a, Phase 1b, Phase 2a/2b/2c extraction + consolidation work
- **web-researcher**: Phase 0 enrichment source briefs
- **security-analyst**: Phase 1b enrichment review, Phase 2e full enrichment review
- **architect**: Phase 1 gate review, Phase 2d cross-agent overlap audit, Phase 3 documentation sync, ADR-023 authorship
- **team-lead**: Phase 1 gate review, capacity/timeline governance across all phases
- **tester**: Phase 3 regression (content-level diff + byte-deterministic re-baseline)
- **devops**: Phase 3 delivery (PR, release-please, issue close)

---

## Appendix A: Mapping PRD 082 → Spec Artifacts

This table confirms that all deferred architect + team-lead concerns from PRD 082 approval have been resolved in this spec.

| Source Concern | PRD Status | Spec Resolution |
|----------------|------------|-----------------|
| Sibling variant framing (architect §1 MEDIUM) | Deferred | FR-1 + FR-16 (ADR-023) |
| Tier-specific line targets (architect §3 MEDIUM) | Applied in PRD | FR-10 + SC-002 |
| Phase 1a/1b sub-phasing (architect C1 HIGH) | Deferred | FR-12 + FR-13 + User Story 4 |
| Shared-ref consumer/producer audit (architect §4 LOW) | Deferred | FR-5 + FR-6 + User Story 3 |
| Q3 directory naming (architect §5 LOW) | Resolved in PRD | FR-3 (`tachi-<agent-name>/`) |
| Q4 MAESTRO (architect §7 LOW) | Resolved in PRD | FR-9 + SC-010 |
| Example coverage gap (architect §6 LOW) | Deferred | A4 explicit note; enrichment validation is source-citation-based |
| AI example findings placement Q7 (architect C2 LOW) | Deferred | Q7 resolved in Open Questions; in-agent default |
| Parallel-wave shared-ref serialization (architect C4 LOW) | Deferred | FR-14 + C10 |
| ADR-023 creation (architect C5 LOW) | Deferred | FR-16 + SC-009 |
| Skill ref as primary docs (architect C6 LOW) | Deferred | FR-4 |
| Timeline widened to 32h (team-lead §1) | Applied in PRD | Implementation Sequencing matches PRD Phase budgets |
| Phase 1 widened to 5-8h (team-lead §1) | Applied in PRD | Implementation Sequencing |
| Parallel-wave serialization (team-lead §2) | Deferred | FR-14 + C10 |
| Milestone owner expansion (team-lead §3) | Deferred | Implementation Sequencing agent assignments |
| Enrichment de-scope discipline (team-lead §5) | Applied in PRD | FR-7 aggregate floor + User Story 5 |
| R6 re-baseline (team-lead §6) | Applied in PRD | FR-17 + SC-008 + Edge Cases |
| Per-agent commit discipline (team-lead §7) | Deferred | FR-15 + C8 + SC-011 |
| Gate retry limit (team-lead §4) | Deferred | FR-12 / FR-13 (max 2 iterations) |

All 11 architect concerns + 8 team-lead concerns are now addressed in spec-phase requirements, success criteria, or resolved open questions. No deferred concern remains unresolved.
