# Research Summary: Platform Adapters (Feature 021)

**Date**: 2026-03-23
**PRD**: docs/product/02_PRD/021-platform-adapters-2026-03-23.md

## Knowledge Base Findings

- No prior KB entries for platform adapter patterns (first feature of this type)
- Existing upstream sync architecture (`docs/architecture/01_system_design/upstream-sync-architecture.md`) establishes the hub-and-spoke model that adapters extend
- ADR-003 (`docs/architecture/02_ADRs/ADR-003-stride-per-element-dispatch.md`) documents the deterministic dispatch logic that adapters must preserve

## Codebase Analysis

### Agent Inventory (21 files in `agents/`)
- **6 STRIDE agents**: spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation
- **5 AI agents**: prompt-injection, data-poisoning, model-theft, agent-autonomy, tool-abuse
- **1 Orchestrator**: orchestrator.md (~120K+ tokens, central dispatcher)
- **2 Report agents**: threat-report.md, threat-infographic.md
- **Shared files**: VoiceProfile.md, StyleGuide.md
- **Content directories**: MasterContent/, Narratives/

### Agent File Format
All agents use markdown with YAML frontmatter containing:
- `agent_name`: Unique identifier (kebab-case)
- `category`: Classification (stride, ai, orchestrator, report)
- `threat_class`: Single letter/acronym (S, T, R, I, D, E, AG, LLM)
- `dfd_targets`: List of DFD element types
- `owasp_references`: Standard framework cross-references
- `output_schema`: Reference to `schemas/finding.yaml`

### Cross-References (Path Patterns)
All paths are relative from project root:
- Agents reference: `schemas/finding.yaml`, `docs/INTERFACE-CONTRACT.md`
- Orchestrator references: all 13 threat agents, 5 schemas, 3 templates
- Convention: forward-slash relative paths (e.g., `agents/stride/spoofing.md`)

### Schemas (5 files in `schemas/`)
- `input.yaml` (v1.0) - 6 input format types
- `finding.yaml` (v1.0) - Atomic threat finding IR (10 fields)
- `output.yaml` (v1.1) - Complete threat model structure (7 required sections)
- `report.yaml` - Threat report narrative structure
- `infographic.yaml` - Visual risk specification structure

### Templates (4 files in `templates/`)
- `threats.md` - Canonical threat model output
- `threats.sarif` - SARIF 2.1.0 format for GitHub Code Scanning
- `threat-report.md` - Narrative report template
- `threat-infographic-spec.md` - Visual risk specification

## Architecture Constraints

### Hub-and-Spoke Model
- **Hub**: `agents/`, `schemas/`, `templates/` — single source of truth, immutable
- **Spokes**: `adapters/{platform}/` — platform-specific transformations
- Adapters derive from hub content; hub is never modified per-adapter

### Interface Contract (docs/INTERFACE-CONTRACT.md v1.1)
- Defines invocation protocol, input formats, dispatch rules, output validation
- STRIDE-per-Element normalization table governs dispatch
- AI keyword dispatch adds secondary layer
- Output requires 7 sections + Section 4a in strict order

### Adapter Transformation Constraints (FR-002)
Allowed changes only:
- File naming → platform convention
- Directory placement → platform path
- Metadata wrapping → platform frontmatter
- Path reference rewriting → resolve from installation location
- NO prompt logic changes, NO content omissions, NO summarization

## Industry Research

### Platform Format Findings

| Platform | Directory | Extension | Required Frontmatter | Agent Dispatch | Prompt Limit |
|----------|-----------|-----------|---------------------|----------------|-------------|
| Claude Code | `.claude/agents/` | `.md` | `name`, `description` | Native (Agent tool) | No hard limit |
| Cursor | `.cursor/rules/` | `.mdc`/`.md` | None (3 optional fields) | None (context injection) | 500 lines guideline |
| Copilot | `.github/agents/` | `.agent.md` | `description` | Native (agents field) | 30,000 characters |
| GitHub Actions | `.github/workflows/` | `.yml` | N/A | API calls | Model-dependent |
| Generic | Any path | `.md` | None | Manual | Provider-dependent |

### PRD Blocker Resolution
1. **Cursor multi-file support**: CONFIRMED. `.cursor/rules/` supports multiple rule files in subdirectories. However, these are context injection rules, not autonomous agents. Cursor has no equivalent of Claude Code's Agent tool dispatch. Each threat agent becomes a separate `.mdc` rule.
2. **Copilot custom agents**: CONFIRMED. `.github/agents/agent-name.agent.md` format with YAML frontmatter. Supports multi-file agent definitions and subagent spawning via `agents` field. Currently in public preview. 30,000-character prompt body limit requires verification against tachi's larger agents.

### Key Platform Differences
- **Claude Code**: Closest match to tachi's native format. Transform frontmatter fields, preserve body.
- **Cursor**: No agent dispatch — rules are passive context, not active subagents. Orchestrator must be `alwaysApply: true`, threat agents are `Agent Requested` rules.
- **Copilot**: Similar to Claude Code but different frontmatter schema. Supports `handoffs` for sequential agent workflows. 30K char limit is a constraint.
- **GitHub Actions**: Architecturally distinct — CI pipeline with LLM API invocation. Recommended: use 200K+ context models, file-based prompt input, SARIF with `partialFingerprints`.
- **Generic**: Simplest — strip frontmatter, add usage instructions, number files for sequential execution.

## Recommendations for Spec

- Define 5 user stories mapping to the 5 adapters, prioritized P0/P1 per PRD timeline
- Spec should focus on what each adapter delivers to the user, not transformation mechanics
- Output parity is the key quality gate — same input must produce semantically equivalent threats.md
- Cursor adapter has a behavioral difference from other adapters (passive context vs. active dispatch) — spec should note this as an expected variation
- Copilot's 30K char limit should be called out as a constraint requiring verification
- GitHub Actions adapter is architecturally distinct and should be specified separately from file-transformation adapters
- VERSION file for drift detection is an MVP requirement per FR-002a
