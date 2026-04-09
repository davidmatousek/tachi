---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-09
    status: APPROVED
    notes: "All 17 requirements covered, 5 user stories addressed, zero scope creep. Wave sequencing logically sound."
  architect_signoff:
    agent: architect
    date: 2026-04-09
    status: APPROVED_WITH_CONCERNS
    notes: "Technical approach sound. M-1 (bare filename pattern corruption) addressed by tiered pattern strategy with path-qualified Tier 2 and manual Tier 3. M-2 (docs/ coverage) and M-3 (*.py glob) incorporated into plan."
  techlead_signoff: null
---

# Implementation Plan: Rename Tachi Commands to tachi.* Namespace

**Branch**: `121-rename-tachi-commands` | **Date**: 2026-04-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/121-rename-tachi-commands/spec.md`

## Summary

Rename all 5 tachi pipeline commands from unprefixed names to the `tachi.*` namespace, create the new `tachi.architecture` command, update ~2,207 cross-references across ~344 files, add deprecated-file cleanup to the install script, and update all documentation. This is a file-rename and content-update project — no application code is involved.

## Technical Context

**Language/Version**: Bash (install script), Markdown + YAML (all other files)
**Primary Dependencies**: None (file operations only)
**Storage**: Filesystem (markdown files, YAML schemas, Typst templates)
**Testing**: Grep-based verification (zero old names outside immutable artifacts)
**Target Platform**: Any OS with Claude Code (macOS, Linux, Windows via WSL)
**Project Type**: Methodology template (no source code)
**Performance Goals**: N/A (no runtime performance)
**Constraints**: Atomic delivery — all renames in a single PR, no partial state on `main`
**Scale/Scope**: 5 command file renames + 1 new command + 3 adapter renames + ~344 files cross-reference updates

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Namespace convention is domain-agnostic |
| III. Backward Compatibility | PASS | Pre-1.0 project; breaking change acceptable with migration docs |
| VII. Definition of Done | PASS | DoD will be verified via grep (SC-001) and install script test (SC-003/SC-004) |
| IX. Git Workflow | PASS | Feature branch `121-rename-tachi-commands`, atomic PR delivery |
| X. Product-Spec Alignment | PASS | PRD approved (all Triad sign-offs), spec PM-approved |

No constitution violations. Proceeding.

## Project Structure

### Documentation (this feature)

```
specs/121-rename-tachi-commands/
├── plan.md              # This file
├── research.md          # Completed during spec phase
├── data-model.md        # Rename mapping and file inventory
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (next step)
```

### Affected File Surfaces (repository root)

This feature modifies files across the existing repository structure. No new directories are created. The affected surfaces are:

```
.claude/commands/                    # 5 renames + 1 new file (FR-001, FR-002)
.claude/agents/tachi/                # ~21 files: cross-reference updates (FR-004)
.claude/skills/tachi-*/              # ~22 files: cross-reference updates (FR-004)
adapters/claude-code/commands/       # 3 renames (FR-003)
adapters/github-actions/             # 1 rename + README (FR-003)
adapters/copilot/                    # Cross-reference updates (FR-004)
adapters/cursor/                     # Cross-reference updates (FR-004)
templates/tachi/                     # ~15 files: CTA text + output schema refs (FR-011)
schemas/                             # ~8 files: cross-reference updates (FR-004)
scripts/install.sh                   # Deprecated-file cleanup (FR-006, FR-007, FR-008)
docs/guides/                         # ~5 consumer/developer guides (FR-009)
INSTALL_MANIFEST.md                  # Manifest update (FR-005)
CLAUDE.md                            # Root doc update (FR-010)
README.md                            # Root doc update (FR-010)
CHANGELOG.md                         # Migration entry (FR-010, FR-012)
```

**Structure Decision**: No new source code directories. This feature operates entirely within the existing repository layout, renaming files and updating content.

## Components

### Component 1: Command File Renames

**Purpose**: Rename the 5 primary command files and create 1 new command
**Files**: `.claude/commands/`

| Current File | New File | Action |
|-------------|----------|--------|
| `threat-model.md` | `tachi.threat-model.md` | Rename (git mv) |
| `risk-score.md` | `tachi.risk-score.md` | Rename (git mv) |
| `compensating-controls.md` | `tachi.compensating-controls.md` | Rename (git mv) |
| `infographic.md` | `tachi.infographic.md` | Rename (git mv) |
| `security-report.md` | `tachi.security-report.md` | Rename (git mv) |
| *(new)* | `tachi.architecture.md` | Create (Issue #120) |

**Approach**: Use `git mv` for renames to preserve git history. After renaming, update internal cross-references within each command file.

### Component 2: Adapter Renames

**Purpose**: Mirror primary renames in adapter directories
**Files**: `adapters/`

| Directory | Current File | New File |
|-----------|-------------|----------|
| `adapters/claude-code/commands/` | `threat-model.md` | `tachi.threat-model.md` |
| `adapters/claude-code/commands/` | `infographic.md` | `tachi.infographic.md` |
| `adapters/claude-code/commands/` | `risk-score.md` | `tachi.risk-score.md` |
| `adapters/github-actions/` | `tachi-threat-model.yml` | `tachi.threat-model.yml` |

### Component 3: Cross-Reference Updates

**Purpose**: Update all mentions of old command names to new names across the codebase
**Scope**: ~344 files, ~2,207 references

**Search-and-replace patterns** organized into two tiers:

**Tier 1: Slash command invocations** (safe — leading `/` is unambiguous):

| Pattern (old) | Replacement (new) | Context |
|---------------|-------------------|---------|
| `/compensating-controls` | `/tachi.compensating-controls` | Slash command invocations |
| `/security-report` | `/tachi.security-report` | Slash command invocations |
| `/threat-model` | `/tachi.threat-model` | Slash command invocations |
| `/risk-score` | `/tachi.risk-score` | Slash command invocations |
| `/infographic` | `/tachi.infographic` | Slash command invocations |

**Tier 2: Path-qualified file references** (must use directory context to avoid corrupting output artifact names):

Bare filenames like `compensating-controls.md` and `risk-scores.md` are ambiguous — they name both command files AND pipeline output artifacts. Tier 2 patterns MUST be path-qualified:

| Pattern (old) | Replacement (new) | Context |
|---------------|-------------------|---------|
| `commands/compensating-controls.md` | `commands/tachi.compensating-controls.md` | Path-qualified command file refs |
| `commands/security-report.md` | `commands/tachi.security-report.md` | Path-qualified command file refs |
| `commands/threat-model.md` | `commands/tachi.threat-model.md` | Path-qualified command file refs |
| `commands/risk-score.md` | `commands/tachi.risk-score.md` | Path-qualified command file refs |
| `commands/infographic.md` | `commands/tachi.infographic.md` | Path-qualified command file refs |

**Tier 3: Manual review for edge cases**:

Some references use bare filenames in skill metadata, agent "Available tools" lists, or schema `command_ref` fields where the context is clearly a command name but lacks a directory prefix. These must be reviewed per-file to distinguish command references from output artifact references. Estimated ~20-30 manual-review instances.

**Exclusion rules** (files that MUST NOT be modified):
- `docs/product/02_PRD/*.md` (historical PRDs — immutable)
- `docs/architecture/02_ADRs/*.md` (architectural decision records — immutable unless explicitly superseded)
- `specs/*/` except `specs/121-rename-tachi-commands/` (archived specs — immutable)
- Historical CHANGELOG entries (only add new migration entry)
- Files containing the string only in git-ignored output (e.g., `_Output/`)
- Pipeline output artifact names (`threats.md`, `risk-scores.md`, `compensating-controls.md` as output files) — these are NOT command files and must NOT be renamed

**Python file coverage**: `scripts/*.py` files contain slash-command strings in user-facing error messages and CTA text. These are covered by Tier 1 patterns (slash-prefixed). Include `*.py` in the search glob alongside `*.md` and `*.yml`.

**Approach**: Prototype-first — rename one command (`threat-model` → `tachi.threat-model`), grep-verify, then scale to remaining 4 commands. This follows PAT-018 (prototype-first gate) from institutional knowledge.

### Component 4: Install Script Cleanup

**Purpose**: Add deprecated-file cleanup to `scripts/install.sh` so upgrades remove old command files
**File**: `scripts/install.sh`

**Design**: Insert a cleanup section between the version checkout block (line 126) and the manifest parsing block (line 130). The cleanup section:
1. Defines a list of deprecated file paths (relative to target directory)
2. Iterates the list, running `rm -f` on each file in the target directory
3. Logs each successful removal
4. Runs silently when files don't exist (fresh install)

**Deprecated files list**:
```
.claude/commands/threat-model.md
.claude/commands/risk-score.md
.claude/commands/compensating-controls.md
.claude/commands/infographic.md
.claude/commands/security-report.md
```

### Component 5: Manifest Update

**Purpose**: Update INSTALL_MANIFEST.md with new filenames
**File**: `INSTALL_MANIFEST.md`

**Changes**:
1. Update human-readable "Command Files" table (lines 21-29) with new names
2. Update machine-parseable section (lines 72-84) with new filenames
3. Add `tachi.architecture.md` to both sections
4. Update file count references (5 → 6 command files)

### Component 6: Documentation Updates

**Purpose**: Update all consumer-facing and developer-facing documentation
**Files**: Guides, root docs, CHANGELOG

**Affected files**:
- `docs/guides/DEVELOPER_GUIDE_TACHI.md` — primary developer walkthrough
- `docs/guides/CONSUMER_GUIDE_TACHI.md` — consumer pipeline guide
- `docs/guides/CONSUMER_GUIDE_TACHI_AOD_INTEGRATION.md` — AOD integration guide
- `docs/guides/CONSUMER_GUIDE_TACHI_RESEARCH.md` — research guide
- `docs/guides/prompts/developer-guide-prompt.md` — guide generation prompt
- `CLAUDE.md` — project-level command reference
- `README.md` — public-facing documentation
- `CHANGELOG.md` — new migration entry (not modifying historical entries)

### Component 7: tachi.architecture Command (Issue #120)

**Purpose**: Create the new architecture description generation command with `tachi.*` namespace from inception
**File**: `.claude/commands/tachi.architecture.md`

**Approach**: Create as a stub or bounded implementation per Issue #120 scope. The command will generate architecture description input for the tachi threat modeling pipeline. Content will be defined by Issue #120 requirements.

## Data Flow

```
User invokes /tachi.threat-model
  → Claude Code resolves tachi.threat-model.md in .claude/commands/
  → Command orchestrates threat analysis agents from .claude/agents/tachi/
  → Agents read schemas from schemas/
  → Output: threats.md

User invokes /tachi.risk-score
  → Reads threats.md as input
  → Output: risk-scores.md

User invokes /tachi.compensating-controls
  → Reads risk-scores.md as input
  → Output: compensating-controls.md

User invokes /tachi.infographic
  → Reads threats.md / risk-scores.md / compensating-controls.md
  → Templates from templates/tachi/infographics/
  → Output: infographic images

User invokes /tachi.security-report
  → Reads all pipeline artifacts
  → Templates from templates/tachi/security-report/
  → Output: PDF security report

User invokes /tachi.architecture
  → Generates architecture description for pipeline input
  → Output: architecture.md (input for /tachi.threat-model)
```

The data flow is unchanged — only the command invocation names change from unprefixed to `tachi.*` prefixed.

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Command definitions | Markdown (`.md`) | Slash command behavior |
| Agent definitions | Markdown (`.md`) | AI agent instructions |
| Schemas | YAML (`.yaml`) | Input/output contracts |
| Templates | Typst (`.typ`) + Markdown | PDF report + output format |
| Install script | Bash | File distribution to consumer projects |
| Manifest | Markdown with HTML comments | Machine-parseable file list |

## Implementation Strategy

### Prototype-First Approach (from PAT-018)

1. **Prototype**: Rename `threat-model` → `tachi.threat-model` (command + adapter + all cross-refs)
2. **Verify**: Run grep for old name, confirm zero matches outside immutables
3. **Scale**: Apply same pattern to remaining 4 commands
4. **Verify all**: Full codebase grep for all 5 old names

### Execution Order

**Wave 1** (Foundation — must complete first):
- Rename all 5 command files via `git mv`
- Rename 3 adapter command copies + 1 GitHub Actions workflow
- Create `tachi.architecture.md` stub
- Update internal cross-references within renamed command files

**Wave 2** (Cross-references — parallelizable by surface):
- Update agents (`.claude/agents/tachi/`)
- Update skills (`.claude/skills/tachi-*/`)
- Update templates (`templates/tachi/`)
- Update schemas (`schemas/`)
- Update scripts (`scripts/`)
- Update adapter docs/configs

**Wave 3** (Infrastructure + Documentation):
- Update `INSTALL_MANIFEST.md`
- Add deprecated-file cleanup to `scripts/install.sh`
- Update guides (`docs/guides/`)
- Update root files (`CLAUDE.md`, `README.md`, `CHANGELOG.md`)

**Wave 4** (Verification):
- Grep verification: zero old names outside immutables
- Install script test: fresh install delivers correct files
- Example validation: all 6 examples reference new names

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Missed cross-references | Medium | Medium | Grep verification as final step (SC-001); prototype-first approach catches pattern issues early |
| Partial rename on main | Low | High | Atomic PR delivery (FR-016); all renames in single PR |
| CTA text in generated output | Certain | Low | Explicitly include skill CTA text in cross-reference sweep (FR-011) |
| Duplicate commands after upgrade | Certain | High | Deprecated-file cleanup in install.sh (FR-006) |
| Dot-separated names not resolving | Low | High | Already confirmed working by `aod.*` pattern; test first rename before bulk |

## Complexity Tracking

No constitution violations found. No complexity justifications needed.
