---
prd_reference: docs/product/02_PRD/021-platform-adapters-2026-03-23.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-23
    status: APPROVED
    notes: "All 9 PRD requirements covered, 5 user stories traceable, P0/P1 priorities match PRD sprint timeline. Both PRD blocker questions resolved by research. Clean approval."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Platform Adapters

**Feature Branch**: `021-platform-adapters`
**Created**: 2026-03-23
**Status**: Draft
**PRD Reference**: docs/product/02_PRD/021-platform-adapters-2026-03-23.md
**Input**: PRD 021 - Platform Adapters: translate tachi's core threat agents into native formats for Claude Code, Cursor, Copilot, GitHub Actions, and any LLM backend

## User Scenarios & Testing

### User Story 1 - Claude Code Native Installation (Priority: P0)

A developer using Claude Code as their primary agentic coding tool wants to install tachi's threat modeling agents natively so they can invoke threat analysis directly from their Claude Code workflow without manual file restructuring.

**Why this priority**: Claude Code is tachi's primary development platform. Native installation removes the biggest adoption barrier for the largest user segment. This adapter also serves as the reference implementation for all other file-transformation adapters.

**Independent Test**: Can be fully tested by copying the adapter directory to a Claude Code project and invoking the orchestrator agent, which should dispatch to all threat agents and produce a valid `threats.md`.

**Acceptance Scenarios**:

1. **Given** the Claude Code adapter directory, **When** a developer copies it to their project's `.claude/agents/tachi/`, **Then** all 14 agent prompts (orchestrator + 6 STRIDE + 5 AI + threat-report + threat-infographic) are available for Claude Code invocation
2. **Given** the installed adapter, **When** the orchestrator dispatches to threat agents, **Then** Claude Code's Agent tool executes them in parallel with no manual intervention
3. **Given** the adapter's installation README, **When** a developer follows its instructions, **Then** installation completes with a single copy command
4. **Given** identical architecture input, **When** threat analysis runs via Claude Code adapter and via the generic adapter, **Then** the output `threats.md` contains identical findings, risk ratings, severity levels, and mitigation recommendations

---

### User Story 2 - Generic Standalone Invocation (Priority: P0)

A developer or architect using any LLM backend wants to run tachi's threat analysis by copying prompts into a chat UI or making API calls, without requiring any specific platform or tooling.

**Why this priority**: The generic adapter ensures tachi works with any LLM, providing a universal fallback and the widest possible reach. It also serves as the baseline for output parity testing.

**Independent Test**: Can be fully tested by copying prompt files sequentially into any LLM chat interface (e.g., Claude.ai, ChatGPT) and verifying that a valid `threats.md` output is produced.

**Acceptance Scenarios**:

1. **Given** the generic adapter's sequential instructions, **When** a user copies each prompt file into a chat UI in numbered order and provides architecture input, **Then** the final output is a valid `threats.md`
2. **Given** the generic adapter's programmatic instructions, **When** a developer sends prompts via any LLM API, **Then** each response follows the expected format and the assembled output is a valid `threats.md`
3. **Given** no platform dependencies, **When** a user uses the generic adapter, **Then** the only requirement is access to an LLM that accepts text prompts
4. **Given** the generic adapter prompts, **When** verified with copy-paste into a standalone LLM chat, **Then** the session produces findings that match the output parity standard

---

### User Story 3 - Cursor Rules Integration (Priority: P1)

A developer using Cursor as their agentic coding tool wants to install tachi's threat agents as Cursor rules so they can access threat analysis capabilities within their Cursor workflow.

**Why this priority**: Cursor is one of the most popular agentic coding tools. Supporting it expands tachi's reach to a large developer community. Scheduled for Sprint 2, pending format research completion.

**Independent Test**: Can be fully tested by installing the Cursor adapter rules and verifying that threat agents are activated when relevant architecture files are open in Cursor.

**Acceptance Scenarios**:

1. **Given** the Cursor adapter, **When** installed to `.cursor/rules/tachi/`, **Then** each threat agent is available as a Cursor rule file
2. **Given** the installed rules, **When** compared to core agent content, **Then** 100% of prompt content is preserved with no lossy transformation
3. **Given** Cursor's rule activation model, **When** the orchestrator rule is loaded, **Then** it provides instructions for invoking threat agents in Cursor's context injection model
4. **Given** Cursor's format requirements, **When** each rule file is loaded, **Then** it follows Cursor's conventions for rule metadata and activation type

---

### User Story 4 - Copilot Agent Installation (Priority: P1)

A developer using GitHub Copilot wants to install tachi's threat agents as Copilot custom agents so they can run threat analysis within their Copilot-enabled IDE.

**Why this priority**: GitHub Copilot has wide enterprise adoption. Supporting it enables tachi in corporate development environments. Scheduled for Sprint 2, pending verification of the Copilot agent format.

**Independent Test**: Can be fully tested by installing the Copilot adapter agents and invoking the orchestrator agent within Copilot's agent framework.

**Acceptance Scenarios**:

1. **Given** the Copilot adapter, **When** installed to `.github/agents/tachi/`, **Then** each threat agent is available as a Copilot custom agent
2. **Given** the installed agents, **When** compared to core agent content, **Then** 100% of prompt content is preserved with no lossy transformation
3. **Given** Copilot's format requirements, **When** each agent file is loaded, **Then** it follows Copilot's `.agent.md` conventions for naming, frontmatter, and structure
4. **Given** all agent prompts, **When** checked against Copilot's character limits, **Then** every agent prompt fits within the platform's size constraints

---

### User Story 5 - GitHub Actions CI Pipeline (Priority: P1)

A CI/CD engineer wants to run tachi threat modeling automatically on pull requests that modify architecture documents so that security threats are caught as part of the CI pipeline.

**Why this priority**: Automated CI integration is a key adoption driver for security-focused teams. This adapter is architecturally distinct from file-transformation adapters (it invokes agents via LLM API at runtime). Scheduled for Sprint 2.

**Independent Test**: Can be fully tested by adding the workflow YAML to a GitHub repository, configuring an LLM API key, and submitting a PR that modifies an architecture file.

**Acceptance Scenarios**:

1. **Given** the GitHub Actions adapter workflow, **When** a PR changes architecture files matching the configured path pattern, **Then** the workflow triggers automatically
2. **Given** the triggered workflow, **When** the orchestrator and threat agents execute via LLM API, **Then** `threats.md` and `threats.sarif` files are generated as workflow artifacts
3. **Given** the generated SARIF output, **When** the workflow completes successfully, **Then** results are uploaded to GitHub Code Scanning and appear in the repository's Security tab
4. **Given** the workflow configuration, **When** a user adds it to `.github/workflows/`, **Then** it works with a configurable LLM API key (stored as a secret) and configurable architecture file path

---

### Edge Cases

- What happens when a core agent file is updated but adapters are not regenerated? The VERSION file enables drift detection, and the adapter README warns about version mismatch.
- How does the system handle platform format changes in a future Cursor/Copilot update? Adapters are thin wrappers with minimal transformation logic, so format updates require minimal adapter changes. The generic adapter always works as a fallback.
- What happens when an agent prompt exceeds a platform's size constraint (e.g., Copilot's 30,000-character limit)? The adapter must detect and report this during generation, and the installation README must document the constraint.
- What happens when the GitHub Actions adapter encounters an LLM API failure (rate limit, timeout, authentication error)? The workflow must fail gracefully with clear error messages and non-zero exit code.
- What happens when the orchestrator prompt exceeds the LLM's context window in GitHub Actions? The adapter documentation must specify minimum context window requirements and recommend compatible models.

## Requirements

### Functional Requirements

- **FR-001**: Each adapter MUST live in its own directory under `adapters/{platform-name}/` with platform-specific agent files, an installation README, and any platform-specific configuration
- **FR-002**: File-transformation adapters (Claude Code, Cursor, Copilot, Generic) MUST preserve 100% of core agent prompt content. Transformation is limited to file naming, directory placement, metadata wrapping, and path reference rewriting. No prompt logic modifications, content omissions, or summarization.
- **FR-003**: Each adapter directory MUST include a VERSION file containing the source Git SHA of the `agents/` directory, the generation date, and a manifest listing all included agent files with their checksums
- **FR-004**: The Claude Code adapter MUST map all 14 agents (orchestrator + 6 STRIDE + 5 AI + threat-report + threat-infographic) into a directory structure compatible with Claude Code's Agent tool, supporting parallel dispatch
- **FR-005**: The Cursor adapter MUST map threat agents into rule files compatible with Cursor's rule activation model, with appropriate activation metadata for each rule type
- **FR-006**: The Copilot adapter MUST map threat agents into agent files compatible with Copilot's custom agent format, with all prompts fitting within the platform's size constraints
- **FR-007**: The GitHub Actions adapter MUST provide a workflow YAML that triggers on architecture file changes, invokes threat agents via configurable LLM API, generates `threats.md` and `threats.sarif`, and uploads SARIF to GitHub Code Scanning
- **FR-008**: The generic adapter MUST provide self-contained prompt files with both sequential invocation instructions (for chat UIs) and programmatic invocation instructions (for LLM APIs)
- **FR-009**: All adapters MUST produce semantically equivalent `threats.md` output given identical architecture input. Acceptable variation includes finding order, platform-specific metadata, and minor formatting. No variation is permitted in finding content, risk ratings, severity levels, or mitigation recommendations.
- **FR-010**: Each adapter MUST include a self-contained installation README with step-by-step instructions, platform prerequisites, and verification steps

### Key Entities

- **Core Agent**: A threat modeling agent definition in `agents/` (the single source of truth). Contains prompt content, metadata, and cross-references.
- **Adapter**: A platform-specific transformation of core agents into a target platform's native format. Contains transformed agent files, installation instructions, and version tracking.
- **VERSION File**: A manifest tracking the source version of core agents used to generate the adapter, enabling drift detection between core and adapter contents.
- **Orchestrator**: The central coordinator agent that dispatches to threat agents and assembles the final output. Each adapter must include a platform-appropriate version.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 5 adapters (Claude Code, Cursor, Copilot, GitHub Actions, Generic) install cleanly following their README instructions with zero errors
- **SC-002**: The same architecture input diagram produces semantically equivalent `threats.md` findings across all file-transformation adapters (identical finding content, risk ratings, severity levels, and mitigation recommendations)
- **SC-003**: Generic adapter verified to produce valid output when prompts are copy-pasted into a standalone LLM chat session
- **SC-004**: GitHub Actions adapter successfully uploads SARIF to GitHub Code Scanning and findings appear in the repository's Security tab
- **SC-005**: 100% of core agent prompt content preserved in every file-transformation adapter — verified by content comparison between source agents and adapter files (excluding platform metadata)
- **SC-006**: Every adapter includes a VERSION file with source SHA and agent manifest, and version mismatch is detectable by comparing the VERSION file against the current `agents/` directory state

## Scope & Boundaries

### In Scope (MVP)

**Sprint 1 (P0)**:
- Claude Code adapter with `.claude/agents/tachi/` mapping and parallel dispatch support
- Generic adapter with standalone prompts and sequential/programmatic instructions
- Output parity validation across Sprint 1 adapters

**Sprint 2 (P1)** — pending format research:
- Cursor adapter with `.cursor/rules/tachi/` mapping
- Copilot adapter with `.github/agents/tachi/` mapping
- GitHub Actions CI integration with LLM API invocation and SARIF upload

### Out of Scope
- Automated adapter generation script (manual transformation with version markers for MVP)
- Automated drift detection CI check (version markers enable manual verification)
- IDE-specific UI extensions or plugins
- Automated cross-adapter output comparison testing framework
- Adapters for non-agentic tools (VS Code extensions, JetBrains plugins)

## Assumptions

- Claude Code's `.claude/agents/` directory structure is stable (HIGH confidence — well documented, actively used by tachi)
- GitHub Actions `codeql/upload-sarif@v3` remains the standard SARIF upload action (HIGH confidence)
- Cursor's `.cursor/rules/` format supports the multi-file rule layout needed for threat agents (MEDIUM confidence — confirmed by research, but format is evolving)
- Copilot's `.github/agents/` format supports custom agent definitions and is available in supported IDEs (MEDIUM-HIGH confidence — documented and functional, public preview)
- All core agent prompts fit within Copilot's 30,000-character prompt body limit (needs verification during implementation)

## Dependencies

- **F-001 (Project Skeleton)**: Agent files, schemas, templates — Delivered
- **F-003 (Orchestrator)**: Orchestrator prompt for dispatch logic — Delivered
- **F-012 (SARIF Output)**: SARIF generation for GitHub Actions adapter — Delivered
