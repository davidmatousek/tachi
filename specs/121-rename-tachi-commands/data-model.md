# Data Model: Rename Tachi Commands to tachi.* Namespace

## Entity: Command File Rename Mapping

The core data model for this feature is the rename mapping — a 1:1 relationship between old and new filenames.

### Primary Commands (`.claude/commands/`)

| Old Filename | New Filename | Old Invocation | New Invocation |
|-------------|-------------|----------------|----------------|
| `threat-model.md` | `tachi.threat-model.md` | `/threat-model` | `/tachi.threat-model` |
| `risk-score.md` | `tachi.risk-score.md` | `/risk-score` | `/tachi.risk-score` |
| `compensating-controls.md` | `tachi.compensating-controls.md` | `/compensating-controls` | `/tachi.compensating-controls` |
| `infographic.md` | `tachi.infographic.md` | `/infographic` | `/tachi.infographic` |
| `security-report.md` | `tachi.security-report.md` | `/security-report` | `/tachi.security-report` |
| *(new)* | `tachi.architecture.md` | *(new)* | `/tachi.architecture` |

### Adapter Commands

| Directory | Old Filename | New Filename |
|-----------|-------------|-------------|
| `adapters/claude-code/commands/` | `threat-model.md` | `tachi.threat-model.md` |
| `adapters/claude-code/commands/` | `infographic.md` | `tachi.infographic.md` |
| `adapters/claude-code/commands/` | `risk-score.md` | `tachi.risk-score.md` |
| `adapters/github-actions/` | `tachi-threat-model.yml` | `tachi.threat-model.yml` |

### Deprecated Files (removed from consumer projects on upgrade)

| Deprecated Path | Reason |
|----------------|--------|
| `.claude/commands/threat-model.md` | Replaced by `tachi.threat-model.md` |
| `.claude/commands/risk-score.md` | Replaced by `tachi.risk-score.md` |
| `.claude/commands/compensating-controls.md` | Replaced by `tachi.compensating-controls.md` |
| `.claude/commands/infographic.md` | Replaced by `tachi.infographic.md` |
| `.claude/commands/security-report.md` | Replaced by `tachi.security-report.md` |

## Entity: Cross-Reference Pattern

Each cross-reference has a search pattern, replacement, and set of exclusion rules.

### Search-Replace Patterns (tiered by safety)

**Tier 1: Slash command invocations** (safe — unambiguous `/` prefix):

| Priority | Search Pattern | Replace Pattern | File Pattern |
|----------|---------------|-----------------|-------------|
| 1 | `/compensating-controls` | `/tachi.compensating-controls` | `*.md`, `*.yml`, `*.py` |
| 2 | `/security-report` | `/tachi.security-report` | `*.md`, `*.yml`, `*.py` |
| 3 | `/threat-model` | `/tachi.threat-model` | `*.md`, `*.yml`, `*.py` |
| 4 | `/risk-score` | `/tachi.risk-score` | `*.md`, `*.yml`, `*.py` |
| 5 | `/infographic` | `/tachi.infographic` | `*.md`, `*.yml`, `*.py` |

**Tier 2: Path-qualified file references** (safe — directory prefix disambiguates from output artifacts):

| Priority | Search Pattern | Replace Pattern | File Pattern |
|----------|---------------|-----------------|-------------|
| 6 | `commands/compensating-controls.md` | `commands/tachi.compensating-controls.md` | `*.md`, `*.yml` |
| 7 | `commands/security-report.md` | `commands/tachi.security-report.md` | `*.md`, `*.yml` |
| 8 | `commands/threat-model.md` | `commands/tachi.threat-model.md` | `*.md`, `*.yml` |
| 9 | `commands/risk-score.md` | `commands/tachi.risk-score.md` | `*.md`, `*.yml` |
| 10 | `commands/infographic.md` | `commands/tachi.infographic.md` | `*.md`, `*.yml` |

**Tier 3: Manual review** (~20-30 instances where bare filenames appear in non-path context and must be individually assessed to avoid corrupting output artifact references).

### Exclusion Rules

| Exclusion | Reason |
|-----------|--------|
| `docs/product/02_PRD/*.md` | Immutable historical PRDs (FR-013) |
| `specs/*/` except `specs/121-rename-tachi-commands/` | Immutable archived specs (FR-014) |
| CHANGELOG entries before migration note | Immutable historical entries (FR-015) |

## Entity: Install Manifest Entry

Each manifest entry is a single line in the machine-parseable section of `INSTALL_MANIFEST.md`.

### Updated Manifest Entries

```
.claude/commands/tachi.threat-model.md
.claude/commands/tachi.risk-score.md
.claude/commands/tachi.compensating-controls.md
.claude/commands/tachi.infographic.md
.claude/commands/tachi.security-report.md
.claude/commands/tachi.architecture.md
```
