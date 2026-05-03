<!--
File: EVAL_CONVENTIONS.md
Description: Comprehensive conventions guide for skill eval suites — file structure, schema, authoring patterns, execution, and grading interpretation
Author/Agent: architect
Created: 2026-03-07
Last Updated: 2026-03-07
-->

# Eval Suite Conventions

This document defines the conventions for authoring, running, and maintaining eval suites for Claude Code skills. It is the authoritative reference for all eval-related work in this project and for template adopters creating custom eval suites.

**Audience**: Template maintainers and adopters who author, run, or interpret skill evals.

**Scope**: Phase 1 covers 3 skills (`~aod-spec`, `~aod-build`, `security`). Conventions apply to all current and future eval suites.

---

## Table of Contents

1. [File Structure](#1-file-structure)
2. [evals.json Schema](#2-evalsjson-schema)
3. [Expectation Authoring Patterns](#3-expectation-authoring-patterns)
4. [Severity Levels](#4-severity-levels)
5. [Pass Threshold Configuration](#5-pass-threshold-configuration)
6. [How to Run Evals](#6-how-to-run-evals)
7. [How to Interpret Grading Results](#7-how-to-interpret-grading-results)
8. [Schema Policy](#8-schema-policy)
9. [Eval Maintenance Guidance](#9-eval-maintenance-guidance)
10. [Creating Custom Eval Suites](#10-creating-custom-eval-suites)
11. [Version Comparison with Comparator](#11-version-comparison-with-comparator)

---

## 1. File Structure

Eval suites are **co-located** with the skill they test. Every skill that has evals contains an `evals/` subdirectory with exactly two files.

### Directory Layout

```
.claude/skills/{skill-name}/
├── SKILL.md                    # Skill definition (unchanged by evals)
├── [existing files...]         # Other skill assets (unchanged)
└── evals/                      # Eval suite directory
    ├── evals.json              # Eval suite definition
    └── README.md               # What this eval covers, how to run, how to interpret
```

Eval results are written to a separate, gitignored directory at the repository root:

```
_eval-results/                  # Gitignored — never committed
└── {skill-name}/
    ├── transcript.md           # Executor output (raw skill responses)
    ├── grading.json            # Grader verdicts (per-expectation PASS/FAIL)
    ├── comparison.json         # Comparator scores (if version comparison was run)
    └── analysis.json           # Analyzer suggestions (if analysis was run)
```

### Co-location Rules

| Rule | Rationale |
|------|-----------|
| `evals/` lives inside the skill directory | Evals travel with the skill — renaming, moving, or deleting a skill naturally includes its evals |
| `evals.json` is the only eval definition file | Single source of truth per skill; no split or partial definitions |
| `README.md` is required alongside `evals.json` | Documents coverage, usage, and interpretation for human readers |
| `_eval-results/` is always gitignored | Eval outputs are non-deterministic LLM responses; committing them would bloat git history with noise |
| The `evals/` directory must not interfere with `SKILL.md` loading | Skills must load and execute identically with or without an `evals/` directory present (FR-016) |

### .gitignore Entry

The repository `.gitignore` must contain:

```
# Eval results (non-deterministic LLM output)
_eval-results/
```

---

## 2. evals.json Schema

Each `evals.json` file defines a single eval suite targeting one skill. The formal JSON Schema is located at `specs/083-skill-eval-suites/contracts/evals-json-schema.json`.

### Top-Level Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | Yes | — | Human-readable suite name. Max 128 characters. Example: `"aod-spec eval suite"` |
| `version` | string | Yes | — | Semantic version of the eval suite. Must match `^\d+\.\d+\.\d+$`. Example: `"1.0.0"` |
| `skill` | string | Yes | — | Target skill name. Must match the parent directory name. Example: `"~aod-spec"` |
| `pass_threshold` | number | Yes | `0.8` | Minimum pass rate (0.0-1.0) for the suite to receive an overall PASS. See [Pass Threshold Configuration](#5-pass-threshold-configuration). |
| `evals` | array | Yes | — | Array of eval pairs (prompt/expectation test cases). Minimum 1 item per schema; Phase 1 convention is 3-5 items. |

### Eval Pair Fields

Each item in the `evals` array represents a single test case.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier within the suite. Lowercase alphanumeric and hyphens only (`^[a-z0-9-]+$`). Example: `"spec-happy-path-01"` |
| `prompt` | string | Yes | Self-contained prompt to execute against the skill. Must embed all necessary context — no external project state dependencies (FR-015). |
| `expectations` | array of strings | Yes | Plain-language assertions for the Grader to evaluate against skill output. Minimum 1 expectation per pair. |
| `context` | string | No | Prerequisite state description for the Executor. Describes what environment or project state the eval assumes. |
| `tags` | array of strings | No | Categorization labels. Allowed values: `"happy-path"`, `"edge-case"`, `"failure-mode"`. |
| `severity` | string | No | Weighting hint for grader results. Allowed values: `"critical"`, `"major"`, `"minor"`. See [Severity Levels](#4-severity-levels). |

### Complete Example

```json
{
  "name": "aod-spec eval suite",
  "version": "1.0.0",
  "skill": "~aod-spec",
  "pass_threshold": 0.8,
  "evals": [
    {
      "id": "spec-happy-path-01",
      "prompt": "Generate a feature specification for a user authentication system. The PRD requires email/password login, OAuth2 support, and session management. The feature branch is 042-user-auth. Include all mandatory sections from the spec template.",
      "expectations": [
        "Output contains a '## Requirements' section with functional requirements listed",
        "Output contains a '## User Scenarios & Testing' section with at least one acceptance scenario",
        "Output references the feature branch '042-user-auth'",
        "Output includes a '## Success Criteria' section with measurable outcomes"
      ],
      "tags": ["happy-path"],
      "severity": "critical"
    },
    {
      "id": "spec-edge-ambiguous-reqs",
      "prompt": "Generate a feature specification for 'improve the dashboard'. No PRD exists. Requirements are vague and incomplete.",
      "expectations": [
        "Output flags the missing PRD reference or requests one",
        "Output includes clarification markers or questions for ambiguous requirements",
        "Output does not fabricate specific requirements that were not provided"
      ],
      "tags": ["edge-case"],
      "severity": "major"
    },
    {
      "id": "spec-failure-missing-prd",
      "prompt": "Generate a feature specification. The PRD file at docs/product/02_PRD/999-nonexistent.md does not exist.",
      "expectations": [
        "Output indicates the PRD reference could not be found or is missing",
        "Output does not produce a full specification without a valid PRD"
      ],
      "context": "No PRD file exists at the referenced path. The skill should handle this gracefully.",
      "tags": ["failure-mode"],
      "severity": "critical"
    }
  ]
}
```

### ID Naming Convention

Use a consistent pattern for eval pair IDs:

```
{skill-short-name}-{tag}-{sequence}
```

Examples:
- `spec-happy-path-01` — first happy-path eval for the spec skill
- `build-edge-case-02` — second edge-case eval for the build skill
- `security-failure-mode-01` — first failure-mode eval for the security skill

---

## 3. Expectation Authoring Patterns

Expectations are plain-language strings that the Grader agent evaluates against skill output. The Grader determines whether the skill output satisfies each expectation, producing a PASS or FAIL verdict with evidence.

### Core Principle: Structural Assertions Over Exact Matching

Because LLM output is non-deterministic, expectations must describe **what** the output should contain or accomplish, not the **exact text** it should produce.

### DO: Structural and Behavioral Assertions

These patterns work reliably across non-deterministic LLM outputs.

```
"Output contains a '## Requirements' section"
"Output lists at least 3 functional requirements"
"Output includes a table with columns for Field, Type, and Description"
"Output references the feature branch name provided in the prompt"
"Output produces a PASS/FAIL summary with counts"
"Output flags the missing prerequisite file"
"Output does not fabricate requirements that were not in the prompt"
"Each requirement has a unique identifier (e.g., FR-001, FR-002)"
"Output includes both happy-path and edge-case scenarios"
"Error message identifies which file or resource is missing"
```

### DON'T: Exact String Matching

These patterns are brittle and will produce false failures due to normal LLM variation.

```
"Output starts with '# Feature Specification: User Authentication'"
"The third line of output is '**Feature Branch**: `042-user-auth`'"
"Output contains exactly the text 'FR-001: The system SHALL...'"
"Output is exactly 47 lines long"
"The summary table has exactly 5 rows"
"Output matches the expected template character-for-character"
```

### Pattern Categories

#### Happy-Path Expectations

Verify that the skill produces correct, complete output for well-formed input.

```json
{
  "tags": ["happy-path"],
  "expectations": [
    "Output contains all mandatory sections: Requirements, User Scenarios, Success Criteria",
    "Output includes a triad sign-off block with PM, Architect, and Team-Lead fields",
    "Functional requirements are numbered sequentially (FR-001, FR-002, etc.)",
    "At least one acceptance scenario uses Given/When/Then format"
  ]
}
```

#### Edge-Case Expectations

Verify that the skill handles unusual, boundary, or ambiguous inputs gracefully.

```json
{
  "tags": ["edge-case"],
  "expectations": [
    "Output includes clarification markers for ambiguous requirements",
    "Output handles the empty input by requesting necessary information",
    "Output correctly processes input with special characters without corruption",
    "Output distinguishes between missing optional and missing required fields"
  ]
}
```

#### Failure-Mode Expectations

Verify that the skill fails gracefully with clear, actionable error information.

```json
{
  "tags": ["failure-mode"],
  "expectations": [
    "Output indicates the referenced file could not be found",
    "Output does not produce a full result when critical prerequisites are missing",
    "Error message is specific enough to identify the root cause",
    "Output does not crash, hang, or produce garbled output"
  ]
}
```

### Expectation Writing Checklist

When authoring expectations for a new eval pair, verify:

- [ ] Each expectation describes a **structural** or **behavioral** property, not exact text
- [ ] Expectations are **independently evaluable** — one failing does not invalidate others
- [ ] The set covers the **critical outputs** of the skill for this scenario
- [ ] Negative assertions ("does not fabricate", "does not crash") are included where failure would be harmful
- [ ] Expectations are **specific enough** for the Grader to produce a clear PASS or FAIL verdict with evidence

---

## 4. Severity Levels

The `severity` field on an eval pair indicates how important that test case is to the overall quality assessment. Severity is a hint for human interpretation and future weighted grading (Phase 2+).

### Levels

| Severity | Description | When to Use | Examples |
|----------|-------------|-------------|----------|
| `critical` | Core functionality that must work for the skill to be useful | Happy-path tests of primary skill behavior; failure modes that could cause data loss or corruption | Spec generates required sections; security scan detects known vulnerabilities |
| `major` | Important behavior that significantly affects quality | Edge cases that real users will encounter; secondary features | Ambiguous input handling; multi-phase checkpoint tracking |
| `minor` | Nice-to-have behavior; polish and completeness | Formatting details; optional feature coverage; cosmetic output quality | Output includes helpful hints; section ordering matches template |

### Phase 1 Behavior

In Phase 1, severity is **advisory only**. All expectations are weighted equally in the pass rate calculation. The severity field serves two purposes:

1. **Human prioritization** — When reviewing failures, address `critical` failures first
2. **Future weighting** — Phase 2+ may implement weighted scoring where `critical` failures count more heavily

### Assignment Guidelines

- Every eval suite should have at least one `critical` eval pair
- Happy-path evals testing core behavior should generally be `critical`
- Edge-case evals are typically `major`
- Failure-mode evals vary: graceful degradation of core features is `critical`, handling of unlikely scenarios is `minor`
- When uncertain, default to `major`

---

## 5. Pass Threshold Configuration

The `pass_threshold` field determines whether an eval suite receives an overall PASS or FAIL status.

### How It Works

```
pass_rate = total_passing_expectations / total_expectations
overall_status = PASS if pass_rate >= pass_threshold else FAIL
```

### Scale

| Value | Meaning | Use Case |
|-------|---------|----------|
| `1.0` | Every expectation must pass | Strict — use for safety-critical skills where any failure is unacceptable |
| `0.8` | 80% of expectations must pass (default) | Standard — accommodates acceptable LLM variance while catching real regressions |
| `0.6` | 60% of expectations must pass | Lenient — use for experimental or rapidly-evolving skills |
| `0.0` | Suite always passes | Disabled — use only for information gathering, not quality gating |

### Default: 0.8

The default threshold of 0.8 means that for a suite with 5 expectations, 4 must pass. This was chosen because:

- It catches genuine regressions (a broken skill will fail multiple expectations)
- It tolerates single-expectation variance from LLM non-determinism
- It aligns with the reproducibility target: same PASS/FAIL status in 4 of 5 consecutive runs (SC-002)

### When to Adjust

| Scenario | Recommended Threshold |
|----------|-----------------------|
| Newly created eval suite (still tuning expectations) | `0.6` |
| Stable skill with well-tested expectations | `0.8` (default) |
| Security or governance skill where failures have consequences | `0.9` or `1.0` |
| Exploratory evals during skill development | `0.0` to `0.6` |

### Calculation Example

Given an eval suite with 4 eval pairs and 12 total expectations across all pairs:

```
Total expectations: 12
Passing expectations: 10
Failing expectations: 2
Pass rate: 10 / 12 = 0.833

Threshold: 0.8
Overall status: PASS (0.833 >= 0.8)
```

---

## 6. How to Run Evals

Eval suites are executed using Anthropic's skill-creator eval pipeline, which orchestrates Executor and Grader sub-agents.

### Prerequisites

- Claude Code agent environment
- Access to Anthropic's skill-creator eval pipeline
- The target skill must exist in `.claude/skills/{skill-name}/` with a valid `SKILL.md`
- An `evals/evals.json` file must exist for the target skill

### Step-by-Step Execution

#### Step 1: Verify the Eval Suite

Confirm the eval suite file exists and is valid JSON:

```bash
cat .claude/skills/{skill-name}/evals/evals.json | python3 -m json.tool
```

If this produces a parse error, fix the JSON syntax before proceeding.

#### Step 2: Run the Eval Suite

Use Anthropic's skill-creator to execute the eval suite. The pipeline operates in two phases:

1. **Executor Phase**: The Executor agent runs each prompt from `evals.json` against the target skill in an independent context. Each prompt is executed in isolation — no shared state between eval pairs.

2. **Grader Phase**: The Grader agent evaluates each expectation against the Executor's output, producing PASS/FAIL verdicts with evidence citations.

Results are written to `_eval-results/{skill-name}/`.

#### Step 3: Review Results

After execution completes:

1. Check `_eval-results/{skill-name}/grading.json` for structured results
2. Review the overall PASS/FAIL status in the summary section
3. For any failing expectations, examine the evidence field to understand why
4. Optionally review `_eval-results/{skill-name}/transcript.md` for raw skill output

### Execution Characteristics

| Property | Value |
|----------|-------|
| Isolation | Each eval pair runs in an independent agent context |
| State modification | None — eval operations are read-only (FR-007) |
| Token cost | Approximately 10-20K tokens per eval pair (skill execution + grading) |
| Suite cost | Approximately 30-100K tokens for a 3-5 pair suite |
| Time target | Under 5 minutes per suite (SC-005) |
| Determinism | Non-deterministic — expect variation between runs (managed by threshold) |

### Running a Version Comparison (Comparator)

To compare two versions of a skill:

1. Ensure both skill versions are accessible (e.g., current version and a modified version)
2. The Comparator agent runs each prompt against both versions independently
3. Outputs are scored blindly on Content and Structure dimensions (1-5 scale)
4. Results are written to `_eval-results/{skill-name}/comparison.json`

For comprehensive coverage of blind evaluation methodology, dimension scoring interpretation, the `comparison.json` output format, and a worked example, see [Section 11: Version Comparison with Comparator](#11-version-comparison-with-comparator).

---

## 7. How to Interpret Grading Results

Grading results follow the schema defined in `specs/083-skill-eval-suites/contracts/grading-output-schema.json`.

### Result Structure Overview

```
grading.json
├── suite_name          # Which eval suite was graded
├── skill               # Which skill was evaluated
├── results[]           # Per-eval-pair results
│   ├── eval_id         # References the eval pair ID from evals.json
│   ├── expectations[]  # Per-expectation verdicts
│   │   ├── expectation # The original expectation string
│   │   ├── verdict     # PASS or FAIL
│   │   └── evidence    # Citation from skill output supporting the verdict
│   ├── summary         # Pair-level stats: pass_count, fail_count, pass_rate
│   └── execution_metrics  # token_usage, elapsed_time_ms
└── summary             # Suite-level aggregate
    ├── total_expectations
    ├── total_pass
    ├── total_fail
    ├── pass_rate
    ├── threshold
    └── overall_status  # PASS or FAIL
```

### Reading the Summary

The top-level `summary` object tells you the overall result:

```json
{
  "summary": {
    "total_expectations": 15,
    "total_pass": 13,
    "total_fail": 2,
    "pass_rate": 0.867,
    "threshold": 0.8,
    "overall_status": "PASS"
  }
}
```

**Interpretation**: 13 of 15 expectations passed (86.7%), which meets the 0.8 threshold. Overall status is PASS.

### Reading Per-Expectation Verdicts

Each expectation within a result includes a verdict and evidence:

```json
{
  "expectation": "Output contains a '## Requirements' section with functional requirements listed",
  "verdict": "PASS",
  "evidence": "The output includes '## Requirements *(mandatory)*' followed by FR-001 through FR-008."
}
```

```json
{
  "expectation": "Output does not fabricate requirements that were not in the prompt",
  "verdict": "FAIL",
  "evidence": "The output includes 'FR-009: The system SHALL support biometric authentication' which was not mentioned in the prompt."
}
```

### Interpreting Failures

When an expectation fails:

1. **Read the evidence** — The Grader cites specific output that led to the FAIL verdict
2. **Check severity** — Is this a `critical`, `major`, or `minor` eval pair? Address critical failures first.
3. **Determine root cause** — Is the failure a genuine skill regression, or is the expectation too strict?
4. **Decide on action**:

| Root Cause | Action |
|------------|--------|
| Genuine skill regression | Fix the skill, re-run eval |
| Expectation too strict (exact string match) | Revise the expectation to be more structural |
| LLM non-determinism (passes on re-run) | Acceptable if within threshold; consider loosening expectation |
| Expectation ambiguous (Grader misinterprets) | Rewrite expectation to be more specific |

### Additional Result Fields

The Grader may produce two optional fields per eval pair:

| Field | Purpose |
|-------|---------|
| `implicit_claims` | Additional quality claims the Grader identified in the output beyond the explicit expectations. Useful for discovering coverage gaps. |
| `feedback` | Suggestions from the Grader for improving eval coverage or expectation clarity. Review these when maintaining eval suites. |

### Comparison Results

When a Comparator run is performed, `comparison.json` contains per-prompt scores:

```json
{
  "prompt": "Generate a feature specification for...",
  "scores": {
    "version_a": {
      "content": { "correctness": 4, "completeness": 5, "accuracy": 4 },
      "structure": { "organization": 5, "formatting": 4, "usability": 5 }
    },
    "version_b": {
      "content": { "correctness": 3, "completeness": 4, "accuracy": 3 },
      "structure": { "organization": 4, "formatting": 3, "usability": 4 }
    }
  },
  "winner": "version_a",
  "evidence": "Version A includes all mandatory spec sections with proper governance markers..."
}
```

Each dimension is scored 1-5. The winner is determined by aggregate scoring across all prompts and dimensions. For the complete `comparison.json` field reference, dimension score definitions, winner determination logic, and a worked example, see [Section 11: Version Comparison with Comparator](#11-version-comparison-with-comparator).

---

## 8. Schema Policy

There is an intentional divergence between the JSON Schema validation rules and the Phase 1 authoring convention.

### The Divergence

| Layer | `evals` Array Constraint | Rationale |
|-------|--------------------------|-----------|
| JSON Schema (`evals-json-schema.json`) | `minItems: 1` | Schema validates **structural correctness**. A suite with 1 eval pair is structurally valid JSON. The schema should not enforce project-specific conventions. |
| Phase 1 Convention (this document) | 3-5 pairs per suite | Convention enforces **quality coverage**. Fewer than 3 pairs cannot cover happy-path, edge-case, and failure-mode categories. More than 5 pairs increases token cost without proportional quality gain in Phase 1. |

### Why This Divergence Exists

1. **Schema reusability** — The JSON Schema may be adopted by other projects or used in automation. Setting `minItems: 3` in the schema would force all consumers into our Phase 1 convention, even when a 1-pair suite is a valid use case (e.g., quick smoke test).

2. **Convention evolution** — Phase 2 may adjust the recommended range (e.g., 5-10 pairs for complex skills). Changing a convention in documentation is a text edit. Changing a schema constraint requires schema versioning and consumer migration.

3. **Separation of concerns** — Schema validates shape. Conventions encode intent. Tooling can enforce either or both depending on context.

### Enforcement

| Check | Phase 1 Enforcement |
|-------|---------------------|
| JSON Schema validation (structural) | Automated — `evals.json` must validate against the schema |
| 3-5 pairs per suite (convention) | Manual review — enforced during Triad review of eval suite PRs |
| All three tag categories covered | Manual review — each suite should have happy-path, edge-case, and failure-mode pairs |

---

## 9. Eval Maintenance Guidance

Eval suites are living artifacts. As skills evolve, their evals must evolve too. Stale evals produce false failures that erode trust in the eval system.

### When to Update Evals

| Skill Change | Eval Action Required |
|--------------|---------------------|
| SKILL.md prompt restructured | Review and update prompts that reference specific instructions |
| New mandatory output section added | Add expectations verifying the new section |
| Output format changed (e.g., table to list) | Update structural expectations to match new format |
| Skill scope expanded (new capability) | Add new eval pairs covering the expanded scope |
| Skill scope reduced (capability removed) | Remove eval pairs and expectations for removed behavior |
| Bug fix for edge case | Add or update edge-case eval pair to prevent regression |
| Pass threshold consistently not met | Investigate: fix skill or adjust expectations/threshold |

### Staleness Detection

An eval suite may be stale if:

- The `evals.json` version has not been incremented in 3+ skill updates
- Running the eval produces consistent failures on expectations that test outdated behavior
- The skill's `SKILL.md` has sections or capabilities not covered by any eval pair
- The Grader's `feedback` array consistently suggests new coverage areas

### When to Re-Author vs. Patch

| Situation | Approach |
|-----------|----------|
| 1-2 expectations need updating | **Patch** — update the specific expectations in place, bump patch version |
| Prompt context is outdated | **Patch** — update the prompt text, bump patch version |
| Skill has been fundamentally rewritten | **Re-author** — create new eval pairs from scratch, bump major version |
| More than half the expectations are failing | **Re-author** — the eval suite no longer reflects the skill's behavior |
| Adding coverage for a new skill capability | **Patch** — add a new eval pair, bump minor version |

### Version Bumping

Eval suites use semantic versioning. Follow these conventions:

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Fix expectation wording | Patch | `1.0.0` -> `1.0.1` |
| Add new eval pair | Minor | `1.0.1` -> `1.1.0` |
| Rewrite suite for skill overhaul | Major | `1.1.0` -> `2.0.0` |

### Maintenance Checklist

When updating a skill, review its eval suite:

- [ ] Do all existing prompts still match the skill's expected input format?
- [ ] Do all expectations reflect the skill's current output structure?
- [ ] Are new skill capabilities covered by at least one eval pair?
- [ ] Has the `version` field been incremented?
- [ ] Does the `evals/README.md` still accurately describe coverage?

---

## 10. Creating Custom Eval Suites

This section is a step-by-step walkthrough for template adopters to create an eval suite for their own custom skill. Target: completable in under 15 minutes (SC-004).

### Prerequisites

- An existing skill in `.claude/skills/{your-skill}/` with a working `SKILL.md`
- Familiarity with the skill's expected inputs and outputs
- A text editor capable of editing JSON

### Step 1: Create the Directory (1 minute)

```bash
mkdir -p .claude/skills/{your-skill}/evals
```

### Step 2: Identify Test Scenarios (3 minutes)

Before writing JSON, decide on 3-5 test scenarios. You need at least one from each category:

| Category | What to Test | Example |
|----------|-------------|---------|
| **Happy path** | Skill works correctly with well-formed input | "Given a complete PRD, the skill generates a spec with all required sections" |
| **Edge case** | Skill handles unusual or boundary input gracefully | "Given ambiguous requirements, the skill flags them for clarification" |
| **Failure mode** | Skill fails gracefully when prerequisites are missing | "Given a missing input file, the skill reports the error clearly" |

Write a one-sentence description of each scenario. These become your eval pairs.

### Step 3: Write the evals.json (5 minutes)

Create `.claude/skills/{your-skill}/evals/evals.json` with the following template:

```json
{
  "name": "{your-skill} eval suite",
  "version": "1.0.0",
  "skill": "{your-skill}",
  "pass_threshold": 0.8,
  "evals": [
    {
      "id": "{skill}-happy-path-01",
      "prompt": "REPLACE: A self-contained prompt that exercises the skill's primary function. Include all necessary context directly in the prompt — do not reference external files or project state.",
      "expectations": [
        "REPLACE: Output contains the primary expected section or artifact",
        "REPLACE: Output follows the expected format or structure",
        "REPLACE: Output includes key governance or quality markers"
      ],
      "tags": ["happy-path"],
      "severity": "critical"
    },
    {
      "id": "{skill}-edge-case-01",
      "prompt": "REPLACE: A prompt with unusual, incomplete, or boundary input that the skill should handle gracefully.",
      "expectations": [
        "REPLACE: Output handles the unusual input without crashing",
        "REPLACE: Output indicates what is missing or ambiguous"
      ],
      "tags": ["edge-case"],
      "severity": "major"
    },
    {
      "id": "{skill}-failure-mode-01",
      "prompt": "REPLACE: A prompt where a critical prerequisite is missing or invalid.",
      "expectations": [
        "REPLACE: Output clearly indicates the error condition",
        "REPLACE: Output does not produce incorrect or misleading results"
      ],
      "context": "REPLACE: Describe the missing prerequisite or invalid state.",
      "tags": ["failure-mode"],
      "severity": "critical"
    }
  ]
}
```

Replace all `REPLACE:` placeholders with content specific to your skill.

**Key rules for IDs**:
- IDs must match `^[a-z0-9-]+$` — only lowercase letters, numbers, and hyphens
- If your skill name has a `~` prefix (e.g., `~my-tool`), strip the `~` for IDs: use `my-tool-happy-path-01`, not `~my-tool-happy-path-01`
- Use a short, recognizable prefix from the skill name (e.g., `~aod-spec` uses `spec-`, `~aod-build` uses `build-`)

**Key rules for prompts**:
- Embed all context directly in the prompt string
- Do not reference files that may or may not exist in the project
- Make the prompt self-contained — it should work the same way regardless of project state

**Key rules for expectations**:
- Describe structural properties ("contains a section", "includes a table")
- Avoid exact text matching ("starts with exactly", "third line is")
- Include at least one negative assertion ("does not fabricate", "does not crash")

### Step 4: Validate the JSON (1 minute)

```bash
cat .claude/skills/{your-skill}/evals/evals.json | python3 -m json.tool
```

If the command outputs formatted JSON without errors, the file is syntactically valid.

For schema validation, verify manually against the field requirements:
- All required top-level fields present: `name`, `version`, `skill`, `pass_threshold`, `evals`
- Each eval pair has required fields: `id`, `prompt`, `expectations`
- `id` values use only lowercase letters, numbers, and hyphens
- `version` follows semver format (e.g., `1.0.0`)
- `pass_threshold` is between 0.0 and 1.0
- `tags` values are from: `happy-path`, `edge-case`, `failure-mode`
- `severity` values are from: `critical`, `major`, `minor`

### Step 5: Write the README (3 minutes)

Create `.claude/skills/{your-skill}/evals/README.md`:

```markdown
# {Your Skill} Eval Suite

## Coverage

| ID | Category | What It Tests |
|----|----------|---------------|
| {skill}-happy-path-01 | Happy path | [one-sentence description] |
| {skill}-edge-case-01 | Edge case | [one-sentence description] |
| {skill}-failure-mode-01 | Failure mode | [one-sentence description] |

## How to Run

Execute this eval suite using Anthropic's skill-creator eval pipeline.
Results are written to `_eval-results/{your-skill}/`.

## How to Interpret Results

- Check `_eval-results/{your-skill}/grading.json` for PASS/FAIL verdicts
- Overall PASS requires {pass_threshold * 100}% of expectations to pass
- Review evidence fields for any FAIL verdicts to understand root cause

## Maintenance

- Update expectations when the skill's SKILL.md changes
- Bump the version in evals.json when modifying eval pairs
- See `docs/standards/EVAL_CONVENTIONS.md` for full conventions
```

### Step 6: Run the Eval Suite (2 minutes)

Execute the eval suite using Anthropic's skill-creator pipeline and review the results in `_eval-results/{your-skill}/grading.json`.

### Completion Checklist

After completing all steps, verify:

- [ ] `.claude/skills/{your-skill}/evals/evals.json` exists and is valid JSON
- [ ] Suite contains 3-5 eval pairs covering happy-path, edge-case, and failure-mode
- [ ] All prompts are self-contained with no external dependencies
- [ ] All expectations use structural assertions, not exact string matching
- [ ] `.claude/skills/{your-skill}/evals/README.md` documents coverage and usage
- [ ] `_eval-results/` is listed in `.gitignore`
- [ ] Eval suite runs successfully and produces grading results

---

## 11. Version Comparison with Comparator

The Comparator is a sub-agent in Anthropic's skill-creator eval pipeline that evaluates two versions of a skill side by side. Unlike the Grader (which checks pass/fail against expectations), the Comparator performs blind quality scoring to determine which version produces better output.

### What the Comparator Is

The Comparator is purpose-built for A/B evaluation of skill versions. Given two versions of a skill and a set of prompts, it:

1. Runs each prompt against both versions independently
2. Scores each version's output on six quality dimensions
3. Determines a per-prompt winner based on aggregate scores
4. Produces structured results in `comparison.json`

The Comparator does not know which version is "old" and which is "new." It receives two skill outputs labeled "Version A" and "Version B" with no metadata about authorship, modification date, or intent. This blind design prevents bias toward the existing implementation.

### When to Use the Comparator

| Scenario | Why Use Comparator |
|----------|--------------------|
| Skill rewrite | Verify the rewritten skill produces equal or better output before replacing the original |
| Major refactor | Confirm that restructuring the skill's SKILL.md does not degrade output quality |
| A/B testing between approaches | Compare two alternative implementations to determine which approach to ship |
| Regression validation | After fixing a bug, confirm the fix does not introduce quality regressions elsewhere |
| Prompt engineering iteration | Compare different prompt strategies within a skill to find the most effective version |

The Comparator is **not** a replacement for the Grader. Use the Grader for pass/fail functional correctness. Use the Comparator for relative quality comparison between two versions.

### How to Run a Comparison

#### Step 1: Prepare Both Versions

Ensure both skill versions are accessible to the eval pipeline. The two versions might be:

- The current `SKILL.md` on the main branch vs. a modified `SKILL.md` on a feature branch
- Two alternative implementations saved as separate files
- The same skill before and after a prompt engineering change

Both versions must be loadable as valid skills with complete `SKILL.md` files.

#### Step 2: Select Prompts

The Comparator uses the same prompts defined in the skill's `evals/evals.json`. Each prompt in the `evals` array is executed against both versions. You do not need to author separate prompts for comparison.

If you want to compare on specific scenarios only, you can provide a subset of prompts. However, using the full eval suite gives the most comprehensive comparison.

#### Step 3: Execute the Comparison

Invoke the Comparator through Anthropic's skill-creator pipeline. The Comparator:

1. Takes each prompt from the eval suite
2. Executes the prompt against Version A in an isolated context
3. Executes the same prompt against Version B in a separate isolated context
4. Passes both outputs (labeled "Version A" and "Version B") to the scoring phase
5. Scores each output on Content and Structure dimensions
6. Determines a per-prompt winner and records evidence

#### Step 4: Review Results

Results are written to `_eval-results/{skill-name}/comparison.json`. See [comparison.json Output Format](#comparisonjson-output-format) below for the complete field reference.

### Blind Evaluation

The Comparator receives outputs labeled "Version A" and "Version B" with no indication of which is the original or modified version. This design is intentional:

- **No version metadata**: The Comparator does not receive commit hashes, dates, author names, or labels like "old" and "new"
- **Randomized assignment**: Which physical version maps to "A" vs. "B" may vary across runs
- **Output-only evaluation**: Scoring is based entirely on the quality of the generated output, not on knowledge of the version's history or intent
- **Bias prevention**: Without knowing which version is the incumbent, the Comparator cannot default to preferring the existing implementation

This mirrors the blind review methodology used in academic peer review and clinical trials, applied to skill output evaluation.

### Content Dimension Scoring

The Content dimension evaluates the substance of the skill's output. Each criterion is scored 1-5.

| Criterion | What It Measures | Score Anchors |
|-----------|------------------|---------------|
| **Correctness** | Factual accuracy of the output | 1: Contains factual errors or contradictions. 3: Mostly accurate with minor issues. 5: Fully accurate with no errors. |
| **Completeness** | Coverage of requirements from the prompt | 1: Major requirements missing. 3: Core requirements covered, some gaps. 5: All requirements thoroughly addressed. |
| **Accuracy** | Precision of details (names, references, values) | 1: Details are wrong or fabricated. 3: Details are approximately right. 5: Details are precise and verifiable. |

**Example**: For a spec-generation skill, Correctness evaluates whether the generated requirements are logically sound, Completeness checks whether all sections from the template are present, and Accuracy verifies that feature branch names, PRD references, and requirement IDs are precise.

### Structure Dimension Scoring

The Structure dimension evaluates how well the output is organized and presented. Each criterion is scored 1-5.

| Criterion | What It Measures | Score Anchors |
|-----------|------------------|---------------|
| **Organization** | Logical flow and section ordering | 1: Disorganized, no clear structure. 3: Reasonable structure with some ordering issues. 5: Logical flow, sections build on each other. |
| **Formatting** | Visual presentation (headings, tables, code blocks) | 1: No formatting, wall of text. 3: Basic formatting present. 5: Professional formatting with consistent visual hierarchy. |
| **Usability** | Ease of use by the reader or downstream consumer | 1: Reader cannot act on the output. 3: Reader can use the output with effort. 5: Reader can immediately act on the output. |

**Example**: For a spec-generation skill, Organization checks whether Requirements precede Testing scenarios, Formatting evaluates consistent use of Markdown headings and tables, and Usability assesses whether a downstream engineer could implement directly from the spec.

### comparison.json Output Format

The Comparator writes results to `_eval-results/{skill-name}/comparison.json`. This file contains a per-prompt breakdown of scores, winners, and evidence.

#### Top-Level Structure

```json
{
  "skill": "~aod-spec",
  "comparison_results": [
    {
      "prompt": "...",
      "scores": { "version_a": { ... }, "version_b": { ... } },
      "winner": "version_a | version_b | tie",
      "evidence": "..."
    }
  ],
  "summary": {
    "version_a_wins": 2,
    "version_b_wins": 1,
    "ties": 0,
    "overall_winner": "version_a"
  }
}
```

#### Comparison Result Fields (per prompt)

Each entry in the `comparison_results` array represents one prompt evaluated against both versions.

| Field | Type | Description |
|-------|------|-------------|
| `prompt` | string | The prompt text used for comparison (sourced from `evals.json`) |
| `scores` | object | Contains `version_a` and `version_b`, each holding a `DimensionScores` object |
| `winner` | string | Per-prompt winner: `"version_a"`, `"version_b"`, or `"tie"` |
| `evidence` | string | Rationale explaining why the winner was chosen, citing specific output differences |

#### DimensionScores Fields

Each version's scores are broken into Content and Structure dimensions.

| Field | Type | Description |
|-------|------|-------------|
| `content` | object | Contains `correctness`, `completeness`, and `accuracy` (each an integer 1-5) |
| `structure` | object | Contains `organization`, `formatting`, and `usability` (each an integer 1-5) |

Full expanded structure:

```json
{
  "content": {
    "correctness": 4,
    "completeness": 5,
    "accuracy": 4
  },
  "structure": {
    "organization": 5,
    "formatting": 4,
    "usability": 5
  }
}
```

#### Score Scale

All dimension criteria use a 1-5 integer scale.

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Poor | Significant deficiencies; output fails on this criterion |
| 2 | Below Average | Notable weaknesses; below acceptable quality |
| 3 | Average | Acceptable quality; meets basic expectations with room for improvement |
| 4 | Good | Strong quality; meets expectations with only minor gaps |
| 5 | Excellent | Exceptional quality; fully meets or exceeds expectations |

#### Winner Determination Logic

The Comparator determines a winner for each prompt and an overall winner across all prompts.

**Per-prompt winner**:

1. Sum all six dimension scores for Version A (correctness + completeness + accuracy + organization + formatting + usability)
2. Sum all six dimension scores for Version B
3. The version with the higher total wins the prompt
4. If totals are equal, the prompt is a `"tie"`

**Overall winner**:

1. Count the number of prompts won by each version
2. The version winning more prompts is the overall winner
3. If both versions win the same number of prompts, the overall result is a tie

**Tie-breaking**: There is no secondary tie-breaker. Ties are a valid and informative outcome -- they indicate that both versions perform at comparable quality and the choice between them may depend on factors outside the Comparator's scope (e.g., code maintainability, consistency with team conventions).

#### Summary Fields

The top-level `summary` object aggregates results across all prompts.

| Field | Type | Description |
|-------|------|-------------|
| `version_a_wins` | integer | Number of prompts where Version A scored higher |
| `version_b_wins` | integer | Number of prompts where Version B scored higher |
| `ties` | integer | Number of prompts with equal scores |
| `overall_winner` | string | `"version_a"`, `"version_b"`, or `"tie"` |

#### Reference

- **Entity definitions**: See `specs/083-skill-eval-suites/data-model.md` for the Comparison Result and Dimension Scores entity specifications
- **Related schema**: See `specs/083-skill-eval-suites/contracts/grading-output-schema.json` for the Grader output schema; `comparison.json` follows a parallel structure documented in the data model

### Worked Example: Comparing ~aod-spec Skill Versions

This walkthrough demonstrates a complete Comparator run. A template maintainer has rewritten the `~aod-spec` skill to improve how it handles architect concerns -- specifically, the rewritten version adds a dedicated "Architect Considerations" section and restructures how non-functional requirements are presented. The maintainer wants to compare the old and new versions before shipping.

#### Scenario

- **Version A**: The current `~aod-spec` skill on the `main` branch
- **Version B**: A rewritten `~aod-spec` skill on the `083-improve-architect-concerns` feature branch
- **Goal**: Determine whether the rewrite improves output quality enough to justify replacing the current version

#### Setup

The maintainer ensures both versions are accessible:

1. The current `SKILL.md` exists at `.claude/skills/~aod-spec/SKILL.md` (Version A)
2. The rewritten `SKILL.md` is available on the feature branch (Version B)
3. The eval suite at `.claude/skills/~aod-spec/evals/evals.json` contains the prompts to use for comparison

No changes to the eval suite are needed. The Comparator reuses the existing prompts.

#### Execution

The maintainer invokes the Comparator through Anthropic's skill-creator pipeline, providing both skill versions. The pipeline:

1. Reads the 3 prompts from `evals.json`
2. Executes each prompt against Version A in isolation
3. Executes each prompt against Version B in isolation
4. Labels the outputs "Version A" and "Version B" (blind -- the Comparator does not know which is old vs. new)
5. Scores each pair of outputs on all 6 dimensions
6. Writes results to `_eval-results/~aod-spec/comparison.json`

#### Sample comparison.json Output

```json
{
  "skill": "~aod-spec",
  "comparison_results": [
    {
      "prompt": "Generate a feature specification for a user authentication system. The PRD requires email/password login, OAuth2 support, and session management. The feature branch is 042-user-auth. Include all mandatory sections from the spec template.",
      "scores": {
        "version_a": {
          "content": { "correctness": 4, "completeness": 4, "accuracy": 5 },
          "structure": { "organization": 4, "formatting": 4, "usability": 4 }
        },
        "version_b": {
          "content": { "correctness": 5, "completeness": 5, "accuracy": 5 },
          "structure": { "organization": 5, "formatting": 4, "usability": 5 }
        }
      },
      "winner": "version_b",
      "evidence": "Version B includes a dedicated 'Architect Considerations' section covering scalability, session storage strategy, and OAuth2 provider abstraction. Version A addresses these concerns only indirectly within the Requirements section. Version B also restructures non-functional requirements into a separate table with measurable targets, improving usability for downstream engineers."
    },
    {
      "prompt": "Generate a feature specification for 'improve the dashboard'. No PRD exists. Requirements are vague and incomplete.",
      "scores": {
        "version_a": {
          "content": { "correctness": 4, "completeness": 4, "accuracy": 4 },
          "structure": { "organization": 4, "formatting": 5, "usability": 4 }
        },
        "version_b": {
          "content": { "correctness": 4, "completeness": 3, "accuracy": 4 },
          "structure": { "organization": 3, "formatting": 4, "usability": 3 }
        }
      },
      "winner": "version_a",
      "evidence": "Version A handles ambiguous input more concisely, producing focused clarification questions grouped by category. Version B attempts to populate the new 'Architect Considerations' section even when requirements are vague, resulting in speculative content that reduces accuracy. Version A's formatting of the clarification section is cleaner with a numbered list vs. Version B's mixed prose and bullets."
    },
    {
      "prompt": "Generate a feature specification. The PRD file at docs/product/02_PRD/999-nonexistent.md does not exist.",
      "scores": {
        "version_a": {
          "content": { "correctness": 4, "completeness": 3, "accuracy": 4 },
          "structure": { "organization": 4, "formatting": 4, "usability": 4 }
        },
        "version_b": {
          "content": { "correctness": 5, "completeness": 4, "accuracy": 5 },
          "structure": { "organization": 4, "formatting": 4, "usability": 5 }
        }
      },
      "winner": "version_b",
      "evidence": "Version B provides a more actionable error response: it identifies the missing PRD, suggests specific next steps (run /aod.define or create the PRD manually), and includes a partial spec template the user can fill in once the PRD exists. Version A correctly identifies the missing PRD but offers only a generic error message without recovery guidance."
    }
  ],
  "summary": {
    "version_a_wins": 1,
    "version_b_wins": 2,
    "ties": 0,
    "overall_winner": "version_b"
  }
}
```

#### Interpretation Walkthrough

**Reading the summary**: Version B won 2 of 3 prompts. Version A won 1 prompt. No ties. The overall winner is Version B.

**Prompt-by-prompt analysis**:

| Prompt | Winner | Version A Total | Version B Total | Key Differentiator |
|--------|--------|-----------------|-----------------|-------------------|
| Happy path (auth system) | Version B | 25 | 29 | Dedicated architect section with measurable NFRs |
| Edge case (vague dashboard) | Version A | 25 | 21 | Concise clarification vs. speculative content |
| Failure mode (missing PRD) | Version B | 23 | 27 | Actionable recovery guidance vs. generic error |

**What the scores reveal**:

- **Version B's strength**: When given well-formed input (happy path) or clear error conditions (failure mode), the rewrite produces notably better output. The architect-focused improvements shine in these scenarios.
- **Version A's strength**: When input is ambiguous, the original version handles uncertainty more gracefully. The rewrite's new sections become a liability with vague requirements, generating speculative content.
- **Formatting parity**: Both versions score similarly on formatting (4-5 range), indicating the rewrite preserved visual quality.

#### Decision Framework

Use the Comparator results to make a ship/iterate/revert decision.

| Outcome | Criteria | Action |
|---------|----------|--------|
| **Ship the new version** | New version wins overall AND does not regress critically on any prompt | Replace the old skill with the new version |
| **Iterate on the new version** | New version wins overall BUT shows weakness on specific scenarios | Address the weak scenarios before shipping; re-run the Comparator to confirm improvement |
| **Revert to the old version** | Old version wins overall OR new version introduces critical regressions | Keep the old version; analyze why the rewrite degraded quality |
| **Tie -- gather more data** | Versions are tied or results are marginal | Add more prompts to the eval suite and re-run; consider testing with domain-specific scenarios |

**Applying the framework to this example**:

The maintainer observes that Version B wins overall (2-1) but regresses on edge-case handling. The recommended action is **iterate**: fix the edge-case behavior in Version B (specifically, prevent speculative content generation when requirements are vague), then re-run the Comparator to confirm the fix resolves the regression without degrading the winning scenarios.

The maintainer should NOT ship Version B as-is, because the edge-case regression (speculative architect content on ambiguous input) could produce misleading specs in real usage. However, the overall direction is positive -- the rewrite improves happy-path and failure-mode handling meaningfully.

---

## Appendix A: Field Reference Quick Card

For quick reference when authoring eval suites.

### evals.json — Required Fields

```
name            string     Suite name (max 128 chars)
version         string     Semver (e.g., "1.0.0")
skill           string     Must match parent directory name
pass_threshold  number     0.0 - 1.0 (default: 0.8)
evals           array      Min 1 item (convention: 3-5)
  id            string     Lowercase alphanumeric + hyphens
  prompt        string     Self-contained, no external deps
  expectations  array      Min 1 string per pair
```

### evals.json — Optional Fields (per eval pair)

```
context         string     Prerequisite state description
tags            array      "happy-path" | "edge-case" | "failure-mode"
severity        string     "critical" | "major" | "minor"
```

### grading.json — Key Fields

```
overall_status  string     "PASS" | "FAIL"
pass_rate       number     0.0 - 1.0
threshold       number     From evals.json pass_threshold
verdict         string     Per-expectation: "PASS" | "FAIL"
evidence        string     Citation supporting the verdict
```

---

## Appendix B: Design Decisions

Rationale for key architectural choices in the eval system.

| Decision | Choice | Why |
|----------|--------|-----|
| File format | JSON (not YAML) | Aligns with Anthropic's skill-creator convention. JSON is the supported format for eval definitions. |
| Assertion style | Plain-language strings | The Grader evaluates natural language expectations. This handles LLM non-determinism better than exact matching or regex patterns. |
| Results storage | Gitignored `_eval-results/` | Eval outputs are non-deterministic LLM responses. Committing them would bloat git history with noise that differs on every run. |
| Self-contained prompts | All context embedded in prompt | Avoids brittle tests dependent on project state. Enables reproducible results regardless of repository condition. |
| Phase 1 gating | Advisory only | Phase 1 establishes patterns and validates conventions. Build gating is deferred to Phase 2 after patterns prove reliable. |
| Co-location | `evals/` inside skill directory | Evals travel with the skill. No orphaned eval files when skills are moved, renamed, or deleted. |

---

*Reference schemas: `specs/083-skill-eval-suites/contracts/evals-json-schema.json`, `specs/083-skill-eval-suites/contracts/grading-output-schema.json`*
