# W5 scratch adopters for PR 1 (T072, part 1)

**Date:** 2026-11-24. **Install commit:** `27d58bd`, W4's pushed and CI-green tip. **Lane:** X (devops). **Inputs:** T072; [w1-adopters.md](w1-adopters.md) section 4; [sc8-baseline.md](sc8-baseline.md) section 1; [prefix-baseline.md](prefix-baseline.md) section 1; [offline-e2e-pr1.md](offline-e2e-pr1.md) section 1; quickstart section 4.

**Result: READY, with one addition to the stated arrangement (finding 1).** Four adopter templates hold the branch build as `scripts/install.sh` installs it, each with its run's inputs committed as a restore point. T072's part 2, the runbook header, waits for T076.
- All four installs exited 0 with `Copied: 45 item(s)` and empty stderr. All 177 installed files equal the install commit's own blobs and modes.
- `plan` matches P1: the scorer plans 326 units in 26 batches and the controls stage 408 in 38, all fresh. The controls template needed one extra file for its units to carry any finding text.
- SC-8's two input digests and the target's tree digest equal [sc8-baseline.md](sc8-baseline.md)'s at `27d58bd`, so SC-8 has the same inputs.
- No tachi command and no Claude Code session ran in a template. This record is the only tracked file written.

## 1. The install

- **Source.** `<install clone>`, detached at `27d58bd`, and clean before and after. `git describe --tags --always` prints `v4.48.4-154-g27d58bdc` (git abbreviates to 8 characters, so the suffix is `g27d58bdc`, not `g27d58bd`). The two later branch commits (`acdceef`, `0e27aaa`) change five files and none is installed: four spec records and `BACKLOG.md`.
- **Method** as w1-adopters.md section 1, with `--source` in place of `--version`. Each template is a fresh `git init -b main` with a one-line README, one commit, the repo-local identity `tachi scratch adopter <adopter@example.invalid>` and no remote. From its root, in section 4's clean environment, `<install clone>/scripts/install.sh --source <install clone>` ran. One commit followed, "Install tachi v4.48.4-154-g27d58bdc", staging the seven top-level directories by path.
- **Output, all four:** exit 0; `Version:  v4.48.4-154-g27d58bdc`; `Copied:   45 item(s)`; stderr 0 bytes. 45 is the entry count between the manifest markers in the commit's `INSTALL_MANIFEST.md`.
- **Placed:** 177 files, 15,956,837 bytes: `.claude/` 93 (22 agent files, 6 commands, 21 skill directories), `templates/` 33, `schemas/` 21, `scripts/` 11, `brand/` 11, `adapters/` 6, `docs/` 2. One executable (`scripts/extract-infographic-data.py`), no symlink. `adapters/claude-code/agents/` holds only `references/`: no adapter agent copy (R-17).
- **Verified against the commit, not against install.sh's own list:**
  1. For every path under a manifest entry, `git ls-tree -r 27d58bd` (mode, blob id, path) equals the template's `git ls-files -s`, its README aside: 177 and 177, identical. Each installed file is byte-identical to the commit's, with the same mode.
  2. Before the install commit, `git status --porcelain --ignored` showed the seven top-level directories untracked and nothing ignored. After it, nothing.
  3. The seven installed subtrees have identical tree ids in all four templates.

## 2. The templates

Each is clean at its restore point, above one install commit and one initial commit. Inputs came from the install commit's objects (`git cat-file blob`, `git archive`), byte for byte. Absolute paths are in the lane's return to the orchestrator, not here (H8).

| Template | Run | Restore point |
|---|---|---|
| `<adopter w5-fixture-score>` | T073, the scorer on the fixture | `93bd5ca` |
| `<adopter w5-fixture-controls>` | T074, the controls stage on the fixture | `b42c12e` |
| `<adopter w5-sc8>` | T075, SC-8's post-fix runs | `4b65f09` |
| `<adopter w5-r27>` | T076, R-27's smoke run | `980b09f` |

- **Fixture inputs, in both fixture templates** (as T021(a) did, nothing else): `docs/security/2026-10-19T09-30-00/threats.md`, the fixture's `baseline/threats.md` (596,028 B, sha256 `44694eb5d2f05b8202ca58643166bbeafb4152b71edf5c9a16ca6f06d3af0f88`), where the directory is the file's own `run_id`; and `docs/security/architecture.md`, `architecture/architecture.md` (10,896 B, sha256 `5ee33b33ca03b5c8ef9020a0f1267c9d0a0da41debd9a2f399bd22c6c933ab6b`).
- **Controls template adds** `docs/security/2026-10-19T09-30-00/risk-scores.md`, the committed `baseline/risk-scores.md` (697,215 B, sha256 `e82da952bddcf4236176e992ff828e0be50083f19175bff9ac89df6a059064f7`), and `controls-target/`, the stub codebase (15 files). **Tree digest** `git rev-parse HEAD:controls-target` = `fb3cfb11ba5479ec2aaacf2e4496198dbd897425`. It equals the stub codebase's tree at `27d58bd` and at `c84ff16`, so SC-8's digest is the same. It adds `baseline/threats.md` too: see finding 1.
- **SC-8 template**, reproducing sc8-baseline.md section 1: `docs/security/2026-04-10T00-00-00/threats.md` from `examples/ascii-web-api/threats.md`, sha256 `4e5f000b616ec06be2b5ca11850ff151303fdda65639e6c6c2bdbc166945cfbc`; `docs/security/architecture.md` from `examples/ascii-web-api/input.md`, sha256 `2791c7bca71fa7e103f44b9d37c7336f1d947e9ba0e9ffb04c6be5ac728817db`; and `sc8-target/`, tree `fb3cfb11ba5479ec2aaacf2e4496198dbd897425`. **All three equal the record's values**, so nothing stopped. In a throwaway clone the Step 1.5 populator grows `threats.md` to 16,540 B, as the record says, and the scorer plans 11 units in 1 batch (size 13).
- **R-27 template:** section 5.

## 3. The `plan` checks

Run in throwaway `git clone`s of the templates (new directory names), never in a template: the populator and `plan` as each command's steps give them, relative paths from the clone root, the run directory as input and output, `--date` today, the clean environment's `python3`. Step 1's presence check printed `tachi-stage.py 4.48.4 (python 3.14.4)` and exited 0. The calls, with `<run>` for `docs/security/2026-10-19T09-30-00` (SC-8's is its own run directory):

```
python3 scripts/populate-affected-assets.py --architecture 'docs/security/architecture.md' --threats '<run>/threats.md'   # scorer only, Step 1.5
python3 scripts/tachi-stage.py plan --stage risk-score --out '<run>' --date <today> --threats '<run>/threats.md'
python3 scripts/tachi-stage.py plan --stage compensating-controls --out '<run>' --date <today> --risk-scores '<run>/risk-scores.md' --target 'controls-target'
```

| Clone of | Stage | Exit | Units | Batches (waves) | Batch sizes | P1 |
|---|---|---|---|---|---|---|
| `w5-fixture-score` | risk-score | 0 | 326 | 26 (16 + 10) | 14 of 13, 12 of 12 | 326 in 26: match |
| `w5-fixture-controls`, as first built | compensating-controls | 0 | 408 | 38 (16 + 16 + 6) | 28 of 11, 10 of 10 | counts match, units hollow |
| `w5-fixture-controls`, as delivered | compensating-controls | 0 | 408 | 38 (16 + 16 + 6) | 28 of 11, 10 of 10 | 408 in 38: match |
| `w5-sc8` | risk-score | 0 | 11 | 1 (1) | 11 | below the threshold |

- **All fresh.** Each fixture plan's only stderr line is the no-baseline warning (the scorer's: "no baseline is used (baseline.source: missing), so every finding is scored fresh"). SC-8's plan wrote none. No unit in the fixture plans' 64 batch inputs carries a baseline result. All 64 batches are pending at attempt 1 with no parent. Retry budgets: 52 (scorer), 76 (controls).
- The populator left the fixture's `threats.md` byte-identical (exit 0, no output). T021(a) at v4.48.4 had seen it rewrite the block, so T073 starts from the committed block.
- Both renderers import and print their usage on the clean environment's Python (`--help`, exit 0). The throwaway clones stay in the lane's scratch, since deleting is blocked, and none is reused.

## 4. Environment

- **Clean environment** (session L's launch environment): `env -i` with `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/zsh`, `TERM=xterm-256color`, `LANG=en_US.UTF-8` and a `PATH` of the user's bin directory, `/opt/homebrew/bin` and the system directories. Its `python3` is `/opt/homebrew/bin/python3`, Homebrew's `python@3.14`, **3.14.4**. This orchestrating shell's `python3` is the repository venv's 3.12.11, which w1-adopters.md section 5 recorded, so the two differ. The offline end-to-end run covered 3.11.13 and 3.9.6, and S-4's determinism claim covers 3.9 to 3.13. 3.14.4 is outside both. The live renderers will be its first run on 3.14 (the checks above ran `plan` and `--help` only).
- `claude` 2.1.330 on the PATH; `--effort` takes `low`, `medium`, `high`, `xhigh` and `max`; `--settings` takes a file. `typst` and `mmdc` are present. `tmux` is present.
- The scripts set `sys.dont_write_bytecode`, so a run adds no `__pycache__`. `plan` writes only `<run dir>/.tachi-build/`.

## 5. R-27's staging (T076)

- **The profile**, saved the way the runbook says: the block between its BEGIN and END markers, outside every template and clone, as `<session profile>`, read-only. 3,156 bytes, **SHA-256 `36df2a9a98e301d783a06ff605d1be7f9548e10f805084b3fe225ff89eef9644`**. That equals section 11's R1 value for the published 18-rule profile. Two routes extracted it (awk and sed, then a regex) and agree byte for byte. It is valid JSON with 18 deny rules, the sandbox on and failing closed, and no permission mode set. The runbook at `27d58bd` equals the one at `0e27aaa`.
- **The example: `examples/ascii-web-api`.** It has the smallest shipped threat model (16,311 B, 11 open findings), so every stage stays below its batching threshold and the run is short. Section 11's live validation used its `input.md` as the architecture description, so T076 compares like with like (that run: 17 SARIF results, about 6 minutes). It is also SC-8's example, which G0 ruled does not double as R-27's run.
- **Template inputs:** `docs/security/architecture.md` from its `input.md` (sha256 as in section 2) and `r27-target/`, the stub codebase, tree `fb3cfb11...`, as above. No earlier run exists, so the threat model runs first, with no baseline, as section 11's R6 did.
- **The commands:** `/tachi.threat-model` with no arguments (default input `docs/security/architecture.md`, default output `docs/security/<timestamp>/`), then `/tachi.risk-score`, then `/tachi.compensating-controls --target r27-target`. Key-less: no `GEMINI_API_KEY`.
- **The "before" listing.** A fresh clone is clean at the restore point, so it is the known tree for section 11's write listing (a hash of every path but `.git/`, before and after).
- **Launch form.** Section 3's form that ran in section 11 uses `SHELL=/bin/bash`. Section 4's environment uses zsh, and this host's zsh startup file loads a Keychain credential into every command Claude Code runs, the case that section 3 warns about. Under the profile the sandbox can reach that Keychain. So R-27 should launch from section 4's environment with `SHELL=/bin/bash`, `TMPDIR` set as section 3 does, `--settings <session profile>` and `--effort medium`. Decision for the orchestrator. Section 3 also says to list the host's local MCP servers in `deniedMcpServers` (user settings) first, as section 11 did. User scope holds no sandbox, hook or env entries; it sets permission mode `auto` and a status line command.
- **The header today.** `docs/guides/ISOLATED_OPERATION_TACHI.md`, section 0, line 5, in the template as in the lane tree:
  > - Last validated: 2026-11-20, on macOS 26.6.2 (arm64), Claude Code 2.1.330, auto mode (one Manual-mode check), key-less and keyed, tachi build `v4.48.2-103-gfe5125a`, with the session profile at SHA-256 `43496fb7d4fca098983a70648def8f1da2a2d1843528b5ca4c14444e32564279`. The published profile adds ten deny rules (§3). A key-less re-check on 2026-11-20 covered its startup, its rule list, the tool inventory, a refused isolated Agent call, the sandbox probes and one `/tachi.threat-model` run (§11).

  Its third refresh trigger (a change to the write set of any tachi command) applies to this release. Part 2 edits this line after T076.

## 6. Dispositions decided in advance (TW-L2; P1's three; session L's launch rule)

- **(a) Exit 5 is the pass state** for T073 and T074 on the fixture. The fixture's `threats.md` has no `**Architecture source**` line (0 matches) and its `baseline.source` names a directory the fixture does not ship, so each run warns `architecture-path:body-line:absent` and `baseline-unresolved`. The command routes exit 5 to Step 6. `evidence-file-unresolved` is a warning too, never a failure (W3's ruling on SA-2).
- **(b) A main-session departure from the command text is off-contract** under TW-L2. Record it, file the follow-up, and don't claim that stage's SC. It is not a shipped-code defect. Examples: a `reconcile` before every listed wave's agents report, or a render before `reconcile` exits 0. T073 and T074 record each run's `reconcile` calls and the wave each ran after.
- **(c) A refusal for a pipe in a Section 7 cell is a code defect.** If T076 refuses a live `threats.md` for one (P1-3), it goes to T147 as a shipped-code defect cured by P1-3's fix, not an agent off its contract.
- **Launch rule (D-L2).** Each live run is a fresh interactive Claude Code session in a detached tmux session, cwd a fresh `git clone` of its template (a new directory name each time), started from section 4's clean environment, so no `CLAUDE_CODE_*` variable and no inherited effort or output cap. Default-effort runs launch `claude --effort medium`, max runs `claude --effort max`. Auto permission mode (the account default). The folder-trust dialog is answered "Yes, I trust this folder". **Recorded deviation from "account defaults":** the account's user settings now open Opus 5.5 at xhigh effort, while T021(a) and (b) recorded medium as the default. The flag restores medium for the default-effort runs, which keeps P-7's same session conditions, and sets max for R-18's second level.

## 7. Findings

1. **`<adopter w5-fixture-controls>` could not give the controls stage its threat model.** The committed `baseline/risk-scores.md` names `source_file: "baseline/threats.md"`. `plan` resolves that against the working directory, not the run directory, so a `threats.md` beside the file doesn't count. As first built, `plan` warned "threats.md is not read (source_file 'baseline/threats.md' can't be used: missing)" and each unit held only a finding ID. The counts matched P1 and the content didn't. **Fix, additive:** `baseline/threats.md`, byte-identical to the run directory's copy, so the fixture file stays untouched. The restore point was amended to `b42c12e`. Units now carry component, layer, threat, mitigation, risk level and delta status. A live T073 to T074 chain doesn't meet this: the renderer writes its own `source_file`.
2. **T074's agent finds no architecture snapshot unless `--architecture-path` is passed.** The control analyzer looks for `architecture.md` beside the `threats` file (here `baseline/`), and the command passes a path only when given one. T021(b)'s controls run passed none, so T075 must not. Whether T074 passes `docs/security/architecture.md` is the orchestrator's call; without it the agent maps components by heuristics.
3. **3.14.4 is outside CI's range** (section 4). If a live renderer exits on a 3.14 incompatibility, that is a shipped-code defect, not an agent off its contract.
4. **T073 to T075 keep `SHELL=/bin/zsh`** as T021 did, so the zsh startup file's credential load also applies to those sessions' commands. Nothing in the commands prints the environment, and no tester should run `env` or `printenv` there.

## 8. Orchestrator decisions (session L)

- **Finding 1: accepted.** The additive `baseline/threats.md` stays, and the fixture file is untouched. It is T065's O4 class (the fixture's stale `source_file`), already on T080's list.
- **Finding 2 (D-L6): the stock invocation.** T074 types `--target` only, as T021(b) and T075 do. An adopter at the default layout gets no architecture snapshot either, so T074 records the agent's heuristic component mapping as an observation, not a deviation.
- **Finding 3 (D-L7): 3.14 is checked offline first.** Before T073's first dispatch, T065's driver re-runs on the clean environment's 3.14.4, so a 3.14 incompatibility can't cost a live attempt.
- **Finding 4 (D-L8): the shells.** T073 to T075 keep T021's `SHELL=/bin/zsh`. T076 launches as the runbook's section 3 does: `SHELL=/bin/bash`, `TMPDIR` as section 3 sets it, `--settings <session profile>` and `--effort medium`. Section 3's user-scope additions (the `deniedMcpServers` entry and the credential Read deny) change the maintainer's own settings, so they are the maintainer's call. T076's record states whether they were applied.

## 9. Re-install on T147's fix (1e3614a)

T147 changed two agent files and two commands, so the second attempts, T075 and T076 run on a new build. `<install clone b>` is detached at `1e3614a` (`git describe` = `v4.48.4-162-g1e3614a`) and clean. Four new templates are arranged as section 2's: the same inputs and digests, the additive `baseline/threats.md` and the same targets. The `w5-*` templates and the first attempts' clones are untouched, as evidence.

| Template | For | Restore point |
|---|---|---|
| `<adopter w5b-fixture-score>` | T073 | `a760439` |
| `<adopter w5b-fixture-controls>` | T074 | `c3d0832` |
| `<adopter w5b-sc8>` | T075 | `4cacfea` |
| `<adopter w5b-r27>` | T076 | `4533c72` |

- **Install**, as section 1: exit 0, `Version:  v4.48.4-162-g1e3614a`, `Copied:   45 item(s)` and stderr 0 bytes in all four. All 177 installed files equal `1e3614a`'s blobs and modes (177 and 177). The seven top-level directories were untracked and nothing ignored before the install commit, and nothing after it. The seven subtrees have identical tree ids in the four templates.
- **The four changed files reached every template.** Each holds `1e3614a`'s blob of `control-analyzer.md`, `risk-scorer.md`, `tachi.compensating-controls.md` and `tachi.risk-score.md`. Against its `w5-*` counterpart each has the same file set (180, 197, 195 and 194 tracked) and differs in exactly those four paths.
- **Inputs:** each digest equals section 2's, checked as the file was written, and the three target directories have tree `fb3cfb11...`. The runbook's profile block is unchanged: SHA-256 `36df2a9a...`, equal to the staged `<session profile>`.
- **`plan`** in throwaway clones, as section 3 (the commands' `plan` calls are unchanged), exit 0 and fresh: the scorer 326 units in 26 batches (16 + 10), the controls stage 408 in 38 (16 + 16 + 6) with threat text in each unit, SC-8's scorer 11 in 1. P1's counts hold, with the same no-baseline warning. The populator again left the fixture's `threats.md` unchanged and grew SC-8's to 16,540 B. Both renderers print usage on 3.14.4.
- **Use `w5b-*`** for the second attempts, T075 and T076. Section 6's launch rule and section 8's decisions apply as before.

## Part 2: the runbook header (after T076)

Pending. T076 decides it: update the line with the run's date, versions and build, or mark the header as predating this release if the run fails (R-27).

**Done: T076 passed ([r27-smoke-pr1.md](r27-smoke-pr1.md)), so line 5 of the runbook now names the 2026-11-24 key-less run on the published 18-rule profile (Claude Code 2.1.331, build `v4.48.4-162-g1e3614a`, SHA-256 `36df2a9a...`) and keeps the 2026-11-20 keyed validation and re-check as the earlier runs.** The edit is that one line. The runbook is not an init-baseline substitution target (H4) and no test pins the header. Section 11 still records only the 2026-11-20 runs, and the new header cites none.
