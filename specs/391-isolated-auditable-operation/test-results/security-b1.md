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
