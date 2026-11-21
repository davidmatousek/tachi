# Security review: B1 archiver, refusal path and redaction design (T034)

**STATUS: PASS_WITH_FINDINGS.** 0 CRITICAL, 3 HIGH, 4 MEDIUM, 8 LOW. The structure is sound: the order of the refusal checks, the file modes, structural redaction, scan before write, and error messages that never echo a value all hold. Three HIGH findings can defeat the SC-007 destination rule or cross the isolation boundary at the post-session step. Fix them, and add the named tests in the last section, before part-b merges. This review changed no code.

| Item | Value |
|---|---|
| Task | T034 (`tasks.md:144`), W1 |
| Reviewer | `security-analyst` |
| Date | 2026-11-19 |
| Reviewed | `scripts/archive-run-transcripts.py`, `schemas/run-manifest.yaml`, `tests/fixtures/transcripts/**` at `f9b5c0a` (branch `391-isolated-auditable-operation-part-b`). Line numbers below are for that commit. |
| Contracts read | `contracts/run-manifest.md`, `contracts/cli-contracts.md`, `data-model.md`, `plan.md` AD-6, `tasks.md` T032 and T034, `test-results/p0-b0-precheck.md` (P0B0-1 to P0B0-11), SBE-B1's W1 notes |
| Method | A full read of the archiver, then runs in a scratch clone at `f9b5c0a` on the system Python 3.9 interpreter with `-I -B`. Every run used a temporary `HOME`, a temporary `CLAUDE_CONFIG_DIR` and a temporary `--dest`, on the synthetic fixtures only. The real `~/.claude` and `~/.tachi` were never touched and no real transcript was read. Key-shaped dummy values were assembled at runtime from fragments, were never printed and were never written to a tracked file. The harness scripts are scratch files and are not committed. |

## SC-007 status

| SC-007 clause | Status at `f9b5c0a` |
|---|---|
| A destination inside any git work tree is refused unless ignored | Met for plain ignore rules (a directory rule, a whitelist, no rule). **Not met** when an ignore rule matches the probe file but not the files the run writes (H-1). Work trees with no `.git` entry are not seen (M-4). Repository config can run a program during the check (H-2). |
| Owner-only modes | **Met.** Exact 0700 and 0600 under umask 000, 022 and 077; files are created with `O_EXCL` and mode 0600, directories with 0700, so there is no window at a wider mode. |
| No planted key in the manifest | **Met** for the six planting sites in both fixture generations and for a raw secret at any manifest position. **Not met** for encoded forms of a secret (M-1) or for padded and multi-line variable values (M-2). Not checkable when the secret-bearing environment is absent, and nothing says so (M-3). |
| A scan hit writes no manifest | **Met.** Exit 1, no manifest, no temporary file, and the message names the rule or the variable, never the value. |

Recommendation to the lane and to T045: do not record the first and third clauses as met in `delivery.md` until H-1, M-1 and M-2 are fixed and tested.

## Findings

| ID | Severity | Finding | Location | Owner |
|---|---|---|---|---|
| H-1 | HIGH | The ignore check probes `<dest>/.probe`, not the files the run writes, so an ignore rule that matches dotfiles accepts a destination that is not ignored | `scripts/archive-run-transcripts.py:541`, `:548-549` | SBE-B1, SBE-TB, T040 |
| H-2 | HIGH | `git check-ignore` runs a program named by the repository's `core.fsmonitor`, with the archiver's secret-bearing environment | `:506-510`, `:513-522`, `:549` | SBE-B1, SBE-TB |
| H-3 | HIGH | The script's own `scripts/` directory is first on `sys.path`: a stdlib-named file planted there runs in the unsandboxed, secret-bearing post-session shell | `:15` (usage), `:43-56` (imports) | SBE-B1, T048 |
| M-1 | MEDIUM | The environment-value scan does not match encoded forms (hex, base32, base64url) of a secret, which fit in host labels, model-chosen names and file names | `:1216-1258` (`:1256`) | SBE-B1, T040 |
| M-2 | MEDIUM | Values with trailing whitespace or several lines are never matched, and common secret-bearing names fall outside the name list | `:153`, `:1216-1224`, `:1256` | SBE-B1, T040 |
| M-3 | MEDIUM | A run without the secret-bearing environment checks zero values and says nothing | `:1216-1224`, `:1341-1344` | SBE-B1 |
| M-4 | MEDIUM | A work tree with no `.git` entry (bare-repository dotfiles layout, `GIT_DIR`, `core.worktree`) is not detected | `:494-503`, `:507`, `:541` | SBE-B1, T048 |
| L-1 | LOW | The no-op branch accepts a destination whose manifest was replaced, and ignores extra files | `:558-575`, `:1325-1331` | SBE-B1 |
| L-2 | LOW | No re-check after the destination is created; `chmod` follows a symlinked destination | `:591-607`, `:1324-1335` | SBE-B1 |
| L-3 | LOW | `--latest` does not validate the session stem, and file-name strings reach the manifest without the token rule | `:1298`, `:1318`, `:1129`, `:1134`, `:1206` | SBE-B1 |
| L-4 | LOW | The `--json` summary and stderr sit outside the scan | `:1164-1179`, `:1394-1400` | SBE-B1 |
| L-5 | LOW | The live-session rule looks at `.jsonl` modification times only | `:578-588` | SBE-B1, T048 |
| L-6 | LOW | A `--dest` under `CLAUDE_CONFIG_DIR` is accepted | `:352-356`, `:1322-1324` | SBE-B1 |
| L-7 | LOW | Key-format patterns have no boundaries (false refusals) and a short format list | `:136-151` | SBE-B1 |
| L-8 | LOW | The docstring says the manifest "is not" sensitive; it lists host names and file names | `:9-11` | SBE-B1, T048 |

## HIGH

### H-1: the destination check asks about `.probe`, not about the files it writes

`:548` builds `<dest>/.probe` and `:549` is the only ignore query. The contract text fixes the same probe (`cli-contracts.md:20`, `plan.md` AD-6), so the defect is in the contract as well as the code.

**Evidence.** Scratch work tree, `--dest <repo>/runs/x`, then `git status --porcelain -uall`:

| Work tree `.gitignore` | Exit | Committable untracked entries afterwards |
|---|---|---|
| none | 1 | 0 |
| `runs/` | 0 | 0 |
| `*` then `!.gitignore` | 0 | 0 |
| `*.jsonl` only | 1 | 0 |
| `.*` | **0** | **16** |
| `.probe` | **0** | **16** |
| `.p*` | **0** | **16** |
| `*probe` | **0** | **16** |

A rule that matches a dotfile ignores the probe, so the check passes, while `runs/x/<session>.jsonl` and its siblings are not ignored. The default layout under `~/.tachi/runs/...` is safe for `.*` because `.tachi` is itself a dot-directory; in a `$HOME` repository it was refused with no rule, and accepted for `.tachi/`, `.*` and `/.tachi/runs/` with zero committable entries. Only a rule that names probe-shaped files reaches the default layout.

**Impact.** A destination that must be refused is accepted, with no signal. The unredacted archive (architecture, code, findings, tool output that held keys) is then written as ordinary untracked files in the work tree, one `git add -A` from a commit.

**Fix.**
1. Ask about the paths the run will create, in one batched call: every `rel` in `source_files`, `run-manifest.json` and `.run-manifest.json.tmp`, as absolute paths, through `git check-ignore --stdin -z -n -v` run from the toplevel. Refuse unless every record names a matching rule; treat any other result as a refusal (deny by default). A prototype gave: `runs/` accepted, `*` accepted, `.*` refused, `.probe` refused, `*.jsonl` refused.
2. Defence in depth, after the check has passed: write `<dest>/.gitignore` containing `*` as the first file (`O_EXCL`, mode 0600). In the `.*` case it took the untracked entries from 16 to 0, and it also covers M-4. It is not part of `transcripts[]`, and the no-op comparison already ignores extra files. `schemas/run-manifest.yaml` `archive_layout` should then name it.
3. Update `cli-contracts.md:20` and `plan.md` AD-6 from "the `<dest>/.probe` check" to "the paths the run writes" (T040).

### H-2: git runs a repository-configured program during the destination check

`_git_env` (`:506-510`) removes only the nine location variables (`:128-132`) and passes every other variable on, secrets included. `_run_git` (`:513-522`) runs git in the work tree that is being judged.

**Evidence** (git 2.52.0). A work tree whose `.git/config` sets `core.fsmonitor` to a program: `git check-ignore` runs it; `git rev-parse --show-toplevel` does not. Started with the archiver's own environment handling, the program could see the secret-named variable. `core.hooksPath`, `core.pager`, `core.sshCommand`, a credential helper and `core.untrackedCache` did not run for either command. A command-line `-c core.fsmonitor=false` stopped it. A minimal environment alone removed the variable from the program's view but the program still ran. A full archiver run into such a work tree completed with exit 0 and the program having run.

**Impact.** Code execution as the operator, in the unsandboxed shell, with secret-named variables in its environment, caused by repository state. The query at `:549` runs before the refusal decision, so a refused destination triggers it too. The refusal text (`:553-554`) tells operators to "ignore the runs directory", which steers them to a destination inside the project's own work tree, the repository the session just ran in. Whether a sandboxed session can write that repository's `.git/config` is a Part A question (T020, T049); the archiver should not depend on the answer.

**Fix.** Put `-c core.fsmonitor=false` on every git call (command-line configuration wins over repository configuration) and pass git an allowlisted environment (`PATH`, `HOME`, `LANG`, `LC_*`, `TMPDIR`, plus the two variables set at `:508-509`) instead of the whole environment. Add the planted-`core.fsmonitor` test below.

### H-3: the script directory is first on `sys.path`

The documented invocation is `python3 scripts/archive-run-transcripts.py` (`:15`, `cli-contracts.md:16`). Python then puts `scripts/` first on `sys.path`, ahead of the standard library, for every import at `:43-56`.

**Evidence.** A copy of the script with a file named `ipaddress.py` beside it executed that file at import when started without `-I`, and did not with `-I`. Modules the interpreter loads at startup (`os`, for example) are not shadowable this way.

**Impact.** The archiver is the one step designed to run outside the sandbox, from a plain shell, with secrets in the environment, in the same project directory the session wrote to. A session that can write a stdlib-named file into the project's `scripts/` directory turns that run into code execution with those secrets. The same property holds for every tachi script, but this is the one run with this exposure by design.

**Fix.** The runbook (T048), the module docstring and `cli-contracts.md` should show `python3 -I -B scripts/archive-run-transcripts.py`. Add a guard so a plain invocation is safe too: after `from __future__ import annotations`, before `import argparse`:

```python
import os
import sys

if __name__ == "__main__" and not sys.flags.isolated and sys.executable:
    os.execv(sys.executable, [sys.executable, "-I", "-B"] + sys.argv)
```

On a scratch copy this stopped both a planted `ipaddress.py` and a planted `os.py` from running on a plain invocation, and loading the module by path (as the tests do) was unaffected because the guard runs only as `__main__`.

## MEDIUM

### M-1: encoded forms of a secret pass the scan

The scan (`:1242-1258`) tests whether the lower-cased raw value is a substring of a manifest string (`:1256`). A secret that appears hex-encoded, base32-encoded or base64url-encoded does not match.

**Evidence** (24-character dummy value in a secret-named variable; raw form exits 1 with no manifest in every position below):

| Position | Raw | Hex | Base32 | Base64url |
|---|---|---|---|---|
| `egress_observed[].host` (a DNS label, at most 63 characters, `[a-z0-9_-]`) | exit 1 | exit 0, in manifest | exit 0, in manifest | exit 0, in manifest |
| `dispatches[].agent` as `tachi-<token>` | exit 1 | not run | not run | exit 0, in manifest |
| a tool name (key of `tool_calls_by_tool`) | not run | not run | not run | exit 0, in manifest |
| `artifacts[].path` (a file name under `--output-dir`) | exit 1 | exit 0, in manifest | not run | not run |

These are the fields where a value is copied from model-chosen or file-system text: hosts (`:665-709`), `subagent_type` (`:859-861`, `:1063`), tool names (`:845`, `:852`) and artifact paths (`:1206`). Every other string field is written by Claude Code or computed.

**Impact.** The manifest is described as safe to share. An agent steered by injected text can hide a secret in a DNS-safe label or a name, and the manifest passes its own scan and carries it out.

**Fix.** For each scanned value derive and match these forms, all lower-cased: hex, base32 and base64 or base64url without padding, percent-encoding, and the JSON-escaped form when it differs. Standalone encodings are enough unless concatenated streams are in scope. Optionally record a host label longer than 40 characters as `<unparseable>`. Add the encoded-plant tests below.

### M-2: value shapes and names the scan cannot match

`:1219` applies the floor to the raw value, and `:1256` looks for the whole value as one substring. Manifest strings are single tokens with no whitespace.

**Evidence.** The same secret held with a trailing newline, with a trailing space, or inside a JSON blob (`{"client":...,"secret":...}`), and planted as a host label: all three exited 0 with the secret in the manifest. The names `PASSPHRASE` and `DATABASE_URL` are outside the five-word name list (`:153`; `data-model.md:34`), so those variables are never read.

**Fix.** Strip each value. For a value that contains whitespace or newlines (JSON credentials, PEM), also scan each whitespace-delimited fragment of 8 or more characters. Consider adding `PASSPHRASE|PASSWD|PWD|PRIVATE|AUTH|DSN` to the name list; the cost is a few more variables compared, and a hit still needs the value to appear in the manifest. T040 folds the list change into `data-model.md:34`.

### M-3: nothing says how much the scan checked

The environment-value half of the scan compares only against the archiver's own environment (`:1216-1224`). Run from a plain shell with no secret-named variable set, a normal session exited 0 and stderr held only the unrelated TW-B1 warning. Under the Part A profile the key is injected at the proxy and may never be in the operator's shell at all, so "run it under the same wrapper" can fail without any visible sign.

**Fix.** Print, and add to the `--json` summary, a line such as `secret scan: 3 environment value(s) checked (variable names listed), 13 format rules`, and warn on stderr when the count is 0. Add a test that asserts both.

### M-4: work trees with no `.git` entry

`_git_marker_above` (`:494-503`) looks for a `.git` entry and only then asks git (`:541`); `GIT_DIR` and `GIT_WORK_TREE` are stripped (`:128-132`, `:507`).

**Evidence.** A bare repository at `~/.cfg` used through an alias with `--git-dir` and `--work-tree` set to the home directory: the archiver accepted `--dest ~/runs/x` (exit 0), and the alias git listed 16 untracked entries under it. A plain `git rev-parse` without those variables cannot see this layout either, so this is not a regression from the contract text, but SC-007 says "any git work tree".

**Fix.** The in-archive `.gitignore` from H-1 removes the consequence. In addition, if `GIT_DIR` or `GIT_WORK_TREE` is set in the operator's environment, run the ignore query against that repository too before the variables are stripped. State in the runbook (T048) that Mercurial, Subversion and Jujutsu trees are not recognised.

## LOW

- **L-1: no-op trusts an unvalidated manifest** (`:558-575`, `:1325-1331`). "Finished" means a regular file named `run-manifest.json` exists. An extra planted file and a replaced manifest containing only `{}` both exited 0 with "already archived". For an audit record, parse the manifest on the no-op path and compare `session_id` and the `transcripts[]` hashes with the source; warn on extra files.
- **L-2: no re-check after creation** (`:591-607`, `:1324-1335`). After `_check_destination` passed, replacing an existing parent with a symlink into a work tree and then calling `_prepare_destination` created the directories inside the work tree. For a new destination the window is the span between `:1324` and `:1334`, which includes the `lstat` of every transcript in `_check_live` (`:1332`). It needs the same user or a writable parent. Separately, `os.chmod(dest_abs, ...)` at `:607` follows a symlinked destination and tightened a 0755 target directory to 0700. After creating the directories, compare `os.path.realpath(dest_abs)` with the checked path and refuse (removing only what this run created) on a difference; refuse a symlink as the final component.
- **L-3: stem and file-name strings skip the token rule** (`:1298`, `:1318`, `:1129`, `:1134`, `:1206`). `--session` is checked against `_SESSION_ID_RE`; `--latest` takes the stem from the file name unchecked. A stem of `a b<BEL>c` went into the manifest `session_id`. A stem of `..` made the source walk cover the whole `projects/` directory and was stopped only because `os.mkdir` on `<dest>/..` failed (exit 2). Apply the session-id pattern in `_discover` for both modes, and apply the token rule or a safe character set to recorded paths.
- **L-4: the summary is not scanned** (`:1164-1179`, `:1394-1400`). An unknown entry `type` that was key-shaped appeared in the `--json` summary on stdout while the manifest excluded it. The labels come from fields Claude Code writes, so likelihood is low. Scan the summary's strings before printing, or print counts only.
- **L-5: the live rule is mtime on `.jsonl` only** (`:578-588`, `:584`). A session idle for longer than the window, or waiting on a long tool run, passes; a change only in `tool-results/` does not count; `--live-window-seconds 0` and `--allow-live` switch the rule off; the no-op branch skips it. This affects completeness of the record, not confidentiality. Also stat the `.meta.json` files and print the age of the newest transcript; the runbook should say to archive after the session has ended.
- **L-6: a destination under the Claude config directory is accepted** (`:352-356`, `:1322-1324`). Claude Code's retention sweep can delete it, and `--latest` can later pick the archived copy as the newest main transcript. Refuse a `--dest` under `<config>/projects` and warn under `<config>` (SBE-B1's own note 14).
- **L-7: key patterns have no boundaries, and the list is short** (`:136-151`). Measured on the repository's 2,931 tracked paths: 0 flagged. All 3 of the long kebab-case artifact names I tried that contain `risk-`, `task-` or `disk-` followed by 32 or more name characters were flagged by `openai-api-key`. Lower-cased host names that start `asia`, `aida` or `aroa` and continue with 16 or more letters or digits were flagged by `aws-access-key-id` (3 of 3), and a real-format identifier inside a longer alphanumeric run still matches. A refusal has no override and the same `--dest` cannot be reused (P0B0-5), so each false refusal costs a new destination. Add a left boundary `(?<![A-Za-z0-9])` to all patterns and a right boundary to the fixed-length formats. The `bearer-credential` and `private-key-block` patterns need whitespace and so can only match path strings. Consider adding current formats (Hugging Face, GitLab personal access, npm, Google OAuth access, Supabase, xAI, Groq).
- **L-8: wording** (`:9-11`). "The manifest is not [sensitive]" overstates. It lists host names (internal ones among them), artifact file names and session ids, and the hash of a small low-entropy file can be guessed offline. Say that it holds no secrets and no message text, and that it should still be read before it is shared.

## P0B0-11: the secret-scan floor

**Ruling: KEEP the 8-character floor and the substring match on the lower-cased value. Do not add a minimum-entropy gate. The architect's text stands, with five amendments.**

| Option | False refusals of clean sessions | Missed secrets | Decision |
|---|---|---|---|
| Floor 8, substring, case-insensitive (current) | Only a value that is a dictionary word or host fragment of 8 or more characters in a secret-named variable | Values under 8 characters | **Keep** |
| Floor 6 | Rises: manifest words such as `sandbox`, `main`, `recorded` become collisions | Fewer | Reject |
| Floor 12 to 16 | Falls only slightly | Loses the 8 to 15 character passwords that real `*PASSWORD*` variables hold | Reject |
| Shannon-entropy gate | Avoids word collisions | Exempts exactly the weak, human-chosen secrets people store; unreliable on short strings | Reject. A hit means the literal value is present in the manifest, which is the case that must be refused. |

**Measured behaviour (secret-named variable, value planted as a host label):** 7 characters not detected; 8 characters detected; a 32-character hex value detected; the word `password` detected; a 12-digit numeric value skipped by the numeric rule; the word `registry` refused because it is a label of the fixture host `registry.example.test`, and the message named the variable and not the value. The floor behaves as ruled. False refusals from it are rare and self-explanatory. The larger practical source of false refusals is the pattern boundaries (L-7), and even that had 0 hits on the repository's real paths.

**Amendments.**
1. **Strip and fragment** (M-2): strip each value; scan whitespace-delimited fragments of 8 or more characters of multi-line values as well.
2. **Encoded forms** (M-1): scan hex, base32, base64 and base64url, percent-encoded and JSON-escaped forms of each value at or above the floor.
3. **Literal rules.** The boolean and null list (`:155`) is dead code under floor 8, because every member is shorter than 8 characters. The numeric rule (`:1221`) is the only literal rule with any effect. Narrow it to values that contain a separator (dates such as `2026-11-19`, versions, IP literals), which are the values that can collide with manifest strings. A string of 8 or more digits cannot be a substring of any manifest string, so scanning it costs no false refusals and covers numeric secrets.
4. **Patterns at any length, with boundaries** (L-7).
5. **Report coverage** (M-3), and keep "names the variable, never the value", which was confirmed on every failure path run.

**Residual.** A value under 8 characters is never scanned. It could reach the manifest only through the model-chosen token fields, it is weak by nature, and structural redaction remains the primary control.

## Reviewed and held

- Refusals create nothing: the live-session refusal, an unignored work tree, a symlink into a work tree and a non-empty destination all left no directory behind.
- `git` absent: exit 2 with nothing created when the destination is inside a work tree; the run proceeds when it is outside any.
- Symlinks: a parent, the destination, or a dangling link that resolves into a work tree is refused even when the target is ignored; a link to a non-work-tree directory is accepted by design and written behind; a dangling link elsewhere exits 2 and creates nothing; a `.git` file that points at a bare git directory, and a destination inside `.git/`, are refused because git cannot name a work tree. Symlinks and non-regular files in the source session tree are refused.
- Default destination in a `$HOME` repository: refused with no rule or a `*.jsonl`-only rule; accepted for `.tachi/`, `.*` and `/.tachi/runs/`.
- `CLAUDE_CONFIG_DIR`: honoured; relative values resolve against the current directory; an empty value falls back to `~/.claude`.
- Failure output: an invalid-JSON line, a tool name with whitespace and an over-long model id, each carrying a key-shaped dummy, exited 1 with no manifest and the dummy absent from stdout, stderr and `--json`.
- A scan hit on a raw value: exit 1, no `run-manifest.json`, no `.run-manifest.json.tmp`.
- Six planting sites, both fixture generations, with the key also held in a secret-named variable: exit 0, key absent from the manifest and from stdout and stderr, present in the verbatim archive as designed.
- The `--` separator and an absolute path are the only user text in git arguments; the `sha256` exclusion in `_iter_strings` (`:1233`) cannot hide a string value.
- The fixtures, script and schema hold no key-shaped value (the only hits are the by-design `fixture-user:__DUMMY_KEY__@` placeholder URL), no absolute path and no user name.

## Residual risks, no action in 391

- `pinned_model`, `tachi_agents_not_dispatched` and `tachi_version` are read from project files at archive time; a session with write access to those files could change them. The manifest is unsigned (BLP-03 scope). Recording a hash of each file read would let an auditor compare them with the install manifest.
- Egress is seen only through URLs in Bash commands and WebFetch inputs (the `AOD-SIMPLIFICATION` at `:695`).
- A pre-existing parent such as `~/.tachi` keeps its mode, so project names and session ids may be listable; the archive directory itself is 0700.
- Backup and indexing tools that read `~/.tachi` will copy the archive.

## Tests to add (T033) and text to carry (T040, T048)

**T033 named negatives.**
1. A work tree with `.*` as its ignore rule, and one with a `.probe`-matching rule: `--dest` inside is refused and nothing is created. A directory rule and the whitelist form are accepted.
2. A planted `core.fsmonitor` program in the destination's work tree does not run, for an accepted and a refused destination.
3. A planted stdlib-named module beside a copy of the script is not executed on a plain invocation.
4. A secret planted hex-encoded, base32-encoded and base64url-encoded in a host label, a `tachi-` name, a tool name and an artifact name exits 1 with no manifest.
5. A secret held with a trailing newline, and one held inside a JSON blob, exits 1 when planted.
6. A run with no secret-named variable prints the coverage line and the warning.
7. A no-op into a destination with a replaced manifest exits 1.
8. `--latest` with a stem that fails the session-id pattern is skipped or refused; a `--dest` under the config directory's `projects/` is refused.
9. A long `risk-...` artifact name and an `asiapacific...` host do not refuse a clean run; a standalone planted key still does.

**T040.** Fold into the contract text: the ignore query covers the paths written (`cli-contracts.md:20`, `plan.md` AD-6); the name list and the value rules above (`data-model.md:34`, `run-manifest.yaml` `redaction`); the in-archive `.gitignore` (`archive_layout`); the coverage line.

**T048.** The runbook invokes the archiver as `python3 -I -B scripts/archive-run-transcripts.py`, says to archive after the session has ended and under the same secret-bearing environment, lists the unrecognised tree types, and does not describe the manifest as non-sensitive.

**T035.** The leakage review of the recorded fixture stays with `security-analyst`; the scrub should include the encoded-form positions in M-1.

---

## T042: W3 snippet review (2026-11-20)

**STATUS: CLEARED_WITH_FINDINGS.** 0 CRITICAL, 1 HIGH, 1 MEDIUM, 6 LOW, 5 INFO. The profile block, the puppeteer snippet, T014's extractor change and the SEC-A application clear: the 18-rule block widens nothing, every added rule only narrows, and the extractor fails closed. The HIGH and the MEDIUM are runbook text, not code. The by-hand report build reopens the isolation boundary on files that the session can write (W3-H1), and two macOS statements about what other processes can read are narrower than what I measured (W3-M1). Fix both before T046. The six LOW items are recommended and the INFO items are optional. This review changed no tracked file except this one.

| Item | Value |
|---|---|
| Task | T042 (`tasks.md:170`), W3, after T021. Scope: the seven items in the brief, with the architect's rulings W3-1, W3-3, W3-3a and W3-5 |
| Reviewer | `security-analyst` |
| Date | 2026-11-20 |
| Reviewed | Part A tip `b2f5e54`. Runbook `docs/guides/ISOLATED_OPERATION_TACHI.md` sections 3, 4, 6, 9 and 11 (`:N` below is a runbook line at that commit unless a file is named), `scripts/extract-report-data.py`, `tests/scripts/test_isolated_profile_contract.py`, `contracts/session-profile.md`, `test-results/security-a.md`, `test-results/w2-live.md`, `.claude/agents/tachi/report-assembler.md` |
| Method | A full read of every snippet, then runs in a scratch clone of `b2f5e54`, with `git -C <clone> log -1` checked before each batch. The contract test and the extractor ran only there. A stub `mmdc` recorded its arguments and wrote a 1x1 PNG, so no browser started. `typst` ran for real. Secret managers and keys were dummies, and process environments were counted, never printed. The public Claude Code docs were read on 2026-11-20 for the rule forms, protected paths, agent teams, shell selection and the messaging variables. Before the clone existed, four read-only git queries ran in the main tree (status, log, rev-parse, worktree list) and wrote nothing. The scratch scripts deleted only their own generated output inside the clone. |
| Not done | No live Claude Code session. Linux, WSL2 and a real secret manager were not run. At `b2f5e54` the maintainer's re-check R1 to R6 was still pending (see the note below). |

**Note on later changes.** While this review ran, another lane recorded the key-less re-check in the working tree's runbook, in the header and in section 11 (not part of `b2f5e54`). It reports R1 to R6 and R4a passed on the same 3,156-byte block (same SHA-256), including a refusal of an Agent call that sets an isolation value, and the header now reads "Last validated: 2026-11-20". That closes the "pending" status of R4a and of the re-check wherever this section uses it (W3-I1 and Limits). It changes none of the findings: the text they name is still in the working tree, with section 11 line numbers 16 higher (the `ps` row at `:617` is now at `:633`). All line numbers in this section are for `b2f5e54`.

### Scope items

| # | Item | Verdict | Basis |
|---|---|---|---|
| 1 | Session profile block: 18 deny rules, `Agent(isolation:*)`, bare-name denies | **Clears** | Structure, diff against the profile that ran live, and the docs' own rule form. INFO W3-I1, W3-I2 |
| 2 | Linux puppeteer snippet, and the macOS text | **Clears** | The trade-off at `:429` matches the docs. The macOS text says not to set the variable (`:398`, `:411`). INFO W3-I3, LOW W3-L5 |
| 3 | T014 extractor change and the build-directory guard | **Clears** | 13 of 13 forms behave as `:427` states. The guard refused every symlink, traversal and shape case. The uncaught `RuntimeError` fails closed and is acceptable; a clean message is recommended (W3-L4) |
| 4 | By-hand report build on macOS | **Clears only with W3-H1 applied** | Its reads, writes and "no model, nothing sent" hold for a clean run folder. The advice leaves out that the session can write the inputs. W3-H1, W3-L1, W3-L5 |
| 5 | Wrapper forms | **Clears with findings** | Validated form: the key is in no file and the guard fails closed on an empty or failed read, on three shells. Argument-free form: no guard (W3-L2). The disclosure is right for Linux and understated for macOS (W3-M1, W3-L3). INFO W3-I4 |
| 6 | SEC-A disposition (T049) | **Clears** | All five elements are applied (see "SEC-A"). Open: the Linux effect of the `/proc` deny (W3-L6) |
| 7 | Section 3 text on startup files, the Keychain and the messaging variables | **Clears** | Each statement traces to the W2 record or to the docs, and carries its "not tested". INFO W3-I5 |

### Findings

| ID | Severity | Item | Finding | Recommendation |
|---|---|---|---|---|
| W3-H1 | HIGH | 4 | The by-hand build runs the project's own `scripts/` and `templates/` and follows symlinks in `{out}`, outside the sandbox, with your full access. `:412` names only the renderer as what it gives up. The docs' list of paths that the sandbox protects from writes holds settings files, `.claude/skills`, `.claude/agents`, `.claude/commands`, `.claude/hooks`, `.mcp.json`, shell startup files, the `.git` hooks and config, and a few other files that Claude Code itself loads. `scripts/` and `templates/` are not on it, so a sandboxed command can edit them (per the docs; not run live), and the session writes `{out}` by design. In the scratch clone: a symlinked `{out}/report-config.typ` was copied into the build directory as a regular file holding the target's text (`:2541-2543`); a symlinked `{out}/attack-trees/` received 10 PNGs outside the project; `typst compile` wrote through a symlink at `{out}/security-report.pdf` and replaced the file it pointed to; a planted regular `report-config.typ` put a project-root file's text into the PDF. The `.env*` read deny does not bind this step. Same class as H-3. HIGH for that consistency, tempered by two facts: the runbook already says to run it without keys, and a compromised session is a precondition. | Add the "Check first" bullet in "Text to carry" 1, and widen the "What it gives up" bullet. In "From what", add `{out}/report-config.typ` and the files that Typst reads under `--root .` (brand logos included). Optional for T014: refuse a symlinked `report-config.typ`, and refuse symlinks under `{out}` in build mode. `python3 -I` only helps against a stdlib-named file: the extractor inserts its own directory on the path itself, and its sibling module `tachi_parsers.py` is project code that the session could edit |
| W3-M1 | MEDIUM | 5 | The macOS exposure statements are narrower than my measurements. (a) `:262` says that on macOS "your own processes" can read the key in `env`'s arguments. On macOS 26.6.2, `/bin/ps` is setuid root, and a non-root `ps` printed the arguments of root-owned processes and of other system accounts' processes, so any local user can. (b) `:266` and the section 11 row at `:617` say that outside the sandbox `ps` showed no process environment. Not reproduced: `ps eww` printed the environment of a same-user Claude Code process (12 Claude Code variable names counted, no values printed) and of a dummy `python3` process, and printed none for a dummy `/bin/sleep`, which is a protected system binary. The live probe may have been such a binary; the observation does not generalise. The larger exposure is not the instant at `:262`. On macOS the real key sits in an environment that same-user processes outside the sandbox can read for the whole session, in either launch form. On Linux `/proc/<pid>/environ` gives the same reach | Correct (a) to "any local user, through `ps`" (on Linux, unless `hidepid` is set). Replace (b), and the `:617` row, with what was probed. Add to "What the mask does and does not do" that same-user processes outside the sandbox can read the real value from the Claude Code process's environment for the whole session, and that only a process-level boundary (section 9) closes that ("Text to carry" 4). Annotate `w2-live.md` section 5.3 (M2) the same way |
| W3-L1 | LOW | 4 | The three by-hand lines are not chained (`:403-405`). Run one after another, a failing extractor does not stop `typst compile`: in the clone, after the inputs were broken, line 1 exited 1 and line 2 still produced a PDF from the earlier build directory, byte-identical to the first. After a failed compile the cleanup line still runs and deletes the build directory that the assembler keeps for debugging (`report-assembler.md:205`) | Join the lines with `&&` ("Text to carry" 2). The block is copied from the assembler per W3-1, so the architect decides |
| W3-L2 | LOW | 5 | The argument-free form (`:241-243`, recommended for shared hosts at `:264`) has no empty-key guard and does not set `SHELL`. Tested on zsh 5.9, bash 5.3 and bash 3.2: an empty or failing secret-manager read starts the session with `GEMINI_API_KEY` set to an empty string or to the error text. The form inherits the caller's `SHELL`, so on macOS sandboxed commands run under zsh and read `~/.zshenv` (the hazard at `:195-200`). The key reached no argument list and no file | Add the guard and `SHELL=/bin/bash` ("Text to carry" 3; tested with stubs on the same three shells). Keep "not yet run live" |
| W3-L3 | LOW | 5 | The disclosure of the instant (`:262`) is accurate but leaves out two things. Tools that record process arguments, such as endpoint monitoring or audit logging, would record the key and keep it past the instant (not tested here). The guard at `:255` stops an empty or failing read, but not an error line printed to standard output with exit status 0: whitespace and an error line both started the session, with that text as the key | Add a clause: if endpoint monitoring on this machine records process arguments, use the argument-free form. Say to use a read command that exits non-zero on error |
| W3-L4 | LOW | 3 | `_mmdc_puppeteer_args` (`:947-972`) raises `RuntimeError` for an empty, relative (a quoted `~` included), missing, dangling or non-regular value. All 10 rejected forms exited 1 with a traceback, made 0 `mmdc` calls and wrote no `report-data.typ`. The build directory stayed as it was, because the render runs before it is recreated (`:2934`, `:3017`), and the assembler stops on any non-zero exit (`report-assembler.md:175`). That fails closed and is acceptable. Gaps: exit 1 is the extractor's "missing required artifact" code; the check runs only when a diagram needs rendering (`:1060`, `:1642`), so a bad value in a run without diagrams passes silently; a symlink to a regular file is accepted | Recommended, not required: validate once at startup in build mode, print one line and exit 2, as `_exit_build_dir_error` does. The value is shown with `!r`, so escapes cannot inject lines |
| W3-L5 | LOW | 4 | By-hand on Linux and WSL2 (`:411`, `:413`): if Chromium reports "No usable sandbox!" outside Claude Code's sandbox too, the text gives no instruction, and the natural next step is `--no-sandbox` with no boundary at all. `:413` also offers the by-hand build as the fallback when the `--no-sandbox` recipe fails, which is where the same flag would be wanted | Add: "If Chromium cannot start here either, stop. Do not add `--no-sandbox` outside Claude Code's sandbox." Say to unset `TACHI_MMDC_PUPPETEER_CONFIG` first if your shell exports it |
| W3-L6 | LOW | 6 | SEC-A's open item N8. On Linux, `Read(//proc/**)` is merged into the sandbox's read denies, and no run has measured what that does to sandboxed Chromium, Node or process substitution. SEC-A section 5.2's fallback (two narrower rules) is not in the runbook, so an adopter whose renderer breaks has one move, deleting the rule, which reopens the environment read. `:189` already says the Linux rule is not yet run live | A decision for the architect: carry the fallback in the Linux section, or keep it in SEC-A. At minimum add to the optional Linux check (`:324-343`) a render and a process substitution, and "if either fails, do not remove the rule; report it" |
| W3-I1 | INFO | 1 | `Agent(isolation:*)` is sound as written. It is the docs' own example of the `Tool(param:value)` form: it matches any explicit isolation value, a parameter the model omits is never matched, and deny is evaluated before ask and allow. tachi's dispatches set none (no `isolation` in any tachi agent, command or skill). Residuals: the live effect is R4a's, and a rule that parsed some other way would deny nothing, with no warning that the docs describe; the rule sees the call's parameter, not an agent definition's frontmatter, so a definition in your own scopes that sets `isolation` is outside it (the same class as hooks and local MCP servers, `:209`). Agent teams are off by default, and the docs say a `--settings` payload applies to split-pane teammates and the lead's deny rules to in-process ones, so they are not a second route | None required. Keep R4a in the re-check, and keep "never ask for `remote`" |
| W3-I2 | INFO | 1 | The nine bare names are sound as written: a bare tool name in a deny rule removes the tool from the model's context, and deny is evaluated first. They are a snapshot of the 2.1.330 inventory. Eight match the tools reference's spelling; `ReadMcpResourceDirTool` is not in the reference and was observed. The docs give a "matches no tool" startup warning for a deny rule that names no tool, so a rename shows, and a new tool never does; the section 4 inventory row (`:317`) checks only that the denied names are absent. `ShareOnboardingGuide` and `RemoteTrigger` are plan- or provider-dependent per the reference, and the docs I read do not say whether such a rule warns when the tool is absent | Optional: at each Claude Code minor release, which is already a refresh trigger, compare the full tool list with section 3. Say that a "matches no tool" warning for a tool your plan does not offer leaves the rule harmless |
| W3-I3 | INFO | 2 | The puppeteer snippet is sound. The file lies outside the project, where the sandbox cannot write; the extractor passes `-p` to both `mmdc` call sites (15 of 15 calls in a sample with 10 trees and 5 chains). It checks the path's shape only, so the file's content stays the adopter's check (`:421`). The only place where macOS and the variable meet is the offline-render note in section 11 (`:657`), which is test scaffolding, not guidance. `:427` says `export`, and the `env -i` form drops exported variables | Optional: a one-line content check and `chmod 444` for the file; in section 11 add "(test scaffolding; the by-hand build leaves it unset)"; at `:427` point to `:264` for the `env -i` line |
| W3-I4 | INFO | 5 | The docs say the proxy "substitutes the real value inside request contents" and do not say headers only. `:36` rests on tachi's own request form, which uses a header. A request body that carries the placeholder could therefore reach the Gemini host with the real key and be echoed into the transcript. Not tested. The host does not change, so the two-host claim holds | Optional: one clause in "What the mask does and does not do", and a line in the maintainer's private scope question (W3-2) |
| W3-I5 | INFO | 7 | Precision. `:193` and `:264` say sandboxed commands "can reach that Keychain" beside Claude Code's own login. The evidence (M3, Z1) is that they reach the Keychain and read an item whose access list trusts `/usr/bin/security`; `:201` correctly says that Claude Code's own sign-in item was not tested. Separately, the sockets that section 6 (`:417`) says the missing seccomp filter leaves open are a container runtime, the inbox sockets and the WSL2 launcher. Credential agents (ssh-agent, gpg-agent, a keyring's D-Bus socket) are the same kind of socket. Not tested | Optional: at the first mention write "can query the login Keychain; whether they can read Claude Code's own sign-in item was not tested". Add credential-agent sockets to the section 6 examples |

### Evidence

**1. Profile block.**
- The block is 3,156 bytes with one trailing newline, SHA-256 `36df2a9a98e301d783a06ff605d1be7f9548e10f805084b3fe225ff89eef9644`, the figure that section 11 records. It is strict JSON, with no duplicate key and no non-standard constant. Its 19 object key paths equal the contract's, and 0 of the 21 named negatives are present. `permissions` holds only `deny`. One domain is allowed, with no wildcard, and `strictAllowlist` is true. The mask's `injectHosts` is that same host. `"$defaults"` is kept in both auto-mode lists. The scalars are as contracted, including `allowUnsandboxedCommands` and `autoAllowBashIfSandboxed` false.
- Against the profile that ran live (2,908 bytes, SHA-256 `43496fb7...`), every key path and value outside `permissions.deny` is identical. Ten rules were added and none removed: the eight AR-21 names, `Workflow` and `Agent(isolation:*)`. A deny rule can only remove capability, and none of the ten is a `Read` rule of the kind that the sandbox merges into its read denies, so each only narrows. The only hosts remain the two: the model provider, reached by the Claude Code process outside the sandbox, and the Gemini host for sandboxed commands.
- The contract test, run in the clone: 202 passed.
- tachi's 21 agents list only Read, Glob, Grep, Write, Agent and Bash. No tachi command or skill sets `allowed-tools`. None names a denied tool: the word "Workflow" appears only in headings. `Agent` is listed by the orchestrator and by `tachi-threat-report`, and neither sets an isolation value.
- The docs confirm the forms: a bare tool name in a deny rule removes the tool from the model's context; `Tool(param:value)` is documented for any built-in tool; and a deny rule on a symlinked path applies when either the requested path or its target matches, so a symlink in the project that points into `/proc` or a credential store is still refused.

**2. Extractor, `TACHI_MMDC_PUPPETEER_CONFIG` (13 forms).**

| Form | Result |
|---|---|
| Unset | Runs; no `-p` passed |
| Absolute path to a regular file; a symlink to one | Runs; `-p <path>` on every `mmdc` call (4 of 4 in one sample; 15 of 15 in the sample with trees and chains) |
| Empty; relative; a quoted `~`; missing; a directory; a symlink to a directory; a dangling symlink; a FIFO; `/dev/null`; a value with a newline | Exit 1, traceback, 0 `mmdc` calls, no `report-data.typ`. The message names the variable and shows the value escaped |

**3. Build-directory guard (12 cases).** Refused with exit 2 and the victim untouched: `.tachi-build` as a symlink to an outside directory; the output directory as a symlink; `security-report` as a symlink to a directory inside the project; an absolute path outside the working directory; `.` and `..`; a wrong last-two-components shape; the template directory; `security-report` as a regular file; `--build-dir` through a symlinked `.tachi-build` (nothing written outside); `--target-dir` inside the build directory. Accepted: a valid path, and the working directory spelled through a symlink above it. A `link/..` spelling is collapsed lexically and removed the in-project directory, not the outside one that the kernel path names. `--build-dir` runs the guard again just before the first deletion, which narrows but cannot close the window between check and removal. The guard covers the build directory's path only. It says nothing about the files in `{out}` (W3-H1).

**4. By-hand build (item 4).**
- Reads and writes match the runbook for a clean run folder, plus brand logos that Typst reads under `--root .` (`report-assembler.md:197`). The two scripts import no network library, `mmdc` is the only program they start, and the templates import no `@preview` package. So "runs no model and sends nothing" holds for unmodified scripts and templates, which is what W3-H1 puts in question. The disconnect, no-key and leave-unset advice is sound, and the disconnect costs nothing (the offline render check, section 11).
- Demonstrations, in the clone, with dummy text: **B** a symlinked `report-config.typ` was copied as a regular file holding the target's text, and `typst` then failed without echoing it; **C** a symlinked `attack-trees/` received 10 PNGs outside the project; **D** `typst` wrote through a symlink at the recipe's own PDF path, and the file it pointed to started with the PDF header afterwards; **E** the lines are not chained (W3-L1); **F** a planted regular `report-config.typ` made a project-root file's text appear in the PDF; **G** the same configuration could not read a file outside the project root (`typst` exited 1, file not found).

**5. Wrapper forms (item 5).** Three shells (zsh 5.9, bash 5.3, bash 3.2), a dummy secret manager and a stub `claude` that prints names, lengths and verdicts only.

| Form | Read ok | Empty | Fails (exit 1) | Fails and prints an error line | Whitespace only | Exit 0 and prints an error line |
|---|---|---|---|---|---|---|
| Validated `env -i` form (`:253-260`) | starts | refused | refused | refused | starts | starts |
| Argument-free form (`:241-243`) | starts | starts, key empty | starts, key empty | starts, key is the error text | starts | starts |
| Guarded argument-free form ("Text to carry" 3) | starts | refused | refused | not run | not run | not run |

In the runs that carried the dummy key, the final process's own argument list held no key and its environment held it. With the validated form the environment held only the names that the form passes, plus the shell's own `PWD`, `SHLVL` and `_`, and `SHELL=/bin/bash`. With the plain forms `SHELL` was the caller's.

**6. SEC-A (item 6).** Present at `b2f5e54`: `Read(//proc/**)` (`:114`), `Read(~/.claude/.credentials.json)` (`:113`) and the `credentials.files` entry for the login file (`:133`), all in the block; the extension note (`:191`) naming `~/.claude.json`, `~/.netrc`, `~/.git-credentials`, `~/.kube`, `~/.docker/config.json` and cloud-CLI directories; the `CLAUDE_CONFIG_DIR` note (`:193`); SEC-A section 5.6's claim text (`:247`) with one added sentence about the scrub; Grep and Glob "best-effort" (`:187`); and the Linux rules marked not yet run live (`:189`, `:324`, the header). The `~/` and `//` path forms are right (SEC-A section 5.3). Open: N8 (W3-L6).

**7. Section 3 text (item 7).**
- Shell selection (`:195`) matches the `CLAUDE_CODE_SHELL` entry in the docs: a path to bash or zsh, else `$SHELL` when it is bash or zsh, else the first working zsh, then bash. The live run supports the rest: the sessions started with `SHELL=/bin/bash` ran bash, and the session recorded as started under zsh (K1a) ran zsh.
- "A startup file loaded a credential under zsh" and "reached the Keychain" trace to Z1 and M3. "Cannot stop this" is the architect's sentence, and the docs I read name no Keychain or Mach default, which fits it. "Not tested" is present for Claude Code's own sign-in item.
- The messaging variables (`:249`) match the docs: both are exported to hooks and Bash commands, and a script posting to the socket sends the token as its first line. The reach claim is hedged with "did not test their use". The Linux half ("where the sandbox does not block Unix sockets, as on Linux and WSL2 without the seccomp filter") is an inference from the docs' "the seccomp filter is optional and adds Unix domain socket blocking"; it is conditional, and the sentence ends with "did not test their use".

**Wording Rules.** The runbook at `b2f5e54`: Pattern A 0 hits, Pattern B 0 hits, no home path. The program name appears only as allowed by name, including in URL slugs. This section was swept before it was appended: Pattern A and B 0 hits, "validated" used for the live record, no claim of standing from Anthropic, no home path, no key material.

### Text to carry (for the T021 owner and T044; the architect decides the wording)

1. **By-hand build, W3-H1.** Add as the first bullet after the code block:
   > **Check first.** The session's sandbox can write to your project, including `scripts/` and `templates/`, and this step runs both with your full access, outside the sandbox. Compare `scripts/` and `templates/tachi/security-report/` with the tachi release you installed from. Read `{out}/report-config.typ` if it exists: a report configuration can pull any file under the project root into the PDF, `.env*` files included. Run `find {out} -type l`, which should print nothing. Run the build only when all three are clean.

   And end the "What it gives up" bullet with: "It also uses whatever the session left in the project."
2. **By-hand build, W3-L1.**
   ```
   python3 scripts/extract-report-data.py --target-dir {out} --build-dir {out}/.tachi-build/security-report \
     && typst compile {out}/.tachi-build/security-report/main.typ {out}/security-report.pdf --root . \
     && python3 scripts/extract-report-data.py --remove-build-dir {out}/.tachi-build/security-report
   ```
3. **Argument-free form, W3-L2.** Replace the one-line form at `:241-243` with the block below, and keep "not yet run live". It was tested only with a stub `claude` and a dummy secret manager.
   ```
   (
     K="$(your-secret-manager-read-command)" && [ -n "$K" ] || { echo "no key; not starting" >&2; exit 1; }
     SHELL=/bin/bash GEMINI_API_KEY="$K" exec "$(command -v claude)" --settings ~/.tachi/session-profile.json
   )
   ```
4. **macOS exposure, W3-M1.**
   - At `:262`, end the sentence: "on macOS, any local user's, through `ps`; on Linux, any user's, unless `/proc` is mounted with `hidepid=1` or higher".
   - In "What the mask does and does not do", add: "Processes of your own user that run outside the sandbox can read the real value from the Claude Code process's environment for the whole session, on macOS with `ps eww` and on Linux through `/proc/<pid>/environ`, whichever launch form you use. Only a process-level boundary (section 9) keeps them out."
   - At `:266` and in the `:617` row, drop "outside the sandbox `ps` showed no process environment", or replace it with: "outside the sandbox, `ps eww` does print the environment of your own non-system processes on macOS".

### Limits

- Docs-based, not run live: `Agent(isolation:*)` (R4a), the plan-dependent tool names, the Linux `/proc` effect, the mask's substitution scope, process-argument recording by endpoint tools, and whether a sandboxed command can read Claude Code's own sign-in item.
- The `ps` check used a same-user Claude Code process from a bundled 2.1.327 build, not the 2.1.330 build of the live run, and counted names without printing values.
- The wrapper-form tests prove the shell logic and where the key goes, not Claude Code's handling of it. The sandbox's behaviour on `scripts/` and `templates/` is from the docs' protected-paths list.
- A path-based removal cannot be made free of a race between the guard and the removal. Not tested: whether a sandboxed background process can outlive the session and race the by-hand build.
