# T146: PR 1's W4 fix lane, the findings as landed (for T070)

**Session:** build session S2, W4, 2026-11-24. T146 fixed the findings of T064 (the W3 security advisory), T065 to T068 (the offline end-to-end run, the oracle, the review and the Step 7 scan) and the oracle triage, before T069's push. It ran as parallel fix instances, one writer per file. No CRITICAL finding was raised. The two HIGH findings, both in T067's review, are fixed.

## Fixed in PR 1

| Finding | Source | What changed | Commit |
|---|---|---|---|
| H1 (HIGH) | T067, part b | The controls SARIF's `recommendation` is built from each fence-aware §4 block with the shared `tachi_parsers.recommendation_text`, and checked against the validated part's body, so a quoted heading in an evidence snippet can't silently empty it | `a6c5687`, `17ea8e6` |
| H2 (HIGH) | T067, parts a and b | One unambiguous reconcile rule in both commands, the shared reference and ADR-050 D6: dispatch every listed wave, then run `reconcile` once | `cbba1e5` |
| M1 | T067, part a | `parse_reference_set` refuses a Section 7 row with an extra pipe, where it read every later column shifted. **Narrowed by W6's P1 batch (P1-3):** GFM's backslash-escaped pipe is a pipe inside its cell for Section 7's reader, through an additive `escaped_pipes` option on `parse_markdown_table`, so only a raw pipe is refused, with the same exit 2 and remedy. The per-finding tables and the extractors keep their rule (NFR-1) | `a6c5687`, W6's P1 batch |
| M2 | T067, part a | The forbidden-character regex and its tests write bidi controls and separators as escapes | `e51c1df` |
| M3 | T067, part a | The baseline SARIF is read with D3's bounded integers, in the scoring rules and in the scorer renderer | `72fc0f0`, `0e6bd78` |
| M1 | T067, part b | A controls fallback member with no result of its own, or no composite score, stops the plan before dispatch | `c129e78`, `17ea8e6` |
| M2 | T067, part b | The controls template's §7 matches the renderer's, with a test | `cbba1e5`, `17ea8e6` |
| M3 | T067, part b | Each controls unit row carries its finding's layer | `c129e78`, `cbba1e5` |
| S7-1 | T068 | The Section 7 reader's whitespace-quadratic and cubic patterns are linear | `a6c5687` |
| S7-2 | T068 | The commands single-quote every repo-derived path in their `python3` fences | `cbba1e5` |
| S7-3 | T068 | `atomic_write` sets the mode on the open descriptor, never on a path, and reads the umask once at import | `e51c1df` |
| SA-4 | T064 | `atomic_write` keeps a replaced file's mode, but two paths still lost it, the renderers' own `os.replace` of the staged files and `fail`'s restore of a pre-image, so T070 found this one partial. **Fixed by W6's P1 batch (P1-2)**, through `atomic_write`'s additive `mode_of` keyword: a 0600 canonical file stays 0600 after each renderer's render and after a `fail` restore | `e51c1df`, W6's P1 batch |
| SA-1, SA-3 (in part) | T064, T065's O2 | The planner refuses a forbidden character in every value that a batch input carries, before dispatch, which also closes T065's O2 (SA-3) for those values. The remainder of SA-3, the values that reach no unit (a carried scorer finding's text, a RESOLVED row, Section 1's and 2's names), stays deferred to T080 | `c129e78` |
| SA-5, SA-10, S7-4 | T064, T068 | Declared-path names are recorded generally; derived inputs are bounded and refuse symlinks | `c129e78` |
| SA-7 | T064 | The Unicode tag block joins the forbidden set | `e51c1df`, `cbba1e5` |
| SA-8 | T064 | `path_problem`'s character-set gap | `e51c1df` |
| SA-11 | T064 | The self-check runs the path guard on every SARIF URI, primary and evidence, as written and decoded once | `72fc0f0` |
| SA-13 | T064 | The Affected Assets reader splits rows on newlines only | `031f575` |
| U-1 (D) | T066, triaged | Each finding's MAESTRO layer comes from its own §3/§4 row, through one reader, `parse_finding_layers` | `d8cf928` |
| R-F | PM W4 ruling | A finding listed in two correlation groups is reported (`correlation-member-repeated`), never silent | `d8cf928`, `977a622` |
| D2 carry claim | T066's re-run (the PM's question, the architect's ruling) | The controls renderer accepts `carried_forward` only where the baseline holds the finding's result, and clears any other claim with its reason (ADR-050 D2, amended at W4) | `bfe3e85`, `9bd337e` |
| SA-2 | T064 | Already answered at W3: a missing evidence file is flagged, not refused | (W3) |

The tests that pin the renderers' own refusals now run past the planner's earlier refusal (`94d69d8`, `17ea8e6`).

## Deferred

- **To T080:** SA-3's remainder (the SA-1 row above names it), the Q3 reader drop, SA-6, SA-9, SA-12 and SA-14 to SA-18. Also T067's LOW and INFO findings, `_SRC_ATTR_KV_PATTERN`'s whitespace cost, the fixture's stale `source_file` in one scenario (T065's O4), `tachi-pytest.yml`'s missing `tests/conftest.py` path, and U-2's colon-form title upgrade.
- **For the architect at T070:**
  - SA-4's mode loss through the renderers' own `os.replace`, which would need a public replace helper (T070 ruled it PR 1's, as a keyword and no helper, and W6's P1 batch fixed it: see the SA-4 row);
  - SA-1's residual: a persisted `matrix_row` or body that is malformed fails the carried copy, which would need a public item check;
  - the `https%3A//` raw-slash URI edge, judged harmless.
- **Ruled by the PM after the re-run (R-H, R-I):** the oracle re-run's 81 `CF` cells join the eighth class, and Run B's 80 diffs fall in the widened fifth class. Under those rulings the re-run is clean for the oracle gate. The gate is confirmed again on PR 1's merge candidate before W6 merges.
