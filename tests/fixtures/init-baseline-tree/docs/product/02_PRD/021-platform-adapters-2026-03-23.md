---
prd:
  number: "021"
  topic: platform-adapters
  created: 2026-03-23
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-23, status: Approved, notes: "PRD authored and revised per Triad feedback"}
  architect_signoff: {agent: architect, date: 2026-03-23, status: Approved, notes: "Both High concerns resolved — sync mechanism (FR-002a) and platform fallback strategy adequate at PRD level"}
  techlead_signoff: {agent: team-lead, date: 2026-03-23, status: Approved, notes: "Timeline veto withdrawn — phased Sprint 1/2 approach resolves capacity and dependency concerns"}
source:
  idea_id: 21
  story_id: null
---

# Platform Adapters - Product Requirements Document

**Status**: Approved
**Created**: 2026-03-23
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1 (High)

---

## Executive Summary

### The One-Liner
Platform adapters translate tachi's core threat agents into native formats for Claude Code, Cursor, Copilot, GitHub Actions, and any LLM backend.

### Problem Statement
Tachi's threat modeling agents are platform-neutral markdown prompt files, but each agentic coding tool expects prompts in its own directory structure and format. Users must manually restructure agent files to install tachi on their platform, creating friction and risking lossy transformations that degrade threat analysis quality.

### Proposed Solution
Create an adapter layer (`adapters/`) that maps core agent definitions from `agents/` into each platform's native format. Adapters fall into two categories:

1. **File-transformation adapters** (Claude Code, Cursor, Copilot, Generic): Pure directory/file transformations — no prompt logic changes. Each ships with an installation README for single-command installation.
2. **CI integration adapter** (GitHub Actions): A workflow pipeline that invokes tachi agents via LLM API at CI time, generating `threats.md` and uploading SARIF to GitHub Code Scanning. This is architecturally distinct from file-transformation adapters.

### Success Criteria
- All 5 adapters install cleanly on their target platforms
- Same input diagram produces semantically equivalent `threats.md` regardless of adapter (output parity — finding content, risk ratings, and recommendations match; execution order and formatting may vary)
- Generic adapter verified with copy-paste into a standalone LLM chat
- Zero lossy transformations — full agent prompt content preserved in every file-transformation adapter

### Timeline
- **Sprint 1 (P0)**: Claude Code adapter + Generic adapter (85% confidence)
- **Sprint 2 (P1)**: Cursor, Copilot, and GitHub Actions adapters (pending format research)

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Platform adapters directly serve the vision of becoming "the default threat modeling toolkit for any team building agentic AI applications." Without adapters, tachi is limited to users willing to manually structure prompts. With adapters, tachi works natively in the 4 most popular agentic coding tools plus any LLM backend.

### Roadmap Fit
**Phase**: Polish (per Consumer Guide sequencing)
**Dependencies**: F-001 (Project Skeleton), F-003 (Orchestrator) — both delivered

---

## Target Users & Personas

### Primary Persona: Claude Code Developer
- **Role**: Developer using Claude Code as their primary agentic coding tool
- **Experience**: Familiar with `.claude/agents/` directory conventions
- **Goals**: Run threat modeling within their existing Claude Code workflow
- **Pain Points**: Must manually copy and restructure tachi agents into `.claude/agents/tachi/`

### Secondary Persona: Cursor / Copilot Developer
- **Role**: Developer using Cursor or GitHub Copilot for AI-assisted coding
- **Experience**: Familiar with `.cursor/rules/` or `.github/copilot/` conventions
- **Goals**: Use tachi without switching to a different platform
- **Pain Points**: tachi agent format doesn't match their tool's expected structure

### Tertiary Persona: CI/CD Engineer
- **Role**: DevOps/security engineer who automates security scanning in CI pipelines
- **Experience**: Experienced with GitHub Actions, familiar with SARIF uploads
- **Goals**: Run tachi automatically on PRs that modify architecture documents
- **Pain Points**: No ready-made workflow YAML; must build invocation pipeline from scratch

### Quaternary Persona: Platform-Agnostic Integrator
- **Role**: Developer or architect using any LLM backend or custom orchestration
- **Experience**: Comfortable with raw prompt files and API calls
- **Goals**: Invoke tachi from any chat UI or LLM API without platform-specific tooling
- **Pain Points**: No clear invocation instructions for standalone/programmatic use

---

## User Stories

### US-001: Claude Code Adapter
**When** I'm setting up tachi in a project that uses Claude Code,
**I want to** install a Claude Code adapter that maps agents into `.claude/agents/tachi/`,
**So I can** invoke tachi natively using Claude Code's Agent tool for parallel execution.

**Acceptance Criteria**:
- **Given** the `adapters/claude-code/` directory, **when** I copy it to my project's `.claude/agents/tachi/`, **then** all agent prompts are available for Claude Code invocation
- **Given** the adapter, **when** the orchestrator dispatches to threat agents, **then** Claude Code's Agent tool executes them in parallel
- **Given** the installation README, **when** I follow its instructions, **then** installation is a single `cp -r` command
- **Given** identical architecture input, **when** I run tachi via Claude Code adapter vs. generic adapter, **then** the output `threats.md` is structurally identical

**Priority**: P0
**Effort**: M

### US-002a: Cursor Adapter
**When** I'm using Cursor as my agentic coding tool,
**I want to** install a Cursor adapter,
**So I can** use tachi without switching to a different development environment.

**Acceptance Criteria**:
- **Given** the Cursor adapter, **when** installed, **then** agents map to `.cursor/rules/` format
- **Given** the adapter, **when** compared to core agent content, **then** full prompt content is preserved with no lossy transformation
- **Given** Cursor's format requirements, **when** the adapter generates files, **then** each file follows Cursor's conventions (naming, structure, metadata)

**Priority**: P1
**Effort**: M
**Prerequisite**: Resolve open question on Cursor multi-file agent support before implementation

### US-002b: Copilot Adapter
**When** I'm using GitHub Copilot as my agentic coding tool,
**I want to** install a Copilot adapter,
**So I can** use tachi without switching to a different development environment.

**Acceptance Criteria**:
- **Given** the Copilot adapter, **when** installed, **then** agents map to `.github/copilot/` format
- **Given** the adapter, **when** compared to core agent content, **then** full prompt content is preserved with no lossy transformation
- **Given** Copilot's format requirements, **when** the adapter generates files, **then** each file follows Copilot's conventions

**Priority**: P1
**Effort**: M
**Prerequisite**: Resolve open question on Copilot directory structure before implementation. If Copilot lacks multi-file orchestration support, downgrade to single-file consolidated prompt with generic adapter fallback.

### US-003: GitHub Actions Adapter
**When** a PR modifies architecture documents in my repository,
**I want to** automatically run tachi threat modeling via GitHub Actions,
**So I can** catch security threats as part of my CI pipeline without manual invocation.

**Acceptance Criteria**:
- **Given** the GitHub Actions adapter, **when** a PR changes architecture files, **then** the workflow triggers automatically
- **Given** the workflow runs, **when** the orchestrator and threat agents execute via LLM API, **then** `threats.md` and `threats.sarif` are generated
- **Given** SARIF output, **when** the workflow completes, **then** results are uploaded to GitHub Code Scanning via `codeql/upload-sarif@v3`
- **Given** the workflow YAML, **when** a user adds it to `.github/workflows/`, **then** it works with configurable LLM API key (secret) and architecture file path

**Priority**: P1
**Effort**: L

### US-004: Generic Adapter
**When** I want to invoke tachi from any LLM backend or orchestration framework,
**I want to** use a generic adapter with standalone prompt files and clear invocation instructions,
**So I can** run threat modeling without platform-specific tooling.

**Acceptance Criteria**:
- **Given** the generic adapter, **when** I read the invocation instructions, **then** I can run tachi sequentially in any chat UI by copy-pasting prompts
- **Given** the generic adapter, **when** I read the programmatic instructions, **then** I can invoke tachi via any LLM API with clear request/response format
- **Given** copy-paste into a standalone LLM chat, **when** I follow the sequential instructions, **then** I get a valid `threats.md` output
- **Given** no platform dependencies, **when** I use the generic adapter, **then** the only requirement is an LLM that accepts text prompts

**Priority**: P0
**Effort**: S

---

## Functional Requirements

### FR-001: Adapter Directory Structure
Each adapter lives in `adapters/{platform-name}/` with:
- Platform-specific agent files (transformed from `agents/`)
- Installation README with step-by-step instructions
- Platform-specific configuration (if applicable)

**Directory layout**:
```
adapters/
├── claude-code/        # .claude/agents/tachi/ format
│   ├── README.md       # Installation instructions
│   └── agents/         # Agent files in Claude Code format
├── cursor/             # .cursor/rules/ format
│   ├── README.md
│   └── rules/          # Agent files in Cursor format
├── copilot/            # .github/copilot/ format
│   ├── README.md
│   └── agents/         # Agent files in Copilot format
├── github-actions/     # GitHub Actions workflow
│   ├── README.md
│   └── tachi-threat-model.yml
└── generic/            # Standalone prompt files
    ├── README.md       # Sequential + programmatic instructions
    └── prompts/        # Self-contained prompt files
```

### FR-002: Core Agent Preservation
File-transformation adapters MUST preserve 100% of core agent prompt content. Transformation is limited to:
- File naming (e.g., `spoofing.md` → platform convention)
- Directory placement (e.g., `agents/stride/` → `.cursor/rules/tachi/`)
- Metadata wrapping (e.g., adding platform-specific frontmatter)
- Path reference rewriting (internal references like `agents/stride/spoofing.md` or `schemas/finding.yaml` must be updated to resolve correctly from the adapter's installation location)
- No prompt logic modifications, no content omissions, no summarization

### FR-002a: Adapter Version Synchronization
Each adapter directory MUST include a `VERSION` file containing:
- `source_version`: Git SHA of the `agents/` directory state used to generate the adapter
- `generated_date`: Date the adapter was last synchronized
- `agent_manifest`: List of all agent files included with their SHA checksums

Core agent changes require regenerating affected adapters. During spec/plan phase, a lightweight sync-check script will be defined to detect drift between `agents/` and adapter contents. Full automation is out of scope for MVP but the version markers enable manual verification.

### FR-003: Claude Code Adapter Specifics
- Maps orchestrator + 13 threat agents (6 STRIDE + 5 AI + threat-report + threat-infographic) into `.claude/agents/tachi/` directory
- Orchestrator uses Claude Code's Agent tool for parallel dispatch
- Includes schema and template references as relative paths from installation location
- Single `cp -r` installation

### FR-004: Cursor Adapter Specifics
- Maps to `.cursor/rules/` directory structure
- Follows Cursor's rule file conventions (naming, metadata)
- Preserves agent identity and dispatch information

### FR-005: Copilot Adapter Specifics
- Maps to `.github/copilot/` directory structure
- Follows GitHub Copilot's agent file conventions
- Preserves agent identity and dispatch information

### FR-006: GitHub Actions Adapter Specifics (CI Integration)
**Note**: This adapter is architecturally distinct from file-transformation adapters. It is a CI/CD integration pipeline with runtime LLM API invocation, not a thin file wrapper.

- Workflow YAML triggers on changes to configurable architecture file paths
- Invokes orchestrator and threat agents via LLM API (configurable provider)
- Must handle the orchestrator's large prompt (~120K+ tokens) — API invocation strategy (chunking, model selection) to be defined in spec phase
- Generates `threats.md` and `threats.sarif`
- Uploads SARIF to GitHub Code Scanning via `codeql/upload-sarif@v3`
- Requires `LLM_API_KEY` secret and architecture file path input
- Supports configurable LLM provider (OpenAI, Anthropic, Google, etc.)
- Includes error handling for API failures, rate limits, and token budget constraints

### FR-007: Generic Adapter Specifics
- Self-contained prompt files that work with any LLM
- Sequential invocation instructions (for chat UIs): numbered steps for copy-paste workflow
- Programmatic invocation instructions (for LLM APIs): request/response format with example code
- No dependencies beyond an LLM that accepts text prompts

### FR-008: Output Parity Guarantee
All adapters MUST produce semantically equivalent `threats.md` output given the same architecture input. Acceptable variation:
- Finding order may differ due to parallel vs. sequential agent dispatch
- Platform-specific metadata in output headers
- Minor formatting differences (whitespace, line breaks)

**No variation permitted** in: finding content, risk ratings, severity levels, mitigation recommendations, or coverage matrix counts. Parity is defined as semantic equivalence, not byte-identical output.

---

## Non-Functional Requirements

### Portability
- Adapters contain only markdown, YAML, and workflow files — no runtime dependencies
- No compilation or build step required for any adapter
- All adapters work offline (except GitHub Actions which requires CI infrastructure)

### Maintainability
- Core agent changes propagate to adapters via version-tracked regeneration (see FR-002a)
- Each adapter includes a `VERSION` file with source SHA and agent manifest for drift detection
- Adapter transformation rules are documented per platform
- Single source of truth remains `agents/` directory — adapters are derived artifacts

### Documentation
- Each adapter includes a self-contained README with installation, configuration, and verification instructions
- Generic adapter includes both sequential (chat UI) and programmatic (API) usage guides

---

## Success Metrics

### Primary Metrics
- **Installation success rate**: 100% of adapters install without errors following README instructions
- **Output parity**: Same input produces identical findings across all adapters
- **Platform coverage**: 5 adapters covering Claude Code, Cursor, Copilot, GitHub Actions, and generic

### Adoption Metrics
- **Generic adapter usability**: Verified with copy-paste into standalone LLM chat
- **GitHub Actions integration**: SARIF upload to Code Scanning confirmed working

---

## Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- Claude Code adapter with `.claude/agents/tachi/` mapping and parallel dispatch
- Generic adapter with standalone prompts and sequential/programmatic instructions
- Output parity validation across adapters

**Should Have (P1)** — Sprint 2, pending format research:
- Cursor adapter with `.cursor/rules/` mapping (requires format verification)
- Copilot adapter with `.github/copilot/` mapping (requires format verification; fallback to consolidated prompt if multi-file unsupported)
- GitHub Actions CI integration with LLM API invocation and SARIF upload

### Out of Scope

- Automated adapter generation script (manual transformation with version markers for MVP)
- Automated drift detection CI check (version markers enable manual verification)
- IDE-specific UI extensions or plugins
- Testing framework for cross-adapter output comparison (manual verification for MVP)
- Adapters for non-agentic tools (VS Code extensions, JetBrains plugins, etc.)

### Assumptions
- Claude Code `.claude/agents/` directory structure is stable (HIGH confidence — well documented)
- GitHub Actions `codeql/upload-sarif@v3` remains the standard SARIF upload action (HIGH confidence)

### Assumptions Requiring Validation (P1 Blockers)
- [ ] Cursor `.cursor/rules/` format supports multi-file agent definitions — **MEDIUM confidence, must verify before Sprint 2**
- [ ] GitHub Copilot `.github/copilot/` format supports custom agent prompts — **LOW confidence, must verify before Sprint 2**. If unsupported, Copilot adapter falls back to consolidated single-file prompt with generic adapter as escape hatch.

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Platform format instability
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Adapters are thin wrappers; format changes require minimal updates
- **Contingency**: Generic adapter always works as fallback

**Risk 2**: LLM API variability in GitHub Actions
- **Likelihood**: Medium
- **Impact**: Medium
- **Mitigation**: Workflow YAML uses configurable provider; document tested providers
- **Note**: Orchestrator prompt is ~120K+ tokens — requires models with large context windows

**Risk 3**: Unverified platform format assumptions (Cursor, Copilot)
- **Likelihood**: Medium
- **Impact**: High (could invalidate 2 of 5 adapters)
- **Mitigation**: Format research via `web-researcher` agent before Sprint 2. Fallback: consolidated single-file prompt for platforms without multi-file support, with generic adapter as escape hatch.
- **Contingency**: If both Cursor and Copilot lack multi-file support, ship 3 adapters (Claude Code, GitHub Actions, Generic) and provide format-specific installation guides that reference the generic adapter.

### Dependencies

**Internal Dependencies**:
- **F-001 (Project Skeleton)**: Agent files, schemas, templates — Delivered
- **F-003 (Orchestrator)**: Orchestrator prompt for dispatch logic — Delivered
- **F-012 (SARIF Output)**: SARIF generation for GitHub Actions adapter — Delivered

**Dependency Graph**:
```
[F-021 Platform Adapters]
  ├── Depends on: F-001 (Project Skeleton) ✅ Delivered
  ├── Depends on: F-003 (Orchestrator) ✅ Delivered
  └── Depends on: F-012 (SARIF Output) ✅ Delivered
```

---

## Open Questions

**P1 Blockers** (must resolve before Sprint 2):
- [ ] What is the exact `.github/copilot/` directory structure for custom agents? - web-researcher - HIGH priority
- [ ] Does Cursor support multi-file agent definitions in `.cursor/rules/`? - web-researcher - MEDIUM priority

**Sprint 2 Planning**:
- [ ] Which LLM providers should the GitHub Actions adapter support out of the box? - product-manager - LOW priority
- [ ] What is the API invocation strategy for the ~120K+ token orchestrator prompt in GitHub Actions? - architect - MEDIUM priority

---

## References

### Product Documentation
- Product Vision: [product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- Consumer Guide: [CONSUMER_GUIDE_TACHI.md](docs/guides/CONSUMER_GUIDE_TACHI.md) (F-009)
- Research: [CONSUMER_GUIDE_TACHI_RESEARCH.md](docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md) (§6, §11)

### Technical Documentation
- Constitution: [constitution.md](.aod/memory/constitution.md)
- Interface Contract: [INTERFACE-CONTRACT.md](docs/INTERFACE-CONTRACT.md)
- System Design: [system design](docs/architecture/01_system_design/README.md)

### Source
- GitHub Issue: #21 (Feature 009: Platform Adapters)
- ICE Score: Impact 8, Confidence 7, Effort 7 = 22

---

## Approval & Sign-Off

| Role | Agent | Status | Date | Comments |
|------|-------|--------|------|----------|
| Product Manager | product-manager | Approved | 2026-03-23 | PRD authored and revised per Triad feedback |
| Architect | architect | Approved | 2026-03-23 | Both High concerns resolved in v1.1 |
| Team Lead | team-lead | Approved | 2026-03-23 | Timeline veto withdrawn; phased approach approved |

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-23 | product-manager | Initial PRD |
| 1.1 | 2026-03-23 | product-manager | Address Architect + Team-Lead review: add version sync mechanism (FR-002a), split US-002 into Cursor/Copilot, phased timeline, redefine output parity as semantic equivalence, add platform fallback strategy, fix agent count to 14, acknowledge GitHub Actions as CI integration |
