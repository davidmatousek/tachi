---
prd:
  number: "066"
  topic: install-script-and-version-tagging
  created: 2026-04-06
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-06
    status: APPROVED
    notes: "PRD authored by PM. Problem statement clear, user stories grounded in real pain (6-step copy process), scope disciplined with explicit deferrals."
  architect_signoff:
    agent: architect
    date: 2026-04-06
    status: APPROVED_WITH_CONCERNS
    notes: "Feasible and well-aligned. Concerns: (1) Change POSIX sh to Bash 3.2+ to match existing conventions, (2) Add machine-parseable section to INSTALL_MANIFEST.md, (3) Require trap handler + dirty-tree check for --version checkout."
  techlead_signoff:
    agent: team-lead
    date: 2026-04-06
    status: APPROVED_WITH_CONCERNS
    notes: "Feasible at 7-10 hours. Concerns: (1) Manifest parsing fragility — recommend machine-parseable section, (2) Specify first tag version number during planning."
source:
  idea_id: 66
  story_id: null
---

# Install Script and Version Tagging — Product Requirements Document

**Status**: Approved
**Created**: 2026-04-06
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P1

---

## Executive Summary

### The One-Liner
Replace tachi's 6 manual copy commands with a single `install.sh` script and adopt git tags for versioned distribution.

### Problem Statement
Installing tachi into a target project requires cloning the repo and running 6+ manual `cp -r` commands, referencing the correct source paths, creating intermediate directories, and remembering which files go where. This process is error-prone — the adapters directory was chronically out of sync — and creates a poor first-time experience for users evaluating tachi.

### Proposed Solution
A shell script (`scripts/install.sh`) that reads `INSTALL_MANIFEST.md` paths and copies all distributable files to the target project in one command. Git tags provide version pinning with zero infrastructure cost.

### Success Criteria
- First-time install reduced from 6+ commands to 1 command
- Script installs all files listed in `INSTALL_MANIFEST.md`
- Users can pin to a specific version via `--version` flag
- README Quick Start reflects the new install path

### Timeline
Single-phase delivery — estimated 1 sprint.

---

## Strategic Alignment

### Product Vision Alignment
**Reference**: [product-vision.md](../01_Product_Vision/product-vision.md)

tachi's mission is to be the default threat modeling toolkit for teams building agentic AI applications. A frictionless install experience directly supports adoption — every manual step in setup is a drop-off point for potential users.

### Roadmap Fit
This is a distribution improvement that unblocks future growth. Once install is scripted, future distribution enhancements (GitHub Releases, curated tarballs, checksums) can build on this foundation.

---

## Target Users & Personas

### Primary Persona: Developer Evaluating tachi
- **Role**: Software engineer building AI agents
- **Experience**: Comfortable with CLI, git, shell scripts
- **Goals**: Quickly add threat modeling to their project
- **Pain Points**: The 6-step copy process is tedious, error-prone, and hard to remember

### Secondary Persona: Existing tachi User Updating
- **Role**: Developer already using tachi who pulls latest changes
- **Goals**: Update tachi files in their project to match latest version
- **Pain Points**: Re-running 6 copy commands after every update; unsure which files changed

---

## User Stories

### US-001: First-Time Install
**When** I clone tachi and want to add threat modeling to my project,
**I want to** run a single install command from my project root,
**So I can** start threat modeling without memorizing 6+ copy commands.

**Acceptance Criteria**:
- **Given** tachi is cloned to `~/Projects/tachi`, **when** I run `install.sh` from my project root, **then** all INSTALL_MANIFEST.md files are copied to the correct locations
- **Given** the install completes, **when** I check the output, **then** I see a summary of what was installed and from which version
- **Given** intermediate directories don't exist, **when** the script runs, **then** it creates them automatically

**Priority**: P0
**Effort**: M

### US-002: Pinned Version Install
**When** I need a reproducible install for CI or team onboarding,
**I want to** install from a specific tagged version,
**So I can** ensure every team member has the exact same tachi version.

**Acceptance Criteria**:
- **Given** tachi has git tags, **when** I run `install.sh --version v4.0.1`, **then** the script checks out that tag, installs files, and restores the previous branch
- **Given** the requested version tag doesn't exist, **when** I run the script, **then** I get a clear error message listing available tags

**Priority**: P1
**Effort**: M

### US-003: Custom Source Location
**When** I have tachi cloned to a non-default directory,
**I want to** specify the source path,
**So I can** install from wherever my local clone lives.

**Acceptance Criteria**:
- **Given** tachi is at `/opt/tools/tachi`, **when** I run `install.sh --source /opt/tools/tachi`, **then** files are copied from that location
- **Given** no `--source` flag, **when** I run the script, **then** it defaults to `~/Projects/tachi`

**Priority**: P1
**Effort**: S

### US-004: Update Existing Install
**When** I pull the latest tachi changes,
**I want to** re-run the install script to update my project,
**So I can** get the latest agents, commands, and schemas without manual diffing.

**Acceptance Criteria**:
- **Given** tachi files already exist in my project, **when** I re-run `install.sh`, **then** updated files overwrite old ones
- **Given** the install completes, **when** I check the output, **then** I see the installed version so I know what changed

**Priority**: P0
**Effort**: S

### US-005: Manual Install Preserved
**When** I prefer manual control over what's copied,
**I want to** still use the documented `cp -r` commands,
**So I can** selectively install only the parts I need.

**Acceptance Criteria**:
- **Given** the README is updated, **when** I look for manual install instructions, **then** they exist in a collapsible `<details>` block
- **Given** `INSTALL_MANIFEST.md` exists, **when** I reference it, **then** it still documents all distributable paths

**Priority**: P1
**Effort**: S

---

## Functional Requirements

### FR-001: Install Script (`scripts/install.sh`)

**Description**: A Bash 3.2+ compatible shell script that copies all distributable files from a tachi source directory to the current working directory (the target project). Bash 3.2+ is chosen to match existing tachi script conventions and macOS system bash.

**Inputs**:
- `--source <path>` — Path to tachi clone (default: `~/Projects/tachi`)
- `--version <tag>` — Git tag to install from (default: current HEAD)
- `--help` — Display usage information

**Processing**:
1. Validate source directory exists and contains `INSTALL_MANIFEST.md`
2. If `--version` specified, verify tag exists and checkout
3. Parse `INSTALL_MANIFEST.md` for distributable paths
4. Create target directories as needed (`mkdir -p`)
5. Copy files and directories to target project root
6. Report installed version (`git describe --tags`) and file count
7. If version checkout was performed, restore original branch/state

**Outputs**:
- All INSTALL_MANIFEST.md files copied to target project
- Summary output: version installed, file/directory count, source path

**Business Rules**:
- Script must be Bash 3.2+ compatible (matching existing tachi script conventions and macOS system bash)
- Script must not modify the source tachi directory (except transient git checkout)
- Script must be idempotent — safe to re-run

**Edge Cases**:
- Source directory missing: Exit with clear error and guidance
- Invalid version tag: Exit with error listing available tags
- Partial install (disk full, permission denied): Report which files failed

### FR-002: Git Version Tagging

**Description**: Adopt semantic version tags on the tachi repository for version-pinned installs.

**Requirements**:
- Tag format: `vMAJOR.MINOR.PATCH` (e.g., `v4.0.0`)
- First tag pushed from current main as the baseline
- `git describe --tags` used by install script to report version
- Tags are lightweight git tags (no GPG signing required at current scale)

### FR-003: README Quick Start Update

**Description**: Update README.md Step 2 to use the install script as the primary path.

**Requirements**:
- Script-based install as the default Step 2
- Existing `cp -r` commands moved into a collapsible `<details>` block labeled "Manual install (alternative)"
- Developer Guide install section updated to match

---

## Non-Functional Requirements

### Portability
- Bash 3.2+ compatibility (macOS system bash, Linux, WSL)
- No external dependencies beyond git and standard Unix tools (cp, mkdir, echo)

### Performance
- Install completes in under 5 seconds for typical file count (~50 files)

### Reliability
- Idempotent execution — running twice produces same result
- No data loss in target project (overwrites tachi files only, never deletes user files)

---

## Scope & Boundaries

### In Scope (P0/P1)
- **P0**: `scripts/install.sh` with INSTALL_MANIFEST.md parsing and file copying
- **P0**: Script reports installed version and file count
- **P1**: `--version` flag for pinned install from tagged checkout
- **P1**: `--source` flag with `~/Projects/tachi` default
- **P1**: README Quick Start updated (script primary, manual in `<details>`)
- **P1**: Developer Guide install section updated
- **P1**: Existing manual install path preserved as alternative
- **P1**: First git tag pushed from current main

### Out of Scope (Deferred)
- **GitHub Actions release workflow** — manual `git tag` sufficient at current scale
- **release-please automation** — premature for current release cadence
- **Curated tarball** (excluding dev files) — source archive + install script handles this
- **Checksums/signing** — premature for current audience size
- **Pre-release channels** — `git tag v4.1.0-rc.1` works natively if needed later

### Escalation Triggers
Revisit CI automation when:
- tachi has >50 stars or >10 external users
- Release cadence exceeds monthly
- Adapter generation needs to be part of the release

### Assumptions
- Users have git installed and available on PATH
- Users have cloned tachi locally before running install
- `INSTALL_MANIFEST.md` is the single source of truth for distributable files

---

## Risks & Dependencies

### Technical Risks

**Risk 1**: INSTALL_MANIFEST.md format changes break script parsing
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Script validates manifest format before processing; clear error if unparseable

**Risk 2**: Version checkout leaves source repo in detached HEAD state
- **Likelihood**: Low
- **Impact**: Medium
- **Mitigation**: Script records current branch before checkout and restores after install

### Dependencies

**Internal Dependencies**:
- `INSTALL_MANIFEST.md` must be current and accurate
- Existing directory structure must match manifest paths

---

## Analysis

Rescoped after applying thinking lenses (from Issue #66):
- **Pareto**: Install script + git tags deliver 80% of distribution value with ~5% of the effort of a full release pipeline
- **Cargo Cult Detection**: GitHub Releases with CI/CD imitates mature OSS distribution patterns that solve problems tachi doesn't have yet (compiled binaries, large user base, package manager integrations)

---

## Reviewer Concerns (Address in Spec)

The following concerns were raised during Triad review and should be addressed during `/aod.plan`:

1. **Machine-parseable manifest section** (Architect + Team-Lead): Add a code block with one path per line to INSTALL_MANIFEST.md so the script parses a clean list, not markdown tables
2. **Trap handler for --version checkout** (Architect): Script must use `trap` to restore branch on any exit; must check for dirty working tree before checkout
3. **Auto-detect source from script location** (Architect): Support inferring `--source` from the script's own path (like existing `generate-adapter-version.sh`), with `--source` as override
4. **Document additive behavior** (Architect): Clarify the script installs/overwrites but never deletes — stale files from prior versions persist
5. **First tag version number** (Team-Lead): Decide version number (`v4.0.0` or similar) during planning

---

## Open Questions

- [x] Should the script support `--dry-run` to preview what would be copied? — Deferred to future enhancement
- [x] Should the script handle `.gitignore` updates in the target project? — Out of scope; user manages their own gitignore

---

## References

### Product Documentation
- Product Vision: [product-vision.md](../01_Product_Vision/product-vision.md)
- Install Manifest: [INSTALL_MANIFEST.md](../../INSTALL_MANIFEST.md)
- Developer Guide: [DEVELOPER_GUIDE_TACHI.md](../../docs/guides/DEVELOPER_GUIDE_TACHI.md)

### Source
- GitHub Issue: [#66 — Install script and version tagging](https://github.com/davidmatousek/tachi/issues/66)
