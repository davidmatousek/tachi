# T147: PR 1's W5 fix lane, the findings as landed (for T080 and the relaunch)

**Session:** build session L, W5, 2026-11-24, lane FX, on the integration tip `0f5e179`. The architect's spec (edits E1 to E9 for findings AW5-1 to AW5-9) is applied as written, as one commit's worth: two agent files (two lines each), both commands and one test module, uncommitted in the lane tree. No script, schema, template, reference or fixture changed, so P1-1 and the oracle are untouched.

## Findings, edits and pins
| Finding | Edit | Site | Pinned by, in `tests/scripts/test_contract_text_374.py` |
|---|---|---|---|
| AW5-1: step 1 shuts the reads out | E1, E3 | `risk-scorer.md:48`, `control-analyzer.md:80` | `test_the_scorer_names_the_references_it_reads_...` (section 12), `test_the_control_analyzer_names_the_references_it_reads_...` (section 13) |
| AW5-2: which reads bind | E2, E4 | step 3: `risk-scorer.md:50` (four files), `control-analyzer.md:82` (three files) | the same two tests |
| AW5-4: Step 6's report | E5, E6, E7 | both commands: the exit-5 row (`:216`, `:194`), Step 6 (`:222`, `:200`), the checklist (`:281`, `:261`) | `test_risk_score_routing_...`, `test_controls_routing_...` (E5); `test_risk_score_reports_...`, `test_controls_reports_...` (E6, E7) |
| AW5-5: inline programs at max | E8, E9 | Who does what (`tachi.risk-score.md:47`, `tachi.compensating-controls.md:52`); Step 2, item 3 (`tachi.risk-score.md:159`) | `test_risk_score_runs_only_...`, `test_controls_runs_only_...` (E8); `test_risk_score_plans_once_...` (E9) |
| AW5-3, AW5-6 to AW5-9 | none | no edit of their own: AW5-3 is this one commit, AW5-6 and AW5-7 are the relaunch's conditions, AW5-8 is T080's list, AW5-9 is information | the whole module |

## The agent files change two lines each
| File | Lines | `git diff --numstat` | Hunks (`-U0`) | The other lines |
|---|---|---|---|---|
| `risk-scorer.md` | 241, unchanged | 2 added, 2 deleted | `@@ -48 +48 @@`, `@@ -50 +50 @@` | 239 of 239 byte-identical (`cmp`) |
| `control-analyzer.md` | 426, unchanged | 2 added, 2 deleted | `@@ -80 +80 @@`, `@@ -82 +82 @@` | 424 of 424 byte-identical (`cmp`) |

Each hunk is a one-line replacement at its own line number, so nothing moved, and deleting only one of the two lines on both sides leaves a difference, so the check can fail. Also changed: `tachi.risk-score.md` 5 lines (281 lines, unchanged), `tachi.compensating-controls.md` 4 lines (261), `test_contract_text_374.py` +70 -5. A spec check compares each E1 to E9 "New" cell with its file: 21 of 21 match, and the same check fails 19 of 21 on the base tree.

## Test runs
Scratch clones of the repository at `0f5e179`, the lane diff applied and committed there only; Python 3.12.11, pytest 9.1. The two lists ran before a last docstring-only reflow of the module, which was then re-run alone on the final diff (318 passed).

| Run | Passed | Failed |
|---|---|---|
| `test_contract_text_374.py`, full | 318 | 0 |
| the same module at the base (old text, old tests) | 316 | 0 |
| the new tests against the old text (negative control) | 309 | 9, the nine pinned tests |
| gated set: `tachi-pytest.yml`'s 23 modules, `-v --timeout=1080` (900 collected) | 899 (1 skipped, the pty case) | 0 |
| f374 list: `f374-offline`'s 12 modules, coverage gate (96.35%, floor 80%) | 5941 (20 skipped) | 1 |
| the same f374 list at the base | 5939 (20 skipped) | 1 |

The f374 failure is `test_tachi_parsers.py::test_text_that_is_not_json_raises_value_error_and_never_echoes_it`, on its 5000-deep JSON case. It is the same test at the base, and that module reads none of the five files. This machine's Python 3.12, 3.13 and 3.14 all parse a 5000-deep document, where the case expects a refusal; CI's 3.11 isn't installed here to check. Python 3.9 isn't installed either (a 3.9 grammar parse of the module passes). No `examples/**` file changed in any scratch clone.

## Notes
- E8's pin covers both of its sentences (the spec lists the first), and the two "reports" tests also pin E7's checklist line and the old line's absence.
- No spec ambiguity or conflict with a test: the new command text avoids "verbatim" and "author", and every old pin still passes.
- AW5-8 stays open: `control-analyzer.md:84`, unchanged under the two-line rule, still asks for scan limits in the reply, and E6 now stops the command relaying replies.
