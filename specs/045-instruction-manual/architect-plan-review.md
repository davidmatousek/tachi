# Architect Plan Review: 045 -- End-to-End tachi Instruction Manual

**Reviewer**: Architect Agent
**Date**: 2026-03-28
**Artifact**: `specs/045-instruction-manual/plan.md`
**Spec Reference**: `specs/045-instruction-manual/spec.md`
**Status**: APPROVED_WITH_CONCERNS

---

## Review Summary

The plan is technically sound for a documentation-only deliverable. Phase sequencing is correct, the per-command section template is well-structured, and the overall approach of targeted insertion over full regeneration is appropriate. Three concerns are documented below -- one medium, two low. None are blocking.

---

## Findings

### Finding 1 (MEDIUM): Agent count correction is inaccurate -- should be 16, not 15

**Location**: plan.md line 108, spec.md FR-005

The plan states the agent count should be corrected from 14 to 15. Actual count of `.md` files in `.claude/agents/tachi/` is **16**:

```
agent-autonomy.md, control-analyzer.md, data-poisoning.md,
denial-of-service.md, info-disclosure.md, model-theft.md,
orchestrator.md, privilege-escalation.md, prompt-injection.md,
repudiation.md, risk-scorer.md, spoofing.md, tampering.md,
threat-infographic.md, threat-report.md, tool-abuse.md
```

The existing GUIDE_PROMPT.md says "14 agent files" (line 243) and "copy 14 agent files" (line 292). The plan proposes correcting to 15, citing "risk-scorer agent added in Feature 035." However, Feature 036 added `control-analyzer.md` and Feature 039 added `threat-infographic.md` as well. The orchestrator (`orchestrator.md`) is also present.

**Recommendation**: During implementation, count the actual agent files at time of writing and use the correct number. The plan should note the count may need to be verified at implementation time rather than hardcoding a specific number. If the original GUIDE_PROMPT.md was written when there were 14 agents (10 STRIDE + 2 AG + 2 LLM), the current count is 16 (those 14 + risk-scorer + control-analyzer), with orchestrator and threat-infographic bringing the total to 16 (or 14 threat-specific + orchestrator + risk-scorer + control-analyzer + threat-infographic + threat-report = 16 md files total, excluding the templates directory).

**Impact**: If left uncorrected, the guide will undercount agents, and users who verify after installation will see a mismatch. Low user impact since it does not affect functionality, but it undermines trust in documentation accuracy.

---

### Finding 2 (LOW): Data flow diagram shows a linear 4-command chain but /infographic does not consume /compensating-controls output

**Location**: plan.md lines 182-207, Data Flow section

The data flow diagram presents a strictly linear pipeline:

```
/threat-model -> /risk-score -> /compensating-controls -> /infographic
```

This suggests `/infographic` consumes the output of `/compensating-controls`. However, verification of the actual infographic command (`adapters/claude-code/commands/infographic.md` and `.claude/commands/infographic.md`) shows:

- `/infographic` auto-detects `risk-scores.md` (preferred) or `threats.md` (fallback)
- `/infographic` has zero references to `compensating-controls.md` or `compensating-controls.sarif`
- The infographic agent (`threat-infographic.md`) declares only two data source types: `threats` and `risk-scores`

The actual pipeline topology is:

```
/threat-model -> /risk-score -> /compensating-controls
                      |
                      +-------> /infographic
```

That is, `/infographic` branches from `/risk-score` output, not from `/compensating-controls` output. Both `/compensating-controls` and `/infographic` independently consume `/risk-score` output.

**Why this matters for the plan**: The plan will guide the developer guide content. The data flow diagram in the plan will likely be reproduced (or closely adapted) in both the prompt specification and the developer guide. If the linear chain is documented as-is, users will incorrectly believe they must run `/compensating-controls` before `/infographic`, and may expect infographic output to reflect compensating controls analysis (residual risk, control coverage).

**Recommendation**: Update the data flow diagram to show the fork after `/risk-score`. The narrative can still present the commands in the order `/threat-model` -> `/risk-score` -> `/compensating-controls` -> `/infographic` (as a recommended sequence), but the diagram should accurately show that `/infographic` reads from `/risk-score` output, not `/compensating-controls` output. A note explaining that `/infographic` and `/compensating-controls` are independently consumable enrichment steps would be accurate.

**Note**: The spec itself (User Story 1, acceptance scenario 1) lists all 4 commands but does not prescribe a strict linear dependency -- the plan introduced the linear data flow diagram. This is a plan-level concern, not a spec deviation.

---

### Finding 3 (LOW): /infographic invocation syntax uses [data_source] positional but actual command uses explicit file path

**Location**: plan.md line 98

The plan describes the invocation as:
```
/infographic [data_source] [--template value] [--output-dir path]
```

The actual command file shows the positional argument is described as "the explicit data source path" (line 34-35 of infographic.md), meaning it accepts a file path (e.g., `path/to/risk-scores.md`) not a generic "data source" label.

This is a minor naming inconsistency. The usage examples in the actual command (lines 193-208) show:
```
/infographic path/to/risk-scores.md
/infographic path/to/threats.md
```

**Recommendation**: When writing the guide, use `[file_path]` or `[path/to/data-source]` rather than `[data_source]` to make it clear the positional argument is a file path, consistent with the actual command behavior and usage examples.

---

## Technical Accuracy Verification

### Command Invocation Syntax

| Command | Plan Claims | Actual (from command files) | Verdict |
|---------|------------|----------------------------|---------|
| `/risk-score` | `[input_dir] [--output-dir path]` | Positional = input directory, `--output-dir` flag | ACCURATE |
| `/compensating-controls` | `[input_dir] [--target path] [--output-dir path]` | Positional = input directory, `--target` flag, `--output-dir` flag | ACCURATE |
| `/infographic` | `[data_source] [--template value] [--output-dir path]` | Positional = explicit data source path, `--template` flag, `--output-dir` flag | MINOR -- see Finding 3 |

### Input/Output Specifications

| Claim | Actual | Verdict |
|-------|--------|---------|
| `/risk-score` input: threats.md (primary), threats.sarif (fallback) | Correct per command file Step 1.2-1.3 | ACCURATE |
| `/risk-score` output: risk-scores.md, risk-scores.sarif | Correct per command file output suite | ACCURATE |
| `/risk-score` scoring: CVSS, exploitability, scalability, reachability | Correct per command file quality checklist | ACCURATE |
| `/compensating-controls` input: risk-scores.md (primary), risk-scores.sarif (fallback) | Correct per command file Step 1.2-1.3 | ACCURATE |
| `/compensating-controls` output: compensating-controls.md, compensating-controls.sarif | Correct per command file output suite | ACCURATE |
| `/compensating-controls` classification: Control Found / Partial Control / No Control Found | Correct per command file quality checklist | ACCURATE |
| `/compensating-controls` residual risk: Inherent x (1 - Factor) | Correct per command file quality checklist line 192 | ACCURATE |
| `/infographic` templates: baseball-card, system-architecture, all | Correct per command file Step 0 and agent metadata | ACCURATE |
| `/infographic` alias: corporate-white -> baseball-card | Correct per command file Step 0 and agent metadata | ACCURATE |
| `/infographic` auto-detection: prefers risk-scores.md over threats.md | Correct per command file Step 1.2 | ACCURATE |
| `/infographic` co-located dependency: threats.md required with risk-scores.md | Correct per command file Step 1.3 | ACCURATE |
| `/infographic` output: threat-{template}-spec.md + threat-{template}.jpg | Correct per command file output suite | ACCURATE |

### Template Names

| Claim | Actual (filesystem) | Verdict |
|-------|---------------------|---------|
| `infographic-baseball-card.md` | `templates/infographic-baseball-card.md` | ACCURATE |
| `infographic-system-architecture.md` | `templates/infographic-system-architecture.md` | ACCURATE |

### File Paths and Naming Conventions

| Path in Plan | Exists on Filesystem | Verdict |
|-------------|---------------------|---------|
| `docs/guides/prompts/GUIDE_PROMPT.md` | Yes | ACCURATE |
| `docs/guides/DEVELOPER_GUIDE_TACHI.md` | Yes | ACCURATE |
| `.claude/commands/compensating-controls.md` | Yes | ACCURATE |
| `adapters/claude-code/commands/risk-score.md` | Yes | ACCURATE |
| `adapters/claude-code/commands/infographic.md` | Yes | ACCURATE |
| Proposed rename target: `developer-guide-prompt.md` | Kebab-case, consistent with project conventions | SOUND |

### Phase Sequencing

| Dependency | Valid | Notes |
|-----------|-------|-------|
| Phase 1 (prompt spec) before Phase 3 (guide) | Yes | Spec is source of truth; guide draws from it |
| Phase 2 (rename) after Phase 1 content update | Yes | Avoids editing a file mid-rename |
| Phase 4 (validation) after Phases 1-3 | Yes | Cross-references require all content to exist |
| No circular dependencies | Confirmed | Strictly linear Phase 1 -> 2 -> 3 -> 4 |

### Architecture Compliance

- Documentation-only deliverable: no code changes, no agent changes, no command changes -- **confirmed**
- No runtime dependencies -- **confirmed**
- No security surface changes -- **confirmed**
- Constitution check passes all applicable principles -- **confirmed**

---

## Per-Command Section Template Assessment

The proposed template structure (What It Does, Prerequisites, Running the Command, Understanding the Output, Scoring/Analysis Details, What to Do Next) is well-designed:

- Mirrors the actual command flow (validate prerequisites -> run -> interpret output -> next step)
- "Running the Command" with copy-pasteable blocks satisfies FR-014
- "What to Do Next" creates natural pipeline flow between sections
- Template is flexible enough to accommodate command-specific differences (e.g., /infographic has template selection, /compensating-controls has target codebase)

No concerns with the template design.

---

## Disposition

**STATUS: APPROVED_WITH_CONCERNS**

| # | Severity | Finding | Recommendation |
|---|----------|---------|----------------|
| 1 | MEDIUM | Agent count should be 16, not 15 | Verify actual count at implementation time |
| 2 | LOW | Data flow diagram implies linear chain; /infographic forks from /risk-score, not /compensating-controls | Update diagram to show fork topology |
| 3 | LOW | /infographic positional arg is a file path, not generic "data source" | Use [file_path] in guide invocation syntax |

All three findings are addressable during implementation without plan restructuring. The plan does not need to be regenerated -- the implementation team should be aware of these corrections when writing the actual documentation content.
