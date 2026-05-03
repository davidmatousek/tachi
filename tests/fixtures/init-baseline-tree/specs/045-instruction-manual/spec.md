---
prd_reference: docs/product/02_PRD/045-instruction-manual-2026-03-28.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-03-28
    status: APPROVED
    notes: "All PRD requirements covered. 15 FRs trace to 5 PRD FRs. All 3 PRD user stories addressed with expanded acceptance criteria. 1 minor note: troubleshooting not listed in spec In Scope but covered by existing guide content."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: End-to-End tachi Instruction Manual

**Feature Branch**: `045-instruction-manual`
**Created**: 2026-03-28
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/045-instruction-manual-2026-03-28.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete Pipeline Guide (Priority: P1)

A security analyst has tachi installed and wants to analyze an application's architecture. They need a step-by-step guide that walks them through the complete 4-command workflow: `/threat-model` to produce structured findings, `/risk-score` to add quantitative scores, `/compensating-controls` to detect existing defenses and identify gaps, and `/infographic` to generate visual reports. The guide must explain the data dependencies between commands so the analyst never has to guess which command runs next or what input it requires.

**Why this priority**: Without the full pipeline documented, users stop after `/threat-model` and never discover the enrichment commands. The pipeline guide is the core value of this feature.

**Independent Test**: A developer with no prior tachi knowledge can follow the guide from architecture description through all 4 commands and produce all 12+ output artifacts.

**Acceptance Scenarios**:

1. **Given** a user has the guide open and an architecture file ready, **When** they follow the pipeline walkthrough from start to finish, **Then** they produce threats.md, threats.sarif, threat-report.md, attack-trees/, risk-scores.md, risk-scores.sarif, compensating-controls.md, compensating-controls.sarif, and infographic spec/image files
2. **Given** the guide covers `/risk-score`, **When** the user reads the invocation section, **Then** the exact command syntax and required input (threats.md) are shown in a copy-pasteable code block
3. **Given** the guide covers `/compensating-controls`, **When** the user reads the invocation section, **Then** the required input (risk-scores.md) and optional target codebase flag are documented
4. **Given** the guide covers `/infographic`, **When** the user reads the invocation section, **Then** the auto-detection behavior (prefers risk-scores.md over threats.md) and template selection flags are documented
5. **Given** the guide includes a pipeline overview, **When** the user reads the data flow section, **Then** they see a diagram showing all 4 commands with their inputs, outputs, and dependencies

---

### User Story 2 - Output Interpretation (Priority: P1)

A user has generated output from one or more commands and needs to understand what each file contains, what each section means, and what to act on first. The guide must explain how to read and interpret output artifacts from all 4 commands, including the 4 risk scoring dimensions (CVSS, exploitability, scalability, reachability), residual risk from compensating controls analysis, and infographic visual elements.

**Why this priority**: Output without interpretation is noise. Users who cannot interpret results cannot act on them, making the tool useless regardless of how well it runs.

**Independent Test**: A user with generated output files can open the guide's interpretation section for any command and understand what each section of the output means without additional documentation.

**Acceptance Scenarios**:

1. **Given** the guide covers threats.md output, **When** the user reads the interpretation section, **Then** all 7 sections plus Section 4a are explained with annotated examples
2. **Given** the guide covers risk-scores.md, **When** the user reads the scoring section, **Then** each of the 4 scoring dimensions is explained with what it measures, score range, and what high/low scores mean
3. **Given** the guide covers compensating-controls.md, **When** the user reads the controls section, **Then** control detection, control mapping, effectiveness assessment, residual risk calculation, and recommendations are all explained
4. **Given** findings have risk levels, **When** the user reads the prioritization guidance, **Then** they understand to prioritize Critical over High over Medium over Low

---

### User Story 3 - Quick Start (Priority: P1)

A first-time user wants to evaluate tachi quickly without reading the full guide. A Quick Start section at the top of the guide gets them from installation to their first threat model in under 5 minutes with 5-6 steps and copy-pasteable commands. The Quick Start introduces all 4 commands so users know the full pipeline exists, even though the detailed walkthrough is deeper in the guide.

**Why this priority**: First impressions determine adoption. A fast path to value lets users evaluate the tool before investing time in the comprehensive guide.

**Independent Test**: A user with Claude Code installed can follow the Quick Start and produce a working threat model in under 5 minutes.

**Acceptance Scenarios**:

1. **Given** a user has Claude Code installed and tachi cloned, **When** they follow the Quick Start, **Then** they complete installation, create an architecture file, and run `/threat-model` in 5-6 steps
2. **Given** the Quick Start is at the top of the guide, **When** the user finishes it, **Then** they have a working threat model and clear pointers to sections covering `/risk-score`, `/compensating-controls`, and `/infographic`
3. **Given** the Quick Start references commands, **When** a command is mentioned, **Then** the exact invocation syntax is shown as a copy-pasteable code block

---

### User Story 4 - Prompt Specification Update (Priority: P1)

The prompt specification (`GUIDE_PROMPT.md`) is the source of truth for guide generation. It must be updated to cover the full 4-command pipeline before the guide can be updated. The updated spec must include sections for `/risk-score`, `/compensating-controls`, standalone `/infographic`, the post-pipeline enrichment workflow, corrected agent count (15, not 14), and current infographic template names.

**Why this priority**: The prompt spec is the source of truth. Updating the guide without updating the spec creates drift that makes future maintenance unreliable. This is a prerequisite for the guide update.

**Independent Test**: The updated prompt spec can be read and covers all 4 commands with invocation, flags, output artifacts, and interpretation guidance.

**Acceptance Scenarios**:

1. **Given** the prompt spec exists at `docs/guides/prompts/GUIDE_PROMPT.md`, **When** the update is complete, **Then** sections for `/risk-score`, `/compensating-controls`, and standalone `/infographic` are present
2. **Given** the prompt spec references agents, **When** the agent count is stated, **Then** it reads 15 (not 14)
3. **Given** the prompt spec references infographic templates, **When** template names appear, **Then** they use current names (`infographic-baseball-card.md`, `infographic-system-architecture.md`)
4. **Given** the updated prompt spec, **When** the rename is applied, **Then** the file exists at `docs/guides/prompts/developer-guide-prompt.md`

---

### User Story 5 - OpenClaw Worked Example Extension (Priority: P2)

The existing OpenClaw worked example covers `/threat-model` output in detail. It must be extended to show the complete pipeline: running `/risk-score` on the OpenClaw threats, running `/compensating-controls` on the scored results, and generating infographics from the enriched data. This provides continuity through a single, familiar example rather than introducing new architectures.

**Why this priority**: A single worked example that progresses through all 4 commands is more valuable than separate examples per command. Continuity reduces cognitive load.

**Independent Test**: The worked example section shows OpenClaw output from all 4 commands with annotated examples.

**Acceptance Scenarios**:

1. **Given** the existing OpenClaw example covers `/threat-model`, **When** the extension is complete, **Then** it also shows `/risk-score` invocation and sample output interpretation
2. **Given** the extended example, **When** the user reads the `/compensating-controls` step, **Then** they see residual risk calculation for OpenClaw findings
3. **Given** the extended example, **When** the user reads the `/infographic` step, **Then** they see template selection and output description for OpenClaw

---

### User Story 6 - Appendix Updates (Priority: P2)

The guide's appendices must be updated to include output file structures for all post-pipeline artifacts: risk-scores.md sections, risk-scores.sarif schema, compensating-controls.md sections, compensating-controls.sarif schema, and infographic spec/image file naming conventions.

**Why this priority**: Reference material is consulted repeatedly during actual use. Incomplete reference sections reduce the guide's long-term utility.

**Independent Test**: A user looking up the structure of any output file can find it in Appendix B.

**Acceptance Scenarios**:

1. **Given** the guide has Appendix B (Output File Reference), **When** the user looks up risk-scores.md, **Then** its sections and fields are documented
2. **Given** Appendix B, **When** the user looks up compensating-controls.md, **Then** its sections (control detection, mapping, effectiveness, residual risk, recommendations) are documented
3. **Given** Appendix B, **When** the user looks up infographic outputs, **Then** both the spec file and image file naming conventions are documented

---

### Edge Cases

- What if the user runs `/risk-score` before `/threat-model`? The guide must explain that `/risk-score` requires `threats.md` as input and direct the user to run `/threat-model` first.
- What if the user runs `/infographic` without running `/risk-score` first? The guide must explain that `/infographic` auto-detects the richest available data source and will fall back to `threats.md` if `risk-scores.md` is absent.
- What if the user does not have a Gemini API key? The guide must explain that `/infographic` produces spec files without a key but requires a Gemini API key for image generation.
- What if the guide references file paths that changed between tachi versions? The guide must use paths consistent with the current tachi version and avoid hardcoded absolute paths.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The prompt specification at `docs/guides/prompts/GUIDE_PROMPT.md` MUST be updated to include `/risk-score` command documentation (invocation, flags, output artifacts, scoring dimensions)
- **FR-002**: The prompt specification MUST be updated to include `/compensating-controls` command documentation (invocation, flags, output artifacts, residual risk calculation)
- **FR-003**: The prompt specification MUST be updated to include standalone `/infographic` command documentation (invocation, template selection, auto-detection of richest data source)
- **FR-004**: The prompt specification MUST be updated to include a post-pipeline enrichment workflow section explaining the 4-command sequence and data dependencies
- **FR-005**: The prompt specification MUST correct the agent count from 14 to 15 and update infographic template names to current values
- **FR-006**: The prompt specification MUST be renamed from `GUIDE_PROMPT.md` to `developer-guide-prompt.md` (kebab-case per project conventions)
- **FR-007**: The developer guide at `docs/guides/DEVELOPER_GUIDE_TACHI.md` MUST be updated with dedicated sections for `/risk-score`, `/compensating-controls`, and standalone `/infographic`
- **FR-008**: The developer guide MUST include a post-pipeline enrichment workflow section with a data flow diagram showing all 4 commands, their inputs, outputs, and dependencies
- **FR-009**: The Quick Start section MUST introduce all 4 commands and get a new user to their first threat model in under 5 minutes
- **FR-010**: The OpenClaw worked example MUST be extended to cover all 4 commands in sequence
- **FR-011**: Appendix B (Output File Reference) MUST include structures for risk-scores.md, risk-scores.sarif, compensating-controls.md, and compensating-controls.sarif
- **FR-012**: Each new command section MUST follow a consistent template: Prerequisites, Invocation, Outputs, Interpretation, Next Step
- **FR-013**: All acronyms MUST be defined on first use (STRIDE, CVSS, SARIF, etc.)
- **FR-014**: All command invocations MUST be shown as copy-pasteable code blocks with both minimal and flagged variants
- **FR-015**: The guide MUST document both integration paths: Standalone and AOD Lifecycle

### Key Entities

- **Prompt Specification**: The source-of-truth document that defines guide content, structure, and requirements. Located at `docs/guides/prompts/` (renamed from `GUIDE_PROMPT.md` to `developer-guide-prompt.md`)
- **Developer Guide**: The published guide artifact generated from the prompt spec. Located at `docs/guides/DEVELOPER_GUIDE_TACHI.md`. Referenced from README.md.
- **Output Artifacts**: The 12+ files produced by the 4-command pipeline (threats.md, threats.sarif, threat-report.md, attack-trees/, risk-scores.md, risk-scores.sarif, compensating-controls.md, compensating-controls.sarif, infographic specs, infographic images)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The published guide at `docs/guides/DEVELOPER_GUIDE_TACHI.md` covers all 4 commands with invocation syntax, flags, output artifacts, and interpretation guidance (100% pipeline coverage)
- **SC-002**: A developer with no prior tachi knowledge can follow the Quick Start and produce a threat model in under 5 minutes
- **SC-003**: The guide documents all 12+ output artifacts with at least one annotated example per artifact type
- **SC-004**: All internal file path references in the guide resolve correctly (zero broken links)
- **SC-005**: The prompt specification at `docs/guides/prompts/developer-guide-prompt.md` covers the same 4-command pipeline as the guide (spec-guide parity)
- **SC-006**: The README.md link to `docs/guides/DEVELOPER_GUIDE_TACHI.md` resolves to the published guide

## Assumptions

- Features 035 (Risk Scoring), 036 (Compensating Controls), and 039 (Standalone Infographic) are stable and delivered -- confirmed from PRD INDEX.md
- The existing GUIDE_PROMPT.md is accurate for `/threat-model` content (~80% of total guide content)
- The existing DEVELOPER_GUIDE_TACHI.md structure is sound and does not need reorganization -- gap is content coverage, not architecture
- The OpenClaw worked example is suitable for extension with post-pipeline steps
- The approach is targeted update (add missing sections) rather than full regeneration, preserving existing quality improvements in the guide not present in the prompt spec
- This is a documentation-only deliverable with no code changes, no agent modifications, and no command changes

## Scope Boundaries

### In Scope
- Update prompt specification with 3 new command sections and pipeline workflow
- Rename prompt specification to customer-friendly filename
- Update developer guide with 3 new command sections, pipeline workflow, Quick Start enhancements, and appendix updates
- Extend OpenClaw worked example through all 4 commands
- Validate all file path references and internal links

### Out of Scope
- Video tutorials or screencasts
- Interactive or web-based guide
- Translations to other languages
- Changes to tachi commands, agents, or code
- Changes to README.md Quick Start
- New example architectures
- CI/CD integration tutorials beyond what the prompt spec already specifies
