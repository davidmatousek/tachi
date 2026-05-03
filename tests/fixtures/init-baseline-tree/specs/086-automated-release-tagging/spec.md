---
prd_reference: docs/product/02_PRD/086-automated-release-tagging-via-github-actions-2026-04-06.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-06
    status: APPROVED
    notes: "All 4 PRD user stories covered with faithful acceptance scenarios. All PRD functional requirements decomposed into 15 granular, testable requirements. No scope creep. Advisory: priority labels shifted one level from PRD but delivery unaffected."
  architect_signoff: null
  techlead_signoff: null
---

# Feature Specification: Automated Release Tagging via GitHub Actions

**Feature Branch**: `086-automated-release-tagging`
**Created**: 2026-04-06
**Status**: Draft
**PRD Reference**: `docs/product/02_PRD/086-automated-release-tagging-via-github-actions-2026-04-06.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Version Tag on Release PR Merge (Priority: P1)

When the maintainer merges a Release PR to main, a git tag and GitHub Release are created automatically based on the conventional commits since the last release. The maintainer no longer runs manual `git tag` commands for standard releases.

**Why this priority**: This is the core value proposition — eliminating manual tagging while maintaining maintainer control over release timing.

**Independent Test**: Can be fully tested by merging a Release PR and verifying a new tag and GitHub Release appear within minutes.

**Acceptance Scenarios**:

1. **Given** conventional commits have been merged to main since the last release, **When** release-please creates a Release PR and the maintainer merges it, **Then** a new semver tag (e.g., v4.1.0) and GitHub Release are created automatically
2. **Given** only `fix:` commits since the last release, **When** the Release PR is merged, **Then** the patch version increments (e.g., v4.0.0 to v4.0.1)
3. **Given** at least one `feat:` commit since the last release, **When** the Release PR is merged, **Then** the minor version increments (e.g., v4.0.0 to v4.1.0)
4. **Given** a commit with `BREAKING CHANGE:` footer or `!` suffix, **When** the Release PR is merged, **Then** the major version increments (e.g., v4.0.0 to v5.0.0)

---

### User Story 2 - Auto-Generated CHANGELOG Entries (Priority: P1)

When release-please creates a Release PR, the PR body contains grouped CHANGELOG entries derived from conventional commit messages. When merged, these entries are written to CHANGELOG.md with the new version header.

**Why this priority**: Eliminates manual CHANGELOG writing while ensuring every release has accurate, commit-linked documentation.

**Independent Test**: Can be tested by inspecting the Release PR body for grouped entries and verifying CHANGELOG.md is updated after merge.

**Acceptance Scenarios**:

1. **Given** conventional commits exist since the last release, **When** release-please creates a Release PR, **Then** the PR body contains entries grouped by type (Features, Bug Fixes, Documentation, etc.)
2. **Given** the Release PR is merged, **When** CHANGELOG.md is checked, **Then** a new version header with grouped entries has been prepended above existing content
3. **Given** manual CHANGELOG entries exist from before automation, **When** a release is created, **Then** the pre-existing manual entries are preserved below the auto-generated entries

---

### User Story 3 - Maintainer Controls Release Timing (Priority: P2)

The maintainer decides when to release by choosing when to merge the Release PR. New commits merged to main after the Release PR is created update the existing PR rather than creating a new one.

**Why this priority**: Ensures the maintainer retains full control — automation handles version calculation, not release timing decisions.

**Independent Test**: Can be tested by leaving a Release PR open, merging additional commits to main, and verifying the PR updates in place.

**Acceptance Scenarios**:

1. **Given** a Release PR is open, **When** additional conventional commits are merged to main, **Then** the existing Release PR is updated with the new entries (no duplicate PR created)
2. **Given** a Release PR exists, **When** the maintainer chooses not to merge it, **Then** no tag or release is created

---

### User Story 4 - Compatibility with Pinned Installs (Priority: P2)

Tags created by release-please work seamlessly with the existing `install.sh --version` command. Users who pin installs to specific versions experience no change in behavior.

**Why this priority**: Preserves backward compatibility with the install workflow established by Feature 066.

**Independent Test**: Can be tested by running `install.sh --version vX.Y.Z` with an auto-generated tag and verifying successful install.

**Acceptance Scenarios**:

1. **Given** release-please creates tag v4.1.0, **When** a user runs `install.sh --version v4.1.0`, **Then** the script checks out that tag and installs files correctly
2. **Given** the tag format is `vMAJOR.MINOR.PATCH`, **When** `git describe --tags` runs during install, **Then** it reports the correct auto-generated version

---

### Edge Cases

- What happens when a commit does not follow conventional commit format? release-please ignores it — no version bump for unrecognized commits
- What happens when no releasable commits exist since the last release? No Release PR is created
- What happens when the Release PR is closed without merging? No tag or release is created; a new Release PR will be created on the next push with releasable commits
- What happens if someone manually creates a git tag that conflicts? release-please tracks version in its manifest file, not from git tags — manual tags do not interfere
- What happens on the first run after setup? release-please reads the manifest baseline (v4.0.0) and creates a Release PR for all conventional commits since v4.0.0; this initial PR may be large

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST create a GitHub Actions workflow that triggers on push to the `main` branch
- **FR-002**: The workflow MUST run release-please to analyze conventional commits since the last release
- **FR-003**: The system MUST create a Release PR when releasable commits are detected (feat, fix, or breaking change)
- **FR-004**: The system MUST auto-determine the semver version bump based on conventional commit types (patch for fix, minor for feat, major for breaking change)
- **FR-005**: The system MUST create a git tag and GitHub Release when the Release PR is merged
- **FR-006**: The system MUST generate CHANGELOG entries grouped by commit type (Features, Bug Fixes, Documentation, etc.)
- **FR-007**: The system MUST update CHANGELOG.md with new version entries prepended above existing content
- **FR-008**: The system MUST preserve existing manual CHANGELOG entries from before automation
- **FR-009**: The system MUST track the current version in a manifest file initialized to the existing baseline (v4.0.0)
- **FR-010**: The system MUST use the tag format `vMAJOR.MINOR.PATCH` to match the existing convention
- **FR-011**: The workflow MUST use only the default GITHUB_TOKEN — no additional secrets required
- **FR-012**: The workflow MUST request minimal permissions (contents write, pull-requests write)
- **FR-013**: The system MUST NOT modify any repository files other than CHANGELOG.md and version metadata during the release process
- **FR-014**: Manual `git tag` MUST continue to work as an escape hatch alongside automation
- **FR-015**: Tags created by the automation MUST be compatible with `install.sh --version`

### Key Entities

- **Release PR**: An auto-generated pull request containing version bump metadata and CHANGELOG entries. One Release PR exists at a time per branch; it accumulates commits until merged.
- **Version Manifest**: A JSON file tracking the current released version. Serves as the baseline for the next version calculation.
- **Release Configuration**: A JSON file defining release behavior — release type, CHANGELOG section groupings, and versioning strategy.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After setup, merging a Release PR produces a correctly versioned git tag and GitHub Release with zero manual intervention
- **SC-002**: CHANGELOG.md entries are auto-generated and grouped by commit type for every release
- **SC-003**: The maintainer controls release timing exclusively through the decision to merge or not merge the Release PR
- **SC-004**: `install.sh --version` works identically with auto-generated tags as with manually created tags
- **SC-005**: Zero manual `git tag` commands required for standard releases after automation is active
- **SC-006**: The workflow adds no infrastructure cost (runs on GitHub-hosted runners using free tier)
- **SC-007**: The total deliverable is 3 new files plus optional documentation updates — no changes to existing application files

## Assumptions

- The repository will continue using conventional commit messages as established by Constitution Principle IX
- GitHub Actions is enabled on the repository (default for public repos)
- The maintainer has write access to the repository for merging Release PRs
- The existing v4.0.0 tag serves as the correct baseline for the first automated release
- The "Unreleased" section in the current CHANGELOG.md will be consumed by the first Release PR
