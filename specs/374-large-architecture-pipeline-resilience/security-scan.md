# Security Scan Report

**Feature**: 374 — large-architecture-pipeline-resilience (PR 1, the W3 tip)
**Branch**: 374-large-architecture-pipeline-resilience
**Commit**: f43440bc6347
**Scan ID**: 7bb73e5b-6948-4a56-aad3-428088befb18
**Timestamp**: 2026-11-24T04:11:35Z UTC
**Status**: PASSED

No CRITICAL or HIGH finding, so the build gate does not block. The scan did find 2 MEDIUM, 1 LOW and 1 INFO finding that the T064 advisory (`test-results/security-advisory-pr1.md`: 0 CRITICAL, 0 HIGH, 2 MEDIUM, 11 LOW, 5 INFO) did not have. T064's findings are referenced below by their IDs (SA-1 to SA-18) and not restated.

**Scope.** `git diff --name-only b040fa1...f43440b`, which is 399 paths. The shipped scripts were scanned as production code (C-9, TL-T5). That overrides the knowledge-system supplement's "no application code" framing, as F-373 and F-391 did.

---

## Summary

| Category | Count |
|---|---|
| Files scanned (SAST) | 40 (30 added, 10 modified), plus 1 deleted file that was checked for dangling references |
| Manifests audited (SCA) | 0 |
| CRITICAL findings | 0 |
| HIGH findings | 0 |
| MEDIUM findings | 2 |
| LOW findings | 1 |
| INFO findings | 1 |

---

## The scripts in this scan

Every script the diff adds, then the ones it changes or retires.

| Script | Status | Lines | What this scan did |
|---|---|---|---|
| `scripts/render-risk-scores.py` | new | 1,941 | AST scan, entry and error paths, staged write, and the 149-line change made after T064's tip |
| `scripts/render-compensating-controls.py` | new | 2,102 | The same, with the 173-line change after T064's tip (SA-2's ruling) |
| `scripts/tachi-stage.py` | new | 1,262 | CLI, plan input and pointer handling, move-and-restore and `fail` read. Finding S7-4 |
| `scripts/tachi_parts.py` | new | 1,774 | `atomic_write`, the ID allow-lists and the forbidden-character set read. Finding S7-3 |
| `scripts/tachi_scoring.py` | new | 526 | First review: T064 left its arithmetic out. No float enters stored values, the private decimal context traps float operations, and every parsed number sits behind a fixed-width pattern. No finding |
| `scripts/tachi_scoring_rules.py` | new | 1,566 | Reader prelude, `_read_bytes`, numeric conversions and the post-T064 change read. All 27 patterns probed. No finding |
| `scripts/sarif_common.py` | modified (+1,385, −13) | 1,542 | The task brief lists it with the new scripts, but the diff shows it existing at `main`: it is the shared emitter, extended. Resolver prelude, post-T064 change and `_id_token_pattern` read. No finding |
| `scripts/tachi_parsers.py` | modified (+922, −19) | 2,997 | Section 7 reader, numeric conversions, SARIF loader and the post-T064 change read. Finding S7-1 |
| `scripts/extract-report-data.py` | modified (+8, −6) | 3,034 | Whole diff read: `decode_references` runs on each cell after the row is split. No finding in the change |
| `scripts/extract-infographic-data.py` | modified (+5, −4) | 2,511 | The same |
| `scripts/generate-risk-scores-sarif.py` | retired (−657) | — | `git grep` finds no live reference: no workflow, command, install file or script names it. Only documentation and comments do |
| `tests/scripts/generate_large_arch_fixture.py` | new test tool | 4,756 | Synthetic fixture generator. It writes only under its `--out` |

The 9 new and 6 modified test modules and the 14 stub-codebase fixture files were scanned too (AST, secrets, process and filesystem calls). There is no `shell=True`. The two `rmtree` calls act on directories the tests created. The 14 stubs are secure-by-design sketches (parameterised query, constant-time compare, ES256, TLS 1.3) and carry no vulnerable construct.

## Method and limits

- **AST triage** of the 40 files (61,461 lines) for code execution, process, deserialization, temp-file, filesystem, network, weak-crypto, environment, `assert`-as-validation and broad-`except` constructs. In the new scripts there is no `eval`, `exec`, `compile`, `pickle`, `subprocess`, `os.system`, network call, `random`, weak hash, environment read or `assert`. The only third-party import in a shipped script is `yaml`, imported inside a function of `extract-report-data.py` (`:1366`), far from this branch's changes there. The three broad `except Exception` sites are the calculator self-test in `render-risk-scores.py` and the `main` of each renderer, and each maps to a documented exit code. The one `except BaseException` is `atomic_write`'s cleanup, which re-raises.
- **Regex backtracking probe** over 237 patterns (every module-level pattern by import, every literal pattern in a function by AST), each fuzzed with adversarial shapes under a 2 s timer. Ten distinct patterns were flagged: 2 are real and new (S7-1), 3 are only slow under `search` but are called through `match` or `fullmatch`, and 5 sit in unchanged lines (O-4). The probe is a heuristic over generated shapes, not a proof.
- **Crash fuzz**: 360,000 calls (two seeds, 30,000 rounds each, six call forms) into four new parsers (the Section 7 reader, the correlation-group reader, the controls assessment-input reader and the SARIF member reader, with and without scores) and into the baseline front-matter reader, which predates the branch. No exception outside the documented refusal types, and no call over 3 s.
- **Secret scan** over all 198,882 added lines of the diff, every file type: 0 hits (cloud keys, private keys, tokens, credential assignments, URL credentials).
- **The seven script files that changed after T064's tip** (`1493efb` to `f43440b`): their changes were read in full. See "T064 advisory: status at this tip".
- **Supplementary, outside the skill's extension filter**: the two CI workflow diffs, and the shell quoting of the command texts that invoke these scripts (which T064 left out).
- **Not covered**: a line-by-line read of the renderer bodies and of `reconcile`'s internals (T064 covered part validation and path handling there, and this scan leans on it plus the mechanical passes); PR 2's writers; the agent prompt-injection surface (#360). Model behaviour was not exercised for S7-2.
- Probes ran in scratch clones only. The lane worktree was clean until this scan's own writes.

---

## Findings

### CRITICAL

None.

### HIGH

None.

### MEDIUM (Review recommended before deploy)

#### tachi-VULN-04622b75c906: A04 Insecure Design — quadratic regex in the Section 7 reader (S7-1)

- **Type**: SAST
- **File**: `scripts/tachi_parsers.py:1465` and `:1468` (the separator pattern is defined at `:1387`)
- **CVSS**: 5.5 MEDIUM, estimated (AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H). CWE-1333
- **EPSS**: Algorithmic-complexity denial of service is exploited mostly against network services. Here the exposure is a stalled or CI-bound run. Not scored per finding.
- **KEV**: N/A
- **Introduced by**: this branch. `parse_reference_set` and `_TITLE_SEPARATOR` do not exist at `main`.
- **Description**: The numbered-list form of Section 7 is read by `_ids_of_a_bolded_lead`. It splits each bold lead with `_TITLE_SEPARATOR.split(bold, 1)` and then `re.split(r"\s*\+\s*", head)`. Both scan from every start position, so a run of n whitespace characters costs O(n²). Measured through the public entry `parse_reference_set` in a scratch clone: 2,500 spaces took 0.04 s, 10,000 took 0.57 s and 40,000 took 9.2 s (16 times per 4 times the length). A 160,000-character line of letters, the control, took 0.007 s. The input cap is 16 MiB per file and not per line, so one line can be the whole file. The planner (`tachi-stage.py:460`) and both renderers (`render-risk-scores.py:645`, `render-compensating-controls.py:823`) call it before any agent runs, so a crafted `threats.md` or baseline stalls the stage.
- **Recommendation**: Replace the separator with `re.compile(r"(?<=\s)[—–-](?=\s)")` and the plus split with `[token.strip() for token in head.split("+")]`. Both are linear (2.56 million characters in 0.04 s) and gave the same heads and tokens as today's code on 300,000 random strings. Add a regression test in `tests/scripts/test_tachi_parsers.py` (the ratchet file, H15): a 200,000-character whitespace run in a bold lead, under a timeout. About 0.03 d.

#### tachi-VULN-0b32c5afe282: A03 Injection — unquoted, repository-derived placeholders in shell command templates (S7-2)

- **Type**: SAST (supplementary: the command texts are Markdown, outside the skill's extension filter, so its code-sink rubric does not apply and this severity is an analyst estimate)
- **File**: `.claude/commands/tachi.risk-score.md:150` (plan), `:186`, `:206`, `:235`. Also `.claude/commands/tachi.compensating-controls.md:127`, `:164`, `:184`, `:215` and `.claude/commands/tachi.threat-model.md:216`
- **CVSS**: 6.2 MEDIUM, estimated. Base 7.0 (AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H), temporal 6.2 (E:U/RL:U/RC:R). CWE-78
- **EPSS**: No code sink, so no class rate applies. Exploitation depends on model behaviour and the permission gate (see #360).
- **KEV**: N/A
- **Introduced by**: extended by this branch. The same unquoted form already exists at `main` for the `populate-affected-assets.py` calls. The branch adds the `tachi-stage.py` and renderer calls.
- **Description**: Each command tells the model to run `python3 scripts/... --out {output_dir} ... --threats {input_dir}/threats.md` and similar, with no quotes. `{input_dir}` is either typed or auto-detected by globbing `docs/security/*/` and taking the newest directory, so the scanned repository chooses the name. `{output_dir}` defaults to the input directory. A directory name with shell metacharacters reaches the shell before any script runs, so `tachi_parts.path_problem` and the other path checks cannot help. Exploitation needs a hostile directory in the scanned repository, a model that substitutes the name without quoting it, and a permission gate that lets the command through. The values `{plan_id}`, `{plan_digest}` and `{reason}` are allow-listed script output and are not the problem.
- **Severity note**: The base score is 7.0, which is HIGH. I rated it MEDIUM because no exploit is known and the last two conditions above are not under the attacker's control. If the team reads the base score as the severity, treat it as HIGH: the fix is the same and small.
- **Recommendation**: (1) Quote every path placeholder in the command texts, for example `--out "{output_dir}"`, `--threats "{input_dir}/threats.md"`, `--target "{target_path}"`, `--architecture "{architecture_path}"`, in the three commands and in the `populate-affected-assets.py` calls. (2) Add one rule to each command's input step: a typed or discovered directory name must match `[A-Za-z0-9._/-]+`, otherwise skip it (when auto-detecting) or stop. (3) Pin it in `tests/scripts/test_contract_text_374.py`: every placeholder in a `python3 scripts/...` line other than `{plan_id}`, `{plan_digest}`, `{reason}`, `{scoring_date}` and `{analysis_date}` is double-quoted. About 0.05 d. The wider class, repository text steering an agent, stays with #360.

### LOW

#### tachi-VULN-0bbf78df23ef: A01 Broken Access Control — `atomic_write` sets the mode by path (S7-3)

- **Type**: SAST
- **File**: `scripts/tachi_parts.py:1563` (and `:1561`)
- **CVSS**: 2.5 LOW, estimated (AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:N). CWE-367
- **EPSS**: Time-of-check to time-of-use races on a local path are rarely exploited without write access to the directory.
- **KEV**: N/A
- **Introduced by**: this branch (`atomic_write` is new). It is the function T064's SA-4 names.
- **Description**: After the temp file's descriptor is closed, `atomic_write` calls `os.chmod(temporary, ...)` on its path. A link swapped in at that name before the call would have its target's mode changed to `0666 & ~umask`. The function also reads the process umask by setting it to 0 and restoring it, a process-wide change that a thread, or a signal between the two calls, can observe. Both need write access to the output directory, where an attacker already holds the canonical files, and the stage is single-threaded, so the risk is small.
- **Recommendation**: Call `os.fchmod(descriptor, ...)` before the descriptor is closed (guard with `hasattr(os, "fchmod")`), and read the umask once at import. Land it with SA-4's fix, which also sets the mode on the descriptor: when the target exists, give the temp file the target's permission bits. About 0.03 d.

### INFO

#### tachi-VULN-e29065b7c07a: A04 Insecure Design — `_input_entry` reads a pointer file with no cap and follows links (S7-4)

- **Type**: SAST
- **File**: `scripts/tachi-stage.py:350`. Call sites `:342`, `:500` and `:502`
- **CVSS**: not scored (hardening). CWE-770
- **KEV**: N/A
- **Introduced by**: this branch
- **Description**: `_input_entry` reads a whole file with a plain `open` and `read()`. Every other input read in these scripts uses the 16 MiB cap and the no-follow reader. The risk-score stage reaches the uncapped read with an operator-named `--risk-scores` file that nothing else reads first (the command text never passes the flag). At `:500` it re-reads the baseline `risk-scores.md` that the capped reader has just accepted, and at `:502` it reads that baseline's SARIF after a `getsize` check. That is SA-6's double read, now without the cap and the no-follow guarantee. No attacker path exists beyond the operator's own arguments, or an injected one (#360), so this is hardening.
- **Recommendation**: Read through the capped no-follow reader (`tachi_scoring_rules._read_bytes` or `tachi_parts`' equivalent), and pass the bytes the baseline reader already has, as SA-6's fix does. About 0.03 d.

---

## T064 advisory: status at this tip

Checked in the code at `f43440b`.

| T064 finding | At this tip |
|---|---|
| SA-1, SA-3, SA-4, SA-5, SA-6, SA-7, SA-8, SA-10, SA-11, SA-12, SA-13 | Present, unchanged |
| SA-2 | Resolved by W3's ruling on the controls render (question 5): an evidence file the resolver refuses is flagged (`input:evidence.file:unresolved`, warning `evidence-file-unresolved`, exit 5) and no longer ends the render. `tachi_parts.evidence_path_problem` (`:429`) now has no caller (O-1) |
| SA-9 | A ruling, unchanged: no escaper changed after T064 |
| SA-14 to SA-18 | INFO, unchanged: the code they name did not change |

The changes to the seven script files after T064's tip were read. The only effects on T064's findings are the one above and one strengthening: a lone surrogate (`U+D800` to `U+DFFF`) joins the forbidden set. The rest is documentation, wiring and the retirement of the old generator. S7-3 and S7-4 are new facets of SA-4 and SA-6: fix each with its T064 sibling.

## Observations (not counted)

- **O-1. A security helper with no caller.** `tachi_parts.evidence_path_problem` (`:429`) was written for the retry path that SA-2 proposed. W3 chose to flag instead, so nothing calls it. Delete it, or keep it with a note, so it does not rot.
- **O-2. CI supply chain.** The F-374 jobs in `.github/workflows/tachi-install-fidelity.yml` install test dependencies by lower bound (`pytest>=8`, `pytest-timeout>=2`, `pyyaml>=6`, and `pytest-cov>=4.1`, which is new) and pin the actions by tag (`checkout@v4`, `setup-python@v5`). The convention predates the branch. The workflows are otherwise sound: `pull_request` and not `pull_request_target`, `permissions: contents: read`, no secrets, and no `github.event` text interpolated into a `run:` step. A pinned requirements file with hashes, and action commit SHAs, would make CI reproducible.
- **O-3. Pre-existing crash paths on hostile cells** (unchanged lines of `tachi_parsers.py`, reached by the report and infographic extractors). `_parse_int` (`:137`) raises `ValueError` for a cell with more than 4,300 digits on a CPython with the int-string limit, and `parse_compensating_controls_md` (`:2358` to `:2368`) raises on a risk-reduction figure of `.`. Both verified in a scratch clone.
- **O-4. Pre-existing patterns the probe flagged** in unchanged lines: `extract-report-data.py:875`, `:877` and `:882` (Mermaid parsing), `extract-infographic-data.py:635` and `tachi_parsers.py:2729`. Same quadratic class as S7-1. Their call shapes were not traced. Candidates for T080.
- **O-5. Scan-log chain.** Two earlier entries do not verify under `.security/README.md`'s rule: entry 5 (F-112) hashes with no predecessor, and entry 34 (F-338) chains from the entry before its predecessor, which looks like two scans appending from one head. The log is append-only, so it was not edited. This scan's entry chains from the stored hash of the last entry and verifies from there.

## Carried open from earlier scans

- `tachi-VULN-d229b69fb5e4` (LOW, F-391): build mode follows links in `scripts/extract-report-data.py`. The file is in this diff, but none of this branch's changes is near the code (`:2536` to `:2548`, `:2562` to `:2568`). Still open. It is not marked REMEDIATED.
- `tachi-VULN-e9b741b0e343` (INFO, F-185): a helper under `specs/185-cwe-catalog-expansion/`. Not in this diff, not re-evaluated.

## SCA

SCA: No dependency manifests changed — skipping dependency audit.

No `requirements.txt`, `pyproject.toml`, `package.json`, lock file or other manifest from the skill's list is in the diff, so no CycloneDX SBOM was written (step 6e writes one when a manifest changed). The shipped scripts import the standard library and each other only (see Method). The CI dependency ranges are in O-2.

> SCA findings are based on Claude training knowledge (cutoff: August 2025). Supplement with real-time CVE scanning (npm audit, pip-audit, Snyk) for production workloads.

## Acknowledgment Decisions

No acknowledgment decisions made in this scan.

---

## Artifacts

- Scan log: `.security/scan-log.jsonl` (one entry appended)
- Vulnerability events: `.security/vulnerabilities.jsonl` (four DETECTED events appended)
- Risk acceptances: `.security/exceptions.jsonl` (none: no blocking finding)
- SARIF report: `.security/reports/f43440bc6347.sarif`
- CycloneDX SBOM: not written (no manifest changed)

**Init-baseline target.** `tests/fixtures/regenerate-baseline.sh` treats one file under `.security/` as a substitution target: `reports/8ab6c9c718cb980629717b1216c12587f861411e.sarif`, whose baseline copy is `tests/fixtures/init-baseline-tree/.security/reports/` with the same name. This scan does not edit it, and the files it adds match none of the script's placeholder patterns. The script's target selection was re-run read-only before and after the writes: the same 61 files both times, equal to the 61 files of the baseline tree, so no regeneration is needed for them.

---

*Security Scan: AI-powered analysis; supplement with dedicated SAST tools for production-critical systems.*
*SCA findings are based on Claude training knowledge (cutoff: August 2025). Supplement with real-time CVE scanning (npm audit, pip-audit, Snyk) for production workloads.*
