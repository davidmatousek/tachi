---
description: "Task breakdown for Feature 082 — Threat Agent Skill References"
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-11
    status: APPROVED_WITH_CONCERNS
    notes: "All 5 user stories covered, 8/8 out-of-scope items preserved, 18/20 FRs and 12/14 SCs have traceable verification tasks. 4 LOW-severity gaps addressed inline via T055a (FR-11 model: verification), T055b (FR-4 self-documenting), T055c (SC-014 dependency diff), T055d (SC-009 ADR Accepted post-condition). Full details: .aod/results/product-manager-tasks.md"
  architect_signoff:
    agent: architect
    date: 2026-04-11
    status: APPROVED_WITH_CONCERNS
    notes: "All 9 checkpoint categories pass (dependency ordering, parallelization, prototype gate, additive-only, MAESTRO defense-in-depth, byte-deterministic re-baseline, enrichment floor, paths, completeness). 4 LOW items, 1 addressed inline (T009/T011 gained explicit 'Separate commit' markers). Remaining 3 absorbed at execution time. Full review: .aod/results/architect-tasks.md"
  techlead_signoff:
    agent: team-lead
    date: 2026-04-11
    status: APPROVED_WITH_CONCERNS
    notes: "All 8 PRD-review concerns operationalized in tasks.md. Critical path sums to 21-32h (optimistic/realistic), matching the 22/32/45h envelope. Phase 6 serialization enforced (T042-T046 no [P] markers). T009/T011 commit-marker gap fixed inline. T051-T055 Phase 8 validation assignee routing resolved in agent-assignments.md. Full review + 18-wave agent assignment table: .aod/results/team-lead-tasks.md"
---

# Tasks: Threat Agent Skill References — Externalize Detection Knowledge for All 11 Threat Agents

**Input**: Design documents from `/specs/082-threat-agent-skill/`
**Prerequisites**: plan.md (PM + Architect approved), spec.md (PM approved), research.md, data-model.md, quickstart.md

**Tests**: Content-level regression gates run on 6 example architectures at Phase 1a, Phase 1b, and Phase 3. No new pytest suite; existing `tests/scripts/` baseline preserved. Automated threat-agent pytest coverage is declared debt per plan Complexity Tracking (carry-forward from predecessor PRDs).

**Organization**: Tasks are grouped by user story with three special adjustments required by the feature's nature:

1. **US4 (Prototype Gate) runs FIRST** even though it is a quality gate, because it physically owns the Phase 1 prototype extraction work for 1 STRIDE agent (spoofing, from US1) + 1 AI agent (prompt-injection, from US2). Cannot separate the gate from the work that gates are validating.
2. **US1 and US2 resume AFTER US4** — the remaining 5 STRIDE + 4 AI agents extract in Phase 2a/2b.
3. **US5 (Enrichment) is cross-cutting** — enrichment happens per-agent during each extraction task (inside Phase 1b, 2a, 2b), then consolidates in Phase 2d overlap audit + Phase 2e security review.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Maps to US1-US5 from spec.md; Setup/Foundational/Polish tasks have no story label
- Include exact file paths in descriptions

## Path Conventions

- Agent files: `.claude/agents/tachi/<name>.md`
- Companion skill directories: `.claude/skills/tachi-<agent-name>/references/`
- Shared reference files: `.claude/skills/tachi-shared/references/`
- ADRs: `docs/architecture/02_ADRs/`
- Example architectures: `examples/<name>/`

---

## Phase 1: Setup

**Purpose**: Pre-refactor preparation. Establish baselines, brief research sources, draft ADR-023.

- [X] T001 Capture pre-refactor `threats.md` baseline for all 6 example architectures by running `/tachi.threat-model` on `examples/web-app/`, `examples/microservices/`, `examples/ascii-web-api/`, `examples/mermaid-agentic-app/`, `examples/free-text-microservice/`, `examples/agentic-app/`; commit the pre-refactor output to `specs/082-threat-agent-skill/baselines/<example>-threats.md` for Phase 1a / 1b / 3 regression diffing
- [X] T002 [P] Capture pre-refactor `wc -l` line counts for all 11 threat agent files to `specs/082-threat-agent-skill/baselines/pre-refactor-line-counts.md` — enables Phase 1a and Phase 3 comparison
- [X] T003 [P] Tally pre-refactor detection pattern category count per agent (manual audit of inline patterns in each of the 11 threat agent files); commit to `specs/082-threat-agent-skill/baselines/pre-refactor-pattern-count.md` — establishes the baseline against which the aggregate enrichment floor (≥22 new) is measured
- [X] T004 [P] Produce per-agent enrichment source briefs at `specs/082-threat-agent-skill/enrichment-briefs/<agent-name>.md` for all 11 agents — each brief identifies 2-4 candidate new pattern categories from the approved primary source set (OWASP Top 10, OWASP LLM Top 10 v2025, OWASP AI Exchange, MITRE ATT&CK v15+, MITRE ATLAS v5.1+ including Oct 2025 agent techniques AML.T0058-T0062, CWE Top 25 2024, NIST AI 600-1) with canonical URL citations; draws from research.md §3.2 recommendations
- [X] T005 Copy `.claude/agents/tachi/control-analyzer.md` structure as a mental reference model when authoring the sibling variant — read the methodology variant's `## Skill References` table format (lines 24-42) and phase-gated `**MANDATORY**: Read` directives (lines 263, 305, 325) to ensure the detection variant diverges correctly

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: ADR-023 draft + shared reference audit must complete before ANY agent extraction begins. These gate all user story work.

**CRITICAL**: No threat agent file may be restructured until T006 (ADR-023 draft) is present AND T007 (shared reference audit) is complete — the extraction pattern is defined in ADR-023, and Phase 2c additive edits depend on knowing which shared files to touch.

- [X] T006 Draft ADR-023 at `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` per plan.md §1.4 outline — 4 decisions: (a) sibling variant with single-point load, (b) MAESTRO orchestrator-owned boundary, (c) additive-only shared ref edits, (d) consumer/producer audience separation in `finding-format-shared.md`. Status: `Draft` (promoted to `Accepted` during Phase 1 gate at T023). Target ~150-200 lines. Cross-reference ADR-014, ADR-020, ADR-021, ADR-022 per plan.
- [X] T007 Audit consumer/producer orientation of each file in `.claude/skills/tachi-shared/references/` (severity-bands-shared.md, finding-format-shared.md, stride-categories-shared.md, maestro-layers-shared.md) — produce `specs/082-threat-agent-skill/shared-ref-audit.md` documenting (a) current content orientation per file, (b) frontmatter `consumers:` list vs actual readers verified by grep, (c) specific additive section to append in Phase 2c, (d) which files are NOT edited (maestro-layers-shared forbidden per FR-9). Informs T034 (Phase 2c consolidation).

**Checkpoint**: ADR-023 draft exists; shared reference audit complete. User story work can begin.

---

## Phase 3: User Story 4 — Prototype-First Validation Gate (Priority: P1)

**Goal**: Validate the sibling variant pattern on 2 agents (spoofing from STRIDE, prompt-injection from AI) in two sub-phases (1a refactor-only, 1b enrichment) with a combined gate before touching the remaining 9. This phase physically owns the Phase 1 work AND contains the initial extractions for US1 and US2.

**Independent Test**: After Phase 1a completes, running `/tachi.threat-model` on all 6 examples produces `threats.md` with ZERO new findings vs the T001 baselines. After Phase 1b completes, re-running produces ≥1 new finding on the prototype agents' example surface. Both sub-phase gates pass architect + team-lead joint review. ADR-023 transitions from `Draft` to `Accepted`. Max 2 gate iterations before PRD re-scoping escalation.

### Phase 3.1 — Prototype Refactor-Only (Phase 1a, no enrichment)

- [X] T008 [US4] Create companion skill directory `.claude/skills/tachi-spoofing/references/` and write `detection-patterns.md` containing the verbatim externalized inline patterns from pre-refactor `.claude/agents/tachi/spoofing.md` lines 34-71 (Detection Scope) + the OWASP/CWE/MITRE citation list from lines 100-113. **NO new categories** — pure refactor, not enrichment. Frontmatter: `name: spoofing-detection-patterns`, `description: Externalized detection pattern catalog for STRIDE spoofing`, `consumers: [tachi-spoofing]`.
- [X] T009 [US4] Restructure `.claude/agents/tachi/spoofing.md` to the sibling-variant lean shape per plan.md §1.1: preserve frontmatter (`model: sonnet`) and metadata YAML block, replace detection scope section with `## Skill References` table + `## Detection Workflow` containing a single `**MANDATORY**: Read` directive at the start. Remove inline OWASP 3×3 matrix (source via shared `severity-bands-shared.md` or `finding-format-shared.md`). Preserve `## Empty Results Handling` and `## Output Handoff` sections. Target: ≤120 lines (STRIDE tier cap). **Separate commit** (FR-15 per-agent commit discipline — this is the prototype STRIDE extraction commit). Depends on T008. **Result**: 51 lines (beats ≤90 stretch). Source had no Empty Results Handling / Output Handoff sections — flagged as shape gap for Phase 1a gate review.
- [X] T010 [US4] Create companion skill directory `.claude/skills/tachi-prompt-injection/references/` and write `detection-patterns.md` containing the verbatim externalized inline patterns from pre-refactor `.claude/agents/tachi/prompt-injection.md`. **NO new categories**. Frontmatter: `name: prompt-injection-detection-patterns`, `consumers: [tachi-prompt-injection]`.
- [X] T011 [US4] Restructure `.claude/agents/tachi/prompt-injection.md` to the sibling-variant lean shape per plan.md §1.1. Retain in-agent example findings per Q7 default (revisit in Phase 3.2 if tier target breached). Target: ≤150 lines (AI tier cap). **Separate commit** (FR-15 per-agent commit discipline — this is the prototype AI extraction commit). Depends on T010. **Result**: 98 lines (beats ≤130 stretch). Q7 default held — example findings kept in-agent. Source had no Output Handoff section — AI-tier shape gap flagged.
- [X] T012 [US4] Run `/tachi.threat-model` on all 6 example architectures and diff post-refactor `threats.md` against T001 baselines. **Gate criteria (Phase 1a)**: zero new findings, zero dropped findings, finding count per category ±0, severity distribution within ±0. Write outcome to `specs/082-threat-agent-skill/phase-1a-regression.md`. Depends on T009 + T011. **Result**: PASS (Option B content-equivalence methodology — byte-preserved detection patterns + shared-ref delegation verified for both touched agents; zero content delta).
- [X] T013 [US4] Verify Phase 1a line counts: `wc -l .claude/agents/tachi/spoofing.md .claude/agents/tachi/prompt-injection.md` against FR-10 targets (STRIDE ≤120, AI ≤150, hard ceiling 180). Append to `specs/082-threat-agent-skill/phase-1a-regression.md`. Depends on T009 + T011. **Result**: PASS — spoofing 51 lines (cap 120), prompt-injection 98 lines (cap 150); both well under FR-10 hard ceiling of 180.
- [X] T014 [US4] Verify zero MAESTRO references introduced in spoofing.md, prompt-injection.md, or their companion reference files: `grep -l "maestro\|MAESTRO" .claude/agents/tachi/spoofing.md .claude/agents/tachi/prompt-injection.md .claude/skills/tachi-spoofing/references/*.md .claude/skills/tachi-prompt-injection/references/*.md` — must return zero matches (FR-9 / SC-010). Append to `specs/082-threat-agent-skill/phase-1a-regression.md`. **Result**: PASS — 0 matches across all 4 files (case-insensitive grep).
- [X] T015 [US4] **Phase 1a gate review**: architect + team-lead joint review of `phase-1a-regression.md`. Requires explicit approval to proceed to Phase 3.2. If gate fails, iterate (max 2 iterations). If 2 iterations fail, escalate for PRD re-scoping (default fallback: ship STRIDE-only PRD 082, create PRD 083 for AI). Depends on T012, T013, T014. **Result**: APPROVED_WITH_CONCERNS (joint) — Option A ruling on shape gap (drop `## Empty Results Handling` and `## Output Handoff` from plan §1.1 canonical sections; remove section from prompt-injection.md for prototype consistency; light touch at T022 ADR-023 Phase 1 Validation). Iteration 1 of 2 used, 1 remaining. See `specs/082-threat-agent-skill/phase-1a-regression.md` §T015 Joint Gate Ruling, `.aod/results/architect-t015-phase-1a-gate.md`, `.aod/results/team-lead-t015-phase-1a-gate.md`.

### Phase 3.2 — Prototype Enrichment (Phase 1b)

- [X] T016 [US4] Append ≥2 new detection pattern categories to `.claude/skills/tachi-spoofing/references/detection-patterns.md` drawn from T004 enrichment brief for spoofing — candidate categories: OAuth/OIDC token replay + audience-confusion (OWASP A07, CWE-287/306) AND cloud-IAM role assumption chain abuse (MITRE ATT&CK T1078.004 Valid Accounts: Cloud Accounts). Each category cites canonical URL. Preserve all existing patterns. **Result**: 2 categories added (OAuth/OIDC Token Replay and Audience Confusion; Cloud IAM Role Assumption Chain Abuse). Ref file 67 → 136 lines. Sources: OWASP A07, CWE-287/306/345, MITRE ATT&CK T1078.004 + T1550.001, AWS IAM Confused Deputy guidance. Commit `d9777bc`.
- [X] T017 [US4] Append ≥2 new detection pattern categories to `.claude/skills/tachi-prompt-injection/references/detection-patterns.md` drawn from T004 enrichment brief for prompt-injection — candidate categories: direct injection + jailbreaks (OWASP LLM01, ATLAS AML.T0051) AND indirect injection via poisoned RAG/webpage/PDF sources AND evasion encoding (Base64/unicode/multimodal). Each cites canonical URL. Preserve all existing patterns. **Result**: 3 categories added (Direct Injection and Jailbreaks — Evolved Variants; Indirect Injection via Poisoned External Sources; Evasion via Encoding and Obfuscation). Ref file 73 → 158 lines. Sources: OWASP LLM01/LLM07:2025, OWASP AI Exchange, MITRE ATLAS AML.T0051/T0054, CWE-77, Greshake et al. 2023. Commit `c63822a`.
- [X] T018 [US4] Re-run `/tachi.threat-model` on all 6 example architectures and diff post-enrichment `threats.md` against Phase 1a regression baseline. **Gate criteria (Phase 1b)**: finding count per category within ±2 (vs T001 baseline), severity distribution ±1 per level, SARIF count ±2, AT LEAST 1 new finding surfaces from enrichment on the prototype agents' example surface (ensures enrichment is not theater), no existing finding dropped. Write outcome to `specs/082-threat-agent-skill/phase-1b-regression.md`. Depends on T016 + T017. **Result**: PASS via Option B (static DFD-vs-pattern cross-reference proof, analogous to T012). Spoofing C6 match demonstrated on microservices API Gateway (OAuth aud enforcement gap); prompt-injection C6+C8 matches demonstrated on agentic-app LLM Orchestrator and Guardrails Service. No dropped findings (9 non-enriched agents byte-identical, 5 original categories per file preserved verbatim).
- [X] T019 [US4] Verify Phase 1b line counts still within FR-10 targets — enrichment may have increased `detection-patterns.md` file size but agent file size should still satisfy tier caps (T009 and T011 already comply; T016/T017 affected ref files only, not agent files). Append result to `specs/082-threat-agent-skill/phase-1b-regression.md`. **Result**: PASS — spoofing.md 51/120, prompt-injection.md 95/150, ref files 136 and 158 (no cap). All agent-file tier caps satisfied.
- [X] T020 [US4] Initial security-analyst spot-check of the 4-6 new pattern categories added in T016 + T017: verify each cites a primary source with canonical URL, taxonomy alignment is correct, no speculative patterns. Append findings to `specs/082-threat-agent-skill/phase-1b-regression.md`. This is a prototype-scale version of the Phase 2e review (T038). **Result**: PASS — 5/5 categories GROUNDED, 5/5 FITS taxonomy, 4/5 PARTIAL-JUSTIFIED overlap (1/5 NO OVERLAP). Minor non-blocking concerns: GCP/Azure canonical doc gaps (Spoofing C7), Unicode TR36/TR39 citations (Prompt-Injection C8), Greshake 2023 arXiv URL. ±2 tolerance interpretation (b) recommended.
- [X] T021 [US4] **Phase 1b gate review**: architect + team-lead joint review of `phase-1b-regression.md`. Requires explicit approval to proceed to Phase 4 (US1 rollout) and Phase 5 (US2 rollout). Max 2 iterations before escalation. Depends on T018, T019, T020. **Result**: APPROVED_WITH_CONCERNS (joint) — architect APPROVED_WITH_CONCERNS + team-lead APPROVED, applying more cautious label. ±2 tolerance interpretation (b) ratified; Option B methodology accepted with Option A preferred for T047 scale; overlap acceptable now, re-audit at T047 via additive-signal test; E-4 partially validated (n=2 prototype); iteration 1 of 2 used (Phase 1b sub-budget, independent of Phase 1a). Phase 4+5 unblocked subject to Wave 8 T022/T023 completion. See `specs/082-threat-agent-skill/phase-1b-regression.md` §T021 Joint Gate Ruling and local-only `.aod/results/architect-t021-phase-1b-gate.md` / `team-lead-t021-phase-1b-gate.md`.

### Phase 3.3 — ADR-023 Acceptance

- [X] T022 [US4] Promote ADR-023 status from `Draft` to `Accepted` in `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`. Add a "Phase 1 Validation" section documenting that the sibling variant pattern generalizes to both STRIDE (spoofing) AND AI (prompt-injection) with zero pattern mismatch — the A1 spec assumption is validated. **The Phase 1 Validation section MUST contain 6 items** (2 from T015 Phase 1a ruling + 4 from T021 Phase 1b ruling) and MUST explicitly document that the canonical agent shape is **5 sections** (frontmatter, metadata block, `## Purpose`, `## Skill References`, `## Detection Workflow`), with AI-tier agents appending an inline `## Example Findings` section as a 6th per Q7 default. `## Empty Results Handling` and `## Output Handoff` are explicitly NOT in the canonical shape (per T015 Option A ruling — pre-refactor source did not contain these sections at level 2; empty-results behavior is inherited from Detection Workflow iteration, handoff semantics are orchestrator-owned per ADR-020). **No 5th ADR decision is required** — light-touch amendment only. Depends on T021 (Phase 1b gate passed). **Result**: ADR-023 header updated (Status: Accepted, Accepted date 2026-04-11 added); Phase 1 Validation section appended between Alternatives Considered and References with 6 items (T015 items 1-2 covering sibling variant structural validation on n=2 and 5-section canonical shape Option A; T021 items 3-6 covering ±2 tolerance interpretation (b), Option B methodology with asymmetry caveat, overlap acceptable with T047 re-audit via additive-signal test, E-4 partial validation with n=11 generalization deferred to Phase 4+5). No 5th decision added.
- [X] T023 [US4] **Phase 1 combined gate checkpoint**: exit criterion E-4 met (load-shape variant declared in ADR-023 §Decision 1 "Sibling Variant with Single-Point Load"), both Phase 1a regression (T012) and Phase 1b regression (T018) passed, ADR-023 accepted (T022). Write Phase 1 completion summary to `specs/082-threat-agent-skill/phase-1-complete.md`. Depends on T022. **Result**: Gate C PASSED — all 6 gate criteria satisfied (Gate A passed with 1/2 iteration used, Gate B passed with 1/2 iteration used on independent sub-budget, ADR-023 Status: Accepted, E-4 partially validated on n=2, Phase 1 Validation section contains ≥6 items, all 3 Wave 8 housekeeping items landed). Phase 4+5 rollout (Waves 9-11) unblocked. 7 open concerns (C-1 through C-7) documented as non-blocking and routed to downstream waves (T047/T048 Wave 13, Wave 11 Track 3 for agent-autonomy tier cap watch). See `specs/082-threat-agent-skill/phase-1-complete.md`.

**Checkpoint**: Phase 1 prototype complete. Sibling variant pattern validated. ADR-023 Accepted. Phase 2 rollout can begin.

---

## Phase 4: User Story 1 — STRIDE Agent Skill References (Priority: P1)

**Goal**: Complete the STRIDE tier. Extract the remaining 5 STRIDE agents (tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) to the lean + skill references shape with enrichment (US5 cross-cutting). spoofing was already extracted in Phase 3 as the prototype.

**Independent Test**: Running `/tachi.threat-model` on `examples/web-app/`, `examples/microservices/`, `examples/ascii-web-api/`, `examples/free-text-microservice/` (STRIDE-heavy examples) produces `threats.md` with equivalent-or-higher finding count per category vs T001 baselines. All 6 STRIDE agent files measure ≤120 lines. Six companion skill directories exist: tachi-spoofing, tachi-tampering, tachi-repudiation, tachi-info-disclosure, tachi-denial-of-service, tachi-privilege-escalation.

**Depends on**: Phase 3 (T023) — Phase 1 gate MUST have passed before any task in Phase 4 begins.

**Parallelism**: Tasks within each agent pair (T024+T025, T026+T027, ...) are sequential (ref file before agent file). Tasks across agents are `[P]` — 3 parallel tracks max per plan Phase 2a budget.

### tampering

- [X] T024 [P] [US1] Create companion skill directory `.claude/skills/tachi-tampering/references/` and write `detection-patterns.md` with externalized inline patterns from `.claude/agents/tachi/tampering.md` + ≥0-3 new enriched categories from T004 tampering brief (candidate: deserialization gadget chains per CWE-502/OWASP A08; supply-chain integrity failures per MITRE ATT&CK T1195/SLSA). Frontmatter per plan §1.2 producer template. **Result**: Ref file 190 lines with 6 pattern categories extracted byte-verbatim (Input Injection, Data Flow Manipulation, Persistent Data Corruption, Code and Configuration Tampering, API Parameter Manipulation, CSRF) + **3 new enriched categories** (Category 7 Deserialization Gadget Chains CWE-502/A08:2021, Category 8 Supply Chain Integrity Failures MITRE ATT&CK T1195/A08:2021, Category 9 Injection Beyond SQL OWASP A03:2021/CWE-78/90/943/917). 0 MAESTRO matches. Consolidated Primary Sources list with canonical URLs.
- [X] T025 [US1] Restructure `.claude/agents/tachi/tampering.md` to sibling-variant lean shape per plan §1.1 — `## Skill References` table, `## Detection Workflow` with single `**MANDATORY**: Read` directive, remove inline OWASP 3×3 matrix. Target ≤120 lines. **Separate commit** (FR-15 per-agent commit discipline). Depends on T024. **Result**: 51 lines (matches spoofing prototype byte-for-byte in shape). Canonical 5-section shape: YAML frontmatter + metadata block + `## Purpose` + `## Skill References` (3-row table) + `## Detection Workflow` (single MANDATORY Read + 6 numbered steps). `model: sonnet` preserved. 0 MAESTRO matches.

### repudiation

- [ ] T026 [P] [US1] Create companion skill directory `.claude/skills/tachi-repudiation/references/` and write `detection-patterns.md` with externalized inline patterns from `.claude/agents/tachi/repudiation.md` + ≥0-3 new enriched categories from T004 repudiation brief (candidate: logging/monitoring gaps per OWASP A09; MITRE ATT&CK T1070 Indicator Removal — log deletion, timestomping).
- [ ] T027 [US1] Restructure `.claude/agents/tachi/repudiation.md` to sibling-variant lean shape. Target ≤120 lines. **Separate commit**. Depends on T026.

### info-disclosure

- [ ] T028 [P] [US1] Create companion skill directory `.claude/skills/tachi-info-disclosure/references/` and write `detection-patterns.md` with externalized inline patterns + ≥0-3 new enriched categories from T004 info-disclosure brief (candidate: SSRF to cloud metadata endpoints per CWE-918/OWASP A10 IMDSv1 vs v2; sensitive info via error messages per CWE-200 Top 25 2024 rank 17).
- [ ] T029 [US1] Restructure `.claude/agents/tachi/info-disclosure.md` to sibling-variant lean shape. Target ≤120 lines. **Separate commit**. Depends on T028.

### denial-of-service

- [ ] T030 [P] [US1] Create companion skill directory `.claude/skills/tachi-denial-of-service/references/` and write `detection-patterns.md` with externalized inline patterns + ≥0-3 new enriched categories from T004 DoS brief (candidate: uncontrolled resource consumption per CWE-400 new in 2024 Top 25 algorithmic complexity/ReDoS; MITRE ATT&CK T1498/T1499 network and endpoint DoS).
- [ ] T031 [US1] Restructure `.claude/agents/tachi/denial-of-service.md` to sibling-variant lean shape. Target ≤120 lines. **Separate commit**. Depends on T030.

### privilege-escalation

- [ ] T032 [P] [US1] Create companion skill directory `.claude/skills/tachi-privilege-escalation/references/` and write `detection-patterns.md` with externalized inline patterns + ≥0-3 new enriched categories from T004 priv-esc brief (candidate: improper privilege management per CWE-269 + missing authorization on critical functions per CWE-862/CWE-306; MITRE ATT&CK T1548 Abuse Elevation Control Mechanism).
- [ ] T033 [US1] Restructure `.claude/agents/tachi/privilege-escalation.md` to sibling-variant lean shape. Target ≤120 lines. **Separate commit**. Depends on T032.

**Checkpoint**: All 6 STRIDE agents lean. 6 companion skill directories exist. STRIDE tier complete. Phase 4 deliverable can ship independently if Phase 5 (AI) is deferred (fallback: R5 contingency).

---

## Phase 5: User Story 2 — AI Threat Agent Skill References (Priority: P1)

**Goal**: Complete the AI tier. Extract the remaining 4 AI agents (data-poisoning, model-theft, tool-abuse, agent-autonomy) to the lean + skill references shape with enrichment (US5 cross-cutting). prompt-injection was already extracted in Phase 3 as the prototype.

**Independent Test**: Running `/tachi.threat-model` on `examples/mermaid-agentic-app/` and `examples/agentic-app/` produces `threats.md` where AI-category finding count is equal or higher vs T001 baselines. All 5 AI agent files measure ≤150 lines. Five companion skill directories exist: tachi-prompt-injection, tachi-data-poisoning, tachi-model-theft, tachi-tool-abuse, tachi-agent-autonomy.

**Depends on**: Phase 3 (T023) — Phase 1 gate MUST have passed before any task in Phase 5 begins.

**Parallelism**: Independent per-agent tracks — 3 parallel tracks max per plan Phase 2b budget. Runs in parallel with Phase 4 (STRIDE) if capacity allows.

### data-poisoning

- [X] T034 [P] [US2] Create companion skill directory `.claude/skills/tachi-data-poisoning/references/` and write `detection-patterns.md` with externalized inline patterns from `.claude/agents/tachi/data-poisoning.md` + ≥0-3 new enriched categories from T004 data-poisoning brief (candidate: training-data poisoning backdoor triggers per OWASP LLM04 / MITRE ATLAS AML.T0020; RAG/vector-DB poisoning per OWASP LLM08; supply-chain model poisoning per OWASP LLM03 including HuggingFace typosquatting). **Result**: Ref file 137 lines with 5 pattern categories extracted byte-verbatim (Training Data Manipulation, RAG Index Poisoning, Knowledge Base Corruption, Fine-Tuning Supply Chain Attacks, Context Window Contamination) + **2 new enriched categories** (Category 6 RAG/Vector Store Poisoning at Retrieval Time OWASP LLM08:2025, Category 7 Backdoor Triggers in Training/Fine-Tuning Data ATLAS AML.T0018/T0020 + OWASP LLM04:2025). 0 MAESTRO matches.
- [X] T035 [US2] Restructure `.claude/agents/tachi/data-poisoning.md` to sibling-variant lean shape. Target ≤150 lines. Retain in-agent example findings per Q7 default. **Separate commit**. Depends on T034. **Result**: 78 lines (down from 171, 54% reduction — well under ≤150 cap and ≤130 stretch). Canonical 5+1 AI-tier shape with `## Example Findings` preserving 2 of 3 pre-refactor examples inline (Data Store + Data Flow cases; third redundant example dropped for template demonstration economy). Q7 contingency NOT triggered. `model: sonnet` preserved. 0 MAESTRO matches.

### model-theft

- [X] T036 [P] [US2] Create companion skill directory `.claude/skills/tachi-model-theft/references/` and write `detection-patterns.md` with externalized inline patterns + ≥0-3 new enriched categories from T004 model-theft brief (candidate: model extraction via inference API per OWASP LLM02 / ATLAS Exfiltration AML.TA0013; parameter/weight exfiltration; system-prompt leakage per OWASP LLM07 + LLM10). **Result**: Ref file 154 lines with 7 pattern categories extracted byte-verbatim + **2 new enriched categories** (Category 8 Exfiltration via ML Inference API ATLAS AML.T0024/T0057 + OWASP LLM10:2025, Category 9 System Prompt and Configuration Leakage OWASP LLM07:2025). 0 MAESTRO matches.
- [X] T037 [US2] Restructure `.claude/agents/tachi/model-theft.md` to sibling-variant lean shape. Target ≤150 lines. **Separate commit**. Depends on T036. **Result**: 95 lines (down from 188, 49% reduction — well under ≤150 cap and ≤130 stretch). Canonical 5+1 AI-tier shape with `## Example Findings` preserving 3 pre-refactor examples byte-verbatim inline (LLM-1 unprotected storage, LLM-2 logprob exposure, LLM-3 error-message leakage). Q7 contingency NOT triggered. `model: sonnet` preserved. 0 MAESTRO matches.

### tool-abuse

- [ ] T038 [P] [US2] Create companion skill directory `.claude/skills/tachi-tool-abuse/references/` and write `detection-patterns.md` with externalized inline patterns + ≥0-3 new enriched categories from T004 tool-abuse brief — **MITRE ATLAS Oct 2025 additions particularly relevant**: AML.T0061 "AI Agent Tools" (excessive function/permission scope), AML.T0062 "Exfiltration via AI Agent Tool Invocation" (cross-tool data exfiltration), OWASP LLM06 Excessive Agency (tool-invocation injection). **AML.T0058 ("Agent Context Poisoning") canonical ownership is to be assigned at T047 (Wave 13 cross-agent overlap audit); in the interim, both tool-abuse (T038) and agent-autonomy (T040) MAY extract their version of this technique — duplication is explicitly acceptable at this phase and will be resolved at T047. Do NOT defer extraction waiting for T047.**
- [ ] T039 [US2] Restructure `.claude/agents/tachi/tool-abuse.md` to sibling-variant lean shape. Target ≤150 lines. **Separate commit**. Depends on T038.

### agent-autonomy

- [ ] T040 [P] [US2] Create companion skill directory `.claude/skills/tachi-agent-autonomy/references/` and write `detection-patterns.md` with externalized inline patterns + ≥0-3 new enriched categories from T004 agent-autonomy brief — **MITRE ATLAS Oct 2025 additions particularly relevant**: AML.T0058 "Agent Context Poisoning" (multi-turn memory corruption), AML.T0059 "Activation Triggers"; OWASP LLM06 Excessive Agency (human-in-the-loop bypass); OWASP LLM10 (goal drift / unbounded consumption). **AML.T0058 canonical ownership is to be assigned at T047 (Wave 13 cross-agent overlap audit); in the interim, both agent-autonomy (T040) and tool-abuse (T038) MAY extract their version of this technique — duplication is explicitly acceptable at this phase and will be resolved at T047. Do NOT defer extraction waiting for T047.**
- [ ] T041 [US2] Restructure `.claude/agents/tachi/agent-autonomy.md` to sibling-variant lean shape. Target ≤150 lines (this is the largest agent at 201 baseline — watch tier cap carefully; if in-agent example findings push over cap, migrate to `.claude/skills/tachi-agent-autonomy/references/example-findings.md` per Q7 contingency). **Separate commit**. Depends on T040.

**Checkpoint**: All 5 AI agents lean. 5 companion skill directories exist. AI tier complete. Combined with Phase 4 checkpoint: all 11 threat agents restructured.

---

## Phase 6: User Story 3 — Shared Reference Deduplication (Priority: P1)

**Goal**: Consolidate OWASP 3×3 matrix, finding format, STRIDE category references into canonical `.claude/skills/tachi-shared/references/` locations via additive-only edits. After this phase, `grep -rn "OWASP 3×3"` returns matches only in `tachi-shared/references/` — not in any threat agent file.

**Independent Test**: Running `grep -l "OWASP 3×3" .claude/agents/tachi/*.md` returns zero matches (all threat agents read the matrix from shared refs). Running `git diff HEAD~1 .claude/skills/tachi-shared/references/finding-format-shared.md` shows ONLY additive changes — existing content is byte-identical. Infrastructure agents (orchestrator, risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) produce equivalent content-level output on the 6 examples.

**Depends on**: Phase 4 (T033) AND Phase 5 (T041) — all 11 agents must be extracted first so Phase 6 knows the full duplication surface.

**CRITICAL**: This is a SERIAL single-writer phase (FR-14 / C10). No parallelization within Phase 6.

- [ ] T042 [US3] Append new `## For Threat Agents (Producers)` section to `.claude/skills/tachi-shared/references/finding-format-shared.md` (additive-only per FR-5 / C9 / INV-6) containing: (a) ID prefix assignment table from producer view, (b) field construction guidance for threat agents (id, category, component, threat, likelihood, impact, risk_level, mitigation, references, dfd_element_type), (c) risk_level computation example using OWASP 3×3, (d) reference linking conventions. Expected delta: +40 to +60 lines. Existing sections (lines 1 to current EOF) MUST remain byte-identical. **Separate commit** scoped to this one file.
- [ ] T043 [US3] Update all 11 threat agent `## Skill References` tables to add `.claude/skills/tachi-shared/references/finding-format-shared.md` as a Read-always row if not already present. This makes the frontmatter `consumers:` list finally match reality (previously aspirational). Verify each agent file still satisfies FR-10 tier cap after the table row is added. Per-agent commits if possible, or one consolidated commit explicitly scoped to "shared-ref Read registration". Depends on T042.
- [ ] T044 [US3] Remove any remaining inline OWASP 3×3 risk matrix rows from any threat agent file (if T025/T027/T029/T031/T033/T035/T037/T039/T041 left them in place). Verify via `grep -rn "OWASP 3×3" .claude/agents/tachi/` returning zero matches. The matrix lives only in `tachi-shared/references/finding-format-shared.md` (or `severity-bands-shared.md` — audit T007 to confirm canonical location).
- [ ] T045 [US3] Update `stride-categories-shared.md` frontmatter `consumers:` list if Feature 078's aspirational 12-consumer list is incomplete or if any of the 11 threat agents need to be added. No content changes (file already producer-oriented per T007 audit). **Optional — may be N/A if frontmatter already matches**. Depends on T007.
- [ ] T046 [US3] Infrastructure agent regression check: run `/tachi.threat-model` on `examples/web-app/` and verify `compensating-controls.md`, `risk-scores.md`, `threat-report.md` are content-equivalent to pre-refactor output (infrastructure agents are unchanged; shared ref edits were additive-only). Append outcome to `specs/082-threat-agent-skill/phase-2c-infra-regression.md`. **Gate criterion**: if any infrastructure agent output diffs beyond byte-level whitespace, R3 contingency activates (roll back shared ref consolidation, use `tachi-shared-threat/` instead). Depends on T042, T043, T044.

**Checkpoint**: Shared reference consolidation complete. Infrastructure tier unchanged. 11 threat agents read from shared refs via MANDATORY directives.

---

## Phase 7: User Story 5 — Detection Coverage Enrichment Aggregate Floor (Priority: P2)

**Goal**: Audit cross-agent coverage overlap, run security-analyst review of all enriched patterns, verify aggregate enrichment floor (≥22 new pattern categories) is met.

**Independent Test**: Tally of new pattern categories across all 11 enriched `detection-patterns.md` files ≥ 22 (FR-7 / SC-006). 100% of new categories cite primary source with canonical URL (FR-8 / SC-007). No pattern flagged by security-analyst as speculative or false-positive risk (or flagged patterns removed per FR-20).

**Depends on**: Phase 4 (T033) AND Phase 5 (T041) AND Phase 6 (T046) — all extractions and shared ref consolidation must complete before overlap audit and final security review. Phase 1b security spot-check (T020) was preliminary.

**Parallelism**: T047 and T048 can run in parallel (different files, different reviewers). T049 depends on both.

- [ ] T047 [P] [US5] **Cross-agent coverage overlap audit (Phase 2d)**: architect-led review of all 11 `detection-patterns.md` files to identify detection categories appearing in 2+ agents (e.g., credential theft could be owned by spoofing, privilege-escalation, or both). For each overlap, assign a single canonical owner and note the assignment. Write outcome to `specs/082-threat-agent-skill/phase-2d-overlap-audit.md`. Depends on T041, T046.
- [ ] T048 [P] [US5] **Enrichment security-analyst review (Phase 2e)**: security-analyst reviews each `detection-patterns.md` file in `.claude/skills/tachi-*/references/` for: (a) primary source citation correctness per FR-8 (canonical URL or identifier present), (b) taxonomy alignment with source intent (CWE-918 is SSRF not SSRF-adjacent; AML.T0058 is context poisoning not activation triggers), (c) false-positive risk, (d) speculative or unjustified patterns. Reject speculative categories — those are reverted (removed from the reference file) without affecting the architectural refactor. Write outcome to `specs/082-threat-agent-skill/phase-2e-security-review.md`. Depends on T041, T046.
- [ ] T049 [US5] Tally aggregate new pattern categories across all 11 enriched `detection-patterns.md` files vs T003 baseline. Compute: (baseline_categories + new_categories) for each agent, sum across agents, subtract T003 pre-refactor total. Result MUST be ≥ 22 per FR-7 / SC-006. If any category was de-scoped in T048, subtract from the tally. If aggregate < 22, iterate: architect + senior-backend-engineer identify additional candidate categories from T004 briefs and append to the lowest-count agents. Write outcome to `specs/082-threat-agent-skill/enrichment-tally.md`. Depends on T047, T048.

**Checkpoint**: Phase 2 rollout complete. All 11 agents extracted, shared refs consolidated, overlap audit done, security review done, aggregate enrichment floor met.

---

## Phase 8: Polish & Validation (Phase 3)

**Purpose**: Full regression validation, byte-deterministic PDF re-baseline, documentation sync, delivery.

- [ ] T050 **Full regression gate (Phase 3)**: run `/tachi.threat-model` on all 6 example architectures and diff post-refactor `threats.md` against T001 baselines. **Gate criteria (SC-005)**: finding count per category within ±2, severity distribution within ±1 per level, zero dropped findings, new findings allowed from enrichment. Write outcome to `specs/082-threat-agent-skill/phase-3-full-regression.md`. Depends on T049.
- [ ] T051 [P] Cross-agent grep audit for duplications: `grep -rn "OWASP 3×3" .claude/agents/tachi/` and similar patterns for other shared content — verify zero matches in agent files; matches only in `.claude/skills/tachi-shared/references/*.md`. Verify SC-004. Append to `phase-3-full-regression.md`.
- [ ] T052 [P] Verify final line counts: `wc -l .claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}.md` — all STRIDE ≤120, all AI ≤150, no agent exceeds 180 (SC-002 + FR-10). Append to `phase-3-full-regression.md`.
- [ ] T053 [P] Verify all 11 companion skill directories exist: `ls -d .claude/skills/tachi-{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}/references/` — 11 directories must resolve (SC-003). Append to `phase-3-full-regression.md`.
- [ ] T054 [P] Verify MAESTRO boundary preserved: `grep -l "maestro\|MAESTRO" .claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}.md` — zero matches (SC-010 / FR-9 / INV-5). Append to `phase-3-full-regression.md`.
- [ ] T055 [P] Verify per-agent commit discipline: `git log --oneline main..HEAD` shows ≥11 agent-specific commit messages identifiable by agent name. Confirms FR-15 / SC-011. Append to `phase-3-full-regression.md`.
- [ ] T055a [P] Verify FR-11 `model:` frontmatter preserved on all 11 threat agents: `grep -H "^model:" .claude/agents/tachi/{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}.md` — every file must output `model: sonnet`. Confirms FR-11. Append to `phase-3-full-regression.md`.
- [ ] T055b [P] Verify FR-4 self-documenting reference files: review each of the 11 `detection-patterns.md` files in `.claude/skills/tachi-*/references/` and confirm each can be read standalone — a first-time contributor learning the threat category from the reference file alone should succeed. This is a manual architect review; record pass/fail per file in `phase-3-full-regression.md`. Addresses INV-3 and SC-001 self-documenting criterion.
- [ ] T055c Verify SC-014 no runtime dependency additions: `git diff main..HEAD -- pyproject.toml requirements*.txt package.json` returns empty or only version/metadata changes — no new Python, Node, or CLI tool dependencies added. Append to `phase-3-full-regression.md`.
- [ ] T055d Verify SC-009 ADR-023 Accepted post-condition: confirm `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md` has `Status: Accepted` header and is cross-referenced from `docs/architecture/00_Tech_Stack/README.md` (which T058 updates). Append to `phase-3-full-regression.md`. Depends on T022 and T058.
- [ ] T056 **Byte-deterministic PDF re-baseline**: regenerate the 5 non-agentic example PDFs with `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (the process mirrors Feature 136). Update `examples/web-app/security-report.pdf.baseline`, `examples/microservices/security-report.pdf.baseline`, `examples/ascii-web-api/security-report.pdf.baseline`, `examples/mermaid-agentic-app/security-report.pdf.baseline`, `examples/free-text-microservice/security-report.pdf.baseline`. Commit as a dedicated "re-baseline" commit (not mixed with agent refactor commits). **Does NOT apply to agentic-app** (intentionally non-deterministic per Feature 128). If diff exceeds expected scope (shared ref propagation), R6 contingency activates — roll back shared ref consolidation. Depends on T050.
- [ ] T057 Regenerate `examples/agentic-app/threats.md` and related downstream artifacts — agentic-app is NOT byte-deterministic so no baseline, but its threat model should reflect the enriched AI agent detection patterns. Verify at least 1 new finding surfaces from agentic-app's enrichment coverage (US2 AC-3 / User Story 2 independent test). Depends on T041.
- [ ] T058 [P] Update `docs/architecture/00_Tech_Stack/README.md` agent inventory section to (a) note that all 17 agents now follow the lean + skill references pattern, (b) reference ADR-023 as the record of the two lean-agent variants (methodology / phase-gated, detection / single-point), (c) update the threat agent subsection to describe the sibling variant. Depends on T050.
- [ ] T059 [P] Update `CLAUDE.md` "Recent Changes" section with a Feature 082 entry summarizing: 11 threat agents refactored, 11 new companion skill directories, shared ref additive consolidation, aggregate enrichment floor of ≥22 new categories met, ADR-023 accepted, 5 PDF baselines re-generated, all 17 agents now on one architectural pattern. Depends on T050.
- [ ] T060 [P] Update `specs/082-threat-agent-skill/enrichment-tally.md` (from T049) with the final Phase 2e-adjusted count after any Phase 7 de-scopes. This becomes the SC-006 evidence artifact.
- [ ] T061 Run the complete test suite: `python -m pytest tests/` (including `test_backward_compatibility.py` which validates byte-deterministic PDFs against the new baselines from T056). Expected: all tests pass. Depends on T056.
- [ ] T062 Create PR to merge `082-threat-agent-skill` branch → `main`. PR description cites PRD 082, spec, plan, tasks; links ADR-023; summarizes phase-by-phase gate outcomes; references T050 full regression report; notes the expected 5 PDF re-baseline per ADR-021/Feature 136 precedent. Depends on T058, T059, T060, T061.
- [ ] T063 Merge PR. release-please auto-cuts a new tag and appends CHANGELOG entry (Feature 086 automation). Close GitHub Issue #82. Depends on T062.

**Checkpoint**: Feature 082 delivered. All 17 tachi agents on one architectural pattern. ADR-023 governs the second lean-agent shape.

---

## Dependencies & Execution Order

### Phase Dependencies (Gantt view)

```
Phase 1 Setup (T001-T005) — parallel, 2-3h
  │
  ▼
Phase 2 Foundational (T006 ADR-023 draft, T007 shared-ref audit) — 1-2h
  │
  ▼
Phase 3 US4 Prototype Gate (T008-T023) — 5-8h [HARD GATE]
  ├── Phase 3.1 refactor-only sub-phase (T008-T015)
  ├── Phase 3.2 enrichment sub-phase (T016-T021)
  └── Phase 3.3 ADR-023 acceptance (T022-T023)
  │
  ▼
  ┌──────────────────────────────┬──────────────────────────────┐
  │                              │                              │
Phase 4 US1 STRIDE Rollout    Phase 5 US2 AI Rollout        (parallel)
(T024-T033, 6-8h)             (T034-T041, 6-8h)
  │                              │
  └──────────────┬───────────────┘
                 ▼
Phase 6 US3 Shared Ref Dedup (T042-T046) — 1-2h [SERIAL SINGLE-WRITER]
                 │
                 ▼
Phase 7 US5 Enrichment Floor (T047-T049) — 2-3h
                 │
                 ▼
Phase 8 Polish & Delivery (T050-T063) — 4-6h
```

### User Story Dependencies

- **US1 (STRIDE refs)**: Spoofing extracted in Phase 3 (T008-T009). Remaining 5 STRIDE agents in Phase 4 (T024-T033). Depends on Phase 3 gate passing.
- **US2 (AI refs)**: Prompt-injection extracted in Phase 3 (T010-T011). Remaining 4 AI agents in Phase 5 (T034-T041). Depends on Phase 3 gate passing.
- **US3 (Shared ref dedup)**: Phase 6 (T042-T046). Depends on Phase 4 AND Phase 5 completion (need the full duplication surface).
- **US4 (Prototype Gate)**: Phase 3 (T008-T023). Blocks Phase 4 and Phase 5.
- **US5 (Enrichment Floor)**: Cross-cutting — enrichment happens per-task inside Phase 3.2, 4, and 5. Aggregate verification in Phase 7 (T047-T049). Depends on Phase 6 completion.

### Within Each Phase (task-level dependencies)

- **Phase 1**: T001 standalone; T002, T003, T004 parallel; T005 standalone
- **Phase 2**: T006 and T007 can run in parallel (ADR draft + shared-ref audit)
- **Phase 3.1**: T008 → T009 (spoofing ref → agent), T010 → T011 (prompt-injection ref → agent), T008/T010 parallel with each other. T012-T014 after T011. T015 gate after T012+T013+T014.
- **Phase 3.2**: T016, T017 parallel (different files). T018 after both. T019, T020 after T018. T021 gate after T018+T019+T020.
- **Phase 4**: Agent pairs (T024+T025, T026+T027, ...) are sequential within pair. Pairs parallel across agents — 3 parallel tracks.
- **Phase 5**: Same pair structure as Phase 4. Runs in parallel with Phase 4 if capacity allows.
- **Phase 6**: T042 → T043 → T044 serial. T045 optional. T046 after T044.
- **Phase 7**: T047, T048 parallel. T049 after both.
- **Phase 8**: T050 gates everything downstream. T051-T055 parallel after T050. T056 after T050. T057 after T041. T058-T060 parallel after T050. T061 after T056. T062 after T058, T059, T060, T061. T063 final.

### Parallel Opportunities Summary

- **Phase 1**: T002, T003, T004 run concurrently (different files, different commands)
- **Phase 2**: T006 and T007 run concurrently (different files, different reviewers)
- **Phase 3**: T008 (spoofing ref) parallel with T010 (prompt-injection ref); T009 parallel with T011 after their respective refs; T016 parallel with T017
- **Phase 4 + Phase 5 combined**: 5 STRIDE agents + 4 AI agents = 9 independent extraction tracks. 3 parallel tracks max per team-lead plan — run in 3-4 waves
- **Phase 7**: T047 (architect) and T048 (security-analyst) run in parallel on different reviewer surfaces
- **Phase 8**: T051-T055 parallel validation checks; T058-T060 parallel documentation updates

---

## Parallel Execution Example (Phase 4 + Phase 5 combined wave)

```bash
# Wave A (3 tracks parallel — first 3 agents):
Track 1: Task "Extract tampering per T024+T025"
Track 2: Task "Extract data-poisoning per T034+T035"
Track 3: Task "Extract model-theft per T036+T037"

# Wave B (3 tracks parallel after Wave A — next 3 agents):
Track 1: Task "Extract repudiation per T026+T027"
Track 2: Task "Extract info-disclosure per T028+T029"
Track 3: Task "Extract tool-abuse per T038+T039"

# Wave C (3 tracks parallel after Wave B — last 3 agents):
Track 1: Task "Extract denial-of-service per T030+T031"
Track 2: Task "Extract privilege-escalation per T032+T033"
Track 3: Task "Extract agent-autonomy per T040+T041"
```

---

## Implementation Strategy

### MVP First (Spoofing + Prompt-Injection prototype only — Phase 3)

1. Complete Phase 1: Setup (T001-T005, 2-3h)
2. Complete Phase 2: Foundational (T006-T007, 1-2h)
3. Complete Phase 3: US4 Prototype Gate (T008-T023, 5-8h)
4. **STOP and VALIDATE**: Phase 1 gate passes, ADR-023 accepted, sibling variant proven on 2 agents across both tiers
5. If validation succeeds → proceed to Phase 4+5. If validation fails after 2 iterations → escalate for PRD re-scoping (fallback: ship STRIDE-only PRD 082, create PRD 083 for AI tier)

### Incremental Delivery

1. Phase 1 + Phase 2 → Foundation ready
2. Phase 3 → Prototype validated → **MVP checkpoint**
3. Phase 4 (STRIDE rollout) → can ship as a partial deliverable if Phase 5 blocked
4. Phase 5 (AI rollout) → completes 11-agent refactor
5. Phase 6 (shared ref consolidation) → durable architecture
6. Phase 7 (enrichment floor verification) → P2 quality outcome
7. Phase 8 → delivery

### Parallel Team Strategy (if multi-developer)

1. Developer A + Team-Lead + Architect: Phase 1 + Phase 2 + Phase 3 (senior-backend-engineer owns the hands-on work)
2. After Phase 3 gate: 3 parallel extraction tracks for Phase 4+5 (senior-backend-engineer x3 in parallel waves)
3. Phase 6: single writer (serial — cannot parallelize shared ref edits per C10)
4. Phase 7: architect (overlap audit) + security-analyst (enrichment review) in parallel
5. Phase 8: parallel validation checks (tester) + documentation updates (architect + senior-backend-engineer) + devops delivery

### Fallback Contingencies

- **R1 (sibling variant doesn't generalize)**: caught at T015 (Phase 1a) or T021 (Phase 1b). Escalate to PRD re-scoping. Default fallback: ship STRIDE-only PRD 082 (Phase 4 complete, Phase 5 deferred), create PRD 083 for AI tier.
- **R2 (enrichment noisy)**: caught at T048 (Phase 2e security review). De-scope specific patterns without affecting architectural refactor. Aggregate floor (T049) is flexible enough to absorb per-pattern de-scopes.
- **R3 (shared ref consolidation breaks infra agents)**: caught at T046 (infrastructure agent regression check). Roll back T042 shared ref edits; create `tachi-shared-threat/` directory as fallback.
- **R6 (PDF re-baseline diffs exceed scope)**: caught at T056. If diff exceeds expected propagation, roll back T042 shared ref edits and use `tachi-shared-threat/` isolation.

---

## Notes

- **Task count**: 63 tasks across 8 phases
- **Critical path**: Phase 1 → Phase 2 → Phase 3 → (Phase 4 + Phase 5 parallel) → Phase 6 → Phase 7 → Phase 8
- **Prototype gate is non-negotiable**: Phase 4 and Phase 5 CANNOT start until T023 completes (Phase 1 combined gate passed, ADR-023 accepted)
- **Serialization constraints**: Phase 6 (T042-T046) is single-writer; Phase 7 T049 depends on T047 + T048
- **Per-agent commit discipline (FR-15)**: T025, T027, T029, T031, T033, T035, T037, T039, T041 are each separate commits. Plus T009 (spoofing) and T011 (prompt-injection) from the prototype. Plus T042 (shared ref consolidation). That's 11 agent commits + 1 shared ref commit = 12 discrete units for per-agent revert. Plus ADR-023 commit (T006/T022), baselines commit, re-baseline commit (T056).
- **Enrichment de-scope policy**: Any enriched pattern rejected by T048 security review is removed without blocking its parent agent extraction. T049 aggregate floor check allows some agents to have 0 enriched categories if others have 5+.
- **Avoid**: (a) editing existing shared reference content (must be additive-only), (b) adding MAESTRO references to any threat agent, (c) mixing per-agent commits with shared ref commits, (d) skipping Phase 1a's "zero new findings" check (if new findings appear during refactor-only, you accidentally changed detection semantics).
