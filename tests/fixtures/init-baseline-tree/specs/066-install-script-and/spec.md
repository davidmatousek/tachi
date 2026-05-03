---
prd_reference: docs/product/02_PRD/066-install-script-and-version-tagging-2026-04-06.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-06
    status: APPROVED
    notes: "Spec faithfully translates PRD into 20 testable FRs with zero scope creep. All 5 PRD user stories mapped, all 5 reviewer concerns resolved as first-class requirements, 7 measurable success criteria, 5 explicit edge cases."
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Install Script and Version Tagging

**Feature Branch**: `066-install-script-and`
**Created**: 2026-04-06
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/066-install-script-and-version-tagging-2026-04-06.md`
**Input**: Replace tachi's 6 manual copy commands with a single install script and adopt git tags for versioned distribution

## User Scenarios & Testing *(mandatory)*

### User Story 1 - First-Time Install (Priority: P0)

A developer evaluating tachi clones the repository and wants to add threat modeling capabilities to their own project. Instead of memorizing and running 6+ manual copy commands, they run a single install command from their project directory. All distributable files are copied to the correct locations automatically, and the developer sees a summary confirming what was installed and which version.

**Why this priority**: This is the core value proposition — eliminating the primary adoption friction. Every manual step in setup is a drop-off point for new users.

**Independent Test**: Can be fully tested by cloning tachi, creating an empty target directory, running the install command, and verifying all expected files exist in the target.

**Acceptance Scenarios**:

1. **Given** tachi is cloned locally and the target project directory exists, **When** the user runs the install command from the target project root, **Then** all files listed in the install manifest are copied to the correct locations in the target project
2. **Given** intermediate directories do not exist in the target project, **When** the install command runs, **Then** required directories are created automatically before copying
3. **Given** the install completes successfully, **When** the user reads the output, **Then** they see the installed version identifier and the count of files/directories copied
4. **Given** the source tachi directory does not exist at the expected location, **When** the user runs the install command, **Then** a clear error message explains the problem and suggests how to fix it

---

### User Story 2 - Update Existing Install (Priority: P0)

A developer already using tachi pulls the latest changes and wants to update the tachi files in their project. They re-run the same install command, and updated files overwrite the old ones. The output shows the installed version so the developer knows they're current.

**Why this priority**: Updates are as frequent as new installs for active users. The install command must be safe and idempotent for re-runs.

**Independent Test**: Can be tested by running the install command twice — the second run should complete without error and produce the same file set.

**Acceptance Scenarios**:

1. **Given** tachi files already exist in the target project, **When** the user re-runs the install command, **Then** updated files overwrite existing ones without error
2. **Given** the install command has run previously, **When** it runs again, **Then** the result is identical to a fresh install (idempotent behavior)
3. **Given** the install completes, **When** the user checks the output, **Then** the installed version is displayed so they can confirm the update

---

### User Story 3 - Pinned Version Install (Priority: P1)

A developer needs a reproducible install for CI or team onboarding. They specify a version tag and the install command installs files from that exact version. If the requested version does not exist, the command lists available versions.

**Why this priority**: Version pinning enables reproducible environments and team consistency — critical for production workflows but not required for first-time evaluation.

**Independent Test**: Can be tested by tagging a known commit, running the install command with that version, and verifying the installed files match that tagged state.

**Acceptance Scenarios**:

1. **Given** tachi has version tags, **When** the user runs the install command specifying a version, **Then** files from that exact version are installed and the original source repository state is fully restored afterward
2. **Given** the requested version tag does not exist, **When** the user runs the command, **Then** an error message is displayed listing available version tags
3. **Given** the source repository has uncommitted changes, **When** the user attempts a version-pinned install, **Then** the command refuses with a clear message explaining why (to prevent data loss in the source repo)
4. **Given** the install is interrupted mid-operation (e.g., Ctrl+C, disk error), **When** the interruption occurs, **Then** the source repository is restored to its original branch/state

---

### User Story 4 - Custom Source Location (Priority: P1)

A developer has tachi cloned to a non-default directory. They specify the source path and the install command uses that location. When no source path is specified, the command automatically detects the source from the install script's own location.

**Why this priority**: Supports varied developer setups and follows the existing auto-detection pattern used by other tachi scripts.

**Independent Test**: Can be tested by copying the script to a different location, running it with an explicit source path, and verifying files are copied from the specified source.

**Acceptance Scenarios**:

1. **Given** tachi is cloned to a non-default location, **When** the user specifies the source path, **Then** files are copied from that location
2. **Given** no source path is specified, **When** the install command runs, **Then** it automatically detects the source directory from the install script's own file location
3. **Given** an explicit source path is provided, **When** it overrides the auto-detected path, **Then** files are copied from the explicitly specified location

---

### User Story 5 - Manual Install Preserved (Priority: P1)

A developer who prefers manual control over which files are copied can still reference the documented copy commands. The README provides the scripted install as the primary path while preserving manual instructions in a collapsible section.

**Why this priority**: Backward compatibility with existing workflows and user autonomy. Some users want selective installs.

**Independent Test**: Can be verified by checking the README contains both scripted and manual install instructions, with manual instructions accessible but not the default.

**Acceptance Scenarios**:

1. **Given** the README is updated, **When** a user looks for install instructions, **Then** the scripted install is the primary (visible) path
2. **Given** a user wants manual control, **When** they expand the manual install section, **Then** they find the existing `cp -r` commands documented and accurate
3. **Given** the developer guide has install instructions, **When** it is updated, **Then** it reflects the scripted install as the primary method with manual as alternative

---

### User Story 6 - Version Tagging Adoption (Priority: P1)

The tachi repository adopts semantic version tags so that the install command can reference specific versions. The first tag is created from the current main branch as a baseline. Future releases are tagged following semantic versioning.

**Why this priority**: Version tags are the foundation for pinned installs (US-003) and version reporting in install output.

**Independent Test**: Can be verified by checking that a version tag exists on the repository, `git describe --tags` returns a meaningful version, and the tag follows the `vMAJOR.MINOR.PATCH` format.

**Acceptance Scenarios**:

1. **Given** no version tags exist yet, **When** the first tag is created, **Then** it follows the format `v4.0.0` and is applied to the current main branch
2. **Given** version tags exist, **When** the install command reports the installed version, **Then** the version string comes from `git describe` and reflects the exact tag or distance from the nearest tag

---

### Edge Cases

- What happens when the install manifest file is missing or empty in the source directory? The install command must exit with a clear error
- What happens when the user has no write permission to the target directory? The install command must report which files failed and exit with a non-zero status
- What happens when disk space runs out during copy? The install command must report partial progress and which files succeeded/failed
- What happens when the install manifest references a path that does not exist in the source? The command must warn about the missing path but continue installing remaining files
- What happens when files from a previous tachi version exist in the target but are no longer in the current manifest? They persist (additive-only behavior — the command never deletes files)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The install command MUST copy all files and directories listed in the install manifest from the source tachi directory to the current working directory (target project)
- **FR-002**: The install command MUST create intermediate directories in the target project as needed before copying
- **FR-003**: The install command MUST report the installed version and the count of files/directories copied upon successful completion
- **FR-004**: The install command MUST accept a source path parameter that overrides the default source location
- **FR-005**: The install command MUST auto-detect the source tachi directory from the install script's own file location when no source path is explicitly provided
- **FR-006**: The install command MUST accept a version parameter that installs files from a specific tagged version
- **FR-007**: When a version parameter is provided, the install command MUST verify the tag exists before proceeding and list available tags on failure
- **FR-008**: When a version parameter is provided, the install command MUST check for uncommitted changes in the source repository and refuse to proceed if the working tree is dirty
- **FR-009**: When a version checkout is performed, the install command MUST restore the source repository to its original branch/state on any exit (success, error, or interruption)
- **FR-010**: The install command MUST be idempotent — running it multiple times produces the same result without error
- **FR-011**: The install command MUST never delete files in the target project — it only adds or overwrites
- **FR-012**: The install command MUST display usage information when invoked with a help flag
- **FR-013**: The install manifest MUST include a machine-parseable section with one distributable path per line, separate from the human-readable documentation tables
- **FR-014**: The install command MUST parse the machine-parseable section of the manifest, not the markdown tables
- **FR-015**: The README MUST present the scripted install as the primary Quick Start path (Step 2)
- **FR-016**: The README MUST preserve manual `cp -r` instructions in a collapsible section labeled as an alternative
- **FR-017**: The developer guide install section MUST be updated to reflect the scripted install as the primary method
- **FR-018**: The tachi repository MUST adopt semantic version tags in `vMAJOR.MINOR.PATCH` format
- **FR-019**: The first version tag MUST be `v4.0.0`, applied to the current main branch as a baseline
- **FR-020**: The install command MUST be compatible with Bash 3.2+ (macOS system bash) and have no external dependencies beyond git and standard Unix tools

### Key Entities

- **Install Manifest**: The source-of-truth document listing all distributable files and directories, containing both human-readable documentation and a machine-parseable path list
- **Version Tag**: A git tag in `vMAJOR.MINOR.PATCH` format that marks a specific release point for version-pinned installs
- **Source Directory**: The local tachi clone from which files are copied — auto-detected from the script's location or specified explicitly
- **Target Directory**: The user's project root (current working directory) where tachi files are installed

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: First-time install reduced from 6+ commands to 1 command
- **SC-002**: Install command copies all files listed in the install manifest (100% manifest coverage)
- **SC-003**: Install command completes in under 5 seconds for typical file count (~50 files)
- **SC-004**: Install command is idempotent — running twice produces identical results with zero errors
- **SC-005**: Version-pinned install restores source repository state in 100% of exit paths (normal, error, interrupt)
- **SC-006**: README Quick Start reflects the scripted install as primary path with manual fallback preserved
- **SC-007**: Install command provides clear error messages for all documented edge cases (missing source, invalid version, dirty tree, missing manifest)

## Assumptions

- Users have git installed and available on PATH
- Users have cloned tachi locally before running the install command
- The install manifest is the single source of truth for distributable files and is kept current
- The first version tag `v4.0.0` aligns with the current state of the main branch
- The additive-only behavior (never deleting stale files) is acceptable — users who want a clean install can remove old tachi files manually
- Auto-detection of source path from the script's location covers the majority of use cases, making the explicit source parameter an edge-case override
