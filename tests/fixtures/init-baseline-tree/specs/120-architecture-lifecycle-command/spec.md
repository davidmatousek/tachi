---
prd_reference: docs/product/02_PRD/120-architecture-lifecycle-command-2026-04-09.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "All 4 PRD user stories fully addressed with strengthened acceptance scenarios. All 4 PRD FRs decomposed into 22 granular spec FRs. All 5 PRD success criteria reflected in 7 spec outcomes. Scope boundaries match exactly. P0/P1 priority alignment identical. Triad review concerns from PRD incorporated into spec FRs and assumptions."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Architecture Lifecycle Command

**Feature Branch**: `120-architecture-lifecycle-command`
**Created**: 2026-04-09
**Status**: Draft
**Input**: PRD 120 — Architecture Lifecycle Command
**PRD Reference**: `docs/product/02_PRD/120-architecture-lifecycle-command-2026-04-09.md`

## User Scenarios & Testing

### User Story 1 — Architecture Version Tracking (Priority: P0)

A security engineer runs `/tachi.architecture` to update their architecture description after deploying a new service. The command detects the existing architecture file, archives the current version, generates an updated file with incremented version metadata, and records a change description — all without the engineer needing to manage version history manually.

**Why this priority**: Without version tracking, every architecture update destroys the previous version. This is the foundational capability that all other stories depend on.

**Independent Test**: Run `/tachi.architecture` on a project with an existing `architecture.md` file. Verify the previous version is archived and the new file has incremented version metadata.

**Acceptance Scenarios**:

1. **Given** an existing `architecture.md` without frontmatter, **When** I run `/tachi.architecture`, **Then** the output file contains YAML frontmatter with `version: 1`, `date` set to today, `description` summarizing the architecture, and a SHA-256 `checksum` of the content body
2. **Given** an existing `architecture.md` with `version: 3` in frontmatter, **When** I run `/tachi.architecture`, **Then** the output file has `version: 4`, the `date` is updated, and `previous_version` points to the archive path `{parent_dir}/.archive/v3/architecture.md`
3. **Given** a freshly generated architecture file, **When** I inspect the frontmatter, **Then** the `checksum` field contains a valid SHA-256 hash prefixed with `sha256:` computed from the markdown body below the frontmatter
4. **Given** a first-time generation (no existing file), **When** I run `/tachi.architecture`, **Then** the output has `version: 1`, `previous_version: null`, and no archive operation occurs

---

### User Story 2 — Architecture Archive (Priority: P0)

A compliance auditor needs to verify which architecture version was assessed during a previous threat model run. They navigate to the `.archive/` directory and find each previous version preserved in its own numbered subfolder with original frontmatter intact.

**Why this priority**: The archive mechanism is required by User Story 1 (version tracking writes to the archive) and User Story 3 (snapshot references archived versions). Without it, version tracking has no storage backend.

**Independent Test**: Run `/tachi.architecture` multiple times on the same project. Verify each previous version appears in `.archive/v{N}/` with its original content and frontmatter preserved.

**Acceptance Scenarios**:

1. **Given** an architecture file at `docs/security/architecture.md` with `version: 3`, **When** I run `/tachi.architecture` to update it, **Then** the v3 file is copied to `docs/security/.archive/v3/architecture.md` with its complete content and frontmatter intact
2. **Given** an archive directory with v1, v2, v3, **When** I list the archive, **Then** each version is in its own numbered subfolder (`v1/`, `v2/`, `v3/`) and each contains the original `architecture.md`
3. **Given** an existing architecture file without frontmatter (legacy file), **When** I run `/tachi.architecture`, **Then** the legacy file is archived as `v0` before the new v1 is written
4. **Given** a first-time generation (no existing file), **When** I run `/tachi.architecture`, **Then** no archive directory is created (v1 is the initial version)

---

### User Story 3 — Automatic Architecture Snapshot in Threat Model Runs (Priority: P0)

A security engineer runs `/tachi.threat-model` and later needs to review which architecture was analyzed. They open the timestamped output folder and find a copy of the architecture file alongside the threat findings — the run is self-contained without needing to cross-reference version numbers.

**Why this priority**: This delivers the core traceability requirement — every threat model output folder becomes self-contained. Without it, users must manually correlate architecture versions with threat model runs.

**Independent Test**: Run `/tachi.threat-model` with an architecture file present. Verify the timestamped output folder contains a verbatim copy of the architecture file.

**Acceptance Scenarios**:

1. **Given** an architecture file at `docs/security/architecture.md`, **When** I run `/tachi.threat-model`, **Then** the timestamped output folder (e.g., `docs/security/2026-04-09T14-30-22/`) contains a copy named `architecture.md`
2. **Given** an architecture file with version frontmatter, **When** the snapshot is taken, **Then** the copy preserves the original frontmatter verbatim — no modifications to the content
3. **Given** no architecture file exists at the expected path, **When** `/tachi.threat-model` runs, **Then** the snapshot step is skipped silently (existing validation in Step 2 handles the missing file error)
4. **Given** a threat model run with a custom output directory, **When** the snapshot is taken, **Then** the architecture copy is placed in the same timestamped subfolder as the threat output

---

### User Story 4 — Guided Architecture Update (Priority: P1)

A security engineer needs to update their architecture after deploying infrastructure changes. Instead of editing the raw markdown, they run `/tachi.architecture` and are walked through a guided update process covering each architectural dimension: new services, removed components, changed data flows, modified trust boundaries, added external entities, and changed AI capabilities.

**Why this priority**: Improves the update experience and ensures completeness, but the core versioning and snapshot functionality works without it. Users can still edit architecture files manually.

**Independent Test**: Run `/tachi.architecture` with an existing architecture file. Verify the command reads the current architecture, presents a guided update flow, and produces an updated file with a change description reflecting the modifications.

**Acceptance Scenarios**:

1. **Given** an existing `architecture.md`, **When** I run `/tachi.architecture`, **Then** the command reads the current architecture and guides me through changes organized by category: new services, removed components, updated data flows, modified trust boundaries, added/removed external entities, changed AI capabilities
2. **Given** a guided update session where I add a payment gateway, **When** changes are applied, **Then** the `description` field in frontmatter summarizes the changes (e.g., "Added payment gateway service, updated API data flows")
3. **Given** a guided update session where I indicate no changes needed, **When** I confirm no changes, **Then** the file is untouched, no archive operation occurs, and no version increment happens

---

### Edge Cases

- **Concurrent updates**: Two users run `/tachi.architecture` simultaneously on the same file. The last write wins — the archive captures whatever version existed at the time of archival. No locking mechanism is required for MVP (local-first, single-user workflow).
- **Corrupted frontmatter**: Architecture file has malformed YAML frontmatter. The command treats it as a legacy file (no valid frontmatter) and archives as v0 before generating v1.
- **Missing parent directory**: The output path's parent directory does not exist. The command creates it (existing behavior in `/tachi.architecture`).
- **Empty architecture file**: The file exists but has no content. Treated as a legacy file — archived as v0 with empty body, new v1 generated from analysis.
- **Archive directory already has the version**: Attempting to archive v3 but `.archive/v3/` already exists (e.g., from a failed previous run). Overwrite the existing archive entry — the archive is idempotent per version number.
- **Non-default architecture file path**: Architecture file is at a custom path (e.g., `security/my-arch.md`). Archive path is derived relative to the file's parent directory: `security/.archive/v{N}/my-arch.md`.
- **Very large architecture files**: Files with extensive Mermaid diagrams or component tables. No size limit — file copy and checksum operations scale linearly.

## Requirements

### Functional Requirements

- **FR-001**: The `/tachi.architecture` command MUST add YAML frontmatter to generated architecture files containing: `version` (integer), `date` (ISO date), `description` (change summary), `checksum` (SHA-256 of content body), and `previous_version` (archive path or null)
- **FR-002**: The `version` field MUST start at 1 for new files and increment by 1 on each update
- **FR-003**: The `checksum` field MUST be a SHA-256 hash of the markdown body only (excluding the YAML frontmatter block), prefixed with `sha256:`
- **FR-004**: The `checksum` MUST be computed using an explicit platform tool invocation (`shasum -a 256` on macOS/Linux) within the command file, not described abstractly
- **FR-005**: Existing architecture files without frontmatter MUST be treated as version 0 — the first managed update produces version 1 with the legacy file archived as v0
- **FR-006**: Before overwriting an architecture file, the `/tachi.architecture` command MUST archive the current version to `{parent_dir}/.archive/v{N}/architecture.md` where `{parent_dir}` is the architecture file's parent directory and `{N}` is the current version number
- **FR-007**: The archive MUST preserve the complete file including frontmatter
- **FR-008**: The archive directory MUST be created automatically if it does not exist
- **FR-009**: The archive MUST be append-only — previous archive entries are never modified by subsequent operations (overwrite is permitted only for the same version number to support idempotent retries)
- **FR-010**: If no existing architecture file is found (first-time generation), no archive operation MUST occur
- **FR-011**: The `previous_version` frontmatter field MUST contain the relative path to the archived previous version (e.g., `.archive/v2/architecture.md`) or null for version 1
- **FR-012**: The `/tachi.threat-model` command MUST copy the current architecture file into the timestamped output folder before invoking the orchestrator
- **FR-013**: The architecture snapshot MUST be a verbatim copy with no modifications to content or frontmatter
- **FR-014**: The snapshot filename MUST match the source filename (default: `architecture.md`)
- **FR-015**: If the architecture file does not exist at snapshot time, the snapshot step MUST be skipped silently without blocking the threat model run
- **FR-016**: The snapshot step MUST execute after the timestamped output directory is created (Step 1.3) and before the orchestrator is invoked (Step 2)
- **FR-017**: When an existing architecture file is detected, the `/tachi.architecture` command MUST enter guided update mode, presenting the current architecture summary and walking the user through change categories: new services, removed components, changed data flows, modified trust boundaries, added/removed external entities, and changed AI capabilities
- **FR-018**: If the user indicates no changes in guided update mode, the file MUST remain untouched with no archive operation and no version increment
- **FR-019**: The `description` frontmatter field MUST summarize the changes made during the update session
- **FR-020**: The archive path MUST be derived relative to the architecture file's parent directory, not hardcoded to any specific path
- **FR-021**: Example architecture files in `examples/` MUST NOT be modified — they remain valid without frontmatter as input to the pipeline
- **FR-022**: Downstream pipeline stages (risk-scorer, control-analyzer, infographic, report-assembler) MUST remain unaffected — they consume `threats.md`, not `architecture.md`

### Key Entities

- **Architecture File**: A markdown document describing system architecture with optional YAML frontmatter containing version metadata. Key attributes: version (integer), date (ISO date), description (string), checksum (SHA-256 hash), previous_version (path or null), body (markdown content).
- **Archive Entry**: A frozen, read-only copy of an Architecture File at a specific version. Stored at `{parent_dir}/.archive/v{N}/architecture.md`. Preserves complete content including frontmatter.
- **Architecture Snapshot**: A verbatim copy of the current Architecture File placed in a threat model output folder for traceability. Read-only, informational — not consumed by any downstream pipeline stage.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of architecture files generated by `/tachi.architecture` contain valid YAML frontmatter with all five required fields (version, date, description, checksum, previous_version)
- **SC-002**: Running `/tachi.architecture` consecutively N times on the same file produces an archive with N-1 entries (v1 through v{N-1}), each with the correct content from that version
- **SC-003**: 100% of `/tachi.threat-model` output folders contain an `architecture.md` snapshot when the source architecture file exists at run time
- **SC-004**: Architecture files without frontmatter (legacy files and example files) continue to work as valid input to `/tachi.threat-model` without errors
- **SC-005**: The SHA-256 checksum in frontmatter matches a re-computation of the file body for every generated architecture file
- **SC-006**: No downstream pipeline stage (risk-scorer, control-analyzer, infographic, report-assembler) requires changes or produces different output due to this feature
- **SC-007**: Guided update mode produces a `description` field that accurately reflects the changes made during the session

## Scope

### In Scope (MVP — P0)

- Architecture frontmatter schema (version, date, description, checksum, previous_version)
- Archive mechanism (`.archive/vN/` structure relative to file parent directory)
- Legacy file handling (files without frontmatter treated as v0)
- Automatic architecture snapshot in `/tachi.threat-model` output folders
- Backward compatibility validation against example architecture files

### In Scope (P1)

- Guided update mode for existing architecture files
- Change description auto-population in frontmatter

### Out of Scope

- Architecture diff visualization between versions
- Automatic architecture change detection from codebase analysis
- Architecture version pinning in threat model commands (e.g., `--arch-version 3`)
- Integration with git history for architecture change tracking
- Downstream pipeline awareness of architecture version (risk-scores, controls, etc.)
- Modification of existing example architecture files to add frontmatter
- Bi-directional architecture version reference in `threats.md` frontmatter (future enhancement)

## Assumptions

- Architecture files are stored on the local filesystem, not in external systems
- The `.archive/` dot-prefix directory convention is acceptable for version storage (follows existing project convention)
- SHA-256 is sufficient for content integrity checking
- `shasum -a 256` is available on target platforms (macOS, Linux); Windows users may need an equivalent tool
- Threat model output folders are created by Step 1.3 of `/tachi.threat-model` before the snapshot step executes
- The orchestrator agent ignores frontmatter in architecture input (validated by research — format detection treats it as free text)
- Single-user, local-first workflow — no concurrent write protection needed for MVP

## Dependencies

- **Feature 074** (Baseline-Aware Pipeline): Provides the timestamped output folder structure used for snapshots
- **Feature 121** (tachi.* Namespace): Established `/tachi.architecture` command file location at `.claude/commands/tachi.architecture.md`
- **No external dependencies**: All operations are local filesystem operations (file copy, SHA-256 hash)

## Risks

- **Frontmatter breaks orchestrator parsing** (Low likelihood, Medium impact): The orchestrator receives architecture via `<architecture-input>` tags and uses format detection that treats unknown content as free text. Mitigation: validate against all 3 example architectures with frontmatter added.
- **Archive directory conflicts with user project structure** (Low likelihood, Low impact): `.archive/` uses dot-prefix convention for hidden/system directories. Mitigation: document the convention; users can adjust `.gitignore` if needed.
- **Platform tool availability** (Low likelihood, Low impact): `shasum -a 256` may not be available on all platforms. Mitigation: document requirement; `sha256sum` is the Linux alternative.
