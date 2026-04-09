---
prd_reference: docs/product/02_PRD/121-rename-tachi-commands-to-namespace-2026-04-09.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "All 8 PRD requirements (R1-R8) covered by FR-001 through FR-017. All 5 user stories present with faithful acceptance criteria. Success criteria aligned. Scope boundaries match exactly with zero creep."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Rename Tachi Commands to tachi.* Namespace

**Feature Branch**: `121-rename-tachi-commands`
**Created**: 2026-04-09
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/121-rename-tachi-commands-to-namespace-2026-04-09.md`
**Input**: Rename all 5 tachi pipeline commands to use `tachi.*` namespace prefix, update all cross-references, add upgrade cleanup, and include the new `tachi.architecture` command.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Namespace-Prefixed Command Invocation (Priority: P1)

A developer has tachi installed alongside their own project-specific commands. They invoke tachi pipeline commands using `tachi.*` prefixed names (e.g., `/tachi.threat-model`, `/tachi.risk-score`) to run threat analysis without colliding with their own commands that may use generic names like `/threat-model`.

**Why this priority**: This is the core value proposition. Without namespaced commands, tachi cannot be safely installed into projects that define their own commands with overlapping names. This directly enables tachi's adoption as a third-party template.

**Independent Test**: Install tachi into a project, invoke each of the 6 `tachi.*` commands, and verify each executes its intended pipeline stage.

**Acceptance Scenarios**:

1. **Given** tachi is installed in a project, **When** the user runs `/tachi.threat-model`, **Then** the threat modeling pipeline executes and produces `threats.md`
2. **Given** tachi is installed in a project, **When** the user runs `/tachi.risk-score`, **Then** quantitative risk scoring executes and produces `risk-scores.md`
3. **Given** tachi is installed in a project, **When** the user runs `/tachi.compensating-controls`, **Then** control analysis executes and produces `compensating-controls.md`
4. **Given** tachi is installed in a project, **When** the user runs `/tachi.infographic`, **Then** infographic generation executes
5. **Given** tachi is installed in a project, **When** the user runs `/tachi.security-report`, **Then** PDF report generation executes
6. **Given** tachi is installed in a project, **When** the user runs `/tachi.architecture`, **Then** architecture description generation executes

---

### User Story 2 - Cross-Reference Integrity (Priority: P1)

A developer follows documentation, agent instructions, or skill references that mention tachi commands. All references consistently use the new `tachi.*` names, so copy-pasting command names from docs works without encountering "command not found" errors.

**Why this priority**: Stale references to old command names would cause confusion and erode trust. This is equal priority to the rename itself because broken docs are functionally equivalent to broken commands.

**Independent Test**: After the rename, search the entire codebase for old command names (`/threat-model`, `/risk-score`, `/compensating-controls`, `/infographic`, `/security-report`). Zero matches should exist outside of immutable historical artifacts (archived PRDs, archived specs, historical CHANGELOG entries).

**Acceptance Scenarios**:

1. **Given** the rename is complete, **When** searching for old command names across commands, agents, skills, templates, schemas, scripts, and docs, **Then** zero matches are found (excluding immutable historical artifacts)
2. **Given** the rename is complete, **When** searching for new `tachi.*` command names, **Then** all active commands, agents, skills, and documentation reference the new names consistently
3. **Given** a developer reads the developer guide, **When** they copy a command name from the guide, **Then** the command executes successfully

---

### User Story 3 - Clean Upgrade Without Duplicates (Priority: P1)

A developer has an existing tachi installation with old unprefixed command names. They upgrade to the new version using `scripts/install.sh`. After the upgrade, only the new `tachi.*` commands exist — no duplicates of old and new commands coexist in their project.

**Why this priority**: Without cleanup, upgrading consumers end up with both `/threat-model` AND `/tachi.threat-model`, causing confusion about which to use and potentially invoking stale command definitions.

**Independent Test**: Start with a project containing old command files, run `scripts/install.sh`, and verify only `tachi.*` prefixed commands exist in `.claude/commands/`.

**Acceptance Scenarios**:

1. **Given** an existing installation with old command files (e.g., `threat-model.md`), **When** the user runs the install script, **Then** old command files are removed and only `tachi.*` prefixed commands exist
2. **Given** a fresh installation (no old files exist), **When** the user runs the install script, **Then** the cleanup step runs silently with no errors and only `tachi.*` commands are installed
3. **Given** the install script runs cleanup, **When** a deprecated file is removed, **Then** a log message confirms the removal (e.g., "Removed deprecated: .claude/commands/threat-model.md")

---

### User Story 4 - Command Discovery via Namespace (Priority: P2)

A developer exploring tachi's capabilities types `/tachi.` in their IDE command palette. All 6 pipeline commands appear as completions, making it easy to discover and select the right command without consulting documentation.

**Why this priority**: This is a natural benefit of the namespace rename — no additional work required beyond the rename itself. It improves developer experience but is not blocking for adoption.

**Independent Test**: In an IDE with tachi installed, type `/tachi.` and verify all 6 pipeline commands appear as completions.

**Acceptance Scenarios**:

1. **Given** tachi is installed, **When** the user types `/tachi.` in their IDE command palette, **Then** all 6 pipeline commands appear as completions: `tachi.threat-model`, `tachi.risk-score`, `tachi.compensating-controls`, `tachi.infographic`, `tachi.security-report`, `tachi.architecture`

---

### User Story 5 - Migration Guidance (Priority: P2)

An existing tachi user reads the CHANGELOG or migration notes after upgrading. They find a clear mapping from old command names to new names, enabling them to update any personal notes, scripts, or workflows that reference the old names.

**Why this priority**: Important for user trust and smooth transition, but the install script handles the actual migration automatically. This is documentation-only work.

**Independent Test**: Read the CHANGELOG migration entry and verify it contains a complete old-to-new command name mapping.

**Acceptance Scenarios**:

1. **Given** the rename is shipped, **When** a user reads the CHANGELOG, **Then** they find a clear old-to-new mapping table for all 5 renamed commands
2. **Given** a user runs an old command name, **When** the old file no longer exists, **Then** the standard "command not found" behavior occurs (no special shim needed)

---

### Edge Cases

- What happens when a consumer project has custom commands that coincidentally match `tachi.*` names? The install script overwrites the target file — this is existing behavior and acceptable since tachi owns the `tachi.*` namespace.
- What happens when the install script is run against a project that never had old command files? The deprecated-file cleanup runs silently (`rm -f` is a no-op on missing files).
- What happens if a partial rename is committed (some commands renamed, others not)? All renames must be delivered atomically in a single PR — partial rename state must never exist on `main`.
- What happens to example output files that reference command names in generated content (e.g., CTA text in infographics)? Skill CTA text strings must be updated as part of the cross-reference sweep.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All 5 existing tachi pipeline command files MUST be renamed to the `tachi.*` namespace: `threat-model.md` to `tachi.threat-model.md`, `risk-score.md` to `tachi.risk-score.md`, `compensating-controls.md` to `tachi.compensating-controls.md`, `infographic.md` to `tachi.infographic.md`, `security-report.md` to `tachi.security-report.md`
- **FR-002**: The new `tachi.architecture` command (Issue #120) MUST be created with the `tachi.*` namespace from inception
- **FR-003**: Adapter command copies in `adapters/claude-code/commands/` and `adapters/github-actions/` MUST follow the same rename pattern as primary commands
- **FR-004**: All cross-references to old command names across commands, agents, skills, templates, schemas, scripts, and documentation MUST be updated to use new `tachi.*` names
- **FR-005**: The `INSTALL_MANIFEST.md` machine-parseable section MUST be updated with new filenames (both human-readable tables and the `<!-- BEGIN MANIFEST -->` section)
- **FR-006**: The install script (`scripts/install.sh`) MUST include a deprecated-file cleanup step that removes old unprefixed command files from the target project before copying new files
- **FR-007**: The deprecated-file cleanup MUST run silently on fresh installations (no errors when old files don't exist)
- **FR-008**: The deprecated-file cleanup MUST log each removal (e.g., "Removed deprecated: .claude/commands/threat-model.md")
- **FR-009**: All consumer-facing guides (`DEVELOPER_GUIDE_TACHI.md`, `CONSUMER_GUIDE_TACHI.md`, `CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md`, `CONSUMER_GUIDE_TACHI_RESEARCH.md`) MUST reference new command names
- **FR-010**: Root documentation files (`CLAUDE.md`, `README.md`, `CHANGELOG.md`) MUST reference new command names
- **FR-011**: Skill CTA (call-to-action) text that appears in generated output (e.g., infographic specifications) MUST reference new command names
- **FR-012**: A CHANGELOG migration entry MUST provide a clear old-to-new command name mapping table
- **FR-013**: Historical PRDs in `docs/product/02_PRD/` MUST NOT be modified (immutable records)
- **FR-014**: Archived specs in `specs/*/` (other than the current feature) MUST NOT be modified (immutable records)
- **FR-015**: Historical CHANGELOG entries MUST NOT be modified — the migration note is added as a new entry
- **FR-016**: All renames MUST be delivered atomically — no partial rename state may exist on `main`
- **FR-017**: Old command names MUST NOT have backward-compatibility aliases or wrappers

### Key Entities

- **Command File**: A markdown file in `.claude/commands/` that defines a slash command's behavior. Named `{prefix}.{name}.md` under the new convention.
- **Cross-Reference**: Any mention of a command name (e.g., `/threat-model`, `threat-model.md`) in commands, agents, skills, templates, schemas, scripts, or documentation that must be updated.
- **Install Manifest**: The machine-parseable file (`INSTALL_MANIFEST.md`) that declares which files the install script delivers to consumer projects.
- **Deprecated File**: An old unprefixed command file that must be removed from consumer projects during upgrade.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After rename, a codebase-wide search for old command invocation patterns (`/threat-model`, `/risk-score`, `/compensating-controls`, `/infographic`, `/security-report`) returns zero matches outside immutable historical artifacts (archived PRDs, archived specs, historical CHANGELOG entries)
- **SC-002**: All 6 tachi pipeline commands (`tachi.threat-model`, `tachi.risk-score`, `tachi.compensating-controls`, `tachi.infographic`, `tachi.security-report`, `tachi.architecture`) exist as files in `.claude/commands/` with correct naming
- **SC-003**: The install script, when run against a project with old command files, removes all 5 deprecated files and installs only `tachi.*` prefixed commands (zero duplicates)
- **SC-004**: The install script, when run against a fresh project, completes without errors and installs all `tachi.*` commands
- **SC-005**: The INSTALL_MANIFEST.md machine-parseable section lists only `tachi.*` command filenames (no old names remain)
- **SC-006**: All 6 example threat model documentation sets pass validation with new command names referenced

## Assumptions

- Claude Code's command resolution supports dot-separated filenames as namespace separators (confirmed by existing `aod.*` commands)
- Tachi is pre-1.0; breaking changes to command names are acceptable with documentation
- The `tachi.architecture` command scope is defined by Issue #120 and will be bounded or stubbed as part of this feature
- The install script's manifest-parsing approach means file renames on disk are automatically picked up — no parser changes needed beyond manifest content updates
- Adapter directories (`adapters/claude-code/commands/`, `adapters/github-actions/`) follow the same naming convention as primary commands
- Approximately 344 files containing ~2,207 cross-references will need updates based on codebase analysis

## Scope Boundaries

### In Scope
- Rename 5 existing command files to `tachi.*` namespace
- Create `tachi.architecture` command (Issue #120 — content bounded or stubbed)
- Rename 3 adapter command copies and 1 GitHub Actions workflow
- Update all cross-references (~2,207 across ~344 files)
- Update INSTALL_MANIFEST.md (human-readable and machine-parseable sections)
- Add deprecated-file cleanup to scripts/install.sh
- Update all consumer/developer guides
- Update root files (CLAUDE.md, README.md, CHANGELOG.md)
- Update skill CTA text in generated output
- CHANGELOG migration entry with old-to-new mapping
- Grep verification: zero old names outside immutable artifacts

### Out of Scope
- Renaming AOD commands (already namespaced as `aod.*`)
- Renaming utility commands (`continue.md`, `execute.md`, etc.)
- Adding command aliases or backward-compatibility wrappers
- Renaming agent files or skill directory names (only internal references change)
- Modifying historical PRDs or archived specs
- Modifying historical CHANGELOG entries

## Dependencies

- **Issue #120 (tachi.architecture command)**: Content for the new command is defined by this issue. Will be created as part of this feature with the `tachi.*` namespace from the start.
- **INSTALL_MANIFEST.md**: Must be updated atomically with the command file renames.
- **scripts/install.sh**: Must be extended with deprecated-file cleanup before the copy step.
