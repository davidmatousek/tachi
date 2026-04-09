---
prd:
  number: 121
  topic: rename-tachi-commands-to-namespace
  created: 2026-04-09
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-09, status: approved, notes: "PRD authored by PM; scope and user value validated"}
  architect_signoff: {agent: architect, date: 2026-04-09, status: approved_with_concerns, notes: "Technical approach sound. Concerns: scope understated (163+ files vs 50+), adapters/scripts/templates/schemas missing from inventory. Address in spec."}
  techlead_signoff: {agent: team-lead, date: 2026-04-09, status: approved_with_concerns, notes: "Feasible single-PR delivery, 2-3 hours. Concerns: adapter command files missing from rename mapping, Issue #120 content scope must be bounded. 3-wave execution plan."}
source:
  idea_id: 121
  story_id: null
---

# Rename Tachi Commands to tachi.* Namespace - Product Requirements Document

**Status**: Approved
**Created**: 2026-04-09
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P0 (Critical)

---

## Executive Summary

### The One-Liner
Give every tachi pipeline command a `tachi.*` namespace prefix so they don't collide with customer commands when installed into projects.

### Problem Statement
Tachi's five pipeline commands (`/threat-model`, `/risk-score`, `/compensating-controls`, `/infographic`, `/security-report`) use generic, unprefixed names. When tachi is installed as a template into a customer project, these names can collide with customer-defined commands. The AOD lifecycle commands already follow the `aod.*` namespace convention, but tachi pipeline commands do not. This inconsistency also makes command discovery harder — users can't type `/tachi.` to see all available pipeline commands.

### Proposed Solution
Rename all tachi pipeline commands to the `tachi.*` namespace, matching the established `aod.*` pattern. Update all cross-references across commands, agents, skills, documentation, and examples. Include the new `/tachi.architecture` command (Issue #120) in the namespace from the start.

### Success Criteria
- All 6 tachi pipeline commands use `tachi.*` namespace
- Zero broken cross-references after rename
- All 6 example threat models validated with new command names
- CLAUDE.md, README.md, and all guides reference new names
- Existing installations receive clear migration guidance

### Timeline
Single-phase delivery — all renames shipped together as one atomic change.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [docs/product/01_Product_Vision/product-vision.md](docs/product/01_Product_Vision/product-vision.md)

Tachi's vision is to be "the default threat modeling toolkit for any team building agentic AI applications." For tachi to be installed cleanly into diverse customer projects, its commands must not collide with existing project commands. Namespace prefixing is a prerequisite for reliable third-party adoption.

### Roadmap Fit
This is a P0 foundational change that should land before any new command additions. It establishes the naming convention that all future tachi commands will follow.

---

## Target Users & Personas

### Primary Persona: Developer Installing Tachi

**Role**: Software developer or DevSecOps engineer
**Experience**: Familiar with CLI tools and agent frameworks
**Goals**: Install tachi into their project and run threat analysis without conflicts
**Pain Points**: Generic command names clash with project-specific commands; no clear namespace makes command discovery difficult

**Why This Matters to Them**: After renaming, typing `/tachi.` reveals all pipeline commands via autocomplete, and no collisions occur with their existing `/threat-model` or `/security-report` commands.

### Secondary Persona: Tachi Contributor

**Role**: Open-source contributor extending tachi
**Goals**: Add new commands following clear conventions
**Pain Points**: Unclear whether new commands should be prefixed or not

**Why This Matters to Them**: The `tachi.*` namespace establishes a clear, documented pattern for all future command additions.

---

## User Stories

### US-1: Namespace-Prefixed Command Invocation
**When**: I have tachi installed in my project alongside my own custom commands
**I want to**: Invoke tachi pipeline commands using `tachi.*` prefixed names
**So I can**: Avoid collisions with my project's commands that may share generic names like `/threat-model`

**Acceptance Criteria**:
- Given tachi is installed, when I run `/tachi.threat-model`, then the threat modeling pipeline executes
- Given tachi is installed, when I run `/tachi.risk-score`, then quantitative risk scoring executes
- Given tachi is installed, when I run `/tachi.compensating-controls`, then control analysis executes
- Given tachi is installed, when I run `/tachi.infographic`, then infographic generation executes
- Given tachi is installed, when I run `/tachi.security-report`, then PDF report generation executes
- Given tachi is installed, when I run `/tachi.architecture`, then architecture description generation executes

**Priority**: P0
**Effort**: M

### US-2: Command Discovery via Namespace
**When**: I'm exploring tachi's capabilities in my IDE
**I want to**: Type `/tachi.` and see all available pipeline commands
**So I can**: Quickly discover and select the right command without consulting docs

**Acceptance Criteria**:
- Given tachi is installed, when I type `/tachi.` in my IDE command palette, then all 6 pipeline commands appear as completions

**Priority**: P1
**Effort**: S (achieved automatically by the rename)

### US-3: Cross-Reference Integrity
**When**: I follow documentation or agent instructions that reference tachi commands
**I want to**: All references to use the new `tachi.*` names consistently
**So I can**: Copy-paste command names from docs without encountering "command not found" errors

**Acceptance Criteria**:
- Given the rename is complete, when I search for old command names (`/threat-model`, `/risk-score`, etc.) across the entire codebase, then zero matches remain (outside of migration notes or historical PRDs)
- Given the rename is complete, when I search for new command names (`/tachi.threat-model`, etc.), then all commands, agents, skills, and docs reference the new names

**Priority**: P0
**Effort**: L

### US-4: Clean Upgrade Without Duplicate Commands
**When**: I have an existing tachi installation and upgrade to the new version
**I want to**: End up with only the new `tachi.*` commands, not duplicates of old and new
**So I can**: Avoid confusion from having both `/threat-model` and `/tachi.threat-model` in my project

**Acceptance Criteria**:
- Given I have an existing installation with old command names, when I run the install script, then old command files (`threat-model.md`, `risk-score.md`, `compensating-controls.md`, `infographic.md`, `security-report.md`) are removed from my `.claude/commands/`
- Given I have an existing installation, when I run the install script, then only `tachi.*` prefixed commands exist in `.claude/commands/` (no duplicates)
- Given the install script adds cleanup logic, when a fresh install is performed (no old files exist), then the cleanup runs silently with no errors

**Priority**: P0
**Effort**: M

### US-5: Migration Guidance for Existing Users
**When**: I have an existing installation using the old command names
**I want to**: Understand what changed and how to update my workflow
**So I can**: Transition to the new names without confusion

**Acceptance Criteria**:
- Given the rename is shipped, when I read the CHANGELOG or migration notes, then I find a clear mapping from old → new command names
- Given the rename is shipped, when I run an old command name, then I get a clear error (standard "command not found" behavior — no special backward-compat shim needed)

**Priority**: P1
**Effort**: S

---

## Functional Requirements

### Core Capabilities

#### R1: Command File Renames
**Description**: Rename 5 existing command markdown files in `.claude/commands/` and include the new architecture command.

**Rename Mapping**:

| Directory | Current File | New File |
|-----------|-------------|----------|
| `.claude/commands/` | `threat-model.md` | `tachi.threat-model.md` |
| `.claude/commands/` | `risk-score.md` | `tachi.risk-score.md` |
| `.claude/commands/` | `compensating-controls.md` | `tachi.compensating-controls.md` |
| `.claude/commands/` | `infographic.md` | `tachi.infographic.md` |
| `.claude/commands/` | `security-report.md` | `tachi.security-report.md` |
| `.claude/commands/` | *(new — Issue #120)* | `tachi.architecture.md` |
| `adapters/claude-code/commands/` | `threat-model.md` | `tachi.threat-model.md` |
| `adapters/claude-code/commands/` | `infographic.md` | `tachi.infographic.md` |
| `adapters/claude-code/commands/` | `risk-score.md` | `tachi.risk-score.md` |
| `adapters/github-actions/` | `tachi-threat-model.yml` | `tachi.threat-model.yml` |

**Business Rules**:
- Old command files are deleted (no symlinks, no backward-compat wrappers)
- New files retain identical content except for updated internal cross-references
- The `tachi.architecture` command is created as part of this feature (scope from Issue #120; content must be bounded or stubbed)
- Adapter command copies follow the same rename pattern as primary commands

#### R2: Cross-Reference Updates
**Description**: Update all references to the old command names across the entire codebase.

**Affected Surfaces** (identified via codebase scan — ~160+ files total):

| Surface | File Count | Examples |
|---------|-----------|---------|
| Commands (`.claude/commands/`) | 5 | Internal cross-references between pipeline commands |
| Agents (`.claude/agents/tachi/`) | 4 | `control-analyzer.md`, `report-assembler.md`, `risk-scorer.md`, `threat-infographic.md` |
| Agents (root `agents/`) | 2 | `orchestrator.md`, `threat-infographic.md` |
| Skills (`.claude/skills/tachi-*/`) | 13 | `tachi-control-analysis/`, `tachi-infographics/`, `tachi-risk-scoring/`, `tachi-report-assembly/` |
| Adapters (`adapters/`) | 10 | `claude-code/commands/` (3 renames), `github-actions/` (1 rename + README + VERSION), `claude-code/agents/`, `copilot/`, `cursor/` |
| Templates (`templates/`) | 6 | Infographic templates (CTA text), output-schemas, security-report |
| Schemas (`schemas/`) | 4 | `finding.yaml`, `risk-scoring.yaml`, `compensating-controls.yaml`, `security-report.yaml` |
| Scripts (`scripts/`) | 2 | `extract-infographic-data.py` (user-facing error messages), `extract-report-data.py` |
| Docs (`docs/`) | 30+ | Guides, ADRs, architecture, devops, planning, research |
| Root files | 4 | `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `INSTALL_MANIFEST.md` |

**Business Rules**:
- Historical PRDs are NOT updated (they document what existed at the time)
- Historical specs (`specs/*/`) are NOT updated (same immutability policy as PRDs)
- Historical CHANGELOG entries are left as-is; a migration note is added at the top
- All other references must be updated to new names
- No "old name" aliases or fallbacks

#### R3: INSTALL_MANIFEST.md Update
**Description**: Update both the human-readable tables and the machine-parseable `<!-- BEGIN MANIFEST -->` section with new filenames.

**Current manifest entries to update** (lines 73-78):
```
.claude/commands/threat-model.md      → .claude/commands/tachi.threat-model.md
.claude/commands/risk-score.md        → .claude/commands/tachi.risk-score.md
.claude/commands/compensating-controls.md → .claude/commands/tachi.compensating-controls.md
.claude/commands/infographic.md       → .claude/commands/tachi.infographic.md
.claude/commands/security-report.md   → .claude/commands/tachi.security-report.md
(add)                                 → .claude/commands/tachi.architecture.md
```

#### R4: Upgrade Cleanup in Install Script
**Description**: Add a cleanup step to `scripts/install.sh` that removes deprecated command files from the target project before copying new files. Without this, consumers upgrading from a previous installation will end up with **duplicate commands** — both old unprefixed and new `tachi.*` prefixed versions.

**Implementation**:
- Add a deprecated-files list (either inline in install.sh or in a `DEPRECATED_FILES.md` manifest)
- Before the copy loop, iterate the deprecated list and `rm -f` each file from the target directory
- Log removals: `"Removed deprecated: .claude/commands/threat-model.md"`
- Silent no-op if file doesn't exist (fresh installs)

**Deprecated files to remove**:
```
.claude/commands/threat-model.md
.claude/commands/risk-score.md
.claude/commands/compensating-controls.md
.claude/commands/infographic.md
.claude/commands/security-report.md
```

#### R5: Example Documentation Updates
**Description**: Update all example threat model documentation to reference new command names where they appear.

#### R6: Guide and Documentation Updates
**Description**: Update ALL consumer-facing and developer-facing guides with new command names.

**Files requiring updates**:
- `docs/guides/DEVELOPER_GUIDE_TACHI.md` — primary developer walkthrough (distributed via install)
- `docs/guides/CONSUMER_GUIDE_TACHI.md` — consumer guide with pipeline workflow
- `docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md` — AOD integration guide
- `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md` — research guide
- `docs/guides/prompts/developer-guide-prompt.md` — prompt template for guide generation
- `README.md` — (~48 command references)
- `CLAUDE.md` — command reference section

#### R7: Skill CTA Text Updates
**Description**: Update user-facing CTA (call-to-action) strings embedded in skill reference files. These strings appear in generated output (e.g., infographic specifications) and will show old command names if not updated.

**Key files with CTA text**:
- `.claude/skills/tachi-infographics/references/template-specific-formats.md` — "Run `/compensating-controls`", "Run `/risk-score`"
- `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` — template loading paths
- All skill reference files containing `/threat-model`, `/risk-score`, `/compensating-controls`, `/infographic`, `/security-report`

#### R8: Migration Documentation
**Description**: Provide clear migration guidance for existing installations.

**Deliverables**:
- CHANGELOG entry with old → new mapping table
- Developer guide updated with new command names
- Consumer guide updated with new command names
- Install script now handles cleanup automatically (R4)

---

## Non-Functional Requirements

### Atomicity
All renames must be shipped in a single PR / commit sequence. Partial renames (where some commands use old names and others use new names) must never exist on `main`.

### Backward Compatibility
- Old command names will stop working immediately (standard behavior — no shims)
- This is acceptable because tachi is pre-1.0 and the install script (`scripts/install.sh`) delivers the full current state
- The CHANGELOG and migration notes provide the transition path

---

## Success Metrics

### Primary Metrics

**Zero Broken References**: After rename, `grep -r` for old command names (outside historical PRDs) returns 0 results.

**Example Validation**: All 6 example threat models pass validation with new command names.

**Install Script Integrity**: Fresh `scripts/install.sh` delivers correctly-named commands.

---

## Scope & Boundaries

### In Scope (P0)

- Rename 5 existing command files to `tachi.*` namespace
- Rename 3 adapter command copies in `adapters/claude-code/commands/`
- Create `tachi.architecture` command (Issue #120 — content bounded or stubbed)
- Update all cross-references across ~160+ files (commands, agents, skills, adapters, templates, schemas, scripts, docs)
- Update root files: `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `INSTALL_MANIFEST.md`
- Update `INSTALL_MANIFEST.md` machine-parseable section with new filenames
- Add deprecated-file cleanup to `scripts/install.sh` to prevent duplicate commands on upgrade
- Update all 5 consumer/developer guides and the guide generation prompt
- Update all skill CTA text that appears in generated output
- CHANGELOG migration entry with old-to-new mapping table
- Grep verification: zero old command name matches outside immutable historical artifacts

### Out of Scope

- Renaming AOD commands (already namespaced as `aod.*`)
- Renaming utility commands (`continue.md`, `execute.md`, etc.)
- Adding command aliases or backward-compatibility wrappers
- Renaming agent files or skill files (only their internal references change)
- Modifying historical PRDs (`docs/product/02_PRD/`) or archived specs (`specs/*/`)
- Modifying historical CHANGELOG entries (migration note added at top instead)

### Assumptions

- tachi is pre-1.0; breaking changes to command names are acceptable with documentation
- The `tachi.architecture` command scope is defined by Issue #120 and will be implemented as part of this feature
- Claude Code's command resolution uses the filename (dot-separated names work as namespace separators)

### Constraints

- All 6 renames must land atomically — no partial rename state on `main`
- Historical PRDs are immutable records and must not be modified

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Dot-separated command filenames may not resolve correctly in all Claude Code versions
- **Likelihood**: Low (the `aod.*` commands already use this pattern successfully)
- **Impact**: High (all commands would break)
- **Mitigation**: Verify with existing `aod.*` commands before starting; test first rename before bulk rename

**Risk 2**: Missed cross-references cause broken documentation or agent instructions
- **Likelihood**: Medium-High (~160+ files need updates)
- **Impact**: Medium (users encounter wrong command names in docs)
- **Mitigation**: Automated grep verification as final validation step; grep must cover both `/command-name` and `command-name.md` patterns, excluding `specs/*/` and historical PRDs; US-3 acceptance criteria enforce zero misses

**Risk 3**: Ghost CTA text in generated infographic output
- **Likelihood**: Certain (templates embed literal command names in CTA text)
- **Impact**: Low (cosmetic — users see old names in generated output)
- **Mitigation**: Update template CTA strings as part of cross-reference sweep

**Risk 4**: Adapter drift if adapter files missed
- **Likelihood**: Low (adapters now included in scope per reviewer feedback)
- **Impact**: Medium (non-Claude-Code platform users see old names)
- **Mitigation**: R1 rename mapping now includes adapter command files

**Risk 5**: Duplicate commands in consumer projects after upgrade
- **Likelihood**: Certain (install script only copies, never deletes)
- **Impact**: High (consumers see both old and new commands, causing confusion and potential invocation of stale commands)
- **Mitigation**: R4 adds deprecated-file cleanup step to install.sh; runs before copy loop; silent no-op on fresh installs

### Dependencies

**Issue #120 (tachi.architecture command)**: The new `/tachi.architecture` command is created as part of this rename. Its content spec is tracked in Issue #120.

---

## Open Questions

- [x] Does Claude Code support dot-separated command filenames? **Yes** — confirmed by existing `aod.*` commands
- [ ] Should the `execute.md` utility command also be namespaced? **Decision: No** — `execute` is a generic AOD utility, not tachi-specific
- [ ] Should example output directories reference command names? **Decision: No** — examples reference output files, not command names

---

## References

### Product Documentation
- Product Vision: [docs/product/01_Product_Vision/product-vision.md](docs/product/01_Product_Vision/product-vision.md)
- GitHub Issue: [#121 — Rename tachi commands to tachi.* namespace](https://github.com/davidmatousek/tachi/issues/121)
- Related Issue: [#120 — tachi.architecture command](https://github.com/davidmatousek/tachi/issues/120)

### Technical Documentation
- Constitution: [.aod/memory/constitution.md](.aod/memory/constitution.md)
- Architecture: [docs/architecture/README.md](docs/architecture/README.md)
- Developer Guide: [docs/guides/DEVELOPER_GUIDE_TACHI.md](docs/guides/DEVELOPER_GUIDE_TACHI.md)
- Consumer Guide: [docs/guides/CONSUMER_GUIDE_TACHI.md](docs/guides/CONSUMER_GUIDE_TACHI.md)
