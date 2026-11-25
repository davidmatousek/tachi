# Contract: entry scripts and exit codes

> Normative for F-374. ADR-050 decision D4 (exit codes and order) and D6 (planner) owns this contract; where this file and the ADR disagree, the ADR governs. Pointers are to `b040fa1`.

## Entry scripts

Every entry script supports `--help` and `--version`. Each one:
- sets `sys.dont_write_bytecode` before its local imports (ADR-049 D8);
- refuses Python below 3.9 before any import, with exit 2. `--version` prints the script's version and the interpreter's, and below 3.9 names the version found, so the commands' Step 1 presence check stops before any dispatch (ADR-050 D4);
- writes only under `--out`, by resolved identity, and recomputes every path from `--out`, the stage and grammar-checked IDs, except the plan's digest-checked `inputs`;
- prints one JSON object on stdout, and errors on stderr. Only PR 1's two renderers, `render-risk-scores.py` and `render-compensating-controls.py`, print summary lines instead. PR 2's writers print one JSON object, as every other entry does (S1P-A27).

Orchestrator fences pass literal arguments only (C6). `PLAN` below stands for `--plan ID --plan-digest HEX`: the plan ID, which overrides `current.json` (a disagreement exits 2), and the `plan_digest` that the last `plan` or `reconcile` printed (a mismatch exits 2).

### Exit codes (copied from ADR-050 D4, which governs)

| Code | Meaning | The caller's next step |
|---|---|---|
| 0 | done | continue |
| 1 | an input is missing or unreadable | stop and print the error |
| 2 | a validation, usage or guard failure; a plan digest or pointer mismatch; a forbidden character in an input (P0-4); or Python below 3.9 | stop, and run the fail step if a plan exists, with three exceptions (below) |
| 3 | batches are pending (`reconcile`), or a Phase 2 wave's deadline passed (`watch`) | after `reconcile`, dispatch exactly the listed batches, then reconcile. After `watch`, write a `timed_out` record for each listed dispatch that still has none, and the lineage rules go on (`threat-model-records.md`, "The watch") |
| 4 | unrecoverable: a cap or the budget is exhausted, or a completeness or parity check failed | run the fail step |
| 5 | done, with warnings (undeclared paths, FR-E.10, R-24, a reissued ID) | print the warnings and continue |

**Row 2's exceptions** (ADR-050 D4):
- `attack-chains.py plan` and `render`: the orchestrator ignores their codes, 2 included, and continues (R-24);
- `attack-chains.py check`: argparse exits 2 on a usage error, so its codes are 0, 2 and 5. The command prints a 2 and continues, as R-24 asks of every chain-check event;
- `fail`: its own 2 means stop with the error, and `fail` never runs a second time.

| Invocation | Exit codes |
|---|---|
| `python3 scripts/tachi-stage.py plan --stage S --out DIR --date YYYY-MM-DD [--threats FILE] [--risk-scores FILE] [--baseline-dir DIR] [--architecture PATH] [--target DIR]` → `{plan_id, plan_digest, waves: [[{batch_id, input_path}]]}`. `--threats` is required for `risk-score`. `compensating-controls` requires `--risk-scores` and `--target` instead, and reaches `threats.md` through `risk-scores.md`'s validated `source_file` ("Readings ruled at W3", below). `threat-model`, the run-level plan, plans no units. `--architecture` is a candidate path that the shared resolver checks in code (D7). A candidate it refuses, whatever check fails, syntactic ones included, is left out of `refs`, printed on stderr and recorded as the plan's `architecture_warning`, and `plan` still exits 0 (ruled at W2) | 0, 1, 2 |
| `python3 scripts/tachi-stage.py reconcile --stage S --out DIR PLAN` → `{status: complete \| pending \| exhausted, plan_digest, done, waves, exhausted: [{batch_id, finding_ids}]}` | 0, 1, 2, 3, 4 |
| `python3 scripts/tachi-stage.py fail --stage S --out DIR PLAN --reason agent-not-spawned \| unrecoverable-batch \| check-failed \| render-failed [--detail TEXT]` → `{moved, restored, record}`. `--detail` is at most 500 characters and is validated as a string field | 0; 2 if a guard refuses a move or the digest differs (the record is still written) |
| `python3 scripts/render-risk-scores.py --out DIR PLAN`, and `render-compensating-controls.py` with the same arguments | 0, 1, 2, 4, 5 |

### Further entry points (names settled in ADR-050)

| Invocation | Track | Exit codes |
|---|---|---|
| `python3 scripts/tachi-stage.py architecture-source --threats FILE --architecture PATH`: upserts the FR-E.18 body line, or removes a stale one (D7) | R | 0, 1, 2; 5 with a carrier warning |
| `python3 scripts/tachi-stage.py id-mark --threats FILE (--baseline FILE \| --no-baseline)`: upserts the ID high-water mark line at Step 2.7 (D7, ruling B) | O | 0, 1, 2 |
| `python3 scripts/tachi-stage.py close --stage threat-model --out DIR PLAN`: folds in the checks' hand-off files, runs the declared-paths check, then writes the stage record (D4). The fold and its exit 2 cases are `part-files.md` §6's | O | 0, 2, 5 |
| `python3 scripts/tachi-stage.py watch --out DIR DSP [DSP ...]`: Phase 2's bound (D6, "A dispatch that never returns"; S1P-A33). It waits until each named dispatch has its record, or until `WATCH_SECONDS` have passed, and writes nothing → `{status: done \| timed-out, pending: [DSP]}`: `pending` is empty on 0, and on 3 it lists the IDs that have no record, in argument order. Every refusal is exit 2, before anything waits ("Readings ruled at T162", below). Its contract is `threat-model-records.md`, "The watch" | O | 0, 2, 3 |
| `python3 scripts/join-threats-md.py --out DIR PLAN`: joins the `threats-md` parts (FR-O.1; the payload is item O-β, D6), and writes the `threats-md` stage record on 0 (RR3) | O | 0, 1, 2, 4 |
| `python3 scripts/attack-chains.py plan\|render\|check --run-dir DIR`. `check` also takes `--plan ID`, the run-level plan, for its hand-off file, `threat-model/<plan_id>/checks/attack-chains.json` (D13; `part-files.md` §6) | O | `plan` and `render`: 0, 1, 2, which the orchestrator ignores (R-24); `check`: 0, 2 (argparse's usage error), 5 |
| `python3 scripts/check-threat-model.py --run-dir DIR --plan ID (--baseline FILE \| --no-baseline)`: FR-N4.5, FR-N4.6, P-11, FR-E.10, FR-E.19's reissue check and D8's repeated-member report (R-F; erratum S1P-A19), with its hand-off file, `threat-model/<plan_id>/checks/provenance.json` (D12; `part-files.md` §6) | O | 0, 2, 4, 5 |
| `python3 scripts/assemble-report.py trees\|report --run-dir DIR PLAN`: `trees` takes the `trees` plan, runs once that stage reconciles to 0, and copies and merges the trees; `report` takes the `report` plan, which pins the trees plan, assembles the report and runs FR-K5.3, FR-K5.5 and FR-K5.7 (D14). Each writes its stage's record on 0 (RR3, ruled at rev. 3) | O | 0, 1, 2, 4 |
| `python3 scripts/generate-threats-sarif.py --threats FILE --out DIR [--architecture PATH]`: the shipped generator on the shared emitter. The path is the command's own, resolved in code (D1, D7, D8). `--architecture` is optional (S1P-A26). Step 2.10 always passes the command's `{architecture_path}`, as Step 2.7 does, and without the flag D7's chain starts at the body line. A refused candidate prints the resolver's warnings on stderr, and the exit stays 0, because Step 2.7's `architecture-source` has already reported the same refusal with exit 5 | O | 0, 1, 2, 4 |

**Helpers** (imported, never run directly; each is installed and listed under F-373's S-13 import gate):
- `tachi_parts.py`: loader, validator, identifier patterns, guards, atomic write, digest, stamp, version and the shared stage-entry path (D3, D4);
- `tachi_scoring.py`: CVSS 3.1, constants, `q1`, `band`, largest remainder and the prefix resolver (D5, D10);
- `tachi_scoring_rules.py`: R-6, R-25, R-26 and R-31 (D5, D9);
- `sarif_common.py`: the shared emitter (D7, D8);
- `tachi_parsers.py`: extended with the reference-set wrapper, `parse_correlation_groups`, the shared reference decoder (D3) and (PR 2) `parse_chain_outcome` and `attack_tree_source`.

The signatures of `tachi_scoring_rules.py` and of lane P's new `tachi_parsers` functions are frozen in [module-signatures.md](module-signatures.md) (W1, T023), together with the persisted-inputs format of `risk-scores.md` §6 and `compensating-controls.md` §7. The shared stage-entry path's names are there too (#443, items 1–4, ruled at W2′'s entry).

### Readings ruled at W1 (2026-11-22, T023)

T017's tests pin these readings for T018. The plan's halving and retry readings are in `part-files.md` ("Readings ruled at W1").

- **`reconcile`'s output** is exactly `{status, plan_digest, done, waves, exhausted}`.
  - `done` lists the finished batch IDs, in plan order.
  - `waves` has `plan`'s shape.
  - `exhausted` is `[{batch_id, finding_ids}]`.
- **`fail`'s output** is `{moved, restored, record}`. `moved` and `restored` list canonical file names, and `record` is the stage record's path.
  - The record's `error.code` is the `--reason`.
  - Under `unrecoverable-batch`, `error.batch_id` and `error.finding_ids` name the exhausted batch. When several lineages are exhausted, they name the first in plan order, and `batches.exhausted` counts them all.
- **KB 21's four moments,** the four times a `fail` can meet earlier outputs:
  - **re-run:** an earlier run's outputs survive a new run that fails before it writes, and the earlier plan directory is left whole;
  - **resume:** a later process can fail the plan using only the last `reconcile`'s digest, and an earlier digest is refused;
  - **failed run:** an earlier run's quarantined files and restored canonical files survive, and `{out}` never holds a failed file under a canonical name;
  - **`--output-dir`:** moves and restores stay inside a non-default `--out`.
- **`architecture-source`** writes from the command's own path only. When the resolver fails that path, it removes any existing line, warns on stderr and exits 5. It never falls back to the constant.
  - It keeps one line, between the frontmatter and the first `## ` heading, outside code fences.
  - A forged copy inside a fence is neither read nor changed.
- **The stamp's `renderer`** is the entry's installed file name, with `.py`, as a literal constant in each entry: `render-risk-scores.py`, `render-compensating-controls.py`, and in PR 2 `join-threats-md.py`, `assemble-report.py`, `attack-chains.py` and `generate-threats-sarif.py`. That one spelling goes in the markdown comment, in SARIF's `tachi_provenance` and in every file an entry stamps, so the name matches `INSTALL_MANIFEST.md` and `REQUIRED_SCRIPT_NAMES`.
- **`--version`** prints `tachi_parts.VERSION` and the interpreter's version on stdout, and exits 0. The refusal below 3.9 goes to stderr, with exit 2. Tests may accept either stream.

### Readings ruled at W2 (2026-11-23)

- **`plan --architecture`** goes through the resolver's own first step, `sarif_common.resolve_explicit`, which `resolve_architecture` also runs. So `plan` and the renderer agree on every check and on the warning's code and text (ADR-050 D7). `architecture-source` makes the same checks under the same code, and keeps its own detail, which says what it did to the line.
  - The pre-check that every other pointer gets (`tachi_parts.path_problem`, which exits 2) doesn't apply to `--architecture`. A control character, backslash or backtick is a refused candidate, as it is for `architecture-source`, and nothing in D7 stops a run.
  - stderr keeps its `WARNING` line, which names the candidate in escaped form and the failed check.
- **The renderers** read `refs` and `architecture_warning` from the plan, never from a batch input (`part-files.md`, "Readings ruled at W2").

### Readings ruled at W3 (2026-11-23)

- **`plan --stage compensating-controls`** (T036, as built):
  - `--risk-scores FILE` and `--target DIR` are required, and either one missing exits 2, because every evidence file resolves under the target (ADR-050 D7). A `--target` that isn't a directory exits 1, and so does a `--risk-scores` that names nothing, unless `risk-scores.sarif` lies beside it: `plan` then reads the SARIF (D8's fallback, AR-T2), and `refs.risk_scores` and `inputs.risk_scores` name the file it read.
  - `threats.md` is reached only through `risk-scores.md`'s frontmatter `source_file`, validated by `check_run_file` (D7, D8). `--threats` is optional and unnecessary, and the command passes none. One that names another file than `source_file` exits 2, because one stage reads one threat model.
  - When `source_file` can't be used, the plan has no `refs.threats` and no `inputs.threats`, each unit holds the finding ID only, nothing is carried, and a `--threats` given is ignored. stderr says so, and `plan` still exits 0.
  - `--baseline-dir` may name a run directory or a file in one, on both stages (D9).
  - A finding whose Section 7 has no Status column is scanned fresh, and nothing is carried for it (ADR-050 D2).
- **Why `threats.md` wasn't reached has no plan key.** `plan` prints the reason on stderr only. The renderer takes reachability from the plan alone, `refs.threats` and `inputs.threats`, and never resolves `source_file` a second time to find a threat model. For its stage record it re-derives the reason with the planner's reading of `source_file` and `check_run_file`. Where that check now passes, the reason says that the plan holds no `threats.md`. A test runs both readings of `source_file` over the same forms and requires the same result.
- **No `--architecture`, on either stage:** `refs` holds no `architecture`, and `plan` never fills it from D7's chain or from a snapshot. The agents read the run's snapshot, and the renderer resolves the body line and then the default (ADR-050 D7).

### Readings ruled at rev. 3 (2026-11-23, T087 and T088)

ADR-050 D6's items O-β and O-γ and its RR3 ruling set these. T092, T097, T106, T108, T109 and T112 follow them.

- **PR 2's batch-stage plans.** Each prints PR 1's `{plan_id, plan_digest, waves}`.
  - `plan --stage threats-md --out DIR --date YYYY-MM-DD` takes no `--threats`. It reads the section manifest at its fixed path (item O-β).
  - `plan --stage trees --out DIR --date YYYY-MM-DD --threats FILE [--baseline-dir DIR]` reads the joined `threats.md` and the baseline's `attack-trees/` listing (D14).
  - `plan --stage report --out DIR --date YYYY-MM-DD --threats FILE --trees-plan ID --trees-plan-digest HEX` runs after `assemble-report.py trees`. It refuses a trees plan whose digest or pointer differs, or that has a batch that isn't `done` (exit 2). It records in its `inputs` the trees plan file, `{out}/attack-trees/.manifest.json`, `threats.md` and, for `chains written`, `attack-chains.md`.
  - The `trees` and `report` plans record `params.reference_digest`, the SHA-256 of the reference set's canonical JSON, through one shared helper. The `report` plan's `refs` is `{}`, as `threats-md`'s is. A batch stage's plan records `out_snapshot` `null`, and a plan with per-section sizes records `batch_size` `null` (`part-files.md` §4 and §5).
- **What `plan` and `reconcile` print for `threats-md`.** Each wave entry is `{batch_id, input_path, part_path, section, finding_ids, rows, problem}` (item O-β; `part-files.md`, "Stage payload: `threats-md`"). The `trees` and `report` stages print PR 1's `{batch_id, input_path}`, because their agents read their batch inputs.
- **The orchestrator's return.** On success it ends with one line, `TACHI PLAN report <plan_id> <plan_digest>`: the report plan as its last `reconcile` printed it. The command passes the two values, as PLAN, to Step 2.9's `assemble-report.py report`, and to Step F's `fail --stage report` if Step 2.9 fails. On failure the orchestrator returns ADR-050 D4's error instead.
- **`fail` for a batch stage.** `fail --stage threats-md|trees|report` writes that stage's failed record and moves nothing. Only `fail --stage threat-model` moves and restores the four canonical files (`part-files.md` §5). The layer that ran the failing step runs it:
  - the orchestrator, when a batch stage's `reconcile` exits 4, an agent it dispatches can't be spawned, or the joiner or `assemble-report.py trees` exits with anything but 0. It then returns D4's error;
  - the command's Step F, with the returned report PLAN, when `assemble-report.py report` exits with anything but 0.
- **Step F's order.** On every failure path, Step F runs `fail --stage threat-model` with the run-level PLAN last, whatever an earlier `fail` returned. Only that `fail`'s 2 means stop with the error. A report plan whose digest was copied wrong still gets its record, with `fail`'s `plan-digest-mismatch` warning.
- **`assemble-report.py report` at Step 2.9** checks every input's digest except `threats.md`'s and `attack-chains.md`'s, which Steps 2.5–2.8 change by design. For `threats.md` it compares `params.reference_digest`, and for the chain file it follows the final outcome record (`part-files.md`, "Stage payload: `report`").

### Readings ruled at W2′'s entry, pass 3 (S1′, 2026-11-24)

From R3b-1's question and lanes T's and OS's tests-first readings (S1P-A42 onward). `part-files.md` holds the rest. T092, T096, T100, T106, T108, T109, T116 and T117 follow them.

- **The directory option (S1P-A42).** Every entry checks its directory option first, through `tachi_parts`' shared checks (`module-signatures.md`), so the words are one: `<option> is not a directory`, with the remedy `create it or correct <option>`. It is exit 1 for each entry whose codes include 1. It is exit 2 for `attack-chains.py check` and `check-threat-model.py`, whose codes have no 1. Then PLAN's two checks follow, exit 2, in PR 1's renderers' words. `check` and `check-threat-model.py` take `--plan ID` alone: it passes the plan allow-list (exit 2) before it becomes part of the hand-off's path. `tachi-stage.py` keeps its own `--out` check.
- **`close`'s stdout (S1P-A50).** One JSON object, `{record, warnings, undeclared_paths}`. `record` is the stage record's path, as `fail`'s is. The two lists are the record's own, so on exit 5 the command prints them without reading the record.
- **`close` has no exit 1 (S1P-A61).** A run-level plan or pointer that is missing is exit 2, with the D3 guard's message. So is a plan of another stage, a digest that differs and a pointer that disagrees.
- **PR 2's plans take only their own pointers (S1P-A63).**
  - `plan --stage threat-model` and `plan --stage threats-md` take `--out` and `--date` only;
  - `trees` also takes `--threats` and, optionally, `--baseline-dir`;
  - `report` also takes `--threats`, `--trees-plan` and `--trees-plan-digest`.

  Any other pointer flag (`--threats`, `--risk-scores`, `--baseline-dir`, `--architecture`, `--target`, `--trees-plan` or `--trees-plan-digest`) is exit 2, and nothing is written, so a stale pointer in a command line is refused, never ignored. PR 1's two stages don't change.
- **`id-mark` refuses a mark it can't compute (S1P-A54).** It exits 2 and writes nothing when this run's Section 7 can't be read, and when the baseline has no mark line and its reference set can't be read. So it never writes a mark below ruling B's rule (ADR-050 D7). A `--threats` or `--baseline` file that is missing is exit 1. A baseline whose mark line reads is enough, whatever its Section 7 holds.
- **`assemble-report.py`'s two modes (S1P-A44, S1P-A47).** `trees` exits 2 for a tree that fails a per-file check and 4 for one that is missing (FR-K5.5, early). `report` checks the trees plan it pins as it checks its own, and for both plans it compares `params.reference_digest` in place of `threats.md`'s bytes. `trees` checks `threats.md` by its bytes, because nothing writes it between the trees plan and `trees` (`part-files.md`).

### Readings ruled at T162 (S1′, 2026-11-25)

From T156's build of `watch` (`95c6a04`). `threat-model-records.md`, "The watch", holds the rest, and `module-signatures.md` the function.

- **`watch`'s codes are 0, 2 and 3 (S1P-A70).** It has no exit 1. `--out` goes through `tachi-stage.py`'s own check, D7's path rule and then a directory, but a directory that isn't there is exit 2 as well: the orchestrator starts a watch after it has written the wave's briefs into `{out}`, so a missing one is a defect in the call, not a missing input. No ID, more than 16, an ID that isn't a full match of the dispatch pattern, and an ID named twice are exit 2 too. Each refusal prints D4's message on stderr, under the banner `TACHI THREAT-MODEL FAILED`, and nothing on stdout. On 0 and 3, stderr is empty. The orchestrator treats any exit other than 0 and 3 as its own error, and the run fails.
- **Exit 3 has one meaning per subcommand** (the exit table, row 3). Its caller knows which subcommand it ran, and in both cases it has work to do before it goes on, so `watch` takes no new code, and no command's routing table changes.
- **`watch`'s stdout** is one JSON object, printed as every subcommand prints one, with sorted keys and a two-space indent. So `pending` comes before `status`, and no reader depends on the order.
