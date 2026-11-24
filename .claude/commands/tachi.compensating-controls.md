---
description: Scan a target codebase against scored threats to detect existing security controls, recommend missing controls, calculate residual risk, and output dual-format results (compensating-controls.md + compensating-controls.sarif)
---

## User Input

```text
$ARGUMENTS
```

Consider user input before proceeding (if not empty).

## Step 0: Parse Flags

1. If `$ARGUMENTS` contains `--target <path>`:
   - Set `target_path` to the specified path
   - Strip `--target <path>` from `$ARGUMENTS` (trim extra whitespace)
2. Default: `target_path = "."` (current working directory)

3. If `$ARGUMENTS` contains `--output-dir <path>`:
   - Set `output_dir` to the specified path
   - Strip `--output-dir <path>` from `$ARGUMENTS` (trim extra whitespace)
4. Default: `output_dir = null` (outputs written to same directory as input risk-scores)

5. If `$ARGUMENTS` contains `--baseline <run-dir>`:
   - Set `baseline_dir` to the specified path (a path to a file counts as the directory that holds it)
   - Strip `--baseline <run-dir>` from `$ARGUMENTS` (trim extra whitespace)
6. Default: `baseline_dir = null` (the run uses the baseline that the threat model behind `risk-scores.md` names in its `baseline.source`, and scans every finding fresh when it names none)

7. If `$ARGUMENTS` contains `--architecture-path <path>`:
   - Set `architecture_flag` to the specified path
   - Strip `--architecture-path <path>` from `$ARGUMENTS` (trim extra whitespace)
8. Default: `architecture_flag = null` (the scripts then take the architecture file from the `**Architecture source**` line of the threat model, and from `docs/security/architecture.md` after that)

9. Remaining `$ARGUMENTS` is treated as the risk-score input directory path.
10. If no input directory was provided in `$ARGUMENTS`:
    - If `./docs/security/` exists in cwd: glob `docs/security/*/`, sort directory names descending (ISO-like `YYYY-MM-DDTHH-MM-SS` timestamps sort correctly as strings), and select the newest directory that contains `risk-scores.md` or `risk-scores.sarif`. Set `input_dir` to that path and display: `Auto-detected input: {input_dir}`.
    - Otherwise, default to current working directory (`.`).

This command takes no date flag. It sets the analysis date once, in Step 2.

## Overview

Single-command entry point for tachi compensating controls analysis — the third link in the pipeline: `/threat-model` → `/risk-score` → `/compensating-controls`. Validates prerequisites, locates risk score input and target codebase, plans the findings into batches, dispatches the control-analyzer agent once per batch, and runs the shipped renderer, which writes the output files.

**Flow**: Validate → Plan → Dispatch → Reconcile → Render → Report

**Output suite** (written by `scripts/render-compensating-controls.py`, never by an agent):
- `compensating-controls.md` — Coverage matrix, control details with file:line evidence, recommendations, residual risk summary, and analysis integrity
- `compensating-controls.sarif` — SARIF 2.1.0 with per-finding residual scores, control properties, and tachi's own alert keys

**Who does what**: the control-analyzer agent supplies judgment only (for each finding, the control status and category, the code evidence, and the recommendation for a gap) and writes one part file per batch. The scripts plan the batches, reconcile them from disk, compute every score, band, factor and total, and write both files. This command runs only the shipped scripts it names, `scripts/tachi-stage.py` and `scripts/render-compensating-controls.py`, each as a single `python3` call with literal arguments. It writes no script of its own, and it stops on a failure rather than working around it.

## Step 1: Validate Prerequisites

1. **Check tachi agents and scripts are installed**:
   - Verify `.claude/agents/tachi/control-analyzer.md`, `scripts/tachi-stage.py` and `scripts/render-compensating-controls.py` exist, and so do the helpers that the scripts import: `scripts/tachi_parts.py`, `scripts/tachi_scoring.py`, `scripts/tachi_scoring_rules.py`, `scripts/sarif_common.py` and `scripts/tachi_parsers.py`
   - If any is missing, display:
     ```
     TACHI CONTROL ANALYZER NOT INSTALLED
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

3. **Check risk score input exists**:
   - Look for `risk-scores.md` in the input directory
   - If not found, look for `risk-scores.sarif` in the input directory
   - If neither exists, display:
     ```
     NO RISK SCORE OUTPUT FOUND
     Neither risk-scores.md nor risk-scores.sarif found in: {input_dir}
     Run /risk-score first to generate scored threat output.
     ```
   - Halt if neither exists.

4. **Determine input file and format**:
   - If `risk-scores.md` exists: set `input_file = risk-scores.md`, `input_format = markdown`
   - If only `risk-scores.sarif` exists: set `input_file = risk-scores.sarif`, `input_format = sarif`
   - `risk-scores.md` is the canonical source; `risk-scores.sarif` is the fallback. The planner reads the fallback when `risk-scores.md` is absent (ADR-050 D8), so this command never parses either file itself.
   - Display: `Input: {input_file} ({input_format} format)`

5. **Validate target codebase**:
   - Verify `target_path` is an existing directory with at least one file
   - If directory does not exist, display:
     ```
     TARGET CODEBASE NOT FOUND
     Directory does not exist: {target_path}
     Provide a valid project path via --target.
     ```
   - Halt if invalid.
   - Display: `Target: {target_path}`

6. **Determine output directory**:
   - If `--output-dir` was specified: use that path
   - Otherwise: use the same directory as the input file
   - Create output directory if it does not exist
   - Display: `Output: {output_dir}`

7. **Architecture file** (optional):
   - The command passes an architecture file only when `--architecture-path` was given (Step 2), and it looks for no `architecture.md` of its own: the path it passes becomes the URI of every SARIF result, so a per-run snapshot must never stand in for it
   - The planner checks the path, and the agents get only a path that passed the check. With none, they map components to files by heuristic discovery

## Step 2: Plan the Batches

**IMPORTANT**: Pass file **paths**, never file contents. The planner reads the scored input once and writes one batch input file per batch. The control-analyzer agent reads its own batch input.

1. Set `analysis_date` to today's date as `YYYY-MM-DD`, once. The plan keeps the date, so a resumed run uses the plan's date, and no later step takes one.

2. Plan the batches:

   ```bash
   python3 scripts/tachi-stage.py plan --stage compensating-controls --out {output_dir} --date {analysis_date} --risk-scores {input_dir}/risk-scores.md --target {target_path}
   ```

   - Add `--baseline-dir {baseline_dir}` when `--baseline` was given.
   - Add `--architecture {architecture_flag}` when `--architecture-path` was given, and only then. The URI of every SARIF result comes from this path, so a per-run snapshot must never stand in for it.
   - Always pass the `risk-scores.md` path, even when only `risk-scores.sarif` exists: `plan` reads `risk-scores.sarif` when `risk-scores.md` is absent.
   - Pass no threat model path. The planner reaches the `threats.md` that the scored input names as its source through the `source_file` of `risk-scores.md`, under its own checks.

3. `plan` prints one JSON object: `plan_id`, `plan_digest`, and `waves`, a list of waves with at most 16 batches each. Every batch is `{batch_id, input_path}`. Keep `plan_id` and the latest `plan_digest` for every later step. A step that prints a newer `plan_digest` replaces it.

4. Route by the exit code:

   | Exit | What to do |
   |------|------------|
   | 0 | Go to Step 3 |
   | 1 | Stop and print the error |
   | 2 | Stop and print the error. No plan exists yet, so there is nothing to fail |

## Step 3: Dispatch the Batches

Dispatch the waves in order, one wave at a time. For each batch in a wave, call the Agent tool with `subagent_type` set to `tachi-control-analyzer` and with this prompt, and no other:

```text
Read and follow the batch input at <input_path>. Write only the part file it names.
```

Replace `<input_path>` with that batch's `input_path`. Send all of a wave's Agent calls in one message, so that they run together. Never send more than 16 in one message, and start a wave only after every agent of the wave before it has reported completion.

Run `reconcile` only after every agent in the wave has reported completion. While an agent you dispatched is still running, don't run the renderer, report a result or end the stage. If you end your turn to wait, resume this loop on each completion notice.

If an Agent call fails because `tachi-control-analyzer` can't be spawned, end the run there. Run no substitute, and dispatch no other agent type. Go to Step F with `--reason agent-not-spawned` and `--detail tachi-control-analyzer`. An agent that was spawned and then failed is not a spawn failure: `reconcile` finds its part missing or invalid and plans the retry.

## Step 4: Reconcile

Reconcile from the files on disk, never from an agent's reply:

```bash
python3 scripts/tachi-stage.py reconcile --stage compensating-controls --out {output_dir} --plan {plan_id} --plan-digest {plan_digest}
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

Run the renderer. It re-validates every part, computes the values (each finding's inherent score and band come from this run's scored input and are never scored again), writes both files to the plan's staging directory, re-reads them and checks them (row parity with the scored input, one SARIF result for each open finding, and agreement between the two files), and only then moves each onto its canonical name. A failed check leaves the canonical files as they were.

```bash
python3 scripts/render-compensating-controls.py --out {output_dir} --plan {plan_id} --plan-digest {plan_digest}
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
  1. Review Critical/High unmitigated findings in compensating-controls.md Section 4
  2. Implement recommended controls starting from highest-risk gaps
  3. Upload compensating-controls.sarif to GitHub Code Scanning with category `compensating-controls`
  4. Run /infographic to generate visual threat infographics (uses compensating-controls.md as richest data source)
  5. Run /security-report to generate the PDF assessment booklet (auto-includes infographic images)
  6. Re-run /compensating-controls after implementing controls to measure improvement
```

## Step F: Fail

Run this step only when an earlier step sends you here, and only once a plan exists:

```bash
python3 scripts/tachi-stage.py fail --stage compensating-controls --out {output_dir} --plan {plan_id} --plan-digest {plan_digest} --reason {reason}
```

- `{reason}` is the one the step named: `agent-not-spawned`, `unrecoverable-batch`, `check-failed` or `render-failed`.
- For `agent-not-spawned`, add `--detail tachi-control-analyzer`.
- `fail` records the failure, moves any output this run changed into the plan's `failed/` directory, and puts the earlier run's outputs back, so the output directory never holds a failed file under a canonical name.
- Then stop with the four-line `TACHI COMPENSATING-CONTROLS FAILED` error that `fail` printed. Whatever `fail` exits with, stop there. `fail` never runs a second time.

## Usage Examples

```text
# Minimal — analyze codebase in current directory using risk-scores in cwd
/compensating-controls

# Specify target codebase
/compensating-controls --target ./my-app

# Specify both target and output
/compensating-controls --target ./my-app --output-dir ./reports/

# Carry control results forward from an earlier run
/compensating-controls --target ./my-app --baseline path/to/earlier-run/

# Name an architecture file that isn't at docs/security/architecture.md
/compensating-controls --target ./my-app --architecture-path docs/design/architecture.md

# Analyze the example app
/compensating-controls --target examples/agentic-app/ examples/agentic-app/sample-report/
```

## Quality Checklist

- [ ] Control-analyzer agent, `tachi-stage.py` and `render-compensating-controls.py` installed
- [ ] Python 3.9 or later present (the presence check passed)
- [ ] Risk score input exists (risk-scores.md or risk-scores.sarif)
- [ ] Input format correctly detected (markdown canonical, SARIF fallback)
- [ ] Target codebase validated (directory exists with files)
- [ ] The plan was made once, and every batch was dispatched with the fixed prompt
- [ ] `reconcile` exited 0 before the renderer ran
- [ ] The renderer exited 0 or 5, and both output files were written by it
- [ ] Every open finding classified (Control Found / Partial / No Control Found), once in each file
- [ ] Residual risk computed by the renderer for every open finding, and the totals equal the sums of the rows
- [ ] One SARIF result for each open finding, and its fingerprint is tachi's own hash
- [ ] Scores consistent between compensating-controls.md and compensating-controls.sarif
- [ ] The summary printed is the renderer's, with no number restated
