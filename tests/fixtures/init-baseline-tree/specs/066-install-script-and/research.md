# Research Summary: Install Script and Version Tagging

## Knowledge Base Findings

- No existing KB entries found for install scripts or distribution workflows
- No prior bug fixes related to file copying or manifest parsing

## Codebase Analysis

### INSTALL_MANIFEST.md Format
- Located at repo root: `INSTALL_MANIFEST.md`
- Uses markdown tables with columns `Directory | Purpose | Required By` for directories
- Command files, agent files listed in separate tables (`File | Slash Command`, `File | Role`)
- Schema files listed as bullet points
- **No machine-parseable code block** — Architect and Team-Lead flagged this; the spec must require a machine-parseable section to avoid fragile markdown table parsing

### Existing Shell Script Conventions
- **Shebang**: `#!/bin/bash` or `#!/usr/bin/env bash` (both used)
- **Strict mode**: `set -euo pipefail` consistently used
- **Path detection**: `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` pattern used by `generate-adapter-version.sh` and `sync-upstream.sh`
- **Argument parsing**: Manual `while/case` pattern (not `getopts`) — supports long flags
- **Color output**: Defines color constants (`RED`, `GREEN`, etc.) for terminal output
- **Error handling**: `die()` helper, early validation, clear error messages
- **Exit codes**: 0 = success, 1 = error
- **Shared utilities**: `.aod/scripts/bash/common.sh` provides `get_repo_root()`, `get_current_branch()`, `has_git()`

### Current Manual Install Process (README.md Step 2)
- 6+ manual `cp -r` commands from `~/Projects/tachi`
- Uses `mkdir -p` for idempotency
- No version information captured
- No summary output
- Hardcoded source path throughout

### Developer Guide
- `docs/guides/DEVELOPER_GUIDE_TACHI.md` Step 2 duplicates the same 6 copy commands
- Troubleshooting section mentions re-copying files if missing
- No version pinning documentation

## Architecture Constraints

- **Relevant docs**: `docs/architecture/README.md` (template-level, no distribution-specific ADRs)
- **No existing ADR** for distribution strategy — the install script is the first formal distribution mechanism
- **Backward compatibility** (Constitution Principle III): Manual install path must be preserved
- **Git workflow** (Constitution Principle IX): First tag must follow semver, feature branch required
- **Testing** (Constitution Principle VI): Script must be testable

## Industry Research

### Shell Script Best Practices
- `set -euo pipefail` is the industry standard strict mode
- Manual `while/case` parsing preferred over `getopts` for long options with Bash 3.2+ portability
- `trap cleanup EXIT` ensures cleanup on all exit paths (normal, error, signal)
- `git status --porcelain` is the recommended dirty-tree check (catches staged, unstaged, and untracked)

### Manifest Parsing
- Use a fenced code block with a specific info string (e.g., ````manifest`) or HTML comment markers (`<!-- BEGIN MANIFEST -->`)
- Skip blank lines and comment lines (`#`) during parsing
- One path per line for reliable parsing

### Git Tagging
- Annotated tags preferred (`git tag -a`) — better `git describe` support, includes metadata
- `git describe --tags --always` provides version string: exact tag or `vX.Y.Z-N-gHASH`
- `--always` flag ensures fallback to commit hash when no tags exist
- List tags with `git tag -l 'v*' --sort=-v:refname` for version-sorted display

### Idempotent Copy
- `cp -r` overwrites by default (desired for updates)
- Never delete files not in manifest (additive-only behavior)
- `mkdir -p` before each target directory

## Recommendations for Spec

- **Require machine-parseable manifest section** in INSTALL_MANIFEST.md (addresses Architect + Team-Lead concern)
- **Require safe version checkout** with dirty-tree detection and guaranteed branch restoration (addresses Architect concern)
- **Require auto-detection of source path** from script location with `--source` as override (addresses Architect concern)
- **Explicitly document additive behavior** — script never deletes, only installs/overwrites (addresses Architect concern)
- **Specify first tag as `v4.0.0`** — matches current major version context (addresses Team-Lead concern)
- **Follow existing script conventions** — `set -euo pipefail`, `BASH_SOURCE` path detection, `while/case` argument parsing
- **Preserve manual install** in collapsible `<details>` block per US-005
