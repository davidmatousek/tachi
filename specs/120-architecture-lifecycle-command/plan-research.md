# Phase 0 Research: Architecture Lifecycle Command

## Technical Decisions

### Decision 1: Frontmatter Format
- **Decision**: Standard YAML frontmatter with `---` delimiters (same as threats.md, spec.md, etc.)
- **Rationale**: Consistent with existing tachi output formats. `tachi_parsers.py` already handles `---` delimited frontmatter via `_extract_frontmatter_text()`.
- **Alternatives considered**: Code-fenced YAML (```yaml --- ... --- ```), JSON frontmatter, separate metadata file. Rejected: non-standard, inconsistent with existing patterns.

### Decision 2: Checksum Tool Invocation
- **Decision**: Use `shasum -a 256` with explicit Bash tool invocation in the command file. Document body extracted by stripping frontmatter first.
- **Rationale**: Team-Lead review flagged that checksum must use explicit tool invocation, not abstract "computed" language. `shasum -a 256` is available on macOS and most Linux distributions.
- **Alternatives considered**: `sha256sum` (Linux-only), Python hashlib (requires Python dependency). Accepted: `shasum -a 256` as primary, document `sha256sum` as Linux alternative.

### Decision 3: Archive Path Derivation
- **Decision**: Derive archive path relative to the architecture file's parent directory: `{dirname}/.archive/v{N}/{filename}`.
- **Rationale**: Team-Lead review flagged that paths must be relative to file parent dir, not hardcoded to `docs/security/`. Supports custom architecture file locations.
- **Alternatives considered**: Hardcoded `docs/security/.archive/` path, centralized archive directory. Rejected: breaks with custom output paths.

### Decision 4: Snapshot Integration Point
- **Decision**: Insert snapshot step between Step 1.3 (output directory creation) and Step 2 (orchestrator invocation) in `/tachi.threat-model`.
- **Rationale**: Architect review specified this exact placement. The timestamped folder must exist before the copy, and the snapshot must be in place before the orchestrator runs.
- **Alternatives considered**: After orchestrator completes, as a post-processing step. Rejected: if orchestrator fails, snapshot would be missing.

### Decision 5: Legacy File Handling
- **Decision**: Files without frontmatter are treated as v0. First managed update archives the legacy file as v0 and produces v1.
- **Rationale**: Consistent with PRD FR-1. Provides a clean migration path without breaking existing files.
- **Alternatives considered**: Skip archiving legacy files, treat as v1. Rejected: loses the pre-versioning content.

## Integration Analysis

### Files Modified (2 files total)
1. `.claude/commands/tachi.architecture.md` — Major rewrite: add frontmatter generation, archive mechanism, version detection, guided update mode
2. `.claude/commands/tachi.threat-model.md` — Minor addition: insert snapshot step (4-5 lines) between Step 1.3 and Step 2

### Files NOT Modified
- `.claude/agents/tachi/orchestrator.md` — Receives architecture via `<architecture-input>` tags; frontmatter is transparent
- `scripts/tachi_parsers.py` — No new parser needed for MVP (architecture frontmatter is produced, not consumed by downstream stages)
- `schemas/finding.yaml` — No schema changes
- `examples/*/architecture.md` — Remain unchanged per PRD Out of Scope
- All downstream pipeline stages — Unaffected (consume threats.md, not architecture.md)

### Validation Requirements
- Test frontmatter generation on first-time generation (new file)
- Test version increment on existing file with frontmatter
- Test legacy file handling (existing file without frontmatter → archive as v0)
- Test snapshot in threat model output folder
- Validate all 3 example architectures still work as input (no frontmatter)
