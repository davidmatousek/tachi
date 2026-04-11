---
prd:
  number: "082"
  topic: threat-agent-skill-references
  created: 2026-04-11
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-04-11, status: APPROVED, notes: "PRD grounded in research phase (spoofing extraction analysis, PRD 029/075/078 predecessor data). Scope disciplined via prototype-first gate + de-scopable enrichment floor. Proceeding to /aod.plan." }
  architect_signoff: { agent: architect, date: 2026-04-11, status: APPROVED_WITH_CONCERNS, notes: "11 concerns (3 medium, 8 low). Key: control-analyzer pattern reframed as sibling variant (single-point load, not phase-gated) — applied to PRD. Tier-specific line targets applied. Q3/Q4 resolved in-PRD. Remaining 8 concerns addressable during /aod.spec (enrichment sub-phasing, shared ref audit, ADR-023). Full details: .aod/results/architect.md" }
  techlead_signoff: { agent: team-lead, date: 2026-04-11, status: APPROVED_WITH_CONCERNS, notes: "8 non-blocking concerns. Timeline widened to realistic 32h midpoint. Phase 1 budget widened to 5-8h. Phase 2 serialization for shared refs added. R6 added for byte-deterministic baseline regeneration. Enrichment explicitly de-scopable. Per-agent commit discipline + milestone owner expansion to land during /aod.plan. Full details: .aod/results/team-lead.md" }
source:
  idea_id: 82
  story_id: null
---

# Threat Agent Skill References: Externalize Detection Knowledge for All 11 Threat Agents

**Status**: Approved
**Created**: 2026-04-11
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High Impact, High Confidence)
**Predecessors**: PRD 029 (Agent Refactoring), PRD 075 (Agent Best Practices), PRD 078 (Agent Context Optimization)

---

## Executive Summary

### The One-Liner
Bring the 11 STRIDE and AI threat detection agents onto the same lean "agent + skill references" architecture already proven by the 6 infrastructure agents — externalize detection patterns, finding templates, and risk matrices into on-demand skill reference files while enriching coverage with deeper industry-specific and MITRE/OWASP/CWE indicators.

### Problem Statement
The tachi agent fleet is split into two architectures. The 6 infrastructure agents (orchestrator, risk-scorer, control-analyzer, threat-infographic, threat-report, report-assembler) use a **lean + skill references** pattern: agent files contain orchestration only, with domain knowledge loaded on-demand from `.claude/skills/tachi-*/references/` files. The 11 threat detection agents (6 STRIDE + 5 AI-specific) use a **self-contained** pattern: all detection patterns, finding templates, and risk matrices are embedded inline in agent files totaling 1,680 lines ([spoofing.md:1-113](.claude/agents/tachi/spoofing.md), [agent-autonomy.md:1-201](.claude/agents/tachi/agent-autonomy.md), etc.).

Three concrete consequences:

1. **Detection coverage is capped by inline space.** A 113-line spoofing agent can carry ~5 detection pattern categories. With skill references, it could access 20+ categories — industry-specific indicators (healthcare PHI, financial PCI), platform-specific heuristics, deeper MITRE ATT&CK technique mappings — all loaded on-demand without context cost until needed.

2. **Per-invocation context waste.** Every threat agent loads its full detection vocabulary on every call, even when analyzing a single DFD element type where most patterns don't apply. PRD 029 measured a **30% instruction-following accuracy improvement** from context reduction (Chroma "Context Rot" study, July 2025); threat agents have never seen that benefit.

3. **Architectural inconsistency.** 6/17 agents follow Pattern A (lean), 11/17 follow Pattern B (inline). Maintenance, onboarding, and contribution suffer from the two-track system. A developer adding a new detection pattern for info-disclosure must edit the agent file directly, while adding the same pattern for control-analyzer means editing a skill reference file.

Threat agents also **duplicate shared content** across all 11 files — the OWASP 3×3 risk matrix, the generic finding template, STRIDE category references. [severity-bands-shared.md](.claude/skills/tachi-shared/references/severity-bands-shared.md) and [finding-format-shared.md](.claude/skills/tachi-shared/references/finding-format-shared.md) already exist and are actively used by infrastructure agents — threat agents just don't reference them.

### Proposed Solution
Apply a **sibling variant** of the lean + skill references pattern — adapted for detection agents, which are structurally different from methodology agents like control-analyzer. Detection agents have effectively one phase (match → detect → emit), not six, so load semantics are **single-point-at-detection-start**, not phase-gated. This variant should be recorded in a new ADR (ADR-023) during the spec phase so both lean-agent shapes (methodology / phase-gated and detection / single-point) are documented.

1. **Each agent file** retains only: frontmatter (including `model:`), role identity, purpose narrative, input/output contract, a `## Skill References` table, and a `## Detection Workflow` section with a single `**MANDATORY**: Read` directive that loads detection knowledge before pattern matching runs.
2. **Each threat agent gets a companion skill directory** at `.claude/skills/tachi-<agent-name>/references/` (naming convention committed: no tier prefix, matches existing `tachi-control-analysis`, `tachi-risk-scoring`, `tachi-orchestration`).
3. **Shared content consolidates** into existing `.claude/skills/tachi-shared/references/` files — severity bands, finding format, STRIDE categories, risk matrix — with **additive-only edits** (append new sections; never modify existing content that infra agents already consume).
4. **Detection coverage expands** per agent during extraction: each externalized detection pattern file gets enriched with additional industry-specific indicators, platform heuristics, and deeper CWE/ATT&CK mappings that wouldn't fit in the old inline format.

This is a **restructure + enrich**, not a pure reduction. The restructure is P0; the enrichment is opportunistic — **de-scopable per agent on the critical path** if research time inflates (see Success Criteria for the aggregate floor).

### Success Criteria
- All 11 threat agents have a `## Skill References` table loading domain knowledge on-demand
- **Tier-specific line targets** (MUST): STRIDE agents ≤120 lines (stretch ≤90); AI agents ≤150 lines (stretch ≤130); hard ceiling 180
- Each companion skill directory exists with ≥1 detection pattern file per agent
- Shared content (severity bands, finding format, STRIDE refs) is deduplicated — each lives in exactly one canonical location, edited additively only
- **Qualitative regression check**: threat-model output on the 6 example architectures remains equivalent or better in finding count; delta ≥ 0 is success (enrichment-driven increases on agentic-app are expected, not required elsewhere)
- **Detection enrichment floor** (aggregate, not per-agent): at least 22 new pattern categories added across all 11 agents collectively, citing primary sources (OWASP, CWE, MITRE ATT&CK/ATLAS, NIST AI RMF). Individual agents may receive 0 or more; enrichment is de-scopable per agent if critical path is at risk.

### Timeline
3 phases with a prototype-first gate. **Realistic midpoint 32h** (team-lead review, Section 1) bounded by:
- **Optimistic**: 22h (lower bound + Phase 2 serialization addition)
- **Realistic**: 32h (upper bound + shared-ref serialization wave + enrichment security review)
- **Pessimistic**: 45h (if R1/R2/R3 materialize or enrichment research is slow)

Phase breakdown:
- **Phase 1** (prototype, 5-8 hours): spoofing + prompt-injection extracted, enriched, and validated against all 6 example architectures. Split into Phase 1a (refactor-only regression) → Phase 1b (enrichment addition) so a failing enrichment can revert independently from a passing refactor.
- **Phase 2** (rollout, 14-20 hours): remaining 9 agents in parallel waves (Phase 2a STRIDE extraction, Phase 2b AI extraction), then **Phase 2c serial shared-reference consolidation** (single-writer, 1-2h), then Phase 2d cross-agent overlap audit (1h), then Phase 2e security-analyst enrichment review (1-2h).
- **Phase 3** (validation, 4-6 hours): regenerate all 6 example threat models, re-baseline the 5 byte-deterministic PDFs, documentation sync.

**Prototype-first gate** (real gate, not a checkbox — PRD 078 evidence): Phase 2 does not begin until Phase 1 outputs pass concrete criteria reviewed by architect + team-lead. **Max 2 gate iterations** before escalation to PRD re-scoping. If the prototype reveals the control-analyzer sibling variant doesn't generalize, fallback is ship STRIDE-only in PRD 082 and defer AI agents to PRD 083 (natural fracture point: STRIDE = 113-141 lines, AI = 167-201 lines).

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's vision is "the default threat modeling toolkit for any team building agentic AI applications." The 5 AI-specific threat agents (prompt-injection, data-poisoning, model-theft, tool-abuse, agent-autonomy) are the core differentiators — and they're also the largest threat agents (167-201 lines), meaning their detection vocabulary hits the inline ceiling first. Externalizing lets the AI-specific coverage grow as the field evolves without further bloating the agent files.

### Roadmap Fit
Continues the quality-improvement arc of PRDs 029, 075, and 078, but finishes the job on the previously-untouched threat agent tier. After this PRD, **all 17 tachi agents** follow a single architectural pattern.

### Predecessor Relationship
| Feature | Scope | Outcome |
|---------|-------|---------|
| PRD 029 | First right-sizing — orchestrator, threat-report, threat-infographic | 47% orchestrator reduction, extraction pattern established |
| PRD 075 | Methodology skill extraction — orchestrator, risk-scorer, control-analyzer | ~2,786 lines net savings, `tachi-*` skill structure proven |
| PRD 078 | Methodology agent tier caps + `model:` fields | 500-line caps enforced on 6 infrastructure agents |
| **This PRD (082)** | **Threat agent skill references + detection enrichment** | **All 17 agents on one architecture; threat detection coverage expanded** |

---

## Target Users & Personas

### Primary Persona: Threat Model User
- **Role**: Developer running `/tachi.threat-model` on their architecture
- **Goal**: Comprehensive threat analysis with accurate, actionable findings
- **Impact**: Richer detection patterns surface threats that the old inline vocabulary missed — particularly industry-specific (healthcare, finance) and platform-specific (AWS IAM, OAuth flows) indicators that couldn't fit in 113-line files. User sees higher-quality findings without knowing the implementation changed.

### Secondary Persona: tachi Contributor
- **Role**: Developer adding new detection patterns or customizing threat coverage
- **Goal**: Extend threat detection without wading through 200-line agent files
- **Impact**: Detection patterns live in focused reference files (typically 50-300 lines each) that are independently editable and reviewable. Adding a new STRIDE indicator is a one-file diff to a reference, not a sprawling agent edit.

### Tertiary Persona: AI Security Researcher
- **Role**: Contributing new AI threat detection categories (LLM jailbreaks, model extraction variants)
- **Goal**: Keep tachi's AI threat coverage current with the latest research
- **Impact**: The `.claude/skills/tachi-prompt-injection/references/` directory becomes the place to add new jailbreak patterns without touching the prompt-injection agent itself — making upstream contributions lower-friction.

---

## User Stories

### US-1: STRIDE Agent Skill References
**When** running threat analysis on a traditional web application,
**I want** each STRIDE agent (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) to load detection patterns from skill references,
**So that** the agent has access to deeper indicator coverage than fits in the current ~120-line inline format.

**Acceptance Criteria**:
- Given a STRIDE agent file, when I open it, then it contains a `## Skill References` table with at least one detection pattern reference and one shared reference
- Given the spoofing agent, when it runs Phase 2 (detection), then it reads `.claude/skills/tachi-spoofing/references/detection-patterns.md` via `**MANDATORY**: Read` directive
- Given the 6 STRIDE agents, when I diff pre/post detection output on the `web-app` example, then finding count is equal or higher and finding detail is preserved

**Priority**: P0
**Effort**: M

### US-2: AI Threat Agent Skill References
**When** running threat analysis on an agentic AI application,
**I want** each AI-specific agent (prompt-injection, data-poisoning, model-theft, tool-abuse, agent-autonomy) to load detection patterns from skill references,
**So that** the agent can surface MAESTRO-layered and AI-specific indicators (jailbreak patterns, tool confusion attacks, autonomy boundary violations) at coverage depth the inline format can't support.

**Acceptance Criteria**:
- Given an AI threat agent file, when I open it, then it contains a `## Skill References` table pointing to a companion skill directory
- Given the prompt-injection agent, when it runs Phase 2 (detection), then it reads its detection patterns reference file for enriched jailbreak taxonomy
- Given the 5 AI agents, when I diff pre/post detection output on the `agentic-app` example, then finding count is equal or higher and at least one new finding category surfaces from the enriched patterns

**Priority**: P0
**Effort**: M

### US-3: Shared Reference Deduplication
**When** an agent needs the OWASP 3×3 risk matrix, finding template, or STRIDE category definitions,
**I want** it to load from the canonical shared reference file,
**So that** changes to shared vocabulary propagate to all 11 agents without 11 file edits.

**Acceptance Criteria**:
- Given a threat agent, when it needs the risk matrix, then it reads `.claude/skills/tachi-shared/references/severity-bands-shared.md` — not an inline copy
- Given the finding template, when any threat agent generates a finding, then it references `finding-format-shared.md` — not an inline copy
- Given all 11 threat agents, when I grep for the OWASP 3×3 matrix, then it appears in exactly one file (the shared reference)

**Priority**: P0
**Effort**: S

### US-4: Prototype-First Validation Gate
**When** this refactor begins,
**I want** the first STRIDE agent and the first AI agent to be extracted and validated before the remaining 9 agents are touched,
**So that** any architectural flaw or quality regression is caught on a 2-agent surface area, not an 11-agent one.

**Acceptance Criteria**:
- Given Phase 1 completion, when I run the full tachi pipeline on all 6 example architectures, then output quality is validated by a reviewer comparing pre/post findings
- Given prototype validation results, when the team-lead reviews them, then Phase 2 only starts on explicit approval
- Given a regression discovered in the prototype, when Phase 1 ends, then the architecture is re-scoped before Phase 2 begins

**Priority**: P0
**Effort**: S

### US-5: Detection Coverage Enrichment
**When** a threat agent's inline detection patterns are extracted to a skill reference file,
**I want** the extraction pass to add at least 2 new pattern categories to that reference file,
**So that** the refactor delivers measurable detection coverage improvement, not just file reorganization.

**Acceptance Criteria**:
- Given any threat agent extraction, when the reference file is created, then it contains the original inline patterns plus ≥2 new pattern categories (industry-specific, platform-specific, or deeper CWE/ATT&CK mappings)
- Given the 11 agents, when I tally total detection pattern categories before/after, then the after count is higher by at least 22 (≥2 per agent)
- Given the enriched detection reference files, when reviewed by a security-analyst, then the new patterns cite primary sources (OWASP, CWE, MITRE ATT&CK, NIST AI RMF)

**Priority**: P1
**Effort**: M

---

## Functional Requirements

### Core Capabilities

#### Requirement 1: Lean Agent File Structure
**Description**: Each threat agent file is restructured to match the control-analyzer pattern: frontmatter, role identity, purpose, input/output contract, skill references table, phase workflow, quality standards.

**Inputs**: Current threat agent files ([.claude/agents/tachi/<name>.md](.claude/agents/tachi/)).
**Processing**: Identify sections to externalize (detection patterns, finding templates, risk matrices, reference citations); move them to skill reference files; replace with `**MANDATORY**: Read` directives in phase workflow sections.
**Outputs**: Restructured agent files, each containing only orchestration logic and skill references.

**Business Rules**:
- Every threat agent must have a `## Skill References` table immediately after the `## Purpose` section
- Every phase section that needs domain knowledge must begin with a `**MANDATORY**: Read <path>` directive
- Agent files must not contain raw detection pattern tables or inline OWASP/CWE/ATT&CK citation lists beyond what's needed for orchestration clarity
- The `model:` frontmatter field must be set (continuing the convention established in PRD 078)

#### Requirement 2: Companion Skill Directory Structure
**Description**: Create one skill directory per threat agent under `.claude/skills/tachi-<agent-name>/references/`, each containing detection pattern files, finding field guidance, and threat-specific references.

**Inputs**: Externalized content from agent files + new enrichment content.
**Processing**: Organize into logical reference files (typically: `detection-patterns.md`, `finding-template.md`, maybe `mitre-attack-mappings.md` for complex threats).
**Outputs**: 11 skill directories with a total of 22-33 new reference files.

**Business Rules**:
- Each skill directory lives at `.claude/skills/tachi-<agent-name>/references/`
- Reference files must be independently usable (can be read without reading the parent agent file)
- Shared content must not be duplicated across per-agent skill directories — it goes in `.claude/skills/tachi-shared/references/` instead

#### Requirement 3: Shared Reference Consolidation
**Description**: Identify cross-agent duplicated content and consolidate into `.claude/skills/tachi-shared/references/`.

**Inputs**: The 4 existing shared reference files plus duplicated content in the 11 threat agent files.
**Processing**: Extract cross-agent duplications — OWASP 3×3 risk matrix, generic finding template extensions, STRIDE category definitions, shared CWE mappings. Update `severity-bands-shared.md`, `finding-format-shared.md`, `stride-categories-shared.md` to be the canonical sources.
**Outputs**: Updated shared reference files; no more duplicated content across the 11 agent files.

**Business Rules**:
- Canonical rule: if content appears in 2+ threat agents, it must move to a shared reference
- Shared references are read-only from the perspective of any individual agent (changes require cross-agent review)
- Existing shared references are already in active use — migrate carefully to avoid breaking control-analyzer, orchestrator, etc.

#### Requirement 4: Detection Coverage Enrichment
**Description**: During extraction, each detection pattern reference file is enriched with new pattern categories beyond what the inline version carried.

**Inputs**: Existing detection patterns + industry/security research sources (OWASP Top 10 latest, OWASP AI Exchange, MITRE ATLAS, NIST AI RMF, CWE Top 25).
**Processing**: Add ≥2 new pattern categories per agent; document each with primary source citation; preserve existing patterns verbatim.
**Outputs**: Enriched detection reference files with measurably broader coverage.

**Business Rules**:
- Enrichment must cite primary sources (no speculative patterns)
- Existing patterns are preserved, not rewritten — additive only
- New categories should prefer breadth (industry verticals, new attack surfaces) over depth on existing categories

---

## Non-Functional Requirements

### Quality Requirements
- **Zero capability regression**: Every finding that the current inline agents produce must still be producible post-refactor on the 6 example architectures
- **Detection coverage must increase**: Total pattern categories across all 11 agents must grow by ≥22 (≥2 per agent)
- **Architectural consistency**: All 17 agents must follow the same lean + skill references pattern after this PRD

### Performance Requirements
- **Per-invocation context**: Each threat agent's loaded agent file must be ≤150 lines (leanest infrastructure agent is 208)
- **Skill loading is on-demand**: Reference files are loaded only during the phase that needs them, not at agent startup
- **Total skill reference size** per agent: 300-800 lines across all reference files (comparable to `tachi-control-analysis` at 537)

### Reliability Requirements
- **Backward compatibility**: The 6 example architectures must produce equivalent `threats.md` output pre/post refactor (finding count, severity distribution, MAESTRO layer assignment)
- **Rollback**: Each agent extraction is an atomic PR-sized change; failure to validate means reverting one agent without affecting others

### Maintainability Requirements
- **Reference files must be self-documenting**: A contributor reading `detection-patterns.md` without reading the parent agent must understand what it's for
- **Cross-references must be explicit**: Any reference to another skill file must use the full path `.claude/skills/tachi-*/references/<file>.md`

---

## Success Metrics

### Primary Metrics

**M1: Architectural Consistency**
- **Definition**: Count of threat agents with `## Skill References` table
- **Baseline**: 0 of 11 (0%)
- **Target**: 11 of 11 (100%)
- **Owner**: architect

**M2: Agent File Size Reduction**
- **Definition**: Total lines across 11 threat agent files
- **Baseline**: 1,680 lines
- **Target (MUST)**: ≤1,650 lines (≤150 avg per agent)
- **Target (STRETCH)**: ≤1,100 lines (~35% reduction, ≤100 avg)
- **Tier targets**: STRIDE ≤120/agent (stretch ≤90); AI ≤150/agent (stretch ≤130); hard ceiling 180
- **Owner**: architect

**M3: Detection Coverage Expansion**
- **Definition**: Count of detection pattern categories across all 11 threat agents (inline or referenced)
- **Baseline**: ~60-70 categories (rough count from inline tables)
- **Target**: ≥82-92 (at least +22)
- **Owner**: security-analyst

**M4: Zero Regression on Examples**
- **Definition**: For each of the 6 example architectures, pre/post `threats.md` finding count delta
- **Baseline**: Current finding counts per example
- **Target**: Delta ≥ 0 (no regressions; some examples may gain findings from enriched patterns)
- **Owner**: tester

### Secondary Metrics

**M5: Shared Reference Utilization**
- **Definition**: Count of threat agents referencing `severity-bands-shared.md` and `finding-format-shared.md`
- **Baseline**: 0 of 11
- **Target**: 11 of 11

**M6: New Skill Directory Count**
- **Definition**: Count of `.claude/skills/tachi-<threat-agent>/` directories
- **Baseline**: 0
- **Target**: 11

---

## Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- ✅ All 11 threat agents restructured to lean + skill references pattern
- ✅ 11 companion skill directories created with detection pattern files
- ✅ Shared reference deduplication (severity bands, finding format, STRIDE categories)
- ✅ `model:` frontmatter field on all 11 threat agents
- ✅ Prototype-first gate (spoofing + prompt-injection validated before rollout)
- ✅ Zero regression validated on 6 example architectures
- ✅ ≥2 new detection pattern categories per agent (22+ total net new)
- ✅ Example regeneration for all 6 architectures

**Should Have (P1)**:
- 🎯 Cross-agent coverage overlap analysis (e.g., if spoofing and privilege-escalation both cover credential theft, note the overlap and assign canonical ownership)
- 🎯 Documentation update: `docs/architecture/00_Tech_Stack/README.md` agent inventory section reflecting the new pattern

### Out of Scope (Future Phases)

**Could Have (P2)** — not in this PRD:
- 🔮 Automated test suite for detection pattern coverage (tests don't exist today for threat agents)
- 🔮 MAESTRO-aware detection pattern tagging in reference files (could enable MAESTRO-stratified detection)
- 🔮 Schema validation for detection pattern files (YAML schema with required fields per pattern)

**Won't Have** — explicitly excluded:
- ❌ Changes to finding schema or output format (schema_version stays 1.3)
- ❌ New threat categories beyond the 11 agents (no new STRIDE letter, no new AI threat category)
- ❌ Changes to orchestrator dispatch rules (orchestrator still calls the same 11 agents)
- ❌ Baseline-aware delta logic changes (PRD 104 stays as-is)

### Assumptions

- **A1**: The control-analyzer pattern (`tachi-control-analysis` skill with 3 references totaling 537 lines) is the correct model — it has been in production since PRD 075 and works well
- **A2**: The 4 existing shared references (`tachi-shared/references/`) are the right consolidation target — no new shared reference files needed
- **A3**: Enrichment sources (OWASP, CWE, MITRE ATLAS, NIST AI RMF) contain enough new patterns to add ≥2 per agent — validated by the fact that the current inline patterns cover only ~5 categories per agent while OWASP Top 10 alone has 10
- **A4**: The 6 example architectures are sufficient regression coverage — they were sufficient for PRDs 029, 075, 078, 084, 091, 104, 128, 136

**Validation Needed**:
- [ ] A1 validated in Phase 1 prototype (if control-analyzer pattern doesn't fit threat agents cleanly, re-scope)
- [ ] A3 validated by security-analyst confirming source material contains enrichment-worthy patterns

### Constraints

**Technical Constraints**:
- **C1**: No new runtime dependencies (scripts remain stdlib-only per PRD 128 convention)
- **C2**: No changes to agent invocation interface — orchestrator's dispatch logic unchanged
- **C3**: Reference files must be markdown, not YAML/JSON, to match existing `.claude/skills/tachi-*` conventions
- **C4**: `SOURCE_DATE_EPOCH=1700000000` byte-determinism must still hold for the 5 non-agentic example PDFs (per ADR-021)

**Process Constraints**:
- **C5**: Prototype-first gate is a hard requirement — Phase 2 does not begin without explicit team-lead approval of Phase 1 results
- **C6**: Each agent extraction is an atomic, independently reviewable unit of work

---

## Timeline & Milestones

### Phase 1: Prototype (4-6 hours)
- Extract spoofing + prompt-injection agents to skill references
- Create `.claude/skills/tachi-spoofing/references/` and `.claude/skills/tachi-prompt-injection/references/`
- Enrich each with ≥2 new detection categories
- Regenerate 6 example threat models; diff pre/post findings
- **Gate**: team-lead + architect review prototype; explicit approval required before Phase 2

### Phase 2: Rollout (10-16 hours)
- Extract remaining 5 STRIDE agents (tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation)
- Extract remaining 4 AI agents (data-poisoning, model-theft, tool-abuse, agent-autonomy)
- Consolidate shared references (severity bands, finding format, STRIDE categories)
- Parallel waves — agents within the same tier (STRIDE vs AI) have no cross-dependencies

### Phase 3: Validation (4-6 hours)
- Final regression check on all 6 example architectures
- Cross-agent dedup audit — grep for duplicated patterns
- Documentation sync: `docs/architecture/00_Tech_Stack/README.md` agent inventory
- CHANGELOG entry + release-please bump

### Key Milestones
| Milestone | Target Date | Owner |
|-----------|-------------|-------|
| PRD Approval | 2026-04-11 | product-manager |
| Plan + Tasks Complete | 2026-04-12 | architect + team-lead |
| Phase 1 Prototype Complete | 2026-04-13 | senior-backend-engineer |
| Phase 1 Gate Decision | 2026-04-13 | team-lead + architect |
| Phase 2 Rollout Complete | 2026-04-15 | senior-backend-engineer |
| Phase 3 Validation Complete | 2026-04-16 | tester |
| Feature Delivered | 2026-04-16 | devops |

---

## Risks & Dependencies

### Technical Risks

**R1: Prototype reveals pattern mismatch**
- **Likelihood**: Low
- **Impact**: High
- **Rationale**: Threat agents have a different shape than control-analyzer (detection vs. analysis). The control-analyzer pattern may not map cleanly.
- **Mitigation**: Prototype-first gate catches this on 2 agents, not 11
- **Contingency**: Re-scope pattern or fall back to a lighter refactor (just add `## Skill References` table without full externalization)

**R2: Enrichment introduces noisy findings**
- **Likelihood**: Medium
- **Impact**: Medium
- **Rationale**: Adding new detection patterns could surface false positives that weren't in the old inline version
- **Mitigation**: security-analyst reviews each enriched reference file; new patterns must cite primary sources
- **Contingency**: Roll back specific enriched patterns while keeping the architectural refactor

**R3: Shared reference consolidation breaks infrastructure agents**
- **Likelihood**: Low
- **Impact**: High
- **Rationale**: `tachi-shared/references/` files are already in active use by control-analyzer, orchestrator, etc. Editing them to consolidate threat agent content could introduce regressions in the infra agents.
- **Mitigation**: Shared reference edits are additive only — no content removal, only additions; validate infra agent output on examples
- **Contingency**: Keep shared references immutable and create threat-only shared files (`tachi-shared-threat/`) if a breaking conflict is found

**R4: Example regeneration surfaces unrelated pipeline changes**
- **Likelihood**: Low
- **Impact**: Medium
- **Rationale**: Regenerating examples could pick up incidental changes unrelated to this PRD, masking regressions
- **Mitigation**: Use `SOURCE_DATE_EPOCH=1700000000` for PDF byte-determinism (per ADR-021); diff `threats.md` at the content level, not byte level
- **Contingency**: Compare findings diff pre/post each agent extraction, not just at Phase 3

**R6: Shared reference edits invalidate byte-deterministic PDF baselines**
- **Likelihood**: High
- **Impact**: Low (expected, documented, re-baselineable)
- **Rationale**: Shared reference edits flow through to infra agents (risk-scorer, control-analyzer, threat-report). Per ADR-021 byte-determinism, any semantic reach into the report pipeline will diff the 5 byte-deterministic PDFs at the byte level even if content is equivalent.
- **Mitigation**: Treat baseline regeneration as an expected Phase 3 outcome. Same pattern as Feature 136 (maestro-layers-shared edit re-baselined 5 PDFs successfully).
- **Contingency**: If regeneration diff exceeds expected scope, roll back shared ref consolidation and keep threat-only shared refs isolated under `tachi-shared-threat/`.

### Business Risks

**R5: Longer timeline than PRD 078 suggests**
- **Likelihood**: Medium
- **Impact**: Low
- **Rationale**: 11 agents is roughly 2x the surface area of PRD 078 (6 agents). Even with parallelism, extraction + enrichment is more work than pure extraction.
- **Mitigation**: Parallel waves in Phase 2; prototype-first gate shrinks scope if needed
- **Contingency**: Ship STRIDE-only refactor first (Phase 2a), AI agents in follow-up PRD (Phase 2b → PRD 083)

### Dependencies

**Internal Dependencies**:
- **`tachi-shared/references/` skill**: Already in active use — must not break during consolidation
- **`tachi-control-analysis/` skill**: Used as reference pattern — no changes, just imitation
- **6 example architectures**: Regression test surface — must remain stable

**External Dependencies**:
- None — this is a pure refactor with no external integrations

**Dependency Graph**:
```
PRD 082 (this)
  ├── Depends on: Control-analyzer pattern (proven in PRD 075)
  ├── Depends on: Shared references (proven in PRDs 075, 078)
  └── Blocks: None (future threat detection enrichment becomes easier)
```

---

## Open Questions

### Product Questions
- [ ] **Q1**: Should the enriched detection patterns cover specific industry verticals (healthcare, finance, gov)? — owner: product-manager — due: during spec
- [ ] **Q2**: Is a 150-line soft target per agent realistic, or should we aim for 100? — owner: architect — due: Phase 1 prototype

### Technical Questions
- [x] **Q3 RESOLVED**: Skill directory naming is `tachi-<agent-name>/` with no tier prefix (matches existing `tachi-control-analysis`, `tachi-risk-scoring`, `tachi-orchestration`). Examples: `tachi-spoofing/`, `tachi-prompt-injection/`, `tachi-agent-autonomy/`.
- [x] **Q4 RESOLVED**: MAESTRO layer inheritance runs entirely orchestrator-side in Phase 3 Table Assembly. Threat agents are MAESTRO-agnostic today (verified: zero threat agents reference MAESTRO). The refactor MUST NOT add MAESTRO references to any threat agent — doing so would duplicate inheritance logic already owned by orchestrator Phase 3.
- [x] **Q5 RESOLVED**: Qualitative pre/post diff per PRD 078 precedent (T014 narrative diff format). Default unless security-analyst argues otherwise during spec.
- [ ] **Q7**: Where do AI agent example findings live post-refactor — in-agent, per-agent skill reference, or shared reference? — owner: architect — due: Phase 1 prototype (default: in-agent, revisit if file size exceeds tier target)

### Research Questions
- [ ] **Q6**: What are the best primary sources for enrichment beyond OWASP Top 10? (OWASP AI Exchange, NIST AI RMF, MITRE ATLAS, CWE Top 25) — owner: web-researcher — due: during spec

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- Prior refactoring PRDs: [029](029-agent-refactoring-right-size-2026-03-25.md), [075](075-tachi-agent-best-practices-2026-03-31.md), [078](078-agent-context-optimization-2026-04-01.md)

### Technical Documentation
- Tech Stack: [docs/architecture/00_Tech_Stack/README.md](../../architecture/00_Tech_Stack/README.md)
- Example reference pattern: [.claude/agents/tachi/control-analyzer.md](../../../.claude/agents/tachi/control-analyzer.md)
- Shared references: [.claude/skills/tachi-shared/references/](../../../.claude/skills/tachi-shared/references/)

### Research Sources (for enrichment)
- OWASP Top 10 2021 — web application threats
- OWASP AI Exchange — AI/LLM threats
- NIST AI Risk Management Framework
- MITRE ATT&CK + MITRE ATLAS (adversarial ML)
- CWE Top 25

### Source Issue
- GitHub Issue #82: [Enrich threat detection quality via skill-referenced domain knowledge for 11 threat agents](https://github.com/davidmatousek/tachi/issues/82)

---

## Appendix A: Current State Inventory

### 11 Threat Agents (baseline measurements from research phase)

| Agent | Category | Lines | Skill Refs? | Extract Target |
|-------|----------|-------|-------------|----------------|
| spoofing.md | STRIDE | 113 | ❌ | Phase 1 (prototype) |
| tampering.md | STRIDE | 126 | ❌ | Phase 2 |
| repudiation.md | STRIDE | 124 | ❌ | Phase 2 |
| info-disclosure.md | STRIDE | 128 | ❌ | Phase 2 |
| denial-of-service.md | STRIDE | 141 | ❌ | Phase 2 |
| privilege-escalation.md | STRIDE | 136 | ❌ | Phase 2 |
| prompt-injection.md | AI | 167 | ❌ | Phase 1 (prototype) |
| data-poisoning.md | AI | 171 | ❌ | Phase 2 |
| model-theft.md | AI | 188 | ❌ | Phase 2 |
| tool-abuse.md | AI | 185 | ❌ | Phase 2 |
| agent-autonomy.md | AI | 201 | ❌ | Phase 2 |
| **Total** | — | **1,680** | **0/11** | — |

### Reference Pattern (from PRD 075, actively in use)

| Infrastructure Agent | Lines | Skill References |
|----------------------|-------|------------------|
| control-analyzer.md | 423 | 4 refs (categories, evidence, residual risk, severity) |
| risk-scorer.md | 497 | 6 refs |
| orchestrator.md | 441 | 10 refs |
| threat-infographic.md | 288 | Template-driven |
| threat-report.md | 268 | 4 refs |
| report-assembler.md | 208 | 4 refs |

### Existing Shared References (`.claude/skills/tachi-shared/references/`)

| File | Lines | Currently Used By |
|------|-------|-------------------|
| maestro-layers-shared.md | 213 | orchestrator, risk-scorer, control-analyzer, threat-report |
| stride-categories-shared.md | 146 | orchestrator, control-analyzer |
| finding-format-shared.md | 177 | orchestrator, threat-report |
| severity-bands-shared.md | 110 | risk-scorer, control-analyzer, threat-report |
| **Total** | **646** | **6 infra agents (0 threat agents)** |

---

## Appendix B: Illustrative Example — Spoofing Extraction

**Current spoofing.md (113 lines)**:
- Lines 1-9: Frontmatter (stays)
- Lines 11-26: Metadata YAML (stays, with `model:` added)
- Lines 30-32: Purpose (stays)
- Lines 34-72: Detection scope with 5 pattern categories (→ extract to `tachi-spoofing/references/detection-patterns.md`, enrich to ≥7)
- Lines 73-88: Finding template (→ reference `finding-format-shared.md` with spoofing-specific extension file)
- Lines 90-98: OWASP 3×3 risk matrix (→ reference `severity-bands-shared.md`)
- Lines 100-113: References section (→ extract to `tachi-spoofing/references/citations.md`)

**Target spoofing.md (~60-80 lines)**:
- Frontmatter + metadata + model field
- Purpose narrative (3 sentences)
- `## Skill References` table (4-5 entries)
- `## Phase Workflow` with `**MANDATORY**: Read ...` directives
- `## Output Format` (brief pointer to shared finding format)

**Companion skill — `.claude/skills/tachi-spoofing/references/`**:
- `detection-patterns.md` (~300-500 lines): 7+ pattern categories with industry-specific indicators
- `citations.md` (~50 lines): OWASP/CWE/CAPEC references specific to spoofing
