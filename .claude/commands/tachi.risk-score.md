---
description: Run quantitative risk scoring on threat model output — produces risk-scores.md and risk-scores.sarif with four-dimensional scores, composite ratings, and governance fields
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0: Parse Flags

1. If `$ARGUMENTS` contains `--output-dir <path>`:
   - Set `output_dir` to the specified path
   - Strip `--output-dir <path>` from `$ARGUMENTS` (trim extra whitespace)
2. Default: `output_dir = null` (outputs written to same directory as input)

3. If `$ARGUMENTS` contains `--baseline <run-dir>`:
   - Set `baseline_dir` to the specified path (a path to a file counts as the directory that holds it)
   - Strip `--baseline <run-dir>` from `$ARGUMENTS` (trim extra whitespace)
4. Default: `baseline_dir = null` (the run uses the baseline that `threats.md` names in its `baseline.source`, and scores every finding fresh when it names none)

5. If `$ARGUMENTS` contains `--architecture-path <path>`:
   - Set `architecture_flag` to the specified path
   - Strip `--architecture-path <path>` from `$ARGUMENTS` (trim extra whitespace)
6. Default: `architecture_flag = null` (the scripts then take the architecture file from the `**Architecture source**` line of `threats.md`, and from `docs/security/architecture.md` after that)

7. Remaining `$ARGUMENTS` is treated as the input directory path (`input_dir`).
8. If no input directory was provided in `$ARGUMENTS`:
   - If `./docs/security/` exists in cwd: glob `docs/security/*/`, sort directory names descending (ISO-like `YYYY-MM-DDTHH-MM-SS` timestamps sort correctly as strings), and select the newest directory that contains `threats.md` or `threats.sarif`. Set `input_dir` to that path and display: `Auto-detected input: {input_dir}`.
   - Otherwise, default to current working directory (`.`).

This command takes no date flag. It sets the scoring date once, in Step 2.

## Overview

Single-command entry point for tachi quantitative risk scoring. Validates prerequisites, locates threat model output, plans the scoring into batches, dispatches the risk-scorer agent once per batch, and runs the shipped renderer, which writes the scored output files.

**Flow**: Validate → Plan → Dispatch → Reconcile → Render → Report

**Output suite** (written by `scripts/render-risk-scores.py`, never by an agent):
- `risk-scores.md` — scored threat table, executive summary, dimensional breakdowns, governance fields, methodology, and score integrity
- `risk-scores.sarif` — SARIF 2.1.0 with per-finding composite scores in `security-severity` and scoring properties in result property bags

**Who does what**: the risk-scorer agent supplies judgment only (a CVSS vector, sub-scores, reachability inputs and rationale for each finding) and writes one part file per batch. The scripts plan the batches, reconcile them from disk, compute every score, and write both files. This command runs only the shipped scripts it names, `scripts/tachi-stage.py`, `scripts/populate-affected-assets.py` and `scripts/render-risk-scores.py`, each as a single `python3` call with literal arguments. It writes no script of its own, and it stops on a failure rather than working around it.

## Step 1: Validate Prerequisites

1. **Check tachi agents and scripts are installed**:
   - Verify `.claude/agents/tachi/risk-scorer.md`, `scripts/tachi-stage.py` and `scripts/render-risk-scores.py` exist
   - If any is missing, display:
     ```
     TACHI RISK SCORER NOT INSTALLED
     Missing: {path of the first missing file}
     Re-run the installer from this project's root: <tachi-repo>/scripts/install.sh
     See: https://github.com/davidmatousek/tachi
     ```
   - Halt if missing.

2. **Check Python 3.9 or later is present** (the presence check). Run:

   ```bash
   python3 scripts/tachi-stage.py --version
   ```

   - Exit code 0 means Python 3.9 or later is present. Continue.
   - Any other result stops the run. That covers a missing `python3`, and exit code 2, which is the script refusing to run below the 3.9 floor. Display, with the Python version the script reported, or `none`:
     ```
     PYTHON 3.9+ NOT FOUND — tachi renders this stage with Python 3.9 or later (found: {version, or none}); install it and re-run
     ```
   - No plan exists yet, so run nothing else.

3. **Check input files exist**:
   - Look for `threats.md` in the input directory
   - If not found, look for `threats.sarif` in the input directory
   - If neither exists, display:
     ```
     NO THREAT MODEL OUTPUT FOUND
     Neither threats.md nor threats.sarif found in: {input_dir}
     Run /threat-model first to generate threat model output.
     ```
   - Halt if neither exists.

4. **Determine input file and format**:
   - If `threats.md` exists: set `input_file = threats.md`, `input_format = markdown`
   - If only `threats.sarif` exists: set `input_file = threats.sarif`, `input_format = sarif`
   - `threats.md` is the canonical source; `threats.sarif` is the fallback. The planner reads the fallback when `threats.md` is absent (ADR-050 D8), so this command never parses either file itself.
   - Display: `Input: {input_file} ({input_format} format)`

5. **Determine output directory**:
   - If `--output-dir` was specified: use that path
   - Otherwise: use the same directory as the input file
   - Create output directory if it does not exist
   - Display: `Output: {output_dir}`

6. **Check for optional architecture.md**:
   - If `--architecture-path` was given: set `architecture_path` to that path
   - Otherwise look for `architecture.md` in the input directory and its parent directory, and if found set `architecture_path` to the resolved path
   - If neither applies: set `architecture_path = null` (reachability will use trust zone data only, or default to 5.0)

## Step 1.5: Ensure Affected Assets Block (idempotent)

> **Pre-render populator gate**: This step is the `/risk-score` equivalent of the
> `/threat-model` Phase 3.7 / Step 2.5 gate — it guarantees the deterministic
> `## Affected Assets` block exists in the input `threats.md` BEFORE Step 2 plans
> the run, so the renderer reads a block that is current.

The renderer takes each finding's asset-sensitivity tags from one source per run
(ADR-050 D2). It uses the `## Affected Assets` block of `threats.md` when the block
equals what the architecture file gives, and otherwise the architecture file's own
tags, with a warning. In the normal flow the block already exists, because the prior
`/threat-model` run wrote it. Re-assert it here, before anything reads `threats.md`,
so the dependency is explicit and idempotent. The populator is deterministic,
byte-stable on re-run (an existing block is replaced, not duplicated), and records
provenance only — it never re-scores.

1. Run this step ONLY when `input_format == markdown` AND `architecture_path` was
   resolved (Step 1 item 6) AND `output_dir` (Step 1 item 5) is the input
   directory — the populator upserts a markdown `threats.md` in place from the
   architecture's inline `[asset:...]` tags:

```bash
# Re-assert the deterministic affected_assets block (idempotent, byte-stable)
python3 scripts/populate-affected-assets.py \
  --architecture {architecture_path} \
  --threats {input_file}
```

2. Skip this step (do NOT fail) when `input_format == sarif` (no markdown
   `threats.md` to populate), when `architecture_path == null` (no architecture
   snapshot to source tags from), or when `--output-dir` names a directory other
   than the input directory (the populator rewrites `threats.md` in place, and
   the input directory stays read-only when the outputs go elsewhere). In all
   three cases the block written by the prior `/threat-model` run is already
   present in `threats.md`, or the renderer recomputes the tags from the
   architecture file. To refresh the block in place, run without `--output-dir`.
   Proceed to Step 2.

## Step 2: Plan the Batches

**IMPORTANT**: Pass file **paths**, never file contents. The planner reads the threat model once and writes one batch input file per batch. The risk-scorer agent reads its own batch input.

1. Set `scoring_date` to today's date as `YYYY-MM-DD`, once. The plan keeps the date, so a resumed run uses the plan's date, and no later step takes one.

2. Plan the batches:

   ```bash
   python3 scripts/tachi-stage.py plan --stage risk-score --out {output_dir} --date {scoring_date} --threats {input_dir}/threats.md
   ```

   - Add `--baseline-dir {baseline_dir}` when `--baseline` was given.
   - Add `--architecture {architecture_flag}` when `--architecture-path` was given, and only then. The URI of every SARIF result comes from this path, so a per-run snapshot must never stand in for it.
   - Always pass the `threats.md` path, even when only `threats.sarif` exists: `plan` reads `threats.sarif` when `threats.md` is absent.

3. `plan` prints one JSON object: `plan_id`, `plan_digest`, and `waves`, a list of waves with at most 16 batches each. Every batch is `{batch_id, input_path}`. Keep `plan_id` and the latest `plan_digest` for every later step. A step that prints a newer `plan_digest` replaces it.

4. Route by the exit code:

   | Exit | What to do |
   |------|------------|
   | 0 | Go to Step 3 |
   | 1 | Stop and print the error |
   | 2 | Stop and print the error. No plan exists yet, so there is nothing to fail |

## Step 3: Dispatch the Batches

Dispatch the waves in order, one wave at a time. For each batch in a wave, call the Agent tool with `subagent_type` set to `tachi-risk-scorer` and with this prompt, and no other:

```text
Read and follow the batch input at <input_path>. Write only the part file it names.
```

Replace `<input_path>` with that batch's `input_path`. Send all of a wave's Agent calls in one message, so that they run together. Never send more than 16 in one message, and start a wave only after every agent of the wave before it has reported completion.

Run `reconcile` only after every agent in the wave has reported completion. While an agent you dispatched is still running, don't run the renderer, report a result or end the stage. If you end your turn to wait, resume this loop on each completion notice.

If an Agent call fails because `tachi-risk-scorer` can't be spawned, end the run there. Run no substitute, and dispatch no other agent type. Go to Step F with `--reason agent-not-spawned` and `--detail tachi-risk-scorer`. An agent that was spawned and then failed is not a spawn failure: `reconcile` finds its part missing or invalid and plans the retry.

## Step 4: Reconcile

Reconcile from the files on disk, never from an agent's reply:

```bash
python3 scripts/tachi-stage.py reconcile --stage risk-score --out {output_dir} --plan {plan_id} --plan-digest {plan_digest}
```

`reconcile` prints `status`, a new `plan_digest`, the finished batches (`done`), the batches still to dispatch (`waves`) and any `exhausted` batches. Keep the new `plan_digest`.

Route by the exit code:

| Exit | Meaning | What to do |
|------|---------|------------|
| 0 | every batch has a valid part | Go to Step 5 |
| 3 | batches are pending | Dispatch exactly the batches `waves` lists, as in Step 3, then run this step again. Repeat while the exit code is 3 |
| 4 | a retry cap or the retry budget ran out | Go to Step F with `--reason unrecoverable-batch` |
| 2 | a guard or a digest check failed | Go to Step F with `--reason check-failed` |
| 1 | an input is missing or unreadable | Stop and print the error |

## Step 5: Render

Run the renderer. It re-validates every part, computes the values, writes both files to the plan's staging directory, re-reads them and checks them (row parity with the threat model, one SARIF result for each open finding, and agreement between the two files), and only then moves each onto its canonical name. A failed check leaves the canonical files as they were.

```bash
python3 scripts/render-risk-scores.py --out {output_dir} --plan {plan_id} --plan-digest {plan_digest}
```

Route by the exit code:

| Exit | What to do |
|------|------------|
| 0 | Success. Go to Step 6 |
| 5 | Success with warnings. Print the warnings, then go to Step 6 |
| 4 | A completeness or parity check failed. Go to Step F with `--reason check-failed` |
| anything else | Go to Step F with `--reason render-failed` |

## Step 6: Report Results

Print the summary lines that the renderer wrote, exactly as it wrote them. Restate no number and compute none: the renderer's counts are the only counts. Then print:

```
Next steps:
  1. Review Critical/High findings in risk-scores.md Section 2
  2. Assign risk owners in Section 4 (Governance Fields)
  3. Run /compensating-controls --target <codebase> to detect existing security controls and calculate residual risk
  4. Upload risk-scores.sarif to GitHub Code Scanning with category `risk-score`
```

## Step F: Fail

Run this step only when an earlier step sends you here, and only once a plan exists:

```bash
python3 scripts/tachi-stage.py fail --stage risk-score --out {output_dir} --plan {plan_id} --plan-digest {plan_digest} --reason {reason}
```

- `{reason}` is the one the step named: `agent-not-spawned`, `unrecoverable-batch`, `check-failed` or `render-failed`.
- For `agent-not-spawned`, add `--detail tachi-risk-scorer`.
- `fail` records the failure, moves any output this run changed into the plan's `failed/` directory, and puts the earlier run's outputs back, so the output directory never holds a failed file under a canonical name.
- Then stop with the four-line `TACHI RISK-SCORE FAILED` error that `fail` printed. Whatever `fail` exits with, stop there. `fail` never runs a second time.

## Usage Examples

```text
# Minimal — score threats in current directory
/risk-score

# Specify input directory
/risk-score path/to/threat-model-output/

# Custom output directory
/risk-score path/to/threat-model-output/ --output-dir reports/risk/

# Carry owners and SLAs forward from an earlier run
/risk-score path/to/threat-model-output/ --baseline path/to/earlier-run/

# Name an architecture file that isn't at docs/security/architecture.md
/risk-score path/to/threat-model-output/ --architecture-path docs/design/architecture.md

# Score a specific example
/risk-score examples/agentic-app/sample-report/
```

## Quality Checklist

- [ ] Risk-scorer agent, `tachi-stage.py` and `render-risk-scores.py` installed
- [ ] Python 3.9 or later present (the presence check passed)
- [ ] Input file exists (threats.md or threats.sarif)
- [ ] Input format correctly detected (markdown canonical, SARIF fallback)
- [ ] Architecture file located when available (improves reachability scoring)
- [ ] The plan was made once, and every batch was dispatched with the fixed prompt
- [ ] `reconcile` exited 0 before the renderer ran
- [ ] The renderer exited 0 or 5, and both output files were written by it
- [ ] Every finding scored with four dimensions (CVSS, exploitability, scalability, reachability)
- [ ] Scored threat table sorted by composite descending
- [ ] One SARIF result for each open finding, and its fingerprint is tachi's own hash
- [ ] Scores consistent between risk-scores.md and risk-scores.sarif
- [ ] The summary printed is the renderer's, with no number restated
