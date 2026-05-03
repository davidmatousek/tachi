---
prd:
  number: 120
  topic: architecture-lifecycle-command
  created: 2026-04-09
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-09, status: APPROVED, notes: "PRD authored by PM — self-approved as drafter"}
  architect_signoff: {agent: architect, date: 2026-04-09, status: APPROVED_WITH_CONCERNS, notes: "7 findings (0 blocking): archive inherits parent .gitignore status (Low), snapshot integration point needs precision — specify after Step 1.3 before Step 2 (Medium). Frontmatter schema, orchestrator compatibility, two-part approach, guided update mode all approved."}
  techlead_signoff: {agent: team-lead, date: 2026-04-09, status: APPROVED_WITH_CONCERNS, notes: "4 concerns (0 blocking): SHA-256 checksum needs explicit tool invocation in command file (Medium), archive path derivation must be relative to file parent dir (Low), proceed with fixed convention for MVP (Low), validation must confirm examples without frontmatter still work (Informational). 3 waves, 75 min realistic estimate."}
source:
  idea_id: 120
  story_id: null
---

# Architecture Lifecycle Command — Product Requirements Document

**Status**: Approved
**Created**: 2026-04-09
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1
**Parent Feature**: 074 (Baseline-Aware Pipeline)

---

## Executive Summary

### The One-Liner
Give architecture files a version history so every threat model knows exactly which architecture produced it.

### Problem Statement
Old threat models lose reference to the architecture that produced them. Architecture files (`docs/security/architecture.md`) have no versioning metadata, no archive history, and no audit trail. The current `/tachi.architecture` command generates architecture descriptions but treats them as disposable — each run overwrites the previous file with no record of what changed. Feature 074 introduced baseline-aware threat detection with delta annotations (`[NEW]`, `[UNCHANGED]`, `[RESOLVED]`), but there is no corresponding "architecture version changed" signal. When a security engineer reviews a threat model from two months ago, there is no way to confirm which architecture version was analyzed or what has changed since.

### Proposed Solution
Two-part approach:

**Part 1 — Enhance `/tachi.architecture` with lifecycle management (standalone)**:
- Add YAML frontmatter to architecture files (version, date, change description, checksum)
- Archive previous versions before overwriting (`docs/security/.archive/vN/architecture.md`)
- Walk users through guided updates (new services, removed components, updated data flows)
- Auto-increment version on each update

**Part 2 — Embed snapshot in `/tachi.threat-model` (automatic)**:
- Before invoking the orchestrator, copy the current `architecture.md` into the timestamped output folder
- Every threat model run becomes self-contained — architecture + threats + reports in one folder
- No new flags, no new workflow — transparent integration with existing pipeline

### Success Criteria
- Architecture files contain YAML frontmatter with version, date, and change description
- Previous architecture versions are archived and retrievable
- Every threat model output folder contains the architecture snapshot that produced it
- Running `/tachi.architecture` on an existing file preserves version history (auto-increment)
- Downstream pipeline stages (risk-scores, controls, infographics, PDF) are unaffected — snapshot is informational

### Timeline
Single implementation phase targeting completion within the current development cycle.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

Architecture lifecycle management directly supports tachi's mission as an automated threat modeling toolkit. Threat models are only useful if traceable to the architecture they analyzed. Without versioning, tachi produces point-in-time snapshots with no continuity — users cannot track how their architecture evolves, which changes introduced new threats, or which version was assessed for compliance. This feature closes the traceability gap between architecture evolution and threat model output.

### Dependency Context
This feature builds on two existing capabilities:
- **Feature 074** (Baseline-Aware Pipeline): Provides delta detection for threat findings but has no architecture versioning signal
- **Feature 121** (tachi.* Namespace): Established `/tachi.architecture` as a named command in the tachi namespace

---

## Target Users & Personas

### Primary Persona: Security Engineer
- **Role**: Runs periodic threat model scans on evolving architectures
- **Goal**: Trace every threat model to the exact architecture that produced it; track architecture evolution over time
- **Pain Point**: Architecture files are overwritten on each update with no history — when reviewing old threat models, cannot determine which architecture version was analyzed

### Secondary Persona: Compliance Auditor
- **Role**: Reviews security assessment artifacts for regulatory compliance
- **Goal**: Verify that threat models were produced against documented, versioned architectures
- **Pain Point**: No audit trail for architecture changes — cannot demonstrate which architecture version was assessed at what point in time

### Tertiary Persona: Engineering Manager
- **Role**: Tracks security posture across releases
- **Goal**: Understand which architecture changes introduced new threat surfaces
- **Pain Point**: No correlation between architecture changes and threat model deltas — impossible to determine if a new threat was introduced by an architecture change or a detection improvement

---

## User Stories

### US-120-1: Architecture Version Tracking
**When** I update my architecture description after adding a new service,
**I want to** have the previous version preserved with version metadata,
**So I can** trace which architecture version was analyzed by each threat model run.

**Acceptance Criteria**:
- **Given** an existing `architecture.md` without frontmatter, **when** I run `/tachi.architecture`, **then** the output file contains YAML frontmatter with `version: 1`, `date`, and `description` fields
- **Given** an existing `architecture.md` with `version: 3` frontmatter, **when** I run `/tachi.architecture`, **then** the output file has `version: 4` and the previous version is archived
- **Given** a freshly generated architecture file, **when** I inspect the frontmatter, **then** it contains a SHA-256 content checksum for integrity verification

**Priority**: P0
**Effort**: M

### US-120-2: Architecture Archive
**When** my architecture changes over time,
**I want to** access previous versions from a structured archive,
**So I can** compare what changed between threat model runs and satisfy audit requirements.

**Acceptance Criteria**:
- **Given** an architecture file at `docs/security/architecture.md` with `version: 3`, **when** I run `/tachi.architecture` to update it, **then** the v3 file is copied to `docs/security/.archive/v3/architecture.md`
- **Given** an archive directory with v1, v2, v3, **when** I list the archive, **then** each version is in its own numbered subfolder with the original frontmatter intact
- **Given** a first-time generation (no existing file), **when** I run `/tachi.architecture`, **then** no archive operation occurs (v1 is the initial version)

**Priority**: P0
**Effort**: S

### US-120-3: Automatic Architecture Snapshot in Threat Model Runs
**When** I run `/tachi.threat-model`,
**I want to** have the current architecture automatically copied into the output folder,
**So I can** always see which architecture was analyzed alongside the threat findings.

**Acceptance Criteria**:
- **Given** an architecture file at `docs/security/architecture.md`, **when** I run `/tachi.threat-model`, **then** the output folder (e.g., `docs/security/2026-04-09T14-30-22/`) contains a copy named `architecture.md`
- **Given** an architecture file with version frontmatter, **when** the snapshot is taken, **then** the copy preserves the original frontmatter verbatim
- **Given** a threat model run with `--output-dir custom/path/`, **when** the snapshot is taken, **then** the architecture copy is placed in the same timestamped subfolder as the threat output

**Priority**: P0
**Effort**: S

### US-120-4: Guided Architecture Update
**When** I need to update my architecture after deploying changes,
**I want to** be walked through a guided update process,
**So I can** ensure all relevant changes are captured without missing components or data flows.

**Acceptance Criteria**:
- **Given** an existing `architecture.md`, **when** I run `/tachi.architecture` with an existing file present, **then** the command reads the current architecture and guides me through changes (new services, removed components, updated data flows, new trust boundaries)
- **Given** a guided update session, **when** changes are applied, **then** the `description` field in frontmatter summarizes what changed (e.g., "Added payment gateway service, updated API data flows")
- **Given** an update with no changes needed, **when** I indicate no changes, **then** the file is untouched and no archive operation occurs

**Priority**: P1
**Effort**: M

---

## User Experience Requirements

### Key User Flows

#### Flow 1: First-Time Architecture Generation
1. User runs `/tachi.architecture`
2. Command analyzes codebase/docs for architectural elements
3. Command generates `architecture.md` with frontmatter (`version: 1`, date, checksum)
4. Command displays summary (components, flows, boundaries) and next step

#### Flow 2: Architecture Update (Guided)
1. User runs `/tachi.architecture` with existing file present
2. Command reads current architecture and displays current state summary
3. Command guides user through changes: new services? removed components? updated flows? new boundaries?
4. Command archives current version to `.archive/vN/`
5. Command writes updated file with incremented version and change description
6. Command displays diff summary and next step

#### Flow 3: Threat Model with Automatic Snapshot
1. User runs `/tachi.threat-model docs/security/architecture.md`
2. Command creates timestamped output folder (existing behavior)
3. **New**: Command copies `architecture.md` into the output folder
4. Command proceeds with orchestrator invocation (existing behavior)
5. Output folder contains: `architecture.md` + `threats.md` + `threats.sarif` + `threat-report.md` + `attack-trees/`

---

## Functional Requirements

### Core Capabilities

#### FR-1: Architecture Frontmatter Schema
**Description**: All architecture files managed by `/tachi.architecture` include YAML frontmatter.

**Schema**:
```yaml
---
version: 1                          # Auto-incremented integer
date: 2026-04-09                    # ISO date of this version
description: "Initial architecture" # Human-readable change summary
checksum: sha256:abc123...          # SHA-256 of content body (below frontmatter)
previous_version: null              # Path to archived previous version (null for v1)
---
```

**Business Rules**:
- `version` starts at 1, increments by 1 on each update
- `date` is set to the current date at generation/update time
- `checksum` is computed from the markdown body only (excluding frontmatter) using `shasum -a 256` (macOS/Linux) or equivalent platform tool
- `previous_version` points to the archive path (e.g., `docs/security/.archive/v2/architecture.md`)
- Archive path is always derived relative to the architecture file's parent directory (e.g., `{dirname}/. archive/vN/`), not hardcoded to `docs/security/`
- Existing architecture files without frontmatter are treated as v0 — first managed update produces v1

#### FR-2: Archive Mechanism
**Description**: Before overwriting an architecture file, the current version is archived.

**Archive Path**: `{parent_dir}/.archive/v{N}/architecture.md`
- Example: `docs/security/.archive/v3/architecture.md`

**Business Rules**:
- Archive preserves the complete file including frontmatter
- Archive directory is created automatically if it doesn't exist
- Archive is append-only — previous archive entries are never modified
- If the file has no frontmatter (legacy file), archive it as `v0` before upgrading
- Archive inherits the git-tracking status of its parent directory; users should adjust `.gitignore` if VCS persistence of the archive is required

#### FR-3: Architecture Snapshot in Threat Model
**Description**: `/tachi.threat-model` copies the architecture file into the timestamped output folder before invoking the orchestrator.

**Integration Point**: After Step 1.3 (output directory creation), before Step 2 (orchestrator invocation). This ensures the timestamped folder exists before the copy.

**Business Rules**:
- Snapshot is a verbatim copy — no modifications to the file
- Snapshot filename matches the source filename (default: `architecture.md`)
- If the architecture file does not exist, skip snapshot silently (existing validation in Step 2 handles the error)
- Snapshot occurs after the timestamped folder is created

#### FR-4: Guided Update Mode
**Description**: When an existing architecture file is detected, `/tachi.architecture` enters guided update mode.

**Update Categories**:
1. New services/components added
2. Components removed or decommissioned
3. Data flows changed (new connections, protocol changes)
4. Trust boundaries modified
5. External entities added/removed
6. AI capabilities changed (new models, tools, agents)

**Business Rules**:
- Current architecture is read and summarized before prompting for changes
- Each category is presented as a guided prompt
- User can skip categories with no changes
- All changes are reflected in the updated architecture and the `description` frontmatter field

### Data Requirements

**Data Model**:
```
Entity: Architecture File
Fields:
  - version: integer - monotonically increasing version number
  - date: date - creation/update date
  - description: string - human-readable change summary
  - checksum: string - SHA-256 content hash
  - previous_version: string|null - path to archived predecessor
  - body: markdown - the architecture description content

Archive Entry: Frozen copy of Architecture File at version N
Location: {parent_dir}/.archive/v{N}/architecture.md
```

**Data Lifecycle**:
- **Creation**: First `/tachi.architecture` run generates v1
- **Updates**: Subsequent runs archive current, write new version
- **Archival**: Previous versions stored indefinitely in `.archive/`
- **Snapshots**: Read-only copies in threat model output folders

---

## Non-Functional Requirements

### Performance Requirements
- Architecture generation: no change to current performance (agent-driven analysis)
- Archive copy: <1s (local file copy)
- Snapshot copy: <1s (local file copy)
- Frontmatter parsing: <100ms

### Compatibility Requirements
- **Backward Compatible**: Architecture files without frontmatter continue to work as input to `/tachi.threat-model` — frontmatter is optional for consumption
- **Forward Compatible**: Downstream pipeline stages (risk-scorer, control-analyzer, infographic, report-assembler) are unaffected — they consume `threats.md`, not `architecture.md`
- **Example Compatibility**: Existing example architecture files in `examples/` remain valid without frontmatter

---

## Success Metrics

### Primary Metrics
- **Traceability**: 100% of threat model output folders contain an architecture snapshot
- **Version Continuity**: Architecture version increments correctly across consecutive updates
- **Archive Integrity**: Archived versions match their original content (checksum verification)

### Adoption Metrics
- **Feature Usage**: Users running `/tachi.architecture` on existing files trigger guided update mode
- **Pipeline Integration**: `/tachi.threat-model` produces self-contained output folders

---

## Scope & Boundaries

### In Scope (MVP)

**Must Have (P0)**:
- Architecture frontmatter schema (version, date, description, checksum)
- Archive mechanism (`.archive/vN/` structure)
- Automatic snapshot in `/tachi.threat-model` output folders
- Legacy file handling (files without frontmatter treated as v0)

**Should Have (P1)**:
- Guided update mode for existing architecture files
- Change description auto-population in frontmatter

### Out of Scope (Future Phases)

**Won't Have** — Explicitly excluded:
- Architecture diff visualization between versions
- Automatic architecture change detection from codebase (requires deep code analysis)
- Architecture version pinning in threat model commands (e.g., `--arch-version 3`)
- Integration with git history for architecture change tracking
- Downstream pipeline awareness of architecture version (risk-scores, controls don't need it)
- Modification of existing example architecture files to add frontmatter (examples remain as-is)

### Assumptions
- Architecture files are stored on the local filesystem (not in external systems)
- The `.archive/` directory convention is acceptable for version storage
- SHA-256 is sufficient for content integrity checking
- Threat model output folders already exist when the snapshot step runs

### Constraints

**Technical Constraints**:
- Must work within the existing command file structure (`.claude/commands/tachi.architecture.md`)
- Must not break existing `/tachi.threat-model` workflow — snapshot is additive
- Frontmatter must be valid YAML parseable by standard YAML libraries
- Archive structure must work on all platforms (macOS, Linux, Windows)

**Scope Constraints**:
- No new dependencies — file copy and SHA-256 are standard operations
- No schema changes to existing output formats (threats.md, risk-scores.md, etc.)

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Frontmatter breaks existing architecture file consumers
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: `/tachi.threat-model` and orchestrator already receive architecture as a file path — frontmatter is ignored by Mermaid parsing and section extraction. Validate against all 3 example architectures.

**Risk 2**: Archive directory conflicts with user project structure
- **Likelihood**: Low
- **Impact**: Low
- **Mitigation**: Use `.archive/` (dot-prefix convention for hidden/system directories). Document the convention.

### Dependencies

**Internal Dependencies**:
- **Feature 074** (Baseline-Aware Pipeline): Provides the timestamped output folder structure used for snapshots
- **Feature 121** (tachi.* Namespace): Established `/tachi.architecture` command file location

**No External Dependencies**: All operations are local file system operations.

---

## Open Questions

- [x] Should frontmatter be required or optional for architecture files consumed by `/tachi.threat-model`? — **Optional** (backward compatible; threat-model reads the file regardless of frontmatter presence)
- [x] Should the archive path be configurable or fixed convention? — **Fixed convention for MVP** (`.archive/vN/` relative to architecture file parent directory). Configurability deferred to future phase.

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- Baseline-Aware Pipeline PRD: [074-baseline-aware-pipeline](074-baseline-aware-pipeline-2026-03-31.md)

### Technical Documentation
- Current `/tachi.architecture` command: `.claude/commands/tachi.architecture.md`
- Current `/tachi.threat-model` command: `.claude/commands/tachi.threat-model.md`
- Example architectures: `examples/agentic-app/architecture.md`, `examples/microservices/architecture.md`, `examples/web-app/architecture.md`

---

## Architecture Update Impact on Pipeline

When an architecture is updated and a new threat model is run:
- **threats.md**: Delta-classified findings with stable IDs via baseline correlation (Feature 074)
- **risk-scores.md**: Unchanged findings inherit scores; new findings scored fresh
- **compensating-controls.md**: Re-scans codebase against updated finding set
- **infographics**: Auto-detect richest data source, reflect current state
- **security-report.pdf**: Assembles from all updated artifacts
- **architecture.md snapshot**: New — frozen copy in the output folder for traceability
