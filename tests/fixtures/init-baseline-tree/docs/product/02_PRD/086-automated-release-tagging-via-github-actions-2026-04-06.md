---
prd:
  number: "086"
  topic: automated-release-tagging-via-github-actions
  created: 2026-04-06
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-06
    status: APPROVED
    notes: "PRD authored by PM. Problem statement grounded in real pain from manual tagging. Scope disciplined with 6 explicit deferrals. Strategic alignment references PRD 066 escalation triggers with pragmatic override."
  architect_signoff:
    agent: architect
    date: 2026-04-06
    status: APPROVED
    notes: "Technically sound. release-please with simple release type is correct for non-package project. install.sh fully compatible with annotated tags. Advisory: first Release PR may be large given 14+ features since v4.0.0."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-06
    status: APPROVED
    notes: "Fully feasible. Realistic effort 2-3 hours, well within 1-sprint estimate. devops agent only, two-wave execution. All dependencies resolved."
source:
  idea_id: 86
  story_id: null
---

# Automated Release Tagging via GitHub Actions — Product Requirements Document

**Status**: Approved
**Created**: 2026-04-06
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1

---

## Executive Summary

### The One-Liner
Replace manual `git tag` commands with Google's release-please GitHub Action so tachi versions itself automatically from conventional commits.

### Problem Statement
Feature 066 introduced version tagging (v4.0.0) and `install.sh --version`, but creating tags remains a manual process: the maintainer must remember to run `git tag`, determine the correct semver bump, write CHANGELOG entries, and push the tag. This is error-prone (wrong version, forgotten tags, inconsistent CHANGELOG) and doesn't scale as release cadence increases.

### Proposed Solution
Adopt Google's release-please GitHub Action, which reads conventional commit messages on merge to main, auto-determines the semver bump, creates a Release PR with generated CHANGELOG entries, and — when the maintainer merges that PR — creates the git tag and GitHub Release automatically. The maintainer retains control over *when* to release while automating *what version*.

### Success Criteria
- Version tags are created automatically when a Release PR is merged
- CHANGELOG entries are generated from conventional commit messages
- Maintainer controls release timing via merge decision on Release PR
- `install.sh --version` continues to work with auto-generated tags
- Zero manual `git tag` commands required for standard releases

### Timeline
Single-phase delivery — estimated 1 sprint.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's mission is to be the default threat modeling toolkit for agentic AI applications. Automated releases reduce maintainer overhead, ensure consistent versioning for users who pin installs, and signal project maturity to potential adopters evaluating tachi.

### Roadmap Fit
This feature was explicitly deferred in PRD 066 under "Out of Scope" with escalation triggers:
- *"Revisit CI automation when tachi has >50 stars or >10 external users"*
- *"Revisit when release cadence exceeds monthly"*

While the star threshold hasn't been met, this is a low-effort, high-value automation that removes a manual bottleneck and sets the foundation for future distribution improvements. The effort (a single GitHub Actions workflow file) is minimal enough that waiting for the escalation trigger would be over-engineering the decision.

---

## Target Users & Personas

### Primary Persona: tachi Maintainer
- **Role**: Project maintainer responsible for releases
- **Experience**: Deep familiarity with git, conventional commits, GitHub
- **Goals**: Release new versions with minimal manual steps
- **Pain Points**: Must manually determine version bump, write CHANGELOG, run `git tag`, push tag, create GitHub Release

### Secondary Persona: tachi User Installing via Version Pin
- **Role**: Developer using `install.sh --version vX.Y.Z`
- **Experience**: Comfortable with CLI, expects stable tagged versions
- **Goals**: Install a specific, tested version of tachi
- **Pain Points**: Tags may lag behind actual releases if maintainer forgets to tag

---

## User Stories

### US-001: Automated Version Bump on Merge
**When** I merge a Release PR to main,
**I want to** have the git tag and GitHub Release created automatically,
**So I can** skip the manual `git tag && git push --tags` workflow entirely.

**Acceptance Criteria**:
- **Given** conventional commits have been merged to main, **when** release-please creates a Release PR and I merge it, **then** a new semver tag (e.g., v4.1.0) and GitHub Release are created automatically
- **Given** only `fix:` commits since last release, **when** the Release PR is merged, **then** the patch version increments (e.g., v4.0.0 → v4.0.1)
- **Given** a `feat:` commit since last release, **when** the Release PR is merged, **then** the minor version increments (e.g., v4.0.0 → v4.1.0)
- **Given** a commit with `BREAKING CHANGE:` footer, **when** the Release PR is merged, **then** the major version increments (e.g., v4.0.0 → v5.0.0)

**Priority**: P0
**Effort**: M

### US-002: Auto-Generated CHANGELOG
**When** a Release PR is created,
**I want to** see auto-generated CHANGELOG entries grouped by commit type,
**So I can** review what's included in the release before deciding to merge.

**Acceptance Criteria**:
- **Given** conventional commits exist since last release, **when** release-please creates a Release PR, **then** the PR body contains grouped entries (Features, Bug Fixes, Documentation, etc.)
- **Given** the Release PR is merged, **when** I check CHANGELOG.md, **then** it contains the same grouped entries with the new version header

**Priority**: P0
**Effort**: S

### US-003: Maintainer Release Control
**When** release-please creates a Release PR,
**I want to** decide when (or whether) to merge it,
**So I can** batch multiple features into a single release or delay a release if needed.

**Acceptance Criteria**:
- **Given** a Release PR is open, **when** new commits are merged to main, **then** the Release PR is updated with the additional changes (not a new PR)
- **Given** a Release PR exists, **when** I choose not to merge it, **then** no tag or release is created (release-please does not auto-merge)

**Priority**: P1
**Effort**: S

### US-004: Compatibility with install.sh --version
**When** a version tag is auto-created by release-please,
**I want to** use that tag with `install.sh --version vX.Y.Z`,
**So I can** pin installs to automatically generated versions.

**Acceptance Criteria**:
- **Given** release-please creates tag v4.1.0, **when** I run `install.sh --version v4.1.0`, **then** the script checks out that tag and installs files correctly
- **Given** the tag format is `vMAJOR.MINOR.PATCH`, **when** `git describe --tags` runs during install, **then** it reports the correct version

**Priority**: P1
**Effort**: S

---

## Functional Requirements

### FR-001: GitHub Actions Workflow (`.github/workflows/release-please.yml`)

**Description**: A GitHub Actions workflow file that runs release-please on push to main.

**Processing**:
1. Trigger on push to `main` branch
2. Run `google-github-actions/release-please-action` with `release-type: simple`
3. If a release is created, the action produces a tag and GitHub Release

**Configuration**:
- Release type: `simple` (no package manager, just tags and CHANGELOG)
- Versioning: Semantic versioning from conventional commits
- CHANGELOG: Auto-generated, committed to `CHANGELOG.md` in repo root
- Tag format: `vMAJOR.MINOR.PATCH` (matches existing v4.0.0 convention from Feature 066)

**Business Rules**:
- The workflow must not modify any files other than CHANGELOG.md and version metadata
- The workflow requires only `contents: write` and `pull-requests: write` permissions
- release-please uses a `release-please-config.json` and `.release-please-manifest.json` for configuration

### FR-002: release-please Configuration Files

**Description**: Configuration files that control release-please behavior.

**Files**:
- `release-please-config.json` — Release type, CHANGELOG sections, versioning strategy
- `.release-please-manifest.json` — Current version tracking (initially `{"." : "4.0.0"}`)

**Configuration Options**:
- `release-type`: `"simple"`
- `changelog-sections`: Map conventional commit types to CHANGELOG groups
- `bump-minor-pre-major`: `true` (feat: bumps minor, not major, until v1.0.0 — not applicable since we're already v4.x)
- `include-component-in-tag`: `false` (single-package repo, no component prefix)

### FR-003: CHANGELOG.md Generation

**Description**: release-please maintains a CHANGELOG.md at the repo root with grouped, versioned entries.

**Requirements**:
- New version entries prepended to existing CHANGELOG.md content
- Entries grouped by type: Features, Bug Fixes, Documentation, Miscellaneous
- Each entry links to its commit or PR
- Manual CHANGELOG entries (pre-automation) are preserved below the auto-generated section

### FR-004: Existing Workflow Compatibility

**Description**: The automation must not break existing manual workflows.

**Requirements**:
- Manual `git tag` still works if needed (escape hatch)
- `install.sh --version` works with both manual and auto-generated tags
- `git describe --tags` reports correct version regardless of tag origin
- Existing v4.0.0 tag is recognized as the release baseline

---

## Non-Functional Requirements

### Reliability
- release-please action runs on GitHub's hosted runners (no self-hosted infrastructure)
- If the action fails, no tag is created — safe failure mode
- Release PR is idempotent — re-running on same commits produces same PR

### Security
- Workflow uses minimal permissions: `contents: write`, `pull-requests: write`
- No secrets required beyond default `GITHUB_TOKEN`
- No third-party actions beyond Google's official `release-please-action`

### Portability
- Configuration is standard GitHub Actions YAML — portable to any GitHub repo
- release-please is the most widely adopted release automation for GitHub (40k+ stars)

---

## Scope & Boundaries

### In Scope (P0/P1)
- **P0**: `.github/workflows/release-please.yml` workflow file
- **P0**: `release-please-config.json` configuration
- **P0**: `.release-please-manifest.json` version tracking (baseline v4.0.0)
- **P0**: Auto-generated CHANGELOG.md entries on release
- **P1**: Documentation in README referencing the release process
- **P1**: Verify `install.sh --version` compatibility with auto-tags

### Out of Scope (Deferred)
- **Curated release artifacts** (tarballs, checksums) — build on this foundation later
- **Pre-release channels** (`v4.1.0-rc.1`) — release-please supports this but not needed yet
- **NPM/PyPI publishing** — tachi is not a package; install is via git clone + script
- **Branch protection rules** — separate operational concern
- **Automated testing in release workflow** — CI tests already run on PR; release workflow just tags
- **CHANGELOG migration** — existing manual CHANGELOG content is preserved as-is below auto-generated section

### Assumptions
- The repository uses conventional commits consistently (established by Constitution Principle IX)
- GitHub Actions is available and enabled on the repository
- The maintainer has write access to the repository

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: Inconsistent conventional commit usage breaks version detection
- **Likelihood**: Low (Constitution mandates conventional commits)
- **Impact**: Low (release-please defaults to patch bump for unrecognized commits)
- **Mitigation**: Existing commit conventions already follow conventional format

**Risk 2**: release-please conflicts with manually created tags
- **Likelihood**: Low
- **Impact**: Low (release-please reads its manifest, not git tags directly)
- **Mitigation**: Set manifest baseline to current version (v4.0.0); manual tags still work

### Dependencies

**Internal Dependencies**:
- Feature 066 (Install Script and Version Tagging) — DELIVERED
- Conventional commit convention — established by Constitution

**External Dependencies**:
- `google-github-actions/release-please-action` — actively maintained, 40k+ GitHub stars
- GitHub Actions platform availability

---

## Analysis

Continuing the analysis from PRD 066:
- **Pareto**: The workflow file + 2 config files deliver full release automation with ~2 hours of effort
- **Build vs Buy**: release-please is the industry standard (Google, Terraform, Angular all use it) — no reason to build custom automation
- **Escalation Trigger**: PRD 066 deferred this to ">50 stars or >10 external users." The effort is so minimal (3 files, zero infrastructure) that the trigger threshold is moot — the cost of *not* automating exceeds the cost of automation

---

## Open Questions

- [x] Should we use `simple` or `node` release type? — `simple` (tachi is not an npm package)
- [x] Should the Release PR auto-merge? — No, maintainer controls timing by merging manually
- [x] What about the existing manual CHANGELOG? — Preserved as-is; new entries prepended above

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- PRD 066 (Install Script): [066-install-script-and-version-tagging-2026-04-06.md](066-install-script-and-version-tagging-2026-04-06.md)

### External Resources
- [release-please GitHub Action](https://github.com/google-github-actions/release-please-action)
- [release-please documentation](https://github.com/googleapis/release-please)
- [Conventional Commits specification](https://www.conventionalcommits.org/)

### Source
- GitHub Issue: [#86 — Automated release tagging via GitHub Actions (release-please)](https://github.com/davidmatousek/tachi/issues/86)
