---
prd:
  number: "045"
  topic: instruction-manual
  created: 2026-03-28
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-03-28, status: APPROVED, notes: "Passes all product alignment checks. Problem statement clear, user stories measurable, scope realistic, vision aligned."}
  architect_signoff: {agent: architect, date: 2026-03-28, status: APPROVED_WITH_CONCERNS, notes: "3 minor factual corrections (agent count 15 not 14, template filenames stale, existing guide acknowledged). All addressed in PRD revision."}
  techlead_signoff: {agent: team-lead, date: 2026-03-28, status: APPROVED_WITH_CONCERNS, notes: "2 concerns (existing guide not acknowledged, regeneration vs update strategy). Both addressed in FR-3 revision. Estimate: 1-2 sessions."}
source:
  idea_id: 45
  story_id: null
---

# End-to-End tachi Instruction Manual - Product Requirements Document

**Status**: Approved
**Created**: 2026-03-28
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P0 (Critical)

---

## Executive Summary

### The One-Liner
A comprehensive developer guide that walks users through the complete tachi workflow from architecture description to visual infographic reports.

### Problem Statement
Users who install tachi have a README Quick Start (6 steps to first run) but no guide explaining how to create effective architecture descriptions, the end-to-end workflow across all four commands (`/threat-model` -> `/risk-score` -> `/compensating-controls` -> `/infographic`), how to read and interpret each output, when and why to run each enrichment command, or how to troubleshoot common issues. The existing `GUIDE_PROMPT.md` prompt specification is ~80% complete but was written before Features 035 (risk scoring), 036 (compensating controls), and 039 (standalone infographic) were delivered. It also has a developer-facing filename that doesn't communicate its purpose to end users.

### Proposed Solution
Update the existing prompt specification to cover the full 4-command pipeline, rename it to a customer-friendly name, generate the actual developer guide from the updated spec, and publish it as a first-class documentation artifact. The guide will include a Quick Start section (first threat model in under 5 minutes) and a comprehensive walkthrough using the OpenClaw worked example.

### Success Criteria
- A published developer guide exists at `docs/guides/DEVELOPER_GUIDE_TACHI.md` (already referenced in README.md)
- The guide covers all 4 commands with worked examples and output interpretation
- A security analyst can follow the guide end-to-end without prior tachi knowledge
- The Quick Start gets a new user to their first threat model in under 5 minutes

### Timeline
Single delivery phase -- documentation-only deliverable with no code changes.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [docs/product/01_Product_Vision/product-vision.md](docs/product/01_Product_Vision/product-vision.md)

tachi's mission is to be an automated threat modeling toolkit for developers building AI agents. A comprehensive instruction manual directly supports this by lowering the barrier to entry for the target audience -- developers who understand architecture but don't have deep security expertise. Without a guide, the toolkit's value is locked behind a learning curve that the README alone cannot flatten.

### Roadmap Fit
This is the first documentation-focused deliverable after the core pipeline is complete (Features 001-039 delivered). It bridges the gap between "toolkit exists" and "toolkit is usable by its target audience."

---

## Target Users & Personas

### Primary Persona: Security Analyst

**Demographics**:
- Role: Security analyst or AppSec engineer
- Experience: Security domain expertise, may be new to tachi specifically
- Goals: Produce a complete threat analysis for an application without guessing which command to run next
- Pain Points: Tools with incomplete documentation force trial-and-error workflows

**Why This Matters to Them**:
A step-by-step manual means they can produce a full threat model (findings + quantitative scores + control analysis + visual report) in a single session, following a documented workflow.

### Secondary Persona: Developer New to Threat Modeling

**Demographics**:
- Role: Software developer building AI applications
- Experience: Strong development skills, minimal security expertise
- Goals: Understand the security posture of their application without becoming a security specialist
- Pain Points: Security tools assume prior knowledge of STRIDE, OWASP, DFD, SARIF

**Why This Matters to Them**:
The guide explains security concepts as it introduces them, defines every acronym on first use, and leads with "here's how to do it" before explaining why.

### Tertiary Persona: Template Adopter

**Demographics**:
- Role: Developer or team lead evaluating tachi for their project
- Experience: Varies -- evaluating whether tachi fits their workflow
- Goals: Get from zero to first threat model quickly to evaluate the tool
- Pain Points: Long setup processes and unclear onboarding

**Why This Matters to Them**:
The Quick Start section at the top of the guide gets them to a working threat model in under 5 minutes with copy-pasteable commands.

---

## User Stories

### US-045-1: Complete Workflow Guide
**When** I have installed tachi and want to analyze my application's architecture,
**I want to** follow a step-by-step instruction manual that walks me through the complete workflow from architecture description to visual infographics,
**So I can** produce a full threat analysis without guessing which command to run next.

**Acceptance Criteria**:
- **Given** a user has tachi installed, **when** they follow the guide from start to finish, **then** they produce all 12+ output artifacts (threats.md, threats.sarif, threat-report.md, attack-trees/, risk-scores.md, risk-scores.sarif, compensating-controls.md, compensating-controls.sarif, infographic specs and images)
- **Given** the guide covers `/threat-model`, **when** the user reaches the enrichment commands section, **then** the guide explains when and why to run `/risk-score`, `/compensating-controls`, and `/infographic` in sequence
- **Given** the guide references output artifacts, **when** the user reads the interpretation sections, **then** each output's key sections are explained with annotated examples

**Priority**: P0
**Effort**: L

### US-045-2: Output Interpretation
**When** I have generated a threat model and am looking at the output files,
**I want to** understand what each command does and how to interpret its output,
**So I can** understand the security posture of my application and know what to fix first.

**Acceptance Criteria**:
- **Given** the guide covers `threats.md`, **when** the user reads the interpretation section, **then** all 7 sections plus Section 4a are explained with example snippets
- **Given** the guide covers risk scores, **when** the user reads the scoring section, **then** the 4 scoring dimensions (CVSS, exploitability, scalability, reachability) are explained
- **Given** the guide covers compensating controls, **when** the user reads the controls section, **then** residual risk calculation and missing control recommendations are explained
- **Given** findings have risk levels, **when** the user reads the prioritization guidance, **then** they understand to work Critical -> High -> Medium

**Priority**: P0
**Effort**: M

### US-045-3: Quick Start
**When** I first install tachi and want to evaluate it quickly,
**I want to** follow a quick start at the top of the guide that gets me to my first threat model in under 5 minutes,
**So I can** see the value before investing time in the full guide.

**Acceptance Criteria**:
- **Given** a user has Claude Code installed and tachi cloned, **when** they follow the Quick Start, **then** they complete installation, create an architecture file, and run `/threat-model` in 5 steps
- **Given** the Quick Start is at the top of the guide, **when** the user finishes it, **then** they have a working threat model and clear pointers to the comprehensive guide sections
- **Given** the Quick Start references commands, **when** a command is mentioned, **then** the exact invocation syntax is shown as a copy-pasteable code block

**Priority**: P0
**Effort**: S

---

## Functional Requirements

### FR-1: Update Prompt Specification

**Description**: Update `docs/guides/prompts/GUIDE_PROMPT.md` to cover the full 4-command pipeline.

**Current State**: The prompt spec covers `/threat-model` and its outputs comprehensively but was written before Features 035, 036, and 039 were delivered. It is missing:
- `/risk-score` workflow section (Feature 035)
- `/compensating-controls` workflow section (Feature 036)
- `/infographic` standalone command section (Feature 039)
- Post-pipeline enrichment workflow (the sequence: `/threat-model` -> `/risk-score` -> `/compensating-controls` -> `/infographic`)

**Required Changes**:
- Add `/risk-score` command documentation: invocation, flags, output artifacts (risk-scores.md, risk-scores.sarif), scoring dimensions
- Add `/compensating-controls` command documentation: invocation, flags, output artifacts (compensating-controls.md, compensating-controls.sarif), residual risk
- Add `/infographic` standalone command documentation: invocation, flags, template selection, auto-detection of richest data source
- Add post-pipeline enrichment workflow section explaining the command sequence and data dependencies
- Update the "Output Artifacts" section to include all 12+ artifacts from the full pipeline
- Update the OpenClaw worked example to include post-pipeline enrichment steps
- Correct agent count from 14 to 15 (Feature 035 added `risk-scorer.md`)
- Update infographic template references from `infographic-corporate-white.md` to current names (`infographic-baseball-card.md`, `infographic-system-architecture.md`) per Feature 039 rename

### FR-2: Rename Prompt Specification

**Description**: Rename `GUIDE_PROMPT.md` to a customer-friendly filename.

**Rationale**: `GUIDE_PROMPT.md` communicates an internal implementation detail (it's a prompt). End users need a filename that communicates purpose. The prompt spec stays in `docs/guides/prompts/` as its source location.

**New Name**: `docs/guides/prompts/developer-guide-prompt.md` (kebab-case per project conventions).

### FR-3: Update Existing Developer Guide

**Description**: Update the existing developer guide at `docs/guides/DEVELOPER_GUIDE_TACHI.md` with the missing post-pipeline command sections.

**Rationale**: The README already references this path in the Integration Reference table. The guide already exists as a 1,366-line document with complete structure (Quick Start, 9 Comprehensive Guide sections, 3 appendices, OpenClaw worked example). The approach is **targeted update, not regeneration from scratch**, to preserve existing quality improvements and content not in the prompt spec (e.g., 1Password CLI setup, `.env.example` references, expanded Gemini key options).

**Current State of Existing Guide**: The guide covers `/threat-model` comprehensively but is missing:
- Dedicated `/risk-score` command workflow section
- Dedicated `/compensating-controls` command workflow section
- `/infographic` as a standalone command (only covered as part of `/threat-model` pipeline)
- Post-pipeline enrichment workflow section
- Quick Start coverage of all 4 commands (currently only covers `/threat-model`)
- Output interpretation for risk-scores.md and compensating-controls.md
- Appendix B references for post-pipeline output file structures

**Update Process**:
1. Read the existing guide to identify precise insertion points
2. Add missing sections for `/risk-score`, `/compensating-controls`, `/infographic`
3. Add post-pipeline enrichment workflow section
4. Update Quick Start to reference all 4 commands
5. Update Appendix B with post-pipeline output file structures
6. Review for consistency with existing content and actual tachi behavior
7. Validate Quick Start flow end-to-end

### FR-4: Quick Start Section

**Description**: The guide must begin with a Quick Start section (target: ~800 words / 2 pages) that gets a new user from zero to first threat model in 5 steps.

**Structure**:
1. Prerequisites (Claude Code, optional Gemini key)
2. Install tachi (clone + copy commands)
3. Verify installation (ls commands)
4. Create architecture file (simple 3-component example)
5. Run `/threat-model`
6. Read results (where to find outputs, what to look at first)

### FR-5: Full Pipeline Walkthrough

**Description**: The comprehensive guide must cover the complete end-to-end workflow including all 4 commands.

**Pipeline Sequence**:
1. Create architecture description
2. Run `/threat-model` (produces threats.md, threats.sarif, threat-report.md, attack-trees/)
3. Run `/risk-score` (produces risk-scores.md, risk-scores.sarif)
4. Run `/compensating-controls` (produces compensating-controls.md, compensating-controls.sarif)
5. Run `/infographic` (produces spec files and .jpg images)

**Data Dependencies**:
- `/risk-score` requires `threats.md` as input
- `/compensating-controls` requires `risk-scores.md` as input
- `/infographic` auto-detects richest source (prefers risk-scores.md over threats.md)

---

## Scope & Boundaries

### In Scope (P0 -- Must Have)

- Update `GUIDE_PROMPT.md` to cover `/risk-score`, `/compensating-controls`, `/infographic`
- Rename `GUIDE_PROMPT.md` to `developer-guide-prompt.md`
- Generate and publish `DEVELOPER_GUIDE_TACHI.md` from the updated prompt spec
- Quick Start section at the top of the generated guide
- Full pipeline walkthrough covering all 4 commands
- OpenClaw worked example extended with post-pipeline enrichment
- Output interpretation for all 12+ artifacts
- Both integration paths documented (Standalone + AOD Lifecycle)
- Troubleshooting and FAQ section

### Out of Scope

- Video tutorials or screencasts
- Interactive/web-based guide (static markdown only)
- Translations to other languages
- Changes to tachi commands or agents (documentation only)
- Changes to README.md Quick Start (the guide supplements, not replaces, the README)
- CI/CD integration tutorials beyond what GUIDE_PROMPT.md already specifies
- New example architectures beyond what exists in `examples/`

### Assumptions

- The existing GUIDE_PROMPT.md is accurate for `/threat-model` content (~80% of the guide)
- Features 035, 036, and 039 are stable and delivered (confirmed -- all three are in Delivered status)
- The OpenClaw worked example in GUIDE_PROMPT.md is suitable for extension with post-pipeline steps
- `docs/guides/DEVELOPER_GUIDE_TACHI.md` is the correct publication path (confirmed -- README references it)

### Constraints

- **Content only**: No code changes, no agent modifications, no command changes
- **Single document**: The guide is one markdown file, not a multi-page site
- **Prompt-driven generation**: The guide is generated from the prompt spec, not written directly -- the prompt spec is the source of truth

---

## User Experience Requirements

### Key User Flows

#### Flow 1: First-Time User (Quick Start)
1. User installs tachi (clone + copy)
2. User creates a simple architecture file
3. User runs `/threat-model`
4. User reads `threats.md` Section 7 (Recommended Actions)
5. User decides whether to continue to full guide

#### Flow 2: Full Pipeline Execution
1. User creates/maintains architecture description
2. User runs `/threat-model` -- reviews structured findings
3. User runs `/risk-score` -- reviews quantitative scores
4. User runs `/compensating-controls` -- reviews existing defenses and gaps
5. User runs `/infographic` -- generates visual reports for stakeholders
6. User prioritizes remediation based on combined insights

#### Flow 3: Output Interpretation
1. User has generated outputs from one or more commands
2. User opens the guide's interpretation section for that command
3. User reads annotated examples explaining each section of the output
4. User understands what to act on and in what priority order

### Information Architecture
- Quick Start at top (immediate value)
- Comprehensive guide below (depth on demand)
- Appendices at end (reference material)
- Each section answers "what do I do?" before "why does this matter?"

---

## Non-Functional Requirements

### Accessibility
- Standard markdown formatting (renders in any markdown viewer)
- No images required for comprehension (images supplement text, not replace it)
- Code blocks are copy-pasteable
- All acronyms defined on first use

### Quality Standards
- Accurate to tachi's actual behavior (commands, flags, output formats)
- Tested: a developer can follow the guide end-to-end and produce the expected outputs
- No broken internal references (section links, file paths)
- Professional tone, beginner-friendly language, no emojis

---

## Success Metrics

### Primary Metrics

**Metric 1**: Guide completeness
- **Definition**: All 4 commands documented with invocation, flags, output artifacts, and interpretation
- **Target**: 100% coverage of the pipeline
- **Timeline**: At delivery

**Metric 2**: Quick Start effectiveness
- **Definition**: A new user can follow the Quick Start and produce a threat model
- **Target**: Achievable in under 5 minutes (assuming Claude Code already installed)
- **Timeline**: At delivery, validated by walkthrough

**Metric 3**: Path accuracy
- **Definition**: `docs/guides/DEVELOPER_GUIDE_TACHI.md` exists and is referenced from README.md
- **Target**: README link resolves to the published guide
- **Timeline**: At delivery

---

## Timeline & Milestones

### Phase 1: Prompt Spec Update + Guide Generation (Single Phase)

- **Step 1**: Update GUIDE_PROMPT.md with /risk-score, /compensating-controls, /infographic sections
- **Step 2**: Rename GUIDE_PROMPT.md to developer-guide-prompt.md
- **Step 3**: Generate DEVELOPER_GUIDE_TACHI.md from updated prompt spec
- **Step 4**: Review generated guide for accuracy
- **Step 5**: Validate Quick Start flow end-to-end
- **Deliverable**: Published guide at docs/guides/DEVELOPER_GUIDE_TACHI.md

---

## Risks & Dependencies

### Risks

**Risk 1**: Generated guide drifts from actual tachi behavior
- **Likelihood**: Medium
- **Impact**: High
- **Mitigation**: Review generated guide section-by-section against actual command behavior; validate code examples by running them

**Risk 2**: Guide length becomes unwieldy
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Quick Start provides immediate value; comprehensive sections are for reference, not linear reading

### Dependencies

**Internal Dependencies**:
- Feature 035 (Risk Scoring): Delivered
- Feature 036 (Compensating Controls): Delivered
- Feature 039 (Standalone Infographic): Delivered
- Existing GUIDE_PROMPT.md: Exists at ~80% completion

**External Dependencies**: None

---

## Open Questions

- [x] What is the final publication path? -- `docs/guides/DEVELOPER_GUIDE_TACHI.md` (confirmed from README.md)
- [x] Are Features 035, 036, 039 stable? -- Yes, all three are in Delivered status per INDEX.md

---

## References

### Product Documentation
- Product Vision: [docs/product/01_Product_Vision/product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- GitHub Issue: [#45](https://github.com/davidmatousek/tachi/issues/45)

### Existing Assets
- Prompt Specification: [docs/guides/prompts/GUIDE_PROMPT.md](docs/guides/prompts/GUIDE_PROMPT.md)
- Example Architectures: [examples/](examples/)
- README Quick Start: [README.md](README.md)
- Interface Contract: [docs/INTERFACE-CONTRACT.md](docs/INTERFACE-CONTRACT.md)
