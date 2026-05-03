---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-06
    status: APPROVED
    notes: "20/20 FRs covered, 6/6 user stories implementable, zero scope creep, all 5 PRD reviewer concerns resolved. 7/7 success criteria verifiable from planned implementation."
  architect_signoff:
    agent: architect
    date: 2026-04-06
    status: APPROVED_WITH_CONCERNS
    notes: "Technically sound. 4 non-blocking concerns: (1) trap handler guard variable for pre-checkout failures, (2) detached HEAD fallback using full SHA, (3) shebang choice is correct improvement, (4) manifest maintenance checklist should include machine-parseable section."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Install Script and Version Tagging

**Branch**: `066-install-script-and` | **Date**: 2026-04-06 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/066-install-script-and/spec.md`

## Summary

Replace tachi's 6-step manual copy process with a single `scripts/install.sh` Bash script that reads a machine-parseable section from `INSTALL_MANIFEST.md` and copies all distributable files to the target project. Adopt git version tags (`v4.0.0` as first baseline) to enable version-pinned installs. Update README.md and Developer Guide to use the scripted install as the primary path.

## Technical Context

**Language/Version**: Bash 3.2+ (macOS system bash compatibility; matches existing tachi scripts)
**Primary Dependencies**: git, standard Unix tools (cp, mkdir, echo, dirname, pwd)
**Storage**: Filesystem only — copy files from source to target directory
**Testing**: Manual testing with shellcheck static analysis; test matrix: macOS Bash 3.2, Linux Bash 5.x
**Target Platform**: macOS (Bash 3.2+), Linux, WSL
**Project Type**: Single shell script + documentation updates (no application code)
**Performance Goals**: Install completes in <5 seconds for ~50 files
**Constraints**: No external dependencies beyond git and coreutils; no Bash 4+ features (associative arrays, `|&`, etc.)
**Scale/Scope**: ~200 line script, 3 documentation updates, 1 manifest update, 1 git tag

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| III. Backward Compatibility | PASS | Manual install preserved in collapsible `<details>` block (FR-016) |
| VI. Testing Excellence | PASS | Shellcheck validation + manual test matrix planned |
| VII. Definition of Done | PASS | DoD steps: push to main via PR, test on macOS+Linux, user validates install |
| IX. Git Workflow | PASS | Feature branch `066-install-script-and`, conventional commits, PR before merge |
| X. Product-Spec Alignment | PASS | Plan derived from PM-approved spec with full PRD traceability |

No violations. No complexity tracking entries needed.

## Project Structure

### Documentation (this feature)

```
specs/066-install-script-and/
├── plan.md              # This file
├── research.md          # Research phase output (completed during spec)
├── spec.md              # Feature specification (PM approved)
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
scripts/
└── install.sh           # NEW — main install script (~200 lines)

INSTALL_MANIFEST.md      # MODIFIED — add machine-parseable section
README.md                # MODIFIED — update Step 2 Quick Start
docs/guides/
└── DEVELOPER_GUIDE_TACHI.md  # MODIFIED — update install section
```

**Structure Decision**: No new directories created. The install script lives in the existing `scripts/` directory alongside `generate-adapter-version.sh`, `sync-upstream.sh`, and `check.sh`. All changes are additions or modifications to existing files at the repository root level.

## Components

### C1: Install Script (`scripts/install.sh`)

The core deliverable. A Bash 3.2+ script that:

1. **Auto-detects source path** from its own location using `${BASH_SOURCE[0]}` + `dirname` + `pwd` (matching the pattern in `generate-adapter-version.sh`), with `--source` as override
2. **Parses arguments** using manual `while/case` pattern (matching `sync-upstream.sh` convention): `--source <path>`, `--version <tag>`, `--help`
3. **Validates environment**: source dir exists, `INSTALL_MANIFEST.md` exists, git available (for version features)
4. **Handles version checkout** (when `--version` specified):
   - Checks for dirty working tree via `git status --porcelain`
   - Records current branch via `git rev-parse --abbrev-ref HEAD`
   - Registers `trap cleanup EXIT` to restore branch on any exit path
   - Validates tag exists; lists available tags on failure
   - Checks out requested tag
5. **Parses manifest**: Extracts paths from the machine-parseable code block (between `<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->` markers), skipping blank lines and comments
6. **Copies files**: For each manifest path, runs `mkdir -p` + `cp -r` to target (current working directory). Counts successes/failures.
7. **Reports summary**: Installed version (via `git describe --tags --always`), file/directory count, source path

**Script conventions** (matching existing tachi scripts):
- Shebang: `#!/usr/bin/env bash`
- Strict mode: `set -euo pipefail`
- Sources `common.sh` for `get_repo_root()` if available
- Color output constants (`RED`, `GREEN`, `NC`) for terminal feedback
- `die()` and `usage()` helper functions
- Exit codes: 0 = success, 1 = error

### C2: Machine-Parseable Manifest Section

Add an HTML comment-delimited section to `INSTALL_MANIFEST.md` containing one distributable path per line. This is the section the install script parses — the existing markdown tables remain for human documentation.

Format:
```markdown
<!-- BEGIN MANIFEST -->
.claude/agents/tachi/
.claude/commands/threat-model.md
.claude/commands/risk-score.md
.claude/commands/compensating-controls.md
.claude/commands/infographic.md
.claude/commands/security-report.md
schemas/
templates/tachi/
adapters/claude-code/agents/references/
brand/
docs/guides/DEVELOPER_GUIDE_TACHI.md
<!-- END MANIFEST -->
```

Each line is either a directory (trailing `/`) or an individual file. The script uses this distinction to choose `cp -r` for directories and `cp` for files.

### C3: README Quick Start Update

Modify README.md Step 2 ("Add tachi to your project"):
- Replace the 6 `cp -r` commands with a single `install.sh` invocation
- Show version-pinned variant as a secondary example
- Move existing manual commands into a `<details><summary>Manual install (alternative)</summary>` collapsible block
- Add reference to `INSTALL_MANIFEST.md` for file details

### C4: Developer Guide Update

Modify `docs/guides/DEVELOPER_GUIDE_TACHI.md` Step 2 install section:
- Replace manual copy commands with `install.sh` invocation (matching README)
- Preserve manual install as alternative reference

### C5: Version Tagging

Create the first semantic version tag on the repository:
- Tag: `v4.0.0` (annotated tag with message)
- Applied to the merge commit on main after this feature's PR is merged
- Enables `git describe --tags` to report meaningful versions

## Data Flow

```
User runs install.sh from target project root
  │
  ├─ 1. Script auto-detects SOURCE_DIR from BASH_SOURCE
  │     (or uses --source override)
  │
  ├─ 2. If --version: check dirty tree → record branch → trap EXIT → checkout tag
  │
  ├─ 3. Read INSTALL_MANIFEST.md from SOURCE_DIR
  │     └─ Extract paths between <!-- BEGIN MANIFEST --> and <!-- END MANIFEST -->
  │
  ├─ 4. For each manifest path:
  │     ├─ mkdir -p (target parent directory)
  │     └─ cp -r (source → target)
  │
  ├─ 5. Report: version, file count, source path
  │
  └─ 6. If --version: trap restores original branch (automatic on EXIT)
```

## Tech Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| Script | Bash 3.2+ | macOS default, matches existing tachi scripts |
| File copy | `cp -r`, `mkdir -p` | Standard coreutils, no external deps |
| Version detection | `git describe --tags --always` | Provides version string from nearest tag |
| Dirty tree check | `git status --porcelain` | Machine-parseable, catches all change types |
| Branch restore | `trap cleanup EXIT` | Guaranteed execution on all exit paths |
| Manifest parsing | `sed`/`awk` between HTML comment markers | No external parser needed, Bash 3.2 compatible |
| Static analysis | shellcheck (if available) | Catches common Bash pitfalls |

## Implementation Phases

### Phase A: Foundation (install.sh core + manifest update)

1. Add machine-parseable section to `INSTALL_MANIFEST.md` with `<!-- BEGIN MANIFEST -->` / `<!-- END MANIFEST -->` markers
2. Create `scripts/install.sh` with:
   - Argument parsing (`--source`, `--version`, `--help`)
   - Source auto-detection from script location
   - Manifest parsing (extract paths from marker-delimited section)
   - File copy loop with `mkdir -p` + `cp -r`
   - Summary output (version, file count, source)
3. Test: run from an empty target directory, verify all manifest files copied

### Phase B: Version checkout support

1. Add dirty tree detection (`git status --porcelain`)
2. Add trap handler for branch restoration on EXIT
3. Add tag validation with available-tags listing on failure
4. Add `git checkout <tag>` with quiet output
5. Test: create a test tag, run with `--version`, verify correct files and branch restoration

### Phase C: Documentation updates

1. Update README.md Step 2 — scripted install primary, manual in `<details>` block
2. Update Developer Guide install section to match
3. Verify `INSTALL_MANIFEST.md` maintenance checklist still accurate

### Phase D: Version tagging

1. After PR merge to main, create annotated tag `v4.0.0` with message
2. Verify `git describe --tags` returns expected version string
3. Run `install.sh --version v4.0.0` end-to-end to validate

## Security Considerations

- **Source repo safety**: Dirty tree check prevents data loss from unintended checkout; trap handler guarantees branch restoration
- **No network access**: Script operates entirely on local filesystem — no downloads, no remote fetches
- **No elevated privileges**: Script requires only read access to source and write access to target; no `sudo`, no system-level changes
- **Additive only**: Script never deletes files in the target project — no risk of data loss from stale manifest entries

## Testing Strategy

| Test | Scope | Method |
|------|-------|--------|
| Fresh install | Core | Run from empty dir, verify all manifest files present |
| Re-install (idempotent) | Core | Run twice, verify identical result, zero errors |
| Missing source dir | Error handling | Run with invalid `--source`, verify error message |
| Missing manifest | Error handling | Remove manifest, verify error message |
| Invalid version tag | Error handling | Run with non-existent tag, verify available tags listed |
| Dirty tree refusal | Safety | Stage a change in source, run with `--version`, verify refusal |
| Branch restoration | Safety | Run with `--version`, verify original branch restored |
| Interrupt restoration | Safety | Ctrl+C during copy with `--version`, verify branch restored |
| Auto-detect source | Path detection | Run script from its installed location, verify correct source |
| Explicit source override | Path detection | Run with `--source /alt/path`, verify files from that path |
| Bash 3.2 compat | Portability | Run on macOS system bash, verify no syntax errors |
| Shellcheck clean | Static analysis | Run shellcheck on install.sh, verify zero warnings |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Manifest format changes break parsing | Low | Medium | HTML comment markers are stable; script validates marker presence |
| Version checkout leaves detached HEAD | Low | Medium | Trap handler on EXIT guarantees restoration |
| Partial copy on disk full | Low | Low | Script reports which files succeeded/failed; re-run after clearing space |
| Bash 3.2 incompatibility | Low | High | Avoid Bash 4+ features; test on macOS system bash explicitly |
