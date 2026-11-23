# Contract: entry scripts and exit codes

> Normative for F-374. ADR-050 decision D4 (exit codes and order) and D6 (planner) owns this contract; where this file and the ADR disagree, the ADR governs. Pointers are to `b040fa1`.

## Entry scripts

Every entry script supports `--help` and `--version`. Each one:
- sets `sys.dont_write_bytecode` before its local imports (ADR-049 D8);
- refuses Python below 3.9 before any import, with exit 2. `--version` prints the script's version and the interpreter's, and below 3.9 names the version found, so the commands' Step 1 presence check stops before any dispatch (ADR-050 D4);
- writes only under `--out`, by resolved identity, and recomputes every path from `--out`, the stage and grammar-checked IDs, except the plan's digest-checked `inputs`;
- prints one JSON object on stdout (the renderer prints summary lines instead), and errors on stderr.

Orchestrator fences pass literal arguments only (C6). `PLAN` below stands for `--plan ID --plan-digest HEX`: the plan ID, which overrides `current.json` (a disagreement exits 2), and the `plan_digest` that the last `plan` or `reconcile` printed (a mismatch exits 2).

### Exit codes (copied from ADR-050 D4, which governs)

| Code | Meaning | The caller's next step |
|---|---|---|
| 0 | done | continue |
| 1 | an input is missing or unreadable | stop and print the error |
| 2 | a validation, usage or guard failure; a plan digest or pointer mismatch; or Python below 3.9 | stop, and run the fail step if a plan exists, with three exceptions (below) |
| 3 | batches are pending (`reconcile` only) | dispatch exactly the listed batches, then reconcile |
| 4 | unrecoverable: a cap or the budget is exhausted, or a completeness or parity check failed | run the fail step |
| 5 | done, with warnings (undeclared paths, FR-E.10, R-24, a reissued ID) | print the warnings and continue |

**Row 2's exceptions** (ADR-050 D4):
- `attack-chains.py plan` and `render`: the orchestrator ignores their codes, 2 included, and continues (R-24);
- `attack-chains.py check`: argparse exits 2 on a usage error, so its codes are 0, 2 and 5. The command prints a 2 and continues, as R-24 asks of every chain-check event;
- `fail`: its own 2 means stop with the error, and `fail` never runs a second time.

| Invocation | Exit codes |
|---|---|
| `python3 scripts/tachi-stage.py plan --stage S --out DIR --date YYYY-MM-DD [--threats FILE] [--risk-scores FILE] [--baseline-dir DIR] [--architecture PATH] [--target DIR]` → `{plan_id, plan_digest, waves: [[{batch_id, input_path}]]}`. `--threats` is required except for `threat-model`, the run-level plan, which plans no units. `--architecture` is a candidate path that the shared resolver checks in code (D7) | 0, 1, 2 |
| `python3 scripts/tachi-stage.py reconcile --stage S --out DIR PLAN` → `{status: complete \| pending \| exhausted, plan_digest, done, waves, exhausted: [{batch_id, finding_ids}]}` | 0, 1, 2, 3, 4 |
| `python3 scripts/tachi-stage.py fail --stage S --out DIR PLAN --reason agent-not-spawned \| unrecoverable-batch \| check-failed \| render-failed [--detail TEXT]` → `{moved, restored, record}`. `--detail` is at most 500 characters and is validated as a string field | 0; 2 if a guard refuses a move or the digest differs (the record is still written) |
| `python3 scripts/render-risk-scores.py --out DIR PLAN`, and `render-compensating-controls.py` with the same arguments | 0, 1, 2, 4, 5 |

### Further entry points (names settled in ADR-050)

| Invocation | Track | Exit codes |
|---|---|---|
| `python3 scripts/tachi-stage.py architecture-source --threats FILE --architecture PATH`: upserts the FR-E.18 body line, or removes a stale one (D7) | R | 0, 1, 2; 5 with a carrier warning |
| `python3 scripts/tachi-stage.py id-mark --threats FILE (--baseline FILE \| --no-baseline)`: upserts the ID high-water mark line at Step 2.7 (D7, ruling B) | O | 0, 1, 2 |
| `python3 scripts/tachi-stage.py close --stage threat-model --out DIR PLAN`: folds in the checks' hand-off files, runs the declared-paths check, then writes the stage record (D4) | O | 0, 2, 5 |
| `python3 scripts/join-threats-md.py --out DIR PLAN`: joins the `threats-md` parts (FR-O.1; the payload is item O-β, D6) | O | 0, 1, 2, 4 |
| `python3 scripts/attack-chains.py plan\|render\|check --run-dir DIR`. `check` also takes `--plan ID`, the run-level plan, for its hand-off file (D13) | O | `plan` and `render`: 0, 1, 2, which the orchestrator ignores (R-24); `check`: 0, 2 (argparse's usage error), 5 |
| `python3 scripts/check-threat-model.py --run-dir DIR --plan ID (--baseline FILE \| --no-baseline)`: FR-N4.5, FR-N4.6, P-11, FR-E.10 and FR-E.19's reissue check, with a hand-off file (D12) | O | 0, 2, 4, 5 |
| `python3 scripts/assemble-report.py trees\|report --run-dir DIR`: `trees` runs once the `trees` stage reconciles to 0, and copies and merges the trees; `report` assembles the report and runs FR-K5.3, FR-K5.5 and FR-K5.7 (D14) | O | 0, 2, 4 |
| `python3 scripts/generate-threats-sarif.py --threats FILE --out DIR --architecture PATH`: the shipped generator on the shared emitter; the path is the command's own, resolved in code (D1, D7, D8) | O | 0, 1, 2, 4 |

**Helpers** (imported, never run directly; each is installed and listed under F-373's S-13 import gate):
- `tachi_parts.py`: loader, validator, identifier patterns, guards, atomic write, digest, stamp and version (D3, D4);
- `tachi_scoring.py`: CVSS 3.1, constants, `q1`, `band`, largest remainder and the prefix resolver (D5, D10);
- `tachi_scoring_rules.py`: R-6, R-25, R-26 and R-31 (D5, D9);
- `sarif_common.py`: the shared emitter (D7, D8);
- `tachi_parsers.py`: extended with the reference-set wrapper, `parse_correlation_groups`, the shared reference decoder (D3) and (PR 2) `parse_chain_outcome`.
