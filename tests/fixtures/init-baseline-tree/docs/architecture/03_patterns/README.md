# Design Patterns - tachi

**Last Updated**: 2026-05-01
**Owner**: Architect

---

## Overview

This directory documents reusable design patterns for tachi.

---

## Pattern Categories

### API Patterns
- Request/response patterns
- Error handling
- Authentication/authorization
- Rate limiting
- Pagination

### Database Patterns
- Query optimization
- Indexing strategies
- Migration patterns
- Concurrency control
- Caching strategies

### Frontend Patterns
- Component composition
- State management
- Data fetching
- Error boundaries
- Performance optimization

### Testing Patterns
- Unit test structure
- Integration test patterns
- E2E test patterns
- Mocking strategies

### Shell Script Patterns (AOD Kit)
- [Atomic File Write (Write-Then-Rename)](#pattern-atomic-file-write)
- [Function Library Sourcing](#pattern-function-library-sourcing)
- [Graceful CLI Degradation](#pattern-graceful-cli-degradation)
- [Additive Optional State Fields](#pattern-additive-optional-state-fields)
- [Append-Only Logging with Graceful Failure](#pattern-append-only-logging)
- [Circuit-Breaker Churn Detection](#pattern-circuit-breaker-churn-detection)
- [Subshell Isolation for Strict Shell Options](#pattern-subshell-isolation-for-strict-shell-options)

### Template Patterns (AOD Kit)
- [Template Variable Expansion](#pattern-template-variable-expansion)
- [Hub-First Typst Template Modularity](#pattern-hub-first-typst-template-modularity)

### Skill Patterns (AOD Kit)
- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation)
- [Compound State Helpers](#pattern-compound-state-helpers)
- [Governance Result Caching](#pattern-governance-result-caching)
- [Read-Only Dry-Run Preview](#pattern-read-only-dry-run-preview)
- [Dual-Surface Injection](#pattern-dual-surface-injection)
- [Minimal-Return Subagent](#pattern-minimal-return-subagent)
- [Governed Skill Phase Loop](#pattern-governed-skill-phase-loop)

### Command Patterns (AOD Kit)
- [Orchestrator-Awareness Guard](#pattern-orchestrator-awareness-guard)
- [Non-Fatal Observability Wrapper](#pattern-non-fatal-observability-wrapper)
- [Built-in Skill Invocation from a Command](#pattern-built-in-skill-invocation-from-a-command)

### Python Script Patterns (AOD Kit)
- [Shared Parser Module Extraction](#pattern-shared-parser-module-extraction)
- [Largest Remainder Method for Deterministic Percentages](#pattern-largest-remainder-method)

### Threat Modeling Patterns (AOD Kit)
- [STRIDE-per-Element Matrix Targeting](#pattern-stride-per-element-matrix-targeting)
- [Cross-Agent Correlation Detection](#pattern-cross-agent-correlation-detection)
- [Heuristic A Enrichment Branch with 11-Host Saturation](#pattern-heuristic-a-enrichment-branch)

### Stack Pack Architecture Patterns (AOD Kit)
- [Two-Level Architecture (Build-Time / Run-Time)](#pattern-two-level-architecture)
- [Convention Contract (STACK.md)](#pattern-convention-contract)

---

## Documented Patterns

### Pattern: Atomic File Write

**Added**: Feature 022 (Full Lifecycle Orchestrator)
**ADR**: [ADR-001](../02_ADRs/ADR-001-atomic-state-persistence.md)

#### Problem
Writing JSON state to disk risks corruption if the process crashes mid-write. Readers may see partial JSON, breaking the orchestrator's ability to resume.

#### Solution
Write to a temporary file first, then atomically rename it to the target path. On POSIX systems, `mv` within the same filesystem is atomic.

#### Example
```bash
# From .aod/scripts/bash/run-state.sh
AOD_STATE_FILE=".aod/run-state.json"
AOD_STATE_TMP=".aod/run-state.json.tmp"

aod_state_write() {
    local json="$1"
    # Validate JSON before writing
    echo "$json" | jq . > "$AOD_STATE_TMP" || { rm -f "$AOD_STATE_TMP"; return 1; }
    # Atomic rename
    mv "$AOD_STATE_TMP" "$AOD_STATE_FILE"
}
```

#### When to Use
- Writing state/config files that must survive crashes
- Any file where partial writes would corrupt consumers
- Single-writer scenarios (no concurrent access needed)

#### When NOT to Use
- Multi-writer concurrent scenarios (use file locking or a database)
- Append-only logs (just append, no need for atomicity on the whole file)

---

### Pattern: Function Library Sourcing

**Added**: Pre-Feature 022, documented during Feature 022

#### Problem
Bash scripts that define functions are invoked as standalone executables (`bash script.sh arg`), but the functions are never called -- only defined.

#### Solution
Source the library file before calling its functions. Use `bash -c 'source lib.sh && function_name args'`.

#### Example
```bash
# CORRECT: source then call
bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_read'
bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_update_stage 22 plan'

# WRONG: functions defined but never called
bash .aod/scripts/bash/run-state.sh aod_state_read
```

**Exception**: `backlog-regenerate.sh` is a standalone script (not a function library):
```bash
bash .aod/scripts/bash/backlog-regenerate.sh
```

#### When to Use
- All `.aod/scripts/bash/*.sh` function libraries
- Any Bash file that exports functions rather than running a main block

#### When NOT to Use
- Standalone scripts with a `main` block or top-level logic

---

### Pattern: Graceful CLI Degradation

**Added**: Feature 022 (Full Lifecycle Orchestrator)

#### Problem
The orchestrator depends on `gh` CLI for GitHub Issue label management, but `gh` may not be installed, authenticated, or the network may be unavailable. Hard-failing would block the entire lifecycle.

#### Solution
Check CLI availability before use, and fall back to artifact-only detection when the CLI is unavailable. Non-critical operations (label updates, backlog refresh) are fire-and-forget.

#### Example
```bash
# Check availability, skip silently if missing
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    gh issue view "$NNN" --json labels
else
    echo "GitHub CLI unavailable. Falling back to artifact-only detection."
    # Infer stage from on-disk artifacts instead
fi

# Fire-and-forget for non-critical operations
bash .aod/scripts/bash/backlog-regenerate.sh 2>/dev/null || true
```

#### When to Use
- External CLI tools that may not be installed (gh, jq, docker)
- Network-dependent operations where offline mode should still work
- Non-critical side effects (label updates, notifications)

#### When NOT to Use
- Core dependencies that the feature cannot function without (e.g., `jq` for JSON state)

---

### Pattern: Additive Optional State Fields

**Added**: Feature 030 (Context Efficiency of /aod.run)

#### Problem
New features need to extend the orchestrator state file (`run-state.json`) with additional data objects (e.g., `governance_cache` in Feature 030). However, existing state files created by earlier features do not contain these new fields. Requiring a schema migration or version bump would break backward compatibility and force users to recreate state files.

#### Solution
Every function that reads a new state field checks whether that field exists before accessing it. If the field is absent, the function returns a safe default value and exits cleanly (return 0). Functions that write to a new field first check for the parent object's existence and skip the write if it is absent. This makes the new state object purely opt-in: it is created only when a new orchestration is initialized with the feature enabled.

The key rules:
1. **Read functions**: Check for field existence; return a default if absent
2. **Write functions**: Check for parent object existence; return 0 (success) if absent
3. **Initialization**: New state object is included in the initial state template for new runs
4. **No migration**: Existing state files from prior features continue to work without modification

#### Example
```bash
# From .aod/scripts/bash/run-state.sh

aod_state_update_optional_field() {
    # ... (args: field_name, value)
    local state
    state=$(aod_state_read) || return 1

    # Check if the optional field exists; skip gracefully if absent (backward compat)
    local has_field
    has_field=$(echo "$state" | jq -r "if .$field_name then \"yes\" else \"no\" end")
    if [[ "$has_field" != "yes" ]]; then
        return 0  # Pre-feature state file — no field present, no error
    fi

    # Proceed with update only if the field exists
    state=$(echo "$state" | jq --arg val "$value" \
        ".$field_name = \$val")
    aod_state_write "$state"
}

aod_state_get_governance_cache() {
    # Returns defaults when governance_cache is absent
    echo "$state" | jq -r '
        if .governance_cache then
            .governance_cache
        else
            null
        end'
}
```

#### When to Use
- Adding new top-level objects to a shared JSON state file across feature releases
- Any schema extension where existing consumers must not break
- When a feature is opt-in and should not require manual state file migration
- State files managed by multiple features at different version levels

#### When NOT to Use
- Breaking changes where the old schema is fundamentally incompatible (use schema version bump)
- Fields that are required for core functionality (missing field = hard failure is correct behavior)
- When the number of optional fields grows large enough to warrant a formal migration system

#### Related Patterns
- [Atomic File Write](#pattern-atomic-file-write) -- all state writes (including optional field updates) use write-then-rename
- [Compound State Helpers](#pattern-compound-state-helpers) -- state summary helpers follow the same pipe-delimited extraction approach
- [Governance Result Caching](#pattern-governance-result-caching) -- `governance_cache` was the first use of this pattern (Feature 030)

---

### Pattern: On-Demand Reference File Segmentation

**Added**: Feature 030 (Context Efficiency of /aod.run), extended to agent prompts in Feature 029 (Agent Refactoring -- Right-Size), extended to agent-to-skill domain extraction in Feature 075 (Tachi Agent Best Practices), extended to shared cross-agent definitions and full-pipeline agent restructuring in Feature 078 (Agent Context Optimization), extended to the detection-tier lean refactor (11 threat agents) via the **detection variant** in Feature 082 (Threat Agent Skill References)
**ADR**: [ADR-002](../02_ADRs/ADR-002-prompt-segmentation.md), extended by [ADR-023](../02_ADRs/ADR-023-threat-agent-skill-references-pattern.md) — introduces the detection variant as a sibling to the methodology variant, completing the lean-agent architecture migration for all 17 tachi agents

#### Problem
A monolithic skill or agent prompt file loads its entire content into the agent's context window at invocation, even when large sections are only needed conditionally (e.g., governance rules at stage boundaries, error recovery on failure, SARIF generation templates, attack tree formatting). This wastes context tokens that could be used for implementation work.

#### Solution
Split the monolithic file into a compact core containing the always-needed execution logic, plus co-located reference files loaded via the Read tool only when their content is needed. Each branch point in the core file includes a Read instruction that loads the relevant reference file before proceeding.

A Reference Documents table in the core file maps every conditionally-needed section to its reference file path and loading trigger, making the structure discoverable.

#### Example 1: Skill-Level Segmentation (Feature 030)
```
# Directory structure
.claude/skills/~aod-run/
  SKILL.md                     # Core loop (~405 lines, always loaded)
  references/
    governance.md              # Loaded at governance gates
    entry-modes.md             # Loaded once per entry mode
    dry-run.md                 # Loaded only with --dry-run
    error-recovery.md          # Loaded on error/completion

# In SKILL.md — branch point with MANDATORY Read instruction
**MANDATORY**: You MUST use the Read tool to load `references/governance.md`
before proceeding with governance gate detection. Do NOT rely on memory of
prior governance content. If the file cannot be read, display an error and STOP.
```

#### Example 2: Agent-Level Reference Extraction (Feature 029)
```
# Directory structure — agent prompts with co-located references
adapters/claude-code/agents/
  orchestrator.md              # Core prompt (1,273 lines, down from 2,085)
  threat-report.md             # Core prompt (472 lines, down from 801)
  threat-infographic.md        # Core prompt (414 lines, down from 592)
  references/
    sarif-generation.md        # Loaded at Phase 4 completion
    validation-checklist.md    # Loaded at pipeline end
    error-templates.md         # Loaded on error conditions
    report-templates.md        # Loaded during attack tree generation
    infographic-gemini-api.md  # Loaded during image generation
    infographic-error-handling.md  # Loaded on infographic errors

# In agent prompt — Reference Documents navigation table
## Reference Documents
| Reference | Path | Load When |
|-----------|------|-----------|
| SARIF Generation | adapters/claude-code/agents/references/sarif-generation.md | Phase 4 completion |
| Error Templates  | adapters/claude-code/agents/references/error-templates.md  | Error condition     |
```

**Key difference from skill-level**: Agent reference documents contain consultation-only content (templates, checklists, detailed procedures) that the agent needs at specific pipeline phases. The core prompt retains the agent's mission, dispatch logic, and structural rules. This yielded 30-41% line reductions across three agents with zero regression on 11 threat agents.

#### Example 3: Agent-to-Skill Domain Knowledge Extraction (Feature 075)
```
# Directory structure — domain knowledge extracted from agents into standalone skills
.claude/skills/tachi-orchestration/
  SKILL.md                       # Level 2: metadata + loading table (36 lines)
  references/
    dispatch-rules.md            # Loaded at Phase 2 (Determine Threats)
    output-schemas.md            # Loaded at Phase 1/3/4
    sarif-specification.md       # Loaded at Phase 4 SARIF generation

.claude/skills/tachi-risk-scoring/
  SKILL.md                       # Level 2: metadata + loading table (29 lines)
  references/
    cvss-vectors.md              # Loaded at CVSS 3.1 base scoring phase
    scoring-dimensions.md        # Loaded at exploitability/scalability/reachability phases
    severity-bands.md            # Loaded at composite calculation phase

.claude/skills/tachi-control-analysis/
  SKILL.md                       # Level 2: metadata + loading table (28 lines)
  references/
    control-categories.md        # Loaded at Phase 3 (Detect Controls)
    evidence-criteria.md         # Loaded at Phase 3-4 (Detect + Classify)
    residual-risk.md             # Loaded at Phase 5 (Recommend + Calculate)

# Agent loads skill reference at specific pipeline phase:
Read `.claude/skills/tachi-orchestration/references/sarif-specification.md`
when entering the SARIF generation step in Phase 4.
```

**Key difference from agent-level**: Domain knowledge lives in skill files rather than agent-adjacent reference files. The agent prompt retains workflow logic, structural rules, and phase sequencing. Domain data (schemas, scoring tables, detection patterns) moves to skills that can be independently versioned and discovered via the skills system. This yielded orchestrator reduction from 1,273 to 769 lines, with risk-scorer and control-analyzer both reduced to under 1,000 lines.

#### Example 4: Shared Cross-Agent Definitions and Full-Pipeline Restructuring (Feature 078)
```
# Directory structure — shared definitions consumed by multiple agents
.claude/skills/tachi-shared/
  SKILL.md                           # Level 2: metadata + loading table
  references/
    severity-bands-shared.md         # Loaded by orchestrator, risk-scorer, control-analyzer
    stride-categories-shared.md      # Loaded by orchestrator, all 6 STRIDE agents
    finding-format-shared.md         # Loaded by all 17 agents

# New skill directories for report agents (Feature 078)
.claude/skills/tachi-report-assembly/
  SKILL.md
  references/
    brand-asset-guidelines.md        # Loaded at PDF assembly phase
    typst-artifacts.md               # Loaded at artifact detection phase
    typst-template-contract.md       # Loaded at data variable binding phase

.claude/skills/tachi-threat-reporting/
  SKILL.md
  references/
    narrative-templates.md           # Loaded at narrative generation phase
    attack-tree-construction.md      # Loaded at attack tree generation phase
    attack-tree-examples.md          # Loaded as reference during tree construction

.claude/skills/tachi-infographics/
  SKILL.md
  references/
    infographic-specifications.md    # Loaded at specification generation phase
    template-specific-formats.md     # Loaded per template type selection
    gemini-prompt-construction.md    # Loaded at image generation phase
    visual-design-system.md          # Loaded at visual encoding phase
```

**Key difference from agent-to-skill**: Shared definitions introduce a cross-cutting concern -- content that multiple independent agents need but that must remain consistent across all consumers. The `tachi-shared` skill acts as a single-source-of-truth hub, preventing drift that occurred when severity bands, category definitions, and finding formats were duplicated across agent prompts. Additionally, Feature 078 applied the agent-to-skill extraction to the remaining 3 report agents (report-assembler, threat-report, threat-infographic), achieving full-pipeline coverage. Combined with model field governance (`model: sonnet` in all 17 agent YAML frontmatter), this yielded 40-60% prompt size reduction across all 6 restructured agents.

#### Example 5: Detection Variant — Single-Point Load for Threat Agents (Feature 082)
```
# Directory structure — 11 threat agents, each paired with a single-reference companion skill
.claude/agents/tachi/
  spoofing.md                    # Core prompt (51 lines, down from 113)
  tampering.md                   # Core prompt (≤120 lines)
  prompt-injection.md            # Core prompt (95 lines, down from 167)
  ... (8 more lean threat agents)
.claude/skills/tachi-spoofing/
  references/detection-patterns.md     # Detection pattern catalog + enriched categories
.claude/skills/tachi-prompt-injection/
  references/detection-patterns.md     # LLM-specific patterns + enriched categories
... (9 more companion skill directories)

# In threat agent file — single-point load at detection start
## Detection Workflow
**MANDATORY**: You MUST use the Read tool to load `.claude/skills/tachi-spoofing/references/detection-patterns.md`
before proceeding with detection. Do NOT rely on memory of prior pattern content.
**MANDATORY**: You MUST use the Read tool to load `.claude/skills/tachi-shared/references/finding-format-shared.md`
for finding construction guidance. Read the "For Threat Agents (Producers)" section.

1. For each dispatched component, match against the detection patterns.
2. Construct findings using the shared finding format.
3. Emit finding list.
```

**Key difference from methodology variant**: Detection agents are **single-pass** — they match dispatched components against pattern catalogs and emit findings once per invocation. There is no multi-phase control flow, so the companion reference file is loaded once at the start of `## Detection Workflow` rather than phase-gated like control-analyzer's 6-phase methodology pipeline (Example 3's `.claude/skills/tachi-control-analysis/` shape). ADR-023 records this as the **detection variant** — a sibling to the methodology variant — and mandates the `## Detection Workflow` section name as the contributor-visible signal that the agent is single-pass rather than multi-phase. This yielded line-count reductions of STRIDE 113-141 → 50-54 lines and AI 167-201 → 78-114 lines across all 11 threat agents (aggregate ~1,680 → ~1,100 lines), every agent within its tier cap (STRIDE ≤120, AI ≤150, hard ceiling ≤180). A secondary structural change: `finding-format-shared.md` gained a "For Threat Agents (Producers)" section via additive-only edit, making the file dual-audience (existing consumer sections for risk-scorer/control-analyzer/threat-report remain byte-identical). **After Feature 082, all 17 tachi agents are on the lean + skill references pattern** — no remaining self-contained inline-pattern agents.

#### When to Use
- Skill files exceeding ~500 lines where content divides into always-needed vs. conditionally-needed
- Agent prompts exceeding ~500 lines with pipeline-phase-specific content (templates, checklists, error handling)
- Agent prompts containing large domain reference data (scoring tables, detection patterns, schema specifications) that can be extracted to standalone skill files
- Skills or agents with distinct operational modes (e.g., normal vs. dry-run vs. error recovery)
- When context window pressure limits the agent's ability to perform downstream work
- When multiple agents share identical reference data (severity bands, category definitions, output formats) that must remain consistent -- extract to a shared skill

#### When NOT to Use
- Files under ~500 lines where the entire content is routinely needed
- Content that is heavily cross-referenced (splitting creates circular Read dependencies)
- When Read tool latency is unacceptable for the use case

#### Related Patterns
- [Compound State Helpers](#pattern-compound-state-helpers) -- reduces state read tokens within the segmented core
- [Governance Result Caching](#pattern-governance-result-caching) -- reduces how often governance.md needs to be loaded

---

### Pattern: Compound State Helpers

**Added**: Feature 030 (Context Efficiency of /aod.run)

#### Problem
Reading the full JSON state file into context at every loop iteration consumes ~315 tokens per read. In a lifecycle with ~15 state reads before the Build stage, this totals ~4,725 tokens for state management alone. Most reads only need 2-3 fields.

#### Solution
Provide compound Bash helper functions that read the JSON once internally, extract multiple fields via a single `jq` query, and return only a pipe-delimited string of the extracted values. The full JSON never enters the agent's context.

#### Example
```bash
# From .aod/scripts/bash/run-state.sh

# Generic multi-field extraction
# Returns: "plan|spec|standard"
aod_state_get_multi ".current_stage" ".current_substage" ".governance_tier"

# Purpose-specific helper for the Core Loop
# Returns: "plan|spec|in_progress"
aod_state_get_loop_context

# Usage in the orchestrator Core Loop (step 1):
# Instead of: state=$(aod_state_read)  → ~315 tokens
# Use:        context=$(aod_state_get_loop_context)  → ~5 tokens
```

#### When to Use
- State files read repeatedly in a loop where only a few fields are needed per iteration
- Any scenario where the full state is large but the consumer needs a small subset
- When cumulative token savings across multiple reads justify adding helper functions

#### When NOT to Use
- One-time reads where the full state is needed (initialization, validation)
- State files small enough that full reads are negligible (~50 tokens or less)

#### Related Patterns
- [Atomic File Write](#pattern-atomic-file-write) -- compound helpers use the same atomic read/write infrastructure
- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation) -- both patterns reduce context consumption

---

### Pattern: Governance Result Caching

**Added**: Feature 030 (Context Efficiency of /aod.run)

#### Problem
Checking governance approval status requires reading full artifact files (spec.md, plan.md, tasks.md) and parsing their YAML frontmatter. Each artifact read consumes ~500 tokens. Governance is checked at stage boundaries and during resume validation, leading to ~3,000 tokens of redundant reads when verdicts have not changed.

#### Solution
Cache governance verdicts (status, date, summary) in the state file under a `governance_cache` object, keyed by artifact and reviewer. On subsequent governance checks, read the cached verdict (~11 tokens) instead of re-reading the artifact (~500 tokens). Invalidate the cache when an artifact is regenerated after a CHANGES_REQUESTED verdict.

#### Example
```bash
# From .aod/scripts/bash/run-state.sh

# Cache a verdict after a governance review completes
aod_state_cache_governance "spec" "pm" "APPROVED" "PM approved spec"

# Check cache before reading artifact (returns "APPROVED|2026-02-11|summary" or "null")
aod_state_get_governance_cache "spec" "pm"

# Invalidate cache when artifact is regenerated
aod_state_clear_governance_cache "spec"
```

```json
{
  "governance_cache": {
    "spec": {
      "pm": {
        "status": "APPROVED",
        "date": "2026-02-11T14:30:00Z",
        "summary": "PM approved spec"
      }
    }
  }
}
```

#### When to Use
- Governance or approval checks that are read frequently but change rarely
- Any expensive read operation whose result is deterministic until the source is modified
- Multi-gate workflows where the same verdict is checked at multiple points

#### When NOT to Use
- When the source artifact changes frequently (cache churn exceeds read savings)
- When governance rules require always-fresh reads (e.g., compliance audits)
- Single-check scenarios where caching adds complexity without savings

#### Related Patterns
- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation) -- cache hits avoid loading governance.md entirely
- [Compound State Helpers](#pattern-compound-state-helpers) -- cache reads use the same incremental extraction approach

---

### Pattern: Read-Only Dry-Run Preview

**Added**: Feature 027 (Orchestrator Dry-Run Mode)

#### Problem
Skills and commands that perform multi-step mutations (writing state files, creating branches, updating GitHub labels, invoking sub-skills) are difficult to reason about before execution. Users cannot predict what the orchestrator will do -- which stages will execute, which will be skipped, and what governance gates will trigger -- without actually running it and potentially creating irreversible side effects.

#### Solution
Add a `--dry-run` flag that reuses the existing detection and classification logic but suppresses all write operations. The pattern has four phases:

1. **Detect**: Run the same read-only detection steps as the normal mode (read state files, query GitHub, scan artifacts on disk)
2. **Classify**: Build the planned execution sequence, governance gate predictions, and artifact predictions using the detected state
3. **Display**: Render a structured preview showing what would happen for each stage
4. **Exit**: Stop immediately without entering the execution loop

The key insight is that detection logic is already separated from mutation logic in well-structured skills. Dry-run reuses detection verbatim and replaces mutation with display.

#### Example
```
# Skill routing (pseudocode from SKILL.md)
if DryRun == true:
    # Phase 1: Detect (reuse existing detection steps, read-only)
    run_detection_phase(mode, suppress_writes=true)

    # Phase 2: Classify
    execution_plan = classify_stages(detected_state)
    gate_predictions = predict_governance_gates(execution_plan, tier)
    artifact_predictions = predict_artifacts(execution_plan, feature_id)

    # Phase 3: Display
    render_preview(execution_plan, gate_predictions, artifact_predictions)

    # Phase 4: Exit -- do NOT enter Core Loop
    EXIT
```

Mutations explicitly suppressed during dry-run:
- No state file writes (`.aod/run-state.json`)
- No git branch creation or switching
- No GitHub label updates
- No sub-skill invocations
- No backlog regeneration

#### When to Use
- Commands or skills with multi-step side effects where users need confidence before committing
- Orchestrators that chain multiple sub-commands with governance gates
- Any workflow where the execution plan depends on detected state (existing artifacts, labels, prior progress)

#### When NOT to Use
- Simple commands with a single, obvious action (e.g., "read this file")
- Commands that are already read-only (e.g., `--status`)
- When the detection phase itself has significant side effects that cannot be separated from mutations

#### Related Patterns
- [Graceful CLI Degradation](#pattern-graceful-cli-degradation) -- dry-run inherits the same `gh` fallback behavior during detection

---

### Pattern: Orchestrator-Awareness Guard

**Added**: Feature 038 (Universal Session State Tracking)

#### Problem
Standalone lifecycle commands (`/aod.define`, `/aod.spec`, etc.) need to write state to `.aod/run-state.json`. However, the orchestrator (`/aod.run`) already manages state when it invokes these same commands as sub-stages. If a standalone command writes state entries while an active orchestrator is managing the state file, the two writers conflict -- potentially corrupting orchestrator loop context.

#### Solution
Before performing any state writes, each standalone command checks whether an active orchestrator owns the state file. The detection uses an implicit heuristic: read the `updated_at` timestamp and current stage status from the state file; if any stage is `in_progress` AND `updated_at` is within 5 minutes of the current time, an orchestrator is presumed active. In that case, the command skips state writes and defers to the orchestrator.

This avoids introducing new flags or environment variables. The 5-minute window is chosen because orchestrator loop iterations typically complete within seconds; a stale `updated_at` beyond 5 minutes indicates an abandoned or crashed orchestration rather than an active one.

The key rules:
1. **Check state existence**: If no state file exists, create one (standalone initialization)
2. **Check orchestrator recency**: Read `updated_at` and stage status; skip if active
3. **Validate feature ID**: Compare branch-derived feature ID against state's `feature_id`; prompt user on mismatch
4. **Proceed or skip**: Write state only in standalone mode

#### Example
```
# From .claude/commands/aod.define.md

1. Check state file:
   bash -c 'source .aod/scripts/bash/run-state.sh && aod_state_exists && echo "exists" || echo "none"'
   - "none" -> create state (step 3)
   - "exists" -> check orchestrator (step 2)

2. Detect active orchestrator:
   aod_state_get_loop_context  -> "plan|spec|in_progress"
   aod_state_get ".updated_at" -> "2026-02-12T10:05:00Z"
   - If stage is in_progress AND updated_at < 5 min ago -> SKIP state writes
   - Otherwise -> standalone mode, continue

3. Create state file (standalone only):
   aod_state_init "{feature_id}" "{feature_name}" "Entity 1"
```

#### When to Use
- Commands that can run both standalone and as sub-stages of an orchestrator
- Any writer that shares a state file with a long-running coordinator process
- Scenarios where an implicit ownership heuristic (recency) is sufficient

#### When NOT to Use
- Commands that are always standalone (no orchestrator coordination)
- When explicit ownership (lock files, PID checks) is required for correctness
- High-frequency concurrent writers where a 5-minute heuristic is too coarse

#### Related Patterns
- [Additive Optional State Fields](#pattern-additive-optional-state-fields) -- state fields follow the same backward-compatible schema extension
- [Graceful CLI Degradation](#pattern-graceful-cli-degradation) -- state operations degrade gracefully (non-fatal) similar to CLI fallbacks
- [Compound State Helpers](#pattern-compound-state-helpers) -- `aod_state_get_loop_context` used for orchestrator detection

---

### Pattern: Non-Fatal Observability Wrapper

**Added**: Feature 038 (Universal Session State Tracking)

#### Problem
Observability and state tracking are secondary concerns -- they must never block the primary skill execution. However, initialization sequences involve multiple steps (state existence check, orchestrator detection, feature ID validation, state creation) that can each fail for various reasons (missing `jq`, corrupted state file, permission errors). Wrapping every individual call in error handling is verbose and error-prone.

#### Solution
Encapsulate the entire observability initialization and completion sequences in clearly demarcated "Non-Fatal" blocks. Every shell command within these blocks uses `|| true` or equivalent error suppression. The block boundary is documented in the command file with an explicit contract: "If any step fails, log the error and continue -- observability is non-fatal."

The completion block follows the same pattern: write state, read summary, and append to output. If any step fails, the observability line is simply omitted from the completion message.

#### Example
```
# Pre-execution block (from command files)
## State Tracking (Non-Fatal)
1. Check state file ...
2. Detect active orchestrator ...
3. Create state file ...
If any step fails, log the error and continue to Step 1.

# Post-execution block (from command files, completion section)
### State Tracking (Non-Fatal)
1. Write state update:
   bash -c '... || true'
2. Read summary:
   bash -c '... || echo "fallback"'
3. If any step fails, omit the observability line.
```

#### When to Use
- Secondary telemetry or observability features that must not impact primary functionality
- Operations where partial success is acceptable (some observability data is better than none)
- Features added to existing stable commands where failure isolation is critical

#### When NOT to Use
- Core functionality where failures must be surfaced and handled
- Operations where partial state is worse than no state (use transactions instead)
- When error details are needed for debugging (non-fatal suppresses error context)

#### Related Patterns
- [Orchestrator-Awareness Guard](#pattern-orchestrator-awareness-guard) -- the non-fatal wrapper contains the orchestrator guard as one of its steps
- [Graceful CLI Degradation](#pattern-graceful-cli-degradation) -- both patterns prioritize continued operation over error reporting
- [Additive Optional State Fields](#pattern-additive-optional-state-fields) -- state read/write functions already handle missing fields gracefully

---

### Pattern: Append-Only Logging with Graceful Failure

**Added**: Feature 049 (Simple Logging Utility)

#### Problem
Scripts need to record timestamped execution events for debugging and auditing, but logging must not interfere with the primary operation if file writes fail (permission denied, disk full, etc.). Additionally, log configuration must be flexible (custom path via environment variable) without requiring code changes.

#### Solution
Implement a logging function that:
1. **Appends to a file** (not atomic, acceptable for logs) using `>>` operator
2. **Prepends ISO 8601 UTC timestamps** for temporal sorting and cross-system consistency
3. **Auto-creates directories** before first write (implicit initialization)
4. **Fails gracefully**: captures write errors, emits a warning to stderr, and returns non-zero exit code without exiting the calling script
5. **Accepts configuration** via environment variable (`AOD_LOG_FILE`) with a sensible default

#### Example
```bash
# From .aod/scripts/bash/logging.sh (Feature 049)

# Default log file path (can be overridden via environment variable)
AOD_LOG_FILE="${AOD_LOG_FILE:-.aod/logs/aod.log}"

# Log a timestamped message to the log file
# Usage: aod_log "message"
# Returns: 0 on success, 1 on failure
aod_log() {
    local message="$1"
    local timestamp

    # Generate ISO 8601 UTC timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Ensure log directory exists
    mkdir -p "$(dirname "$AOD_LOG_FILE")" 2>/dev/null || {
        echo "[aod] Warning: Cannot create log directory" >&2
        return 1
    }

    # Append formatted log entry to file
    echo "$timestamp $message" >> "$AOD_LOG_FILE" 2>/dev/null || {
        echo "[aod] Warning: Cannot write to log file" >&2
        return 1
    }

    return 0
}
```

**Usage in other scripts**:
```bash
# Source the logging utility
source .aod/scripts/bash/logging.sh

# Log a message (will use default path .aod/logs/aod.log)
aod_log "Stage started"

# Log with custom path (set environment variable)
AOD_LOG_FILE=/tmp/custom.log aod_log "Custom path message"

# Caller continues even if logging fails
aod_log "This might fail" || echo "Warning: logging failed"
```

**Log format**:
```
2026-02-13T10:30:00Z Stage started
2026-02-13T10:30:01Z Discover stage complete
2026-02-13T10:30:15Z Define stage started
```

#### When to Use
- Any script that needs diagnostic output for later review without blocking execution
- Lifecycle commands where logging is secondary to primary functionality
- Situations where log files may be on read-only or space-constrained filesystems
- Multi-step processes where you want to track progress independent of return codes

#### When NOT to Use
- Critical alerts that must be delivered (use stderr/exit for critical errors)
- High-frequency logging where append overhead matters (logs only at stage boundaries, not per-call)
- Systems requiring guaranteed atomic writes or concurrent write safety (append mode is best-effort only)
- Requirements for structured logging (JSON, tags, log levels) -- this is plain-text only

#### Implementation Guarantees
- **No hard failure**: Write errors emit a stderr warning but never crash the caller
- **Cross-platform**: Works on macOS and Linux with standard shell utilities (`date`, `mkdir`, `echo`)
- **Portable configuration**: Environment variable override allows scripts to be used unchanged in different contexts
- **Self-healing**: Auto-creates parent directories before first write, no manual initialization needed

#### Related Patterns
- [Graceful CLI Degradation](#pattern-graceful-cli-degradation) -- logging gracefully degrades similar to optional CLI tools
- [Function Library Sourcing](#pattern-function-library-sourcing) -- logging.sh is a function library meant to be sourced by other scripts

---

### Pattern: Circuit-Breaker Churn Detection

**Added**: Feature 054 (Parallel Execution Hardening)
**ADR**: [ADR-006](../02_ADRs/ADR-006-non-fatal-observability-operations.md)

#### Problem
When an operation fails repeatedly with the same error, the orchestrator may enter a "churn loop" -- retrying the same failing operation until context is exhausted. Observed: 17+ minutes of retries before hard failure, wasting substantial tokens and user time.

#### Solution
Implement a circuit-breaker pattern that tracks consecutive failures by error signature. After 3 identical failures, the circuit-breaker "opens" and triggers a diagnostic pause with a message to the user. The circuit-breaker resets when:
- An operation succeeds (proves the issue is resolved)
- The error signature changes (indicates a different problem)
- A new session starts (fresh context, worth retrying)

#### Example

The governance circuit breaker in `governance.md` tracks consecutive `gate_rejections`. When 3 identical failures occur, it escalates to the user rather than retrying.

```json
{
  "gate_rejections": [
    { "stage": "plan", "substage": "spec", "reviewer": "product-manager", "attempt": 1 },
    { "stage": "plan", "substage": "spec", "reviewer": "product-manager", "attempt": 2 },
    { "stage": "plan", "substage": "spec", "reviewer": "product-manager", "attempt": 3 }
  ]
}
```

When 3 rejections accumulate for the same gate, the circuit breaker fires and escalates to the user.

#### When to Use
- Operations that can fail repeatedly with the same root cause
- Long-running orchestrations where churn wastes significant resources
- Any retry logic where detecting futile retries provides value

#### When NOT to Use
- Operations expected to fail before succeeding (e.g., polling for async completion)
- When different failures are related (consider aggregating to a single signature)
- Single-shot operations without retry logic

#### Error Signature Design

The error signature is `operation_name:error_type` (e.g., `governance_review:timeout`). Choosing the right granularity is important:

- **Too specific**: Every failure looks different, circuit-breaker never triggers
- **Too general**: Unrelated failures accumulate, false positives occur

Good signatures group failures by root cause, not surface symptoms.

#### Related Patterns
- [Non-Fatal Observability Wrapper](#pattern-non-fatal-observability-wrapper) -- circuit-breaker functions are non-fatal
- [Graceful CLI Degradation](#pattern-graceful-cli-degradation) -- circuit-breaker degrades to "closed" on read errors

---

### Pattern: Dual-Surface Injection

**Added**: Feature 058 (Stack Packs)
**ADR**: [ADR-007](../02_ADRs/ADR-007-stack-pack-dual-surface-injection.md)

#### Problem
Stack packs need to inject technology-specific context into AI agents at two distinct points with different loading semantics: (1) broad coding rules that all agents should follow, auto-loaded via `.claude/rules/` discovery at session start; and (2) role-specific persona supplements that only specialized/hybrid agents should load, on-demand during task execution. A single injection surface would either over-load all agents with role-specific details (wasting context tokens) or under-serve specialized agents with only generic rules.

#### Solution
Inject pack content through two independent surfaces with different loading triggers:

**Surface 1 -- Rules injection** (auto-loaded, all agents): On activation, copy `.md` files from `stacks/{pack}/rules/` to `.claude/rules/stack/` and generate a `persona-loader.md` directive. These files are discovered by Claude Code's standard rules loading mechanism and apply to every agent in the session.

**Surface 2 -- Persona injection** (on-demand, specialized/hybrid agents only): During `/aod.build`, the build command reads `.aod/stack-active.json` to determine the active pack, then augments dispatched agent prompts with instructions to read `stacks/{pack}/agents/{agent-name}.md`. Core agents (product-manager, architect, team-lead, orchestrator, web-researcher) are never augmented.

Files are **copied** (not symlinked) from pack source to the rules directory for cross-platform safety and source immutability. Activation state is tracked in `.aod/stack-active.json` (JSON, consistent with `run-state.json` pattern).

#### Example
```
# Activation flow (/aod.stack use nextjs-supabase)

# Surface 1: Copy rules to auto-discovery location
stacks/nextjs-supabase/rules/conventions.md  -->  .claude/rules/stack/conventions.md
stacks/nextjs-supabase/rules/security.md     -->  .claude/rules/stack/security.md
(generated)                                  -->  .claude/rules/stack/persona-loader.md

# Surface 2: State file enables build-time persona injection
.aod/stack-active.json = {"pack": "nextjs-supabase", "activated_at": "2026-02-27T14:30:00Z", "version": "1.0"}

# During /aod.build, when dispatching frontend-developer:
#   1. Read .aod/stack-active.json -> pack = "nextjs-supabase"
#   2. Agent is "specialized" tier -> inject persona read instruction
#   3. Agent reads stacks/nextjs-supabase/agents/frontend-developer.md
#   4. Agent applies stack-specific conventions from supplement

# During /aod.build, when dispatching product-manager:
#   1. Agent is "core" tier -> no persona injection
#   2. Rules from .claude/rules/stack/ still apply (auto-loaded)
```

```
# Deactivation flow (/aod.stack remove)
rm .claude/rules/stack/conventions.md
rm .claude/rules/stack/security.md
rm .claude/rules/stack/persona-loader.md
rm .aod/stack-active.json
# Pack source files in stacks/ are untouched
# Previously scaffolded project files are untouched
```

#### When to Use
- Injecting context into agents at multiple points with different loading semantics (auto-loaded vs. on-demand)
- When different agent roles need different subsets of injected content
- Plugin/pack systems where activation must be reversible without side effects on source files
- Context-budget-constrained environments where selective loading is necessary

#### When NOT to Use
- Single-surface injection is sufficient (all agents need the same content)
- Content is small enough that loading everything everywhere fits within context budget
- When symlinks are acceptable (single-platform, no immutability requirement)

#### Related Patterns
- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation) -- persona supplements use the same principle of loading content only when needed
- [Additive Optional State Fields](#pattern-additive-optional-state-fields) -- `stack-active.json` follows the same JSON state pattern, and the system gracefully handles its absence
- [Graceful CLI Degradation](#pattern-graceful-cli-degradation) -- inconsistent state detection in `/aod.stack` commands follows the same degrade-gracefully philosophy

---

### Pattern: Subshell Isolation for Strict Shell Options

**Added**: Feature 062 (Auto-Create GitHub Projects Board During Init)

#### Problem
Scripts that use `set -e` (errexit) will abort if any command returns a non-zero exit code. When such a script sources a function library and calls a function that may fail (e.g., a network-dependent GitHub API call), the failure propagates through the `source` chain and terminates the parent script -- even when the caller intends to handle the failure gracefully with `|| true`.

The core issue is that `set -e` propagates into sourced files and their function calls. A `source lib.sh && some_function` expression inherits the parent's `set -e` context, so any internal failure within `some_function` causes the parent to exit before the `|| true` guard can execute.

#### Solution
Wrap the source-and-call sequence in `bash -c '...'`, which spawns a child process with a fresh shell environment. The child process does NOT inherit `set -e` from the parent. The parent captures the child's exit code and output, then handles failure with `|| true` or conditional logic.

This creates a clean boundary: the parent script keeps its strict error handling for its own operations, while the sourced library functions execute without `set -e` interference.

#### Example
```bash
# From scripts/init.sh (Feature 062)
# Parent script has: set -e

# CORRECT: Subshell isolation — set -e does NOT propagate into the child
board_output=$(bash -c 'source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_board' 2>&1) || true

# WRONG: Direct source — set -e propagates, any internal failure kills init.sh
source .aod/scripts/bash/github-lifecycle.sh
aod_gh_setup_board || true  # Too late — set -e already killed the script

# WRONG: Subshell syntax — ( ) inherits set -e from parent
board_output=$(source .aod/scripts/bash/github-lifecycle.sh && aod_gh_setup_board 2>&1) || true
```

The key distinction is between `bash -c '...'` (new process, clean environment) and `$(...)` or `( )` (subshell that inherits shell options from the parent).

#### When to Use
- Calling function libraries from scripts that use `set -e`
- Isolating non-critical operations (board creation, telemetry) from critical init flows
- Any scenario where a sourced function may fail and the caller must continue

#### When NOT to Use
- Scripts without `set -e` (no isolation needed, direct source is fine)
- When you need the sourced functions to share variables with the parent (child process has separate scope)
- Critical operations where failure SHOULD abort the parent script

#### Related Patterns
- [Function Library Sourcing](#pattern-function-library-sourcing) -- the standard pattern for calling library functions; subshell isolation is the variant for `set -e` contexts
- [Graceful CLI Degradation](#pattern-graceful-cli-degradation) -- the outer pattern that skips non-critical operations; subshell isolation is the mechanism that makes graceful degradation safe under `set -e`
- [Non-Fatal Observability Wrapper](#pattern-non-fatal-observability-wrapper) -- both patterns ensure secondary operations cannot block primary execution

---

### Pattern: Built-in Skill Invocation from a Command

**Added**: Feature 065 (Add /simplify Command to AOD Process)
**ADR**: [ADR-008](../02_ADRs/ADR-008-opt-out-flag-for-default-quality-gates.md)

#### Problem
A command workflow needs to invoke a built-in platform skill (one that is not a custom `.claude/skills/` file, but a first-party capability like `/simplify`) as a named step. Two sub-problems arise:

1. **Discoverability**: The skill is invisible in the command file -- there is no file path to reference, only a slash-command name. Readers of the command file cannot tell what the skill does without knowing the platform.
2. **Opt-out**: Some execution contexts make the built-in step inappropriate (e.g., methodology-only repos with no source code to simplify, CI runs that must be deterministic). A blanket invocation with no escape hatch forces all users to accept the step.

#### Solution
Reference the built-in skill by its slash-command name in the command file's step list, with a parenthetical that describes what it does. Gate the step behind an opt-out flag (e.g., `--no-simplify`) that is checked before the step executes. The flag default is **on** (quality gate runs unless explicitly skipped), preserving the quality intent while providing a documented escape hatch.

The opt-out flag must be:
1. Declared in the command's flag-parsing section near the top of the file
2. Checked immediately before the step that invokes the skill
3. Documented in the command reference and in CLAUDE.md

The step text uses the Skill tool (not Bash) to invoke the built-in, since built-ins are agent capabilities, not shell commands.

#### Example
```markdown
# In .claude/commands/aod.build.md

## Flags
- `--no-security`: Skip the security scan step (Step 6)
- `--no-simplify`: Skip the code simplification step (Step 7)

## Steps

...

### Step 6: Security Scan (skip if --no-security)
Invoke the /security skill to analyze changed code files and manifests for
OWASP Top 10 vulnerabilities and known CVE patterns.
- If `--no-security` flag is present: skip this step, write security-scan.md "Skipped" entry
- Otherwise: Use the Skill tool to invoke `security` on changed files

### Step 7: Code Simplification (skip if --no-simplify)
Invoke the /simplify skill to reduce complexity and improve readability of
any files modified during this build session.
- If `--no-simplify` flag is present: skip this step entirely, log "Simplification skipped (--no-simplify)"
- Otherwise: Use the Skill tool to invoke `/simplify` on changed files
```

```markdown
# In CLAUDE.md commands section
/aod.build [--no-security] [--no-simplify]  # Execute with auto architect checkpoints; --no-security skips security scan (Step 6); --no-simplify skips code simplification (Step 7)
```

#### When to Use
- Integrating a platform built-in (e.g., `/simplify`, `/lint`, `/format`) as a named workflow step
- When the built-in is appropriate by default but not universally (methodology repos, CI-only runs)
- When you want the quality gate to be explicit in the command file so reviewers understand the workflow

#### When NOT to Use
- Built-ins that are always appropriate with no valid reason to skip (just invoke unconditionally)
- Built-ins that are rarely appropriate (make the step opt-in with a `--with-X` flag instead)
- Custom skills in `.claude/skills/` (use On-Demand Reference File Segmentation pattern instead)

#### Related Patterns
- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation) -- applies to custom skill files; this pattern applies to platform built-ins
- [Read-Only Dry-Run Preview](#pattern-read-only-dry-run-preview) -- `--dry-run` and `--no-simplify` follow the same flag-gating convention for skipping steps

---

### Pattern: Template Variable Expansion

**Added**: Feature 061 (init.sh Personalize All Template Files)
**ADR**: [ADR-009](../02_ADRs/ADR-009-template-variable-expansion-scope.md)

#### Problem
Template files shipped with the kit contain the kit's own name ("Agentic Oriented Development Kit") as hardcoded text. When an adopter runs `make init`, these files are not personalized, so all user-facing documentation still shows the kit name instead of the adopter's project name. This causes confusion and requires manual find-and-replace by adopters.

#### Solution
Use the `tachi` double-brace placeholder wherever the project name should appear in a template file. `scripts/init.sh` already performs a `sed` substitution pass over template files during `make init`, replacing `tachi` with the adopter's actual project name. No new code or infrastructure is needed -- add the placeholder to the file content and the init script handles the rest.

The convention aligns with other template variables in the kit (`2026-03-21`, `{{TEMPLATE_VARIABLES}}`, etc.) and is consistent with the pre-existing usage in `.aod/memory/constitution.md`.

#### Files Using This Pattern
| File | Placeholder Locations |
|------|-----------------------|
| `CLAUDE.md` | File header, project structure comment |
| `README.md` | Title, description, header references |
| `.claude/README.md` | Title, overview |
| `.claude/agents/_README.md` | Title, overview |
| `.claude/rules/commands.md` | Overview line |
| `.claude/rules/context-loading.md` | Overview line |
| `.claude/rules/deployment.md` | Overview line |
| `.claude/rules/git-workflow.md` | Overview line |
| `.claude/rules/governance.md` | Overview line |
| `.claude/rules/scope.md` | Title, description lines |
| `docs/product/02_PRD/INDEX.md` | Header |
| `.aod/memory/constitution.md` | Pre-existing usage |

#### When to Use
- Any template file that would display "Agentic Oriented Development Kit" to an adopter after `make init`
- Headers, titles, and overview lines in files that adopters will read, share, or modify
- New `.claude/rules/*.md` or `.claude/agents/*.md` files added to the kit

#### When NOT to Use
- Internal implementation files that adopters never read directly (e.g., shell scripts, JSON state files)
- Comments in script files where the kit name is intentional (e.g., attribution headers)
- Files that are NOT processed by `scripts/init.sh` -- check `init.sh` to confirm a file is in scope before adding the placeholder

#### Checklist for New Template Files
When adding a new user-facing template file to the kit:
1. Identify every occurrence of "Agentic Oriented Development Kit" or its abbreviation
2. Replace with `tachi`
3. Verify the file is included in the `scripts/init.sh` substitution loop
4. Test with `make init` on a fresh clone to confirm replacement occurs

#### Related Patterns
- None -- this is a content convention, not a runtime pattern

---

### Pattern: Hub-First Typst Template Modularity

**Added**: Feature 060 (Professional PDF Security Assessment Report)
**KB Reference**: [PAT-013](../../INSTITUTIONAL_KNOWLEDGE.md) — Typst Template Modularity Requires Hub-First Architecture

#### Problem
Multi-file Typst template systems with shared theming suffer from inconsistent token usage and repeated rework when page templates are authored before the theme layer is stabilized. Developers change a color or font in one file and must hunt through all others to propagate it.

#### Solution
Establish a hub-first architecture with a strict import chain: `main.typ` → `theme.typ` → `shared.typ` → individual page templates. The theme file centralizes all brand tokens (colors, fonts, logo paths), and shared utilities consume them via imports. Individual pages never define their own colors or font stacks — they reference theme tokens exclusively.

Freeze the theme token API and shared utility layer in a dedicated foundation phase before any page-level work begins.

#### Files Using This Pattern
| File | Role |
|------|------|
| `templates/tachi/security-report/theme.typ` | Hub — brand colors, fonts, logo paths |
| `templates/tachi/security-report/shared.typ` | Utilities — imports theme, provides layout functions |
| `templates/tachi/security-report/report-config.typ` | Configuration — page visibility toggles, metadata |
| `templates/tachi/security-report/main.typ` | Orchestrator — imports all, assembles pages |
| `templates/tachi/security-report/*.typ` (pages) | Spokes — import shared, use theme tokens |

#### When to Use
- Multi-file Typst template systems with 5+ page templates
- Projects requiring brand customization (logo, colors, fonts)
- Any template system where visual consistency across pages is critical

#### When NOT to Use
- Single-file Typst documents that don't need theming
- Prototype/throwaway reports where consistency doesn't matter

#### Related Patterns
- [Template Variable Expansion](#pattern-template-variable-expansion) — content-level personalization
- PAT-012: Docs-Only Template Features Complete Faster Than Estimated (KB)

---

### Pattern: Two-Level Architecture

**Added**: Feature 064 (Knowledge System Stack Pack)

#### Problem
Knowledge-intensive domains (resume writing, publishing, education, consulting) need AI-orchestrated workflows to produce quality outputs. A naive approach treats orchestration design and content production as a single activity, leading to non-reusable one-off generation, no quality framework, and re-running the full SDLC for every output.

#### Solution
Separate the system into two distinct operational levels with different lifecycles:

**Build-time (AOD lifecycle)**: Use `/aod.define` through `/aod.deliver` to design and construct the orchestration itself -- commands, agent personas, content architecture, quality rubric, and context loading configuration. The product of build-time is a working orchestration system.

**Run-time (domain orchestration)**: Use the commands built during build-time (e.g., `/new`, `/draft`, `/review`, `/export`) to produce domain outputs -- tailored resumes, edited chapters, lesson plans, consulting deliverables. The product of run-time is domain content.

The rule: AOD commands design the system. Product commands operate the system. Never use AOD commands as run-time product commands. Never build product commands that duplicate AOD lifecycle functions.

#### Example
```
# BUILD-TIME: Constructing the orchestration (AOD lifecycle)
/aod.define "resume builder"    # Define command inventory, audience, content domains
/aod.spec                       # Specify commands, agents, content architecture
/aod.project-plan               # Plan orchestration: command flow, context loading
/aod.tasks                      # Break down into: command files, agent personas, templates
/aod.build                      # Author commands, build agents, configure context loading
/aod.deliver                    # Validate end-to-end orchestration

# RUN-TIME: Operating the built system (product commands)
/new senior-resume              # Initialize output instance from master content
/draft --preset formal-exec     # Generate draft using voice + style + context
/review                         # Evaluate against scoring rubric
/export pdf                     # Format for delivery
```

#### When to Use
- Stack packs targeting content-intensive or knowledge-management domains
- Any system where the orchestration layer is itself the product (not application code)
- Domains where quality is measured by rubric scoring rather than test suites

#### When NOT to Use
- Traditional software stack packs (e.g., nextjs-supabase) where build-time produces application code directly
- Simple automation scripts with no reusable orchestration layer

#### Related Patterns
- [Dual-Surface Injection](#pattern-dual-surface-injection) -- mechanism for loading pack conventions into agents
- [Command-per-Workflow](#pattern-orchestrator-awareness-guard) -- each user workflow maps to one command (documented in `stacks/knowledge-system/STACK.md`)

---

### Pattern: Minimal-Return Subagent

**Added**: Feature 073 (Minimal-Return Architecture for Subagent Context Optimization)
**ADR**: [ADR-010](../02_ADRs/ADR-010-minimal-return-architecture.md)

#### Problem

Subagents invoked for governance reviews (Triad reviewers, code reviewers) return their complete findings inline to the calling orchestrator. A thorough review runs 500-2,000 tokens per return. A full Triad review cycle (3 reviewers) therefore consumes 1,500-6,000 tokens in the main context before any implementation work can proceed. In long-running orchestrations with 10+ delegations, this overhead exhausts the context window within 30-60 minutes -- well before the Build stage.

The core tension: governance reviews are valuable because they are thorough. Truncating returns would lose the rationale, specific concerns, and recommendations that make reviews actionable. The problem is not what the subagent produces, but where it lives.

#### Solution

Decouple the subagent's work product from its return to the main context using **file-based offloading**:

1. The subagent writes its complete findings to `.aod/results/{agent-name}.md` before returning
2. The subagent returns only a brief status summary to the main context: STATUS + ITEMS count + DETAILS file path, capped at 10 lines
3. The main agent reads the results file on-demand when it needs to act on specific findings (e.g., when CHANGES_REQUESTED)
4. Results files use overwrite semantics -- each invocation replaces the prior file, keeping only the current review

The approach has two enforcement layers:
- **Project-wide**: A "Subagent Return Policy" section in CLAUDE.md establishes the convention for all agents
- **Agent-level**: A "Return Format (STRICT)" section in each agent prompt specifies exact format and line limits

The `.aod/results/` directory is gitignored as ephemeral session-scoped artifacts.

#### Example

```markdown
# In .claude/agents/architect.md

## Return Format (STRICT)

When invoked as a **subagent** (via the Agent tool), you MUST:

1. Write your full review to `.aod/results/architect.md` (overwrite, do not append)
2. Return to the caller ONLY the following format:

```
STATUS: [APPROVED | APPROVED_WITH_CONCERNS | CHANGES_REQUESTED | BLOCKED]
ITEMS: [N findings/concerns]
DETAILS: .aod/results/architect.md
```

Maximum return: 10 lines. Do NOT include review rationale, specific concerns,
recommendations, code snippets, or file contents in the return.

This restriction applies ONLY when invoked as a subagent. When invoked directly
by the user, provide full output.
```

```
# Results file written by architect: .aod/results/architect.md
STATUS: CHANGES_REQUESTED
ITEMS: 3

## Finding 1: Missing rate limiting on public endpoints (BLOCKING)
[Full rationale, code references, recommendations ...]

## Finding 2: ...
```

```
# Return to main orchestrator (from architect subagent) — ~8 lines, ~80 tokens
STATUS: CHANGES_REQUESTED
ITEMS: 3
DETAILS: .aod/results/architect.md
```

#### When to Use

- Subagents that produce review or audit outputs (Triad reviewers, code reviewers, security analysts)
- Long-running orchestrations where cumulative subagent return overhead threatens context budget
- Any agent invoked multiple times per session where return content repeats similar structure
- Multi-reviewer workflows where the main agent must aggregate results but act on each individually

#### When NOT to Use

- Agents invoked for debugging or diagnostic work where the diagnostic output IS the deliverable (return the content inline)
- Simple status-check subagents where the return is already minimal (< 5 lines)
- Agents invoked directly by the user (not as a subagent) -- the return format restriction does not apply
- Single-shot orchestrations where context budget is not a concern

#### Implementation Notes

- The `{agent-name}.md` filename convention ensures each agent type has a stable, known path (e.g., `product-manager.md`, `architect.md`, `team-lead.md`)
- If two instances of the same agent type run in parallel, the last write wins (overwrite semantics -- acceptable given sequential Triad reviews)
- If the results directory does not exist, the subagent creates it before writing (self-healing initialization)
- Non-compliance degrades gracefully: a verbose return is larger than intended but does not break the workflow

#### Token Savings Reference

| Scenario | Before | After | Reduction |
|----------|--------|-------|-----------|
| Single reviewer return | 500-2,000 tokens | ~80 tokens | ~95% |
| Full Triad cycle (3 reviewers) | 1,500-6,000 tokens | <600 tokens | ~90% |
| Full `/aod.run` lifecycle (10+ delegations) | Context exhausted ~30-60 min | 90+ min sustained | 2-3x session length |

#### Related Patterns

- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation) -- same principle of deferring content to disk until needed; applied to skill files rather than subagent returns
- [Governance Result Caching](#pattern-governance-result-caching) -- complements this pattern by caching governance verdicts; minimal returns reduce what needs to be cached
- [Non-Fatal Observability Wrapper](#pattern-non-fatal-observability-wrapper) -- non-compliance in return format degrades gracefully, never blocks governance

---

### Pattern: Governed Skill Phase Loop

**Added**: Feature 071 (One-Shot Bug Fix Command — `/aod.bugfix`)
**Skill**: `.claude/skills/~aod-bugfix/SKILL.md`

#### Problem

A skill needs to execute a multi-phase workflow where: (1) phases must be announced so the user knows progress without having to infer it from output; (2) at least one phase applies irreversible mutations (file edits) that require explicit user consent before proceeding; (3) secondary phases (knowledge base operations) are valuable but must not abort the primary loop if they fail; and (4) a user-reviewable artifact must be generated and approved before being persisted.

A linear sequence of instructions with no phase structure, no confirmation gate, and no non-fatal boundary handling produces a skill that silently edits files, suppresses KB failures as errors, and leaves users uncertain about progress.

#### Solution

Structure the SKILL.md as a sequence of explicitly numbered and announced phases. Each phase follows this contract:

1. **Entry announcement**: Print `[Phase N] <name>...` before executing the phase body
2. **Mutation gate**: Before any file write or code change, present a fix plan (affected files + nature of change + confidence level) and wait for explicit user confirmation. Do NOT proceed if the user declines.
3. **Non-fatal secondary phases**: Phases that perform optional enhancements (KB lookup, KB write, external reads) use non-fatal handling: announce failure, continue to next phase. The primary loop must complete regardless of secondary phase outcomes.
4. **Artifact review gate**: When a phase generates a user-facing artifact (e.g., KB entry draft), display it before writing. Allow inline editing. Write only after re-confirmation.
5. **Completion summary**: At loop end, emit a structured summary: root cause identified, files changed, verification status, artifact location (or "skipped").

#### Phase Structure (from `/aod.bugfix`)

```
Phase 0   — Input Acknowledgment & Context Summary (always runs)
Phase 0b  — KB Pre-Check (non-fatal; skips on failure, proceeds to Phase 1)
Phase 1   — Root Cause Analysis (5 Whys methodology; states root cause in plain language)
Phase 2   — Fix Plan + Confirmation Gate (BLOCKING: must receive explicit confirm before Phase 3)
Phase 3   — Implementation (applies ONLY the changes described in Phase 2)
Phase 3b  — Commit Prompt (non-blocking advisory)
Phase 4   — Verification (best-effort; SKIPPED is valid if no test commands available)
Phase 5   — KB Entry Review Gate (non-fatal; show draft → review → write after confirm)

[Completion Summary]
```

#### Key Invariants

- Phase 3 MUST NOT execute unless Phase 2 received explicit user confirmation
- Phase 3 MUST report exactly which files were edited if it fails mid-execution (no silent partial state)
- Phase 0b failure MUST NOT prevent Phase 1 from starting
- Phase 5 failure MUST NOT mark the loop as failed (KB write is non-fatal per ADR-006)
- Secondary phases (0b, 5) are always announced, never silently skipped

#### When to Use

- Skills that perform multi-step workflows with at least one irreversible mutation step
- Workflows where KB or knowledge document operations are secondary (valuable but not critical path)
- Developer-facing skills where progress transparency reduces cognitive load
- Any skill following the diagnose → plan → implement → verify → document lifecycle shape

#### When NOT to Use

- Simple single-step skills where phase structure adds no navigational value
- Skills with no mutation phases (no confirmation gate needed)
- Background or non-interactive skills where user confirmation gates are inappropriate

#### Related Patterns

- [Non-Fatal Observability Wrapper](#pattern-non-fatal-observability-wrapper) — the same non-fatal principle applied to bash observability functions; this pattern applies it to AI skill phase boundaries
- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation) — for skills exceeding ~500 lines, combine with this pattern to split conditionally-needed phase content into on-demand reference files

---

### Pattern: Convention Contract

**Added**: Feature 058 (Stack Packs), validated across Features 064 and 078

#### Problem

Stack packs need to communicate technology conventions, coding rules, and architectural constraints to AI agents in a predictable format. Without a standardized contract, each pack would define conventions differently -- some as prose, some as rules files, some embedded in agent prompts -- making it impossible for the stack activation skill to load conventions consistently. Agents would not know where to find the authoritative source for "how to write code in this stack."

#### Solution

Define a `STACK.md` file as the required convention contract for every stack pack. The file follows a fixed structure with a budget cap (500 lines max) to prevent context bloat:

1. **Header block**: Pack metadata (target audience, stack versions, use case, deployment, philosophy) in a standardized format that the activation skill can parse
2. **Architecture Pattern section**: Layered architecture with explicit ALWAYS/NEVER rules per layer (routes, services, models, schemas, etc.)
3. **Conventions sections**: Backend conventions, frontend conventions, API communication patterns, testing requirements, security rules -- each with concrete examples
4. **Validation checklist**: A checklist agents can evaluate code against to verify convention compliance

The contract is loaded into every agent invocation when the pack is active (via the dual-surface injection mechanism). Agents treat STACK.md as authoritative for technology-specific decisions.

#### Example
```
stacks/fastapi-react/STACK.md (354 lines):
  Header        → Target, Stack, Use Case, Deployment, Philosophy
  Architecture  → Backend (layered: routes → services → ORM)
                → Database (SQLAlchemy 2.0 async + asyncpg)
                → Frontend (React SPA with TanStack Query)
  Conventions   → Backend (Pydantic schemas, dependency injection)
                → Frontend (TypeScript strict, component patterns)
  Security      → CORS, auth, SQL injection prevention
  Testing       → pytest-asyncio, httpx, Vitest + RTL
  Validation    → 15-item compliance checklist
```

#### When to Use
- Every stack pack must include a STACK.md (it is the only required file in a pack)
- When defining technology conventions that agents must follow during code generation
- When multiple agent personas need a shared authoritative source for coding rules

#### When NOT to Use
- For runtime configuration (use `defaults.env` or scaffold config files instead)
- For agent persona definitions (use `agents/*.md` persona supplements instead)
- For rules that apply regardless of stack (use `.claude/rules/*.md` instead)

#### Related Patterns
- [Dual-Surface Injection](#pattern-dual-surface-injection) -- mechanism that loads STACK.md into agent context at activation time
- [Two-Level Architecture](#pattern-two-level-architecture) -- knowledge-system packs use STACK.md to define both build-time and run-time conventions

---

### Pattern: STRIDE-per-Element Matrix Targeting

**Added**: Feature 005 (STRIDE Threat Agents)
**ADR**: [ADR-003](../02_ADRs/ADR-003-stride-per-element-dispatch.md)

#### Problem

Threat agents that analyze all components for all threat categories produce irrelevant findings (e.g., Tampering analysis on an External Entity that the agent does not control). Generic, untargeted threat analysis reduces signal quality and generates noise that security reviewers must manually filter.

#### Solution

Each STRIDE threat agent declares its applicable DFD element types in YAML frontmatter (`dfd_targets` field). When invoked, the agent filters the architecture input to analyze only components whose DFD classification appears in its target list. This enforces the Microsoft STRIDE-per-Element methodology at the agent level.

The matrix is a fixed lookup table -- no probabilistic reasoning or LLM judgment determines which components an agent analyzes:

| DFD Element Type | Applicable Agents |
|------------------|-------------------|
| External Entity  | Spoofing (S), Repudiation (R) |
| Process          | All 6: S, T, R, I, D, E |
| Data Store       | Tampering (T), Info Disclosure (I), DoS (D) |
| Data Flow        | Tampering (T), Info Disclosure (I), DoS (D) |

#### Example
```yaml
# From agents/stride/spoofing.md frontmatter
---
agent_name: spoofing
category: stride
threat_class: S
dfd_targets: [External Entity, Process]
owasp_references:
  - "OWASP API Security 2023 API2 — Broken Authentication"
  - "CWE-287: Improper Authentication"
output_schema: schemas/finding.yaml
---

# Agent logic:
# 1. Receive full architecture input from orchestrator
# 2. Filter components: keep only those classified as External Entity or Process
# 3. For each filtered component, apply Spoofing detection patterns
# 4. Produce findings with S-prefixed IDs referencing specific component names
# 5. Skip components classified as Data Store or Data Flow (not in dfd_targets)
```

#### When to Use
- Threat agents that analyze architecture inputs through a specific threat lens
- Any dispatch system where component type determines which analyzers are applicable
- When reducing false positives from structurally inapplicable threat categories is important

#### When NOT to Use
- Analysis that must consider all components regardless of classification (use full-matrix dispatch)
- When DFD classification is unavailable or unreliable (agents cannot filter without element types)
- Single-purpose analyzers that always analyze all components (no filtering benefit)

#### Related Patterns
- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation) -- agent prompts follow a similar selective-loading principle (analyze only what is relevant)
- [Graceful CLI Degradation](#pattern-graceful-cli-degradation) -- agents default ambiguous components to Process (broadest coverage) rather than failing

---

### Pattern: Cross-Agent Correlation Detection

**Added**: Feature 010 (Deduplication & Risk Rating)
**ADR**: [ADR-012](../02_ADRs/ADR-012-cross-agent-correlation-detection.md)

#### Problem

When STRIDE and AI threat agents independently analyze the same architecture, they produce overlapping findings on the same component from different threat perspectives. For example, a Tampering finding (T-2) and a Data-Poisoning finding (LLM-1) on the same LLM pipeline both address data integrity. Reporting these as independent findings inflates risk counts in the coverage matrix and risk summary, misleading security reviewers about the actual distinct threat count.

#### Solution

After all agent findings are collected (Phase 3), apply deterministic correlation detection before coverage matrix generation (Phase 4). Five fixed rules map STRIDE-to-AI category pairs based on shared threat semantics. Findings are grouped by target component first, then cross-category pairs are checked against the rule table. Matched findings are grouped into correlation groups (CG-N). Each finding belongs to at most one group.

The correlation is non-destructive: original findings remain in their STRIDE and AI tables. Correlation groups appear in a separate Section 4a. Deduplication affects only the coverage matrix cell counts and the risk summary totals.

| Rule | STRIDE Category | AI Category | Correlation Basis |
|------|----------------|-------------|-------------------|
| CR-1 | Tampering (T) | Data-Poisoning (LLM) | Data integrity |
| CR-2 | Privilege-Escalation (E) | Agent-Autonomy (AG) | Excessive permissions |
| CR-3 | Info-Disclosure (I) | Prompt-Injection (LLM) | Information leakage |
| CR-4 | Repudiation (R) | Agent-Autonomy (AG) | Accountability gaps |
| CR-5 | Denial-of-Service (D) | Tool-Abuse (AG) | Resource exhaustion |

#### Example

```markdown
# Orchestrator Phase 3 correlation detection (pseudocode)

# 1. Group findings by target component
groups = findings.group_by(component)

# 2. For each component group, check cross-category pairs against 5 rules
for component, component_findings in groups:
    stride_findings = [f for f in component_findings if f.category in STRIDE]
    ai_findings = [f for f in component_findings if f.category in AI]

    matched = []
    for sf in stride_findings:
        for af in ai_findings:
            if (sf.category, af.category) matches any CR-1..CR-5:
                matched.append((sf, af))

    # 3. If matches found, create one correlation group per component
    if matched:
        CG-N = CorrelationGroup(
            findings=flatten(matched),
            risk_level=max(risk_level for f in flatten(matched)),
            component=component
        )

# 4. Self-check: no finding in more than one group
```

Output in Section 4a:

```markdown
## 4a. Correlated Findings

| Group | Findings | Component | Threat Summary | Risk Level |
|-------|----------|-----------|----------------|------------|
| CG-1  | T-2, LLM-1 | LLM Agent Pipeline | Tampering: data corruption; Data-Poisoning: training data manipulation | High |
```

Coverage matrix uses deduplicated counts (CG-1 members count as 1 per cell). Three-state cell model: integer (deduplicated count), "---" (analyzed-but-clean), "n/a" (not-applicable).

#### When to Use
- Multi-agent threat analysis where different agents analyze the same components through different lenses
- When inflated finding counts from overlapping agent perspectives reduce output credibility
- When downstream consumers (coverage matrix, risk summary) need accurate distinct threat counts

#### When NOT to Use
- Single-agent analysis (no cross-agent overlap possible)
- When finding overlap is acceptable and deduplication would obscure important perspectives
- When findings target different components (correlation requires same-component matching)

#### Related Patterns
- [STRIDE-per-Element Matrix Targeting](#pattern-stride-per-element-matrix-targeting) -- the dispatch mechanism that produces the findings being correlated
- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation) -- correlation rules are embedded in the orchestrator prompt, not loaded from external files

---

### Pattern: Heuristic A Enrichment Branch

**Added**: Feature 219 (F-3 single-agent execution); Feature 229 (F-5 two-agent execution); Feature 232 (F-6 three-agent execution); Feature 237 (F-7 four-or-five-agent execution); Feature 241 (F-241 11-host saturation execution — final BLP-01 closure)
**ADRs**: [ADR-032](../02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md) (single-agent precedent); [ADR-034](../02_ADRs/ADR-034-llm10-unbounded-consumption-audit.md) (two-agent precedent); [ADR-035](../02_ADRs/ADR-035-ml-top-10-coverage-bundle.md) (three-agent precedent); [ADR-036](../02_ADRs/ADR-036-mobile-top-10-coverage-bundle.md) (four-or-five-agent precedent); [ADR-037](../02_ADRs/ADR-037-web-api-coverage-attestation-and-populator-wiring.md) (11-host saturation closure)

#### Problem

When new threat-modeling coverage requirements arrive — e.g., adding a new OWASP framework family entry — the naive response is to author a new threat-detection agent file. At BLP-01 plan time, with 10 framework entries to close (LLM Top 10 + Agentic Top 10 + ML Top 10 + Mobile Top 10 + Web/API combined Top 10) and 11 existing detection-tier hosts, naive new-agent-per-entry growth would have spawned 50+ new agent files, exploding the agent inventory and proliferating bespoke pattern-catalog directories. Each new agent carries fixed costs: ~120 lines of agent file + ~400 lines of companion skill + schema bump + consumers-list edit + orchestrator/dispatch edit. The ADR-023 zero-edit invariant on existing detection agents would have shattered under naive growth.

The orthogonal problem: when a new framework entry's signal-class boundary aligns with an existing host agent's threat semantics, authoring a new agent creates vocabulary collision and inconsistent classification at the dispatch tier (which agent emits the finding when both could?).

#### Solution

The **Heuristic A enrichment branch** extends an existing detection-tier host agent (rather than authoring a new sibling agent) when the new framework entry's signal-class boundary aligns with the host's existing threat semantics. Pattern characteristics:

1. **Signal-class boundary alignment test**: New framework entry's vocabulary / CWE-mapping / mitigation-taxonomy is a vocabulary-disjoint extension of (not overlap with) an existing host's signal class. If alignment holds, enrich the host. If alignment fails, author a new agent (the standalone branch — F-1 / F-2 / F-4).
2. **Additive-only edits per ADR-023 Decision 3**: Three host-agent anchor points (metadata `owasp_references`, `## Purpose` extension, Detection Workflow Step 5 references list) + N new Pattern Categories appended to companion `detection-patterns.md` + Pattern Category Disambiguation subsection clarifying boundary against pre-existing categories. **Categories pre-existing on the host stay byte-identical** to the pre-enrichment baseline (SC-006 BLOCKER per F-3 precedent).
3. **5/5-dimension reduction vs new agent**: Zero new agent files / Zero new skill directories / Zero schema bumps (reuses host's existing finding-ID prefix family) / Zero consumers-list edits / Zero functional orchestrator/dispatch edits.
4. **Per-host edit cost stays linear with fan-out scope**: F-3 enriched 1 host (1x cost); F-5 enriched 2 hosts (2x cost); F-6 enriched 3 hosts (3x cost); F-7 enriched 5 hosts (5x cost); F-241 enriched 11 hosts (11x cost). The reduction holds at every scope through 11-host saturation.
5. **Saturation point**: At 11/11 detection-tier hosts populating `source_attribution`, the pattern reaches saturation — no further fan-out is possible within the current detection-tier surface. Future growth occurs at the cross-framework attribution tier (BLP-02 envelope) or the asymmetric-pattern application tier rather than within the detection-tier surface.

The pattern is governed by the cumulative ADR-032 → ADR-034 → ADR-035 → ADR-036 → ADR-037 lineage (one ADR per execution), each citing the previous as direct precedent and forecasting the next scope tier. ADR-037 caps the lineage at 11-host scope and closes the four-feature F-A3 deferral lineage.

#### Five-Execution Empirical Cost Reduction Table

| Dimension                              | F-3 (1) | F-5 (2) | F-6 (3) | F-7 (5) | F-241 (11) | Cost saved (vs new agents)            |
|----------------------------------------|:-------:|:-------:|:-------:|:-------:|:----------:|---------------------------------------|
| New agent file                         |    0    |    0    |    0    |    0    |     0      | ~120 lines × 11 = ~1320 lines saved   |
| New skill directory                    |    0    |    0    |    0    |    0    |     0      | ~400 lines × 11 = ~4400 lines saved   |
| Schema bump (`finding.yaml`)           |  none   |  none   |  none   |  none   |   none     | ADR + schema review cycle eliminated  |
| Consumers-list edit                    |  none   |  none   |  none   |  none   |   none     | ADR-023 invariant proof scope shrinks |
| Functional orchestrator/dispatch edit  |  none   |  none   |  none   |  none   |   none     | Orchestrator regression risk eliminated |

#### Cross-Agent Decomposition Sub-Pattern

A complementary sub-pattern emerged across F-5 / F-6 / F-7: **single OWASP framework entry decomposes across two host agents along a non-trivial axis**. Three executions in BLP-01:

| Feature | OWASP Entry | Decomposition Axis | Host A | Host B |
|---------|-------------|--------------------|--------|--------|
| F-5     | LLM10:2025 Unbounded Consumption | Q1 SPLIT vector axis | DoS Cat 13 (latency) | model-theft Cat 11 (cost) |
| F-6     | ML06 AI Supply Chain | Two-facet axis (corpus-side vs artifact-side) | data-poisoning Cat 10 (corpus) | model-theft Cat 14 (artifact) |
| F-7     | Mobile M8 Security Misconfiguration | Architectural-tell axis (privilege-gain vs accountability-loss) | privilege-escalation host (privilege gain) | repudiation host (accountability loss) |

Disjoint architectural-tells / vocabularies / mitigation-taxonomies prevent duplicate emission on architectures that surface both halves of the decomposed entry. The sub-pattern is documented at the ADR layer only — no schema-tier impact.

#### When to Use

- New framework-entry coverage requirement that aligns with an existing detection-tier host's signal class
- When the alternative (authoring a new sibling agent) would carry vocabulary collision risk at the dispatch tier
- When the additive-only edit invariant per ADR-023 can be preserved (Categories pre-existing on the host stay byte-identical)
- When the host's existing finding-ID prefix family can absorb the new entry without bumping `schemas/finding.yaml::id.pattern`

#### When NOT to Use

- New framework entry's vocabulary / CWE-mapping / mitigation-taxonomy is **vocabulary-disjoint** from the host's existing signal class — author a new sibling agent under the standalone branch (F-1 / F-2 / F-4 precedent)
- When extending the host would expand the line cap beyond the FR-014 hard cap (≤200 lines per agent file at the F-241 enrichment surface; ≤180 lines pre-F-241)
- When the new entry's DFD-targets do not align with the host's `dfd_targets` field — DFD targeting is structural, not extensible via enrichment

#### Saturation Implications for Post-BLP-01 Future Work

After F-241, the detection-tier surface is **saturated at 11 hosts** populating `source_attribution`. F-9+ candidates that introduce new framework entries should:

1. **Score against the 5/5-dimension reduction checklist at SDR time** to determine whether enrichment-branch eligibility holds
2. **Default to the enrichment branch** when signal-class alignment holds; default to the standalone branch otherwise
3. **Cap line growth per host** at FR-014 (≤200 lines for enrichment surface; ≤180 lines pre-enrichment)
4. **Use the surgical Section 9-only backfill approach (ADR-037 D-11)** when the only baseline-impacting change is at the Coverage Attestation YAML level — reduces wall-clock cost ~60% on multi-baseline scope vs full pipeline regen

#### Related Patterns
- [STRIDE-per-Element Matrix Targeting](#pattern-stride-per-element-matrix-targeting) — the dispatch mechanism that determines which host agent receives the new framework-entry pattern category
- [On-Demand Reference File Segmentation](#pattern-on-demand-reference-file-segmentation) — pattern catalogs live in companion `detection-patterns.md` files loaded on-demand at detection start (single `**MANDATORY**: Read` directive per ADR-023)

---

### Pattern: Shared Parser Module Extraction

**Added**: Feature 071 (Deterministic Infographic Extraction)
**ADR**: [ADR-017](../02_ADRs/ADR-017-deterministic-infographic-extraction.md)

#### Problem
Multiple scripts need to parse the same markdown artifacts (threats.md, risk-scores.md, compensating-controls.md) but were developed at different times. Feature 067 introduced `extract-report-data.py` with inline parsing logic. Feature 071 needed the same parsers for infographic data extraction. Duplicating ~750 lines of parsing code across scripts creates divergence risk where the same source artifact could be interpreted differently by different pipelines.

#### Solution
Extract shared parsing functions into a dedicated module (`tachi_parsers.py`) that both scripts import. The module provides all artifact-specific parsers (markdown tables, YAML frontmatter, severity distributions, findings, scope data, compensating controls) and shared constants (severity ordering, STRIDE prefix mapping, exit codes). Each consuming script imports only the functions it needs and adds its own output-format-specific logic (Typst for reports, JSON for infographics).

#### Example
```python
# scripts/tachi_parsers.py — shared module
SEVERITY_ORDER = ["Critical", "High", "Medium", "Low", "Note"]

def parse_markdown_table(text, header_pattern):
    """Parse a markdown table following a header matching the pattern."""
    ...

def parse_threats_severity(threats_content):
    """Extract severity distribution from threats.md Section 6."""
    ...

# scripts/extract-report-data.py — report consumer
from tachi_parsers import parse_threats_severity, parse_frontmatter, SEVERITY_ORDER

# scripts/extract-infographic-data.py — infographic consumer
from tachi_parsers import parse_threats_severity, parse_frontmatter, SEVERITY_ORDER
```

The `sys.path` insertion ensures the module is importable regardless of the working directory:
```python
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tachi_parsers import parse_markdown_table, parse_frontmatter
```

#### When to Use
- Two or more scripts parse the same file formats or data structures
- Parsing correctness is critical (security artifacts, audit data) and must be identical across consumers
- Scripts share the same zero-dependency constraint (stdlib only)

#### When NOT to Use
- A single script consumes the parsing logic (no duplication to eliminate)
- Parsers are trivial (one or two regexes) and not worth the module overhead
- Different consumers intentionally need different interpretations of the same data

#### Related Patterns
- [Atomic File Write](#pattern-atomic-file-write) -- both patterns prioritize determinism and correctness in file operations

---

### Pattern: Largest Remainder Method for Deterministic Percentages

**Added**: Feature 071 (Deterministic Infographic Extraction)
**ADR**: [ADR-017](../02_ADRs/ADR-017-deterministic-infographic-extraction.md)

#### Problem
Converting raw counts to integer percentages using simple `round()` can produce values that do not sum to exactly 100. For example, three items with counts [1, 1, 1] produce exact percentages [33.33, 33.33, 33.33], and rounding each independently gives [33, 33, 33] = 99. In infographic visualizations (pie charts, severity distributions), percentages that do not sum to 100 create visual inconsistencies and undermine credibility with executive audiences.

#### Solution
Use the Largest Remainder Method (Hamilton method): compute exact percentages, take the floor of each, then distribute the remaining units (target minus sum of floors) to items with the largest fractional remainders. Break ties deterministically using lexicographic label order.

#### Example
```python
def largest_remainder(percentages_map, target=100):
    """Integer percentages summing to exactly `target`."""
    total = sum(percentages_map.values())
    if total == 0:
        return {label: 0 for label in percentages_map}

    exact = {label: (count / total) * target
             for label, count in percentages_map.items()}
    floored = {label: math.floor(v) for label, v in exact.items()}
    remainder = target - sum(floored.values())

    # Sort by fractional remainder descending, then label ascending for ties
    by_remainder = sorted(
        exact.keys(),
        key=lambda k: (-(exact[k] - floored[k]), k)
    )

    for i in range(remainder):
        floored[by_remainder[i]] += 1

    return floored
```

Input: `{"Critical": 5, "High": 14, "Medium": 10, "Low": 4, "Note": 1}` (total=34)
Output: `{"Critical": 15, "High": 41, "Medium": 29, "Low": 12, "Note": 3}` (sum=100)

#### When to Use
- Displaying integer percentages in charts, dashboards, or specifications where the total must be exact
- Any scenario where multiple rounded values must sum to a fixed target
- When determinism is required (same input must always produce the same output)

#### When NOT to Use
- Floating-point percentages are acceptable (no rounding needed)
- A single percentage value (no summation constraint)
- When the rounding method must match a specific regulatory or accounting standard (verify which method is required)

#### Related Patterns
- [Shared Parser Module Extraction](#pattern-shared-parser-module-extraction) -- the Largest Remainder Method is implemented in the infographic extraction script that imports from the shared module

---

## Pattern Template

```markdown
# Pattern: [Pattern Name]

## Problem
[What problem does this pattern solve?]

## Solution
[How does the pattern solve it?]

## Example
```[language]
[Code example]
```

## When to Use
- [Scenario 1]
- [Scenario 2]

## When NOT to Use
- [Anti-pattern scenario]

## Related Patterns
- [Link to related patterns]
```

---

**Template Instructions**: Create pattern documents as you establish conventions. Organize by category (api-patterns/, db-patterns/, etc.).
