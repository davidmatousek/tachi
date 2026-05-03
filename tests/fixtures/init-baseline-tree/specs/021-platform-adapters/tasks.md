---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-23
    status: APPROVED
    notes: "All 5 user stories covered, 10/10 FRs traceable, no scope creep, P0/P1 phasing correct, VERSION and README tasks present for all 5 adapters, output parity validation present."
  architect_signoff:
    agent: architect
    date: 2026-03-23
    status: APPROVED_WITH_CONCERNS
    notes: "Dependencies correctly ordered, parallel opportunities well identified, transformation rules match plan. Concerns: Copilot path depth corrected to 3 levels (M1 fixed), instructions file naming aligned (M2 noted), copilot/instructions/ added to T001 skeleton (L1 fixed)."
  techlead_signoff:
    agent: team-lead
    date: 2026-03-23
    status: APPROVED_WITH_CONCERNS
    notes: "Feasible timeline ~7h total (3h Sprint 1, 3h Sprint 2, 1h Polish). 7 parallel waves, 14/40 tasks parallelizable, 65% parallel capacity. Concerns: T003/T004 must be sequential (same file), Copilot instructions mechanism needs validation in T024, T032 is highest-complexity task."
---

# Tasks: Platform Adapters

**Input**: Design documents from `/specs/021-platform-adapters/`
**Prerequisites**: plan.md (required), spec.md (required), research.md

**Tests**: Not explicitly requested in spec. Manual verification via content comparison and output parity testing.

**Organization**: Tasks grouped by user story (5 adapters). P0 adapters (Claude Code, Generic) in Phases 3-4. P1 adapters (Cursor, Copilot, GitHub Actions) in Phases 5-7.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create adapter directory structure and shared tooling

- [X] T001 Create adapter directory skeleton: `adapters/claude-code/agents/`, `adapters/generic/prompts/`, `adapters/cursor/rules/`, `adapters/copilot/agents/`, `adapters/copilot/instructions/`, `adapters/github-actions/`
- [X] T002 Create VERSION file generation script at `scripts/generate-adapter-version.sh` that computes Git commit SHA and SHA-256 checksums for all files in `agents/` and outputs VERSION YAML format

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared conventions used by all file-transformation adapters

**CRITICAL**: All file-transformation adapters (US1, US3, US4) depend on these conventions being finalized

- [X] T003 Document the shared `## Metadata` YAML code block format for relocating tachi frontmatter fields (`category`, `threat_class`, `dfd_targets`, `owasp_references`, `output_schema`) into the markdown body — write convention to `specs/021-platform-adapters/conventions.md`
- [X] T004 Document path rewriting rules per platform (Claude Code: 3 levels up, Cursor: 3 levels up, Copilot: 4 levels up, sibling agent references become flat) — append to `specs/021-platform-adapters/conventions.md`

**Checkpoint**: Shared conventions finalized — adapter implementation can begin

---

## Phase 3: User Story 1 — Claude Code Native Installation (Priority: P0) MVP

**Goal**: Map all 14 agents into `.claude/agents/tachi/` format with Claude Code frontmatter, supporting parallel dispatch via Agent tool

**Independent Test**: Copy `adapters/claude-code/agents/` to a project's `.claude/agents/tachi/`, invoke the orchestrator, verify all threat agents dispatch and produce valid `threats.md`

### Implementation for User Story 1

- [X] T005 [US1] Transform orchestrator agent: replace tachi frontmatter with Claude Code `name`/`description`, rewrite `references.agents` paths to flat sibling references (e.g., `agents/stride/spoofing.md` → `spoofing.md`), rewrite schema/template paths to `../../../schemas/` and `../../../templates/`, add `## Metadata` section — write to `adapters/claude-code/agents/orchestrator.md`
- [X] T006 [P] [US1] Transform 6 STRIDE agents (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation): replace frontmatter with `name: tachi-{agent_name}` and auto-generated `description`, add `## Metadata` section, rewrite path references — write to `adapters/claude-code/agents/{agent-name}.md`
- [X] T007 [P] [US1] Transform 5 AI agents (prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse): same transformation as T006 — write to `adapters/claude-code/agents/{agent-name}.md`
- [X] T008 [P] [US1] Transform 2 report agents (threat-report, threat-infographic): replace frontmatter with Claude Code `name`/`description`, add `## Metadata` section, rewrite path references — write to `adapters/claude-code/agents/{agent-name}.md`
- [X] T009 [US1] Generate VERSION file for Claude Code adapter using `scripts/generate-adapter-version.sh` — write to `adapters/claude-code/VERSION`
- [X] T010 [US1] Create installation README with single `cp -r` command, platform prerequisites (Claude Code installed), and verification steps (invoke orchestrator, check agent list) — write to `adapters/claude-code/README.md`
- [X] T011 [US1] Verify content preservation: compare prompt body content of each source agent (`agents/`) against transformed adapter file (`adapters/claude-code/agents/`) — confirm 100% body content match excluding frontmatter and metadata section

**Checkpoint**: Claude Code adapter complete — installable with single copy command, all 14 agents available

---

## Phase 4: User Story 2 — Generic Standalone Invocation (Priority: P0)

**Goal**: Create self-contained numbered prompt files with sequential and programmatic invocation instructions

**Independent Test**: Copy-paste prompt files sequentially into any LLM chat UI, provide architecture input, verify valid `threats.md` output

### Implementation for User Story 2

- [X] T012 [US2] Create generic orchestrator prompt (`adapters/generic/prompts/00-orchestrator.md`): strip frontmatter, convert dispatch instructions to sequential workflow guide ("Step 1: Run Spoofing prompt..."), add `{{ARCHITECTURE_INPUT}}` placeholder, add "How to Use" header — this is the justified FR-002 exception
- [X] T013 [P] [US2] Create 6 generic STRIDE prompts (`adapters/generic/prompts/01-spoofing.md` through `06-privilege-escalation.md`): strip frontmatter, remove internal path references, add "How to Use" header with input/output instructions, make each file self-contained
- [X] T014 [P] [US2] Create 5 generic AI prompts (`adapters/generic/prompts/07-prompt-injection.md` through `11-tool-abuse.md`): same self-contained transformation as T013
- [X] T015 [P] [US2] Create 2 generic report prompts (`adapters/generic/prompts/12-threat-report.md` and `13-threat-infographic.md`): strip frontmatter, remove path references, add usage instructions
- [X] T016 [US2] Generate VERSION file for generic adapter — write to `adapters/generic/VERSION`
- [X] T017 [US2] Create README with two usage modes: (1) Sequential chat UI instructions with numbered copy-paste steps, (2) Programmatic API instructions with example curl and Python code — write to `adapters/generic/README.md`

**Checkpoint**: Generic adapter complete — usable with any LLM via copy-paste or API calls

---

## Phase 5: User Story 3 — Cursor Rules Integration (Priority: P1)

**Goal**: Map threat agents into `.cursor/rules/tachi/` as `.mdc` rule files with appropriate activation metadata

**Independent Test**: Install to `.cursor/rules/tachi/`, open architecture files in Cursor, verify orchestrator rule loads and threat agents are available via Agent Requested matching

### Implementation for User Story 3

- [X] T018 [US3] Transform orchestrator to Cursor rule: replace frontmatter with `alwaysApply: true` and `description`, add body text explaining Cursor's context injection model (no active dispatch), add `## Metadata` section, rewrite paths — write to `adapters/cursor/rules/orchestrator.mdc`
- [X] T019 [P] [US3] Transform 6 STRIDE agents to Cursor rules: `alwaysApply: false`, `description` set for Agent Requested matching, add `## Metadata` section, rewrite paths — write to `adapters/cursor/rules/{agent-name}.mdc`
- [X] T020 [P] [US3] Transform 5 AI agents to Cursor rules: same transformation as T019 — write to `adapters/cursor/rules/{agent-name}.mdc`
- [X] T021 [P] [US3] Transform 2 report agents to Cursor rules: same transformation as T019 — write to `adapters/cursor/rules/{agent-name}.mdc`
- [X] T022 [US3] Generate VERSION file for Cursor adapter — write to `adapters/cursor/VERSION`
- [X] T023 [US3] Create README documenting behavioral difference (passive context injection vs. active dispatch), installation to `.cursor/rules/tachi/`, and invocation workflow — write to `adapters/cursor/README.md`

**Checkpoint**: Cursor adapter complete — rules install cleanly, orchestrator always loaded, threat agents available via description matching

---

## Phase 6: User Story 4 — Copilot Agent Installation (Priority: P1)

**Goal**: Map threat agents into `.github/agents/tachi/` as `.agent.md` files with size constraint handling for oversized agents

**Independent Test**: Install to `.github/agents/tachi/`, invoke orchestrator agent in Copilot, verify threat agents are available and dispatch

### Implementation for User Story 4

- [X] T024 [US4] Transform orchestrator for Copilot with size-split strategy: create compact dispatcher agent (under 30K chars) at `adapters/copilot/agents/orchestrator.agent.md` with `agents` field listing spawnable threat agents; create full context file at `adapters/copilot/instructions/tachi-orchestrator-context.instructions.md` with `applyTo` referencing architecture file patterns
- [X] T025 [P] [US4] Transform 6 STRIDE agents to Copilot format: `name: tachi-{agent_name}`, `description`, `user-invocable: false`, add `## Metadata` section, rewrite paths (3 levels up from `.github/agents/tachi/`) — write to `adapters/copilot/agents/{agent-name}.agent.md`
- [X] T026 [P] [US4] Transform 5 AI agents to Copilot format: same transformation as T025 — write to `adapters/copilot/agents/{agent-name}.agent.md`
- [X] T027 [US4] Transform threat-report with size-split strategy (43K chars exceeds 30K limit): compact agent at `adapters/copilot/agents/threat-report.agent.md`, full context at `adapters/copilot/instructions/tachi-threat-report-context.instructions.md`
- [X] T028 [P] [US4] Transform threat-infographic to Copilot format (26K chars — fits within 30K limit): standard transformation — write to `adapters/copilot/agents/threat-infographic.agent.md`
- [X] T029 [US4] Verify all agent prompt bodies fit within Copilot's 30,000-character limit (or are properly split into agent + instructions)
- [X] T030 [US4] Generate VERSION file for Copilot adapter — write to `adapters/copilot/VERSION`
- [X] T031 [US4] Create README documenting installation to `.github/agents/tachi/` and `.github/instructions/`, Copilot prerequisites, size constraint notes, and verification steps — write to `adapters/copilot/README.md`

**Checkpoint**: Copilot adapter complete — all agents installable, oversized agents properly split into agent + instructions

---

## Phase 7: User Story 5 — GitHub Actions CI Pipeline (Priority: P1)

**Goal**: Create workflow YAML that triggers on architecture file changes, invokes agents via LLM API, generates `threats.md` + `threats.sarif`, uploads SARIF to Code Scanning

**Independent Test**: Add workflow to a GitHub repo, configure LLM API key secret, submit PR changing an architecture file, verify workflow triggers and SARIF appears in Security tab

### Implementation for User Story 5

- [X] T032 [US5] Create GitHub Actions workflow YAML at `adapters/github-actions/tachi-threat-model.yml`: trigger on `pull_request` with configurable `paths` filter, inputs for `LLM_API_KEY` secret and `architecture-path`, steps for checkout → read input → invoke LLM API → parse output → generate `threats.md` → generate `threats.sarif` → upload SARIF via `codeql/upload-sarif@v3` with `category: tachi-threat-model` → upload `threats.md` as artifact
- [X] T033 [US5] Add error handling to workflow: retry once on 429 rate limit with exponential backoff, clear error messages for auth failures and timeout, non-zero exit on API errors
- [X] T034 [US5] Add `partialFingerprints.primaryLocationLineHash` computation to SARIF generation step to prevent duplicate alerts across runs
- [X] T035 [US5] Generate VERSION file for GitHub Actions adapter — write to `adapters/github-actions/VERSION`
- [X] T036 [US5] Create README documenting workflow installation, LLM API key configuration (secrets), architecture path configuration, minimum context window requirements (200K+ recommended), supported LLM providers, and SARIF output verification — write to `adapters/github-actions/README.md`

**Checkpoint**: GitHub Actions adapter complete — workflow installs, triggers on PRs, generates SARIF, uploads to Code Scanning

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Output parity validation, documentation updates, and final quality checks

- [X] T037 [P] Update `adapters/README.md` to document both purposes: existing knowledge-system config files and new platform adapter subdirectories
- [X] T038 Run output parity validation: provide identical architecture input to Claude Code adapter and generic adapter, compare `threats.md` output for semantic equivalence (identical findings, risk ratings, severity levels, mitigations)
- [X] T039 [P] Update PRD INDEX at `docs/product/02_PRD/INDEX.md` to reflect Feature 021 status
- [X] T040 Final review: verify all 5 adapters have README.md, VERSION file, and correct file count (14 agent files for file-transformation adapters)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — defines conventions shared by all adapters
- **US1 Claude Code (Phase 3)**: Depends on Phase 2 — P0 MVP
- **US2 Generic (Phase 4)**: Depends on Phase 1 only (no shared conventions needed — strips all metadata) — P0, can run in parallel with Phase 3
- **US3 Cursor (Phase 5)**: Depends on Phase 2 — P1 Sprint 2
- **US4 Copilot (Phase 6)**: Depends on Phase 2 — P1 Sprint 2
- **US5 GitHub Actions (Phase 7)**: Depends on Phase 1 only (architecturally distinct, no shared conventions) — P1 Sprint 2
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (Claude Code, P0)**: Independent after Phase 2
- **US2 (Generic, P0)**: Independent after Phase 1 (no Phase 2 dependency)
- **US3 (Cursor, P1)**: Independent after Phase 2
- **US4 (Copilot, P1)**: Independent after Phase 2
- **US5 (GitHub Actions, P1)**: Independent after Phase 1 (no Phase 2 dependency)

### Parallel Opportunities

**Sprint 1 (P0)**:
- US1 (Claude Code) and US2 (Generic) can run fully in parallel after Phase 1
- Within US1: T006, T007, T008 are parallelizable (different files, no dependencies)
- Within US2: T013, T014, T015 are parallelizable

**Sprint 2 (P1)**:
- US3 (Cursor), US4 (Copilot), and US5 (GitHub Actions) can all run in parallel
- Within US3: T019, T020, T021 are parallelizable
- Within US4: T025, T026, T028 are parallelizable
- US5 has no internal parallelism (sequential workflow construction)

---

## Parallel Example: Sprint 1

```
Wave 1 (Setup):
  T001 (directory skeleton)
  T002 (VERSION script)

Wave 2 (Conventions + Generic kickoff):
  T003 (metadata convention)
  T004 (path rewriting rules)
  T012 [US2] (generic orchestrator — no Phase 2 dependency)

Wave 3 (US1 + US2 in parallel):
  Agent A (US1 Claude Code):
    T005 (orchestrator)
    T006 + T007 + T008 (STRIDE + AI + report agents in parallel)
    T009 (VERSION)
    T010 (README)
    T011 (verify content)

  Agent B (US2 Generic):
    T013 + T014 + T015 (STRIDE + AI + report prompts in parallel)
    T016 (VERSION)
    T017 (README)

Wave 4 (Parity check):
  T038 (output parity validation)
```

---

## Implementation Strategy

### MVP First (Sprint 1: US1 + US2)

1. Complete Phase 1: Setup (directory skeleton + VERSION script)
2. Complete Phase 2: Foundational (shared conventions)
3. Complete Phase 3: Claude Code adapter (US1) — reference implementation
4. Complete Phase 4: Generic adapter (US2) — universal fallback
5. **STOP and VALIDATE**: Run output parity check (T038)
6. Deploy Sprint 1 adapters

### Incremental Delivery (Sprint 2: US3 + US4 + US5)

7. Complete Phase 5: Cursor adapter (US3) — test independently
8. Complete Phase 6: Copilot adapter (US4) — test independently
9. Complete Phase 7: GitHub Actions adapter (US5) — test independently
10. Complete Phase 8: Polish — final validation across all 5 adapters

### Parallel Team Strategy

With multiple agents:
- Phase 1-2 completed together (2 tasks setup, 2 tasks conventions)
- Sprint 1: Agent A on US1, Agent B on US2 (in parallel)
- Sprint 2: Agent A on US3, Agent B on US4, Agent C on US5 (all in parallel)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each adapter is independently installable and testable
- Content preservation (FR-002) verified per adapter in checkpoint tasks
- Generic adapter orchestrator conversion is the only justified FR-002 exception
- Copilot size-split affects only orchestrator (120K) and threat-report (43K)
- Total: 40 tasks across 8 phases, 14 parallelizable
