# CLI Contracts (Feature 391)

House conventions for all three: `#!/usr/bin/env python3`, module docstring with feature id, purpose, constraints (stdlib-only) and exit codes; `from __future__ import annotations`; `_build_arg_parser()` with `prog=`; `main(argv=None) -> int`; `raise SystemExit(main())`; errors to stderr with a `[391]` prefix; `--json` prints `json.dumps(summary, sort_keys=True, indent=2)`.

## `scripts/check-agent-privileges.py` (Part A3)
```
python3 scripts/check-agent-privileges.py [--repo-root PATH]
    [--matrix docs/standards/CLAUDE_PERMISSIONS.md]
    [--agents-dir .claude/agents/tachi] [--commands-glob ".claude/commands/tachi.*.md"]
    [--runbook docs/guides/ISOLATED_OPERATION_TACHI.md] [--self-test] [--json]
```
Checks, all run, all reported: **C1 roster**, bidirectional (walk the agents dir recursively; `*.md` only — any other **tracked** file (`git ls-files` when a git tree exists) is red, untracked junk such as `.DS_Store` is ignored; a symlink anywhere is red; a file with leading YAML frontmatter — detected leniently: BOM, blank lines, CRLF tolerated — is an agent candidate and must carry `name: tachi-*`, unique, with a §8 row; the allow-list (`_TACHI_AGENT_BEST_PRACTICES.md`) applies only to files with **no** leading frontmatter, so an allow-listed name that gains frontmatter is classified as an agent candidate; anything else is red; and every §8 row must have a file); **C2 tools** set equality per agent (block list, flow list and comma string all parsed; any other shape → exit 2); **C3 model** equality; **C4 key set** == `{name, description, tools, model}`; **C5 command frontmatter** equals the §8 commands table's recorded keys; **C6 Bash families**: in fenced blocks labelled `bash`, `sh`, `shell` or `zsh` (indented fences included; unlabelled fences out of scope, and agent commands must use labelled fences) of the three Bash-capable agents: join `\` continuations, detect `$(` and backticks on the raw segment first, tokenize with `shlex.shlex(s, posix=True, punctuation_chars=True)` + `whitespace_split=True` (quoted `|` regexes stay one token; `&&`, `||`, `;`, `|` split), strip leading `VAR=value` assignments, skip shell reserved words (`if then elif else fi for while until do done case esac in ! { } [[ ]]`) so the next word is the family (`[` and `test` are families), require it ∈ the per-agent allow-list; `$(…)`, backticks, `eval`, `bash -c`/`sh -c` and `xargs` are red with no construct allow-list in 391; prose is never scanned; **C7 writes cross-check**: the runbook's write-locations table equals the §8 writes column; **C8 self-test** (`--self-test`): copy the tree to a temp dir and assert a failure for each mutation: a tool added to one agent; a planted `name: helper` agent; an unlisted file without frontmatter; a duplicate name; `_TACHI_AGENT_BEST_PRACTICES.md` with planted frontmatter. `--self-test` runs C1–C7 on the live tree and then C8. Exit **0** pass, **1** drift (every finding listed), **2** infra (matrix/section missing, unparsable frontmatter or `tools:` shape, a self-test mutation that fails to fail). The §8 table is parsed between `## 8.` and `## Cross-references`. CI: a `python3` presence step precedes it in `tachi-permissions-verify.yml`.

## `scripts/archive-run-transcripts.py` (Part B1)
```
python3 -I -B scripts/archive-run-transcripts.py (--session SESSION_ID | --latest)
    [--project-dir PATH=cwd] [--dest PATH] [--output-dir PATH]
    [--allow-live] [--live-window-seconds 120] [--json]
```
A plain `python3` start re-executes itself under `-I -B` (T034 H-3).

Discovery: `~/.claude/projects/` (or `$CLAUDE_CONFIG_DIR/projects/`), the project found by matching transcripts' `cwd` to `realpath(--project-dir)`; roster for `tachi_agents_not_dispatched` = the `name:` values of the installed `.claude/agents/tachi/*.md`; `Z`-suffixed timestamps parsed with `strptime`/`replace("Z", "+00:00")` (3.9); `--latest` = newest main transcript for that project. Destination default `~/.tachi/runs/<project-dir-name>/<YYYY-MM-DD>-<session>/` (date = first timestamp, UTC).

Refusals (exit 1, reason on stderr):
- a destination inside a git work tree, unless git ignores every path the run writes there. The paths are each copied source file, `run-manifest.json` and `.run-manifest.json.tmp`, asked as real paths in one batched `git check-ignore --stdin -z -n -v` from the toplevel, and any other outcome refuses. The repository named by the operator's `GIT_DIR` or `GIT_WORK_TREE` is asked too;
- a non-empty destination, unless it is a finished archive of the same session: `run-manifest.json` present and parsed, with `session_id` and `transcripts[]` (path, bytes, sha256) equal to the source, gives exit 0, a no-op. Hash-equal transcripts without the manifest give exit 1, "incomplete archive" (P0B0-5);
- a destination that is a symbolic link, or a symbolic link on its path that resolves into a work tree;
- a destination under `<config>/projects` (elsewhere under `<config>` it is accepted with a warning);
- a live session (any file of the session tree changed within the window) without `--allow-live`.

Every git call is `git -c core.fsmonitor=false …` with an allowlisted environment (T034 H-2). The archive's own `.gitignore` (`*`) is written first. Mercurial, Subversion and Jujutsu work trees are not recognized. `--latest` skips stems that fail the session-id pattern. Parse failures (exit 1, no manifest) also include a line nested too deeply, a non-ASCII `version` and a timestamp out of range once its offset is applied. The run prints how many secret-named values the final scan compared (`secret_scan` in `--json`), and warns when the count is zero.

Writes: dirs 0700, files 0600, `O_EXCL`; copies `<session>.jsonl` and the whole `<session>/` directory verbatim. Manifest per `run-manifest.md`; parse failures and the final secret scan exit 1 with no manifest written. Exit 2: missing projects dir, unreadable transcript, `git` absent when a work-tree check is needed. Runs from a plain shell after the session (under the profile's sandbox the default destination is unwritable by design), under the same secret-injection wrapper as the session so the final scan sees the same values. Copies without following symlinks. Archives are never swept. Attribution follows dispatches at any depth (see `run-manifest.md`). Python ≥ 3.9 (chunked `hashlib.sha256().update`, `timezone.utc`). Joins `INSTALL_MANIFEST.md`'s script whitelist.

## `scripts/stamp-tachi-version.py` (Part B2)
```
python3 scripts/stamp-tachi-version.py --threats PATH [--marker templates/tachi/VERSION] [--check] [--json]
```
Idempotent: inserts `tachi_version: "<value>"` immediately after `schema_version:` in the YAML frontmatter, or updates it; `<value>` from the marker line or `unknown` when the marker is absent or malformed (reason to stderr). `--schema-version-from-template` is not built. CF-21 measured churn (`test-results/t038a-measurement.md`), so `schema_version` stays model-authored and declared-only, and the flag is rejected as an unknown argument (exit 2). Exit 0: stamped, already stamped, or `--check` finds nothing to change. Exit 1: `--check` finds the field missing, different or not in the written form, and nothing is written. Exit 2: any error (an unreadable or unwritable file, not a regular file, no frontmatter, a bad argument). This follows the house convention of the guard and the archiver (1 = finding, 2 = infrastructure). Step 2.6 reacts to any non-zero exit. Invoked at the command layer as **Step 2.6 of `.claude/commands/tachi.threat-model.md`**, between the Step 2.5 populator re-assert and Step 3; `orchestrator.md` is untouched; the model never writes the field. When `schema_version:` is absent the field is appended at the end of the frontmatter. Python ≥ 3.9 (no `hashlib.file_digest`, no `datetime.UTC`).

## `scripts/extract-report-data.py` — two new flags (Part A2, architect ruling RC-T4)
```
python3 scripts/extract-report-data.py --target-dir DIR --build-dir PATH [existing flags…]
python3 scripts/extract-report-data.py --remove-build-dir PATH
```
`--build-dir PATH`: path-shape guard, fails loud (exit 2) unless `realpath(PATH)` is under `realpath(cwd)`, ends in `.tachi-build/security-report`, is not `cwd` or a parent of it, is not the templates directory and is not a symlink; `shutil.rmtree` any existing build directory; `shutil.copytree(templates/tachi/security-report, PATH)`; copies `{target_dir}/report-config.typ` in when present; writes `report-data.typ` there and computes every relative path (images, brand assets) against it. `--remove-build-dir PATH`: same guard; removes the build directory after a verified compile (the agent keeps it on failure). `TACHI_MMDC_PUPPETEER_CONFIG=<absolute path to a regular file>` adds `-p <path>` to both `mmdc` invocations; any other value fails loud. The report-assembler's Bash families stay {`test`, `python3`, `typst`}; no `rm -rf` appears in any agent recipe.
