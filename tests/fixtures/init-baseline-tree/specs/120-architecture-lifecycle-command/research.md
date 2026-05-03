# Research Summary: Architecture Lifecycle Command (Feature 120)

## Knowledge Base Findings

- **PAT-014** (Feature 067): YAML frontmatter must be parsed with script-based deterministic extraction (regex, stdlib), never LLM parsing. `tachi_parsers.py` is the single extraction point — add new field parsing there first.
- **PAT-017** (Feature 074): When modifying YAML schemas with corresponding output templates, **template parity validation** must be an explicit checkpoint task. Two critical parity issues found in Feature 074 at final validation.
- **KB-023** (Feature 104): Centralized parser module (`tachi_parsers.py`) enables same-day cross-cutting propagation. Backward compatibility via presence checks (fields included only when data exists).
- No bug fix entries exist in the KB yet.

**Key Lessons**:
1. Script-based YAML frontmatter parsing only — no LLM extraction for structured fields
2. Add new frontmatter fields to `tachi_parsers.py` first; downstream scripts consume via shared API
3. Explicit template parity checkpoint after every schema change
4. Backward compatibility via presence checks, not schema versioning flags

## Codebase Analysis

### Current `/tachi.architecture` Command
- **File**: `.claude/commands/tachi.architecture.md`
- 4-step command: Determine Scope → Analyze Architecture → Generate Description → Report
- No YAML frontmatter, no versioning, no archive logic, no checksum
- Output: plain markdown with overview, Mermaid diagram, components table, data flows, trust boundaries, external entities
- Default output: `docs/security/architecture.md`

### Current `/tachi.threat-model` Command
- **File**: `.claude/commands/tachi.threat-model.md`
- **Step 1.3**: Creates timestamped output directory (e.g., `docs/security/2026-04-09T14-30-22/`)
- **Step 2**: Reads architecture file, invokes `tachi-orchestrator` agent with content in `<architecture-input>` tags
- **Snapshot insertion point**: Between Step 1.3 (output dir creation) and Step 2 (orchestrator invocation)

### Orchestrator Agent
- Receives architecture via `<architecture-input>` boundary tag (data, not instructions)
- Parses file content — frontmatter is transparent/ignored during format detection
- No changes needed to the orchestrator itself

### Frontmatter Patterns
- `threats.md` uses standard `--- ... ---` YAML delimiters with: `schema_version`, `date`, `input_format`, `classification`, `run_id`, `baseline` (nested)
- `tachi_parsers.py` handles both code-fenced and standard frontmatter via `_extract_frontmatter_text()`
- Nested blocks require separate parser functions (e.g., `parse_baseline_frontmatter()`)

### Example Architecture Files
- All three examples (`agentic-app`, `microservices`, `web-app`) have **no frontmatter** — plain markdown
- PRD explicitly states examples remain unchanged (Out of Scope)

### Utilities to Reuse
- `tachi_parsers.py` — centralized parsing, `_extract_frontmatter_text()` for frontmatter extraction
- `shasum -a 256` — macOS/Linux SHA-256 tool (explicit shell invocation needed in command file)

## Architecture Constraints

- ADRs are the vehicle for significant technical decisions
- `.archive/vN/` follows existing dot-prefix hidden-directory convention
- Archive path must be relative to architecture file's parent directory, not hardcoded
- Timestamped output folders already exist for baseline detection — snapshot `architecture.md` won't conflict (baseline scans for `threats.md`)
- Baseline `run_id` format: `YYYY-MM-DDTHH-MM-SS`; frontmatter `date` uses `YYYY-MM-DD` — no collision
- Feature 120 adds no new fields to `schemas/finding.yaml` — downstream stages unaffected
- Snapshot copy is a file-system concern at the command layer, invisible to the orchestrator agent

### Files Directly Touched
1. `.claude/commands/tachi.architecture.md` — add frontmatter generation, archive mechanism, guided update mode
2. `.claude/commands/tachi.threat-model.md` — insert snapshot step between Step 1.3 and Step 2

## Industry Research

### Architecture Description Versioning
- Dominant approach: treat docs like code with Git versioning + self-describing `version:` frontmatter field
- C4 Model / arc42 community favors Git-native history over folder-copy archives
- For files needing self-describing versions (parseable without Git), frontmatter `version:` is the standard pattern

### YAML Frontmatter Best Practices
- Common fields: `schema_version`, `version`, `title`, `created_at`, `updated_at`
- Two-field pattern recommended: `schema_version` (format compatibility) + `version` (content currency)
- `attributes:` as free-form key-value block for extensibility

### Security Assessment Traceability
- OWASP and Security Compass emphasize threat models must be refreshed on every major architecture change
- OTM and Threagile pattern: embed `architecture_ref` in threat model pointing to assessed version
- Architecture-change-triggered refresh preferred over calendar-only schedules

### Anti-Patterns
- Folder-copy archives without Git lose diff history
- Storing version only in filenames breaks machine parsing
- Single monolithic `version:` field — separate schema version from content version
- Calendar-only threat model refresh — architecture-change-triggered is required

## Recommendations for Spec

- Follow the PRD's frontmatter schema exactly (`version`, `date`, `description`, `checksum`, `previous_version`) — aligns with industry best practices
- Use `tachi_parsers.py` as the single parsing point for architecture frontmatter (add new parser function)
- Archive mechanism (`.archive/vN/`) is acceptable for MVP; Git history provides diff capability
- Snapshot step placement is clear: between Step 1.3 and Step 2 in `/tachi.threat-model`
- Guided update mode (P1) should be specified but clearly delineated from P0 requirements
- Validate against all 3 example architectures (no frontmatter) to confirm backward compatibility
- No schema changes to existing output formats — downstream pipeline unaffected
- Explicit checksum computation step using `shasum -a 256` (not abstract "computed")
