---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-06
    status: APPROVED
    notes: "All 15 spec requirements covered. Zero scope creep. Phases correctly sequenced P0 before P1. Risks reasonable with concrete mitigations."
  architect_signoff:
    agent: architect
    date: 2026-04-06
    status: APPROVED
    notes: "Architecture sound. release-please v4 simple type correct for non-package repo. install.sh compatibility verified at code level. Security minimal and correct. Constitution compliance confirmed. Advisory: CHANGELOG will have two visual styles after first release."
  techlead_signoff: null
---

# Implementation Plan: Automated Release Tagging via GitHub Actions

**Branch**: `086-automated-release-tagging` | **Date**: 2026-04-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/086-automated-release-tagging/spec.md`

## Summary

Automate version tagging using Google's release-please GitHub Action. Three configuration files are added to the repository: a GitHub Actions workflow, a release-please config, and a version manifest. No existing application files are modified. CHANGELOG.md will be auto-maintained by release-please on each release.

## Technical Context

**Language/Version**: YAML (GitHub Actions workflow syntax), JSON (release-please config)
**Primary Dependencies**: `googleapis/release-please-action@v4` (GitHub Action)
**Storage**: `.release-please-manifest.json` (version tracking, JSON)
**Testing**: Manual validation — merge a conventional commit, verify Release PR creation, merge Release PR, verify tag + GitHub Release
**Target Platform**: GitHub Actions (GitHub-hosted runners)
**Project Type**: Configuration-only (no source code changes)
**Performance Goals**: N/A — workflow runs asynchronously on push events
**Constraints**: Workflow must use only default GITHUB_TOKEN; no additional secrets or self-hosted runners
**Scale/Scope**: Single workflow file, 2 config files, optional README update

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Release automation is domain-agnostic — works for any project |
| II. API-First Design | N/A | No APIs involved; this is CI/CD configuration |
| III. Backward Compatibility | PASS | Manual `git tag` still works; install.sh unchanged |
| IV. Concurrency & Data Integrity | N/A | No concurrent state mutations |
| V. Privacy & Data Isolation | PASS | No sensitive data; uses only default GITHUB_TOKEN |
| VI. Testing Excellence | PASS | Manual validation sufficient for 3 config files; no application logic to unit test |
| VII. Definition of Done | PASS | Will validate via actual release workflow execution |
| VIII. Observability | N/A | GitHub Actions provides built-in logging |
| IX. Git Workflow | PASS | Feature branch workflow followed; conventional commits are the input |
| X. Product-Spec Alignment | PASS | PRD 086 approved, spec approved with PM sign-off |
| XI. SDLC Triad | PASS | Triple sign-off in progress |

No violations. All applicable gates pass.

## Project Structure

### Documentation (this feature)

```
specs/086-automated-release-tagging/
├── plan.md              # This file
├── research.md          # Research phase output (completed)
├── spec.md              # Feature specification (approved)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (pending)
```

### Source Code (repository root)

```
.github/
└── workflows/
    └── release-please.yml       # NEW: GitHub Actions workflow

release-please-config.json      # NEW: Release configuration
.release-please-manifest.json   # NEW: Version manifest (baseline v4.0.0)
CHANGELOG.md                    # EXISTING: Auto-maintained by release-please
```

**Structure Decision**: No source code directories needed. This feature adds 3 files at the repository root level (2 JSON configs) and in `.github/workflows/` (1 YAML workflow). The existing CHANGELOG.md is modified only by release-please during releases, not during implementation.

## Components

### Component 1: GitHub Actions Workflow (`.github/workflows/release-please.yml`)

**Purpose**: Triggers release-please on every push to `main` branch.

**Configuration**:
- Trigger: `on: push: branches: [main]`
- Permissions: `contents: write`, `pull-requests: write`
- Action: `googleapis/release-please-action@v4`
- Release type: `simple`

**Behavior**:
1. On push to main, release-please analyzes commits since last release
2. If releasable commits found, creates or updates a Release PR
3. When Release PR is merged, creates git tag + GitHub Release

### Component 2: Release Configuration (`release-please-config.json`)

**Purpose**: Controls release-please behavior — release type, CHANGELOG grouping, versioning.

**Key settings**:
- `release-type`: `"simple"` (no package manager integration)
- `changelog-sections`: Maps conventional commit types to CHANGELOG groups (Features, Bug Fixes, Documentation, Miscellaneous)
- `include-component-in-tag`: `false` (single-package repo)

### Component 3: Version Manifest (`.release-please-manifest.json`)

**Purpose**: Tracks current released version. release-please reads this to determine the baseline for the next version bump.

**Initial value**: `{"." : "4.0.0"}` — matches existing v4.0.0 tag from Feature 066.

## Data Flow

```
Developer merges PR to main
         │
         ▼
GitHub Actions triggers release-please.yml
         │
         ▼
release-please reads .release-please-manifest.json (current: 4.0.0)
         │
         ▼
Analyzes conventional commits since v4.0.0
         │
         ├─ No releasable commits → Exit (no action)
         │
         └─ Releasable commits found
              │
              ▼
         Creates/updates Release PR
         (PR body = grouped CHANGELOG entries)
              │
              ├─ Maintainer does NOT merge → PR stays open, accumulates
              │
              └─ Maintainer merges Release PR
                   │
                   ▼
              release-please creates:
              1. Git tag (e.g., v4.1.0)
              2. GitHub Release with notes
              3. Updates CHANGELOG.md
              4. Updates .release-please-manifest.json to new version
```

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| CI/CD | GitHub Actions | Already the platform; zero additional infrastructure |
| Release Automation | release-please v4 | Industry standard (40k+ stars), maintained by Google, used by Terraform/Angular |
| Configuration | JSON | release-please's native config format |
| Versioning | Semantic Versioning | Matches existing v4.0.0 convention from Feature 066 |

## Implementation Phases

### Phase 1: Core Configuration (P0)

**Deliverables**:
1. Create `.github/workflows/release-please.yml`
2. Create `release-please-config.json`
3. Create `.release-please-manifest.json` with baseline `{"." : "4.0.0"}`

**Validation**: Files are syntactically valid YAML/JSON. Workflow passes GitHub Actions syntax check.

### Phase 2: Verification & Documentation (P1)

**Deliverables**:
1. Verify tag format compatibility with `install.sh --version`
2. Update README with release process documentation (optional section)
3. Verify CHANGELOG.md format is compatible with release-please

**Validation**: End-to-end verification after merge to main — Release PR appears with correct version and CHANGELOG entries.

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| First Release PR is large (14+ features since v4.0.0) | High | Low | Expected behavior — maintainer reviews and merges when ready |
| CHANGELOG format conflict with existing manual entries | Low | Low | release-please prepends new entries; manual entries preserved below |
| release-please action version breaking change | Low | Medium | Pin to `@v4`; Dependabot can manage updates |

## Complexity Tracking

No constitution violations. No complexity justifications needed.
