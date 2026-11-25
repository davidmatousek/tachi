# T080: PR 1's follow-ups, filed (the ledger)

**Date:** 2026-11-24. **Lane:** CO (architect), build session S3, W6. **Base:** detached `401078a`. **Filed:** 35 issues, #427 to #461, all `stage:discover`: 33 from the first pass and two from the architect's P2 checkpoint (#460, #461). The 23 enhancements carry `enhancement`, and the 12 defects `type:bug`. Each was filed with `.aod/scripts/bash/create-issue.sh` after a phrase search of its title over the open issues found no match, so the script updated no existing issue (H12). The bodies follow #410's sections and passed a public-hygiene scan (H8, NFR-6). **Docs:** KB Entry 27 and the CI guide's three `f374-*` jobs, which T081 commits with the regenerated init baseline (H4). Also the system-design README's `score_source` lines (`docs/architecture/01_system_design/README.md:1662-1664`, P2-3(b)), another init-baseline target, which devops regenerates again.

## For T079

The notes must link:
- **S-16's three:** #428 (the snapshot's file name), #429 (the deny rule) and #430 (Phase 2 from the command layer).
- **T078's (1):** #433, from the known-limitation line on the default-effort scorer's skipped reads.
- **Q3(b):** #435, from item 4's Section 3 line.
- **Q4:** #436, from item 2's first-run line.
- **W5 follow-ups above 10% fallback:** none. The highest rate was 1.3% (1 of 80, one run), so no rate link is owed.

The notes may also link #431 (max effort's cost and its output-cap stops, G-8), #437 (U-2's regenerate remedy, item 4), #432 (item 4's R-34 line) and #427 (R-17, if the notes mention the adapter).

## The issues

| # | Kind | Title | Sources |
|---|---|---|---|
| #427 | enhancement | enhancement: retire or regenerate the Claude Code adapter's superseded agent copies and its stale install sections | R-17, FR-C.1; S1's VERSION note; P0's README note |
| #428 | defect | defect(threat-model): the architecture snapshot keeps the source file's name, while the populator and the later stages look for architecture.md | S-16 (1), research item 11 |
| #429 | enhancement | enhancement: deny the general-purpose agent type in the isolated-operation session profile | S-16 (2), S-10 |
| #430 | enhancement | enhancement: dispatch the threat model's Phase 2 agents from the command layer, an escalation that needs a scope ruling first | S-16 (3), RK-4, TW-CTX |
| #431 | enhancement | enhancement: at max effort, agents' thinking-only output-cap stops are invisible to the stage record: record them, or size max-effort batches narrower | W5 §7 item 3, G-8 |
| #432 | enhancement | enhancement: render compensating-controls.md Sections 2 and 4 from the part fields, so the checked Section 2 cells become filled ones | FR-K8.1, R-34 |
| #433 | enhancement | Agents can skip the reference files their instructions require: deliver the rules in the batch input, or check the reads structurally | T078 (1); W5 §7 item 1, R1, G-5 |
| #434 | enhancement | Agents can read files outside their declared read list: close the list, and check read scope structurally | T078 (2); W5 §7 item 2, R2, G-6 |
| #435 | enhancement | enhancement: controls report: decide whether detected controls that map to no finding are listed: a closed part field and a rendered inventory, or a template line that excludes them | PM Q3(b), with Q3(a)'s template marking |
| #436 | defect | defect(pipeline): first-run threat models can omit Section 7's Status column, so the scorer and controls stages flag every finding and exit 5: write the column on every run (NEW on a first run), and don't flag an absent status when there is no baseline | PM Q4; replaces W5 §7 item 7 |
| #437 | enhancement | enhancement: read a legacy baseline's colon-form title as the carried threat text when its Section 2 cell is the documented truncation | U-2 |
| #438 | enhancement | enhancement: decide what a run shows for a list-form Section 7 with no baseline, where every finding gets placeholder component and threat text | S2's PM question |
| #439 | defect | defect(controls): the control analyzer's scan limits (file budget, truncation, unmapped components) reach no output now that the command doesn't relay its reply | W5 §7 item 4, AW5-8; session L |
| #440 | enhancement | enhancement: command rules for the main session's own output: bound the status notes before the final report, and state one rule for a filter in a Step 1 listing | W5 §7 items 5 and 6, G-12, G-7 |
| #441 | enhancement | enhancement: the large-architecture test fixture can't exercise the architecture-aware paths, or the controls stage's threat-model join in one scenario | W5 §7 item 8; T065's O4 |
| #442 | defect | defect(parsers): the strict JSON loaders' nesting limit depends on the Python version, and CI runs no Python above 3.11 | W5 §7 item 9; session L |
| #443 | enhancement | enhancement: consolidate the stage entry plumbing and the duplicated helpers into tachi_parts at the start of Feature 374's PR 2 | EC-1, EC-3, EC-4, EC-6, EC-11 to EC-13; SA-12; T067a L3 to L5; T067b L1; T068 O-1 |
| #444 | defect | defect(stage): a forbidden character in an input value that reaches no batch unit is refused only at render, after every agent has run | SA-3's remainder, Q3's reader drop |
| #445 | defect | defect(controls): a baseline controls result edited into a form the part validator rejects fails its batch on every attempt | SA-1's residual |
| #446 | defect | defect(scoring): a legacy-carried rationale that starts with ** or --- is lost on the next read, and the staged read-back can't see it: fix the reader and widen the check together | T067a L8 with the read-back widening |
| #447 | enhancement | enhancement: after Feature 374's PR 1 merges, read each input once through one reader: SARIF details, the layer and zone chain, baseline vectors, section lookups and fence rules | EC-5, EC-7 to EC-10; SA-6; T067a L1, L2; T067b L5 (controls), I2 |
| #448 | defect | defect(stage): the declared-paths check turns itself off once an output directory holds about 20,000 entries from earlier plans | T067a L9; SA-14, SA-15 |
| #449 | enhancement | enhancement: rendered markdown text: decide whether to escape link syntax, stop showing escaped text in code spans, and refuse a line break in a controls matrix row | SA-9, SA-17; T067b L4 |
| #450 | enhancement | enhancement: tighten the renderers' self-checks and the stage record's counts | T067b L3; T067a L7; the `https%3A//` hardening; P0-12; W5 §7 item 10, G-3 |
| #451 | enhancement | enhancement: tighten Feature 374's tests: exact exit codes, named negative cases, escaped Trojan Source characters and a dead allowance | T067a L10; T067b L6, L9; S1's `WIRED_BY_T047` |
| #452 | enhancement | enhancement: close tachi-pytest.yml's path-filter gaps, and gate the deferred-yaml-import test that one script now fails | T067b L7; S1's paths gaps and `yaml` import |
| #453 | enhancement | enhancement: align command, agent and script text with Feature 374's PR 1: helper presence checks, the populator's input path, the CF instruction, the controls renderer's help and the roster table | P0-11; T067b L2, I3 to I5; T067a L6; S1's roster rows |
| #454 | enhancement | enhancement: check and linearize the regular expressions in the extractors and parsers that long hostile text can make quadratic | T068 O-4; `_SRC_ATTR_KV_PATTERN` |
| #455 | defect | defect(extractors): the risk-scores and controls readers behind the report and infographics find a section by substring, so earlier text that repeats a heading makes them read the wrong table | W3's heading-capture ruling; ADR-050 Known limitations |
| #456 | enhancement | enhancement: correlation groups: report a finding that two threats.sarif groups list, and decide whether groups that share a member should merge | ADR-050 Known limitations; S2's idea, R-F |
| #457 | enhancement | enhancement: align the scorer and controls SARIF taxa names with tachi's catalogs, and make the rules' OWASP relationship targets resolve | PM W3 ruling 2c; `sarif-result.md`; S1's ASI01 note |
| #458 | enhancement | enhancement: check each controls evidence snippet against its cited file, and weigh what refusal messages echo to the orchestrating model | SA-16, SA-18 (#360's family) |
| #459 | defect | defect(docs): the isolated-operation runbook's live-validation record has no entry for the 2026-11-24 run that its header cites | session L |
| #460 | defect | defect(controls): give a pipe from the unit row's threat or component text a spelling that the controls matrix row can hold | P2-2 (for PR 2) |
| #461 | defect | defect(stage): an output file that its owner can't read makes plan end in a traceback instead of the stage's failure message | P2-6 |

## The ledger, by source

### (a) T080's task line, with spec S-16, FR-C.1 (R-17) and FR-K8.1

| Item | Disposition |
|---|---|
| R-17's adapter follow-up, in the #369 family (FR-C.1) | filed #427, which references #369 |
| S-16 (1): the architecture snapshot's basename | filed #428 |
| S-16 (2): an `Agent(general-purpose)` deny rule for the isolated-operation profile | filed #429 |
| S-16 (3): dispatching Phase 2 from the command layer | filed #430. Its triggers are PR 2's: T104 (the S-9 spike) and T130 and T131 (TW-CTX) |
| FR-K8.1's rendering of controls Sections 2 and 4 | filed #432. PR 2 may take it on if that doesn't move its date (R-34) |
| Any W5 follow-up | source (b) below |
| SV-1's issue (FR-K4.2 to FR-K4.4, if TW-K4 recorded (b)) | not filed: TW-K4 recorded (c) |
| S-16's KB entry on output-cap overflow | not an issue: KB Entry 27, written here, which links #428 to #431 |
| The f374 jobs in the CI guide | not an issue: `docs/devops/CI_CD_GUIDE.md`, written here |
| P-11 ("otherwise it joins S-16's follow-ups") | not filed: adopted in PR 2's D12 (plan.md), so it doesn't join S-16's list |

### (b) `w5-gate-pr1.md`

| Item | Disposition |
|---|---|
| §7 item 1: scorer agents at default skipped reference reads (G-5) | folded into #433 |
| §7 item 2: controls agents at max read shipped scripts (G-6) | folded into #434 |
| §7 item 3: thinking-only output-cap stops at max, unseen by the record (G-8) | filed #431; also KB Entry 27 |
| §7 item 4: the controls agent's scan limits have no part field (AW5-8) | filed #439 |
| §7 item 5: the main session's notes outside Step 6 (G-12) | filed #440 |
| §7 item 6: one rule for a filter in a Step 1 listing (G-7) | folded into #440 |
| §7 item 7: a first-run threat model has no delta status | not filed as written: replaced by the PM's Q4 defect, filed #436 |
| §7 item 8: no live record of the architecture-aware paths | filed #441 |
| §7 item 9: Python 3.14 outside CI's range, and the 5,000-deep JSON case | filed #442 |
| §7 item 10: the controls fallback rate's denominator (G-3) | folded into #450 |
| §7 item 11: the "cheaper" claim, "default (medium)" and max's cost | T079 (notes) |
| §7 item 12: every pre-PR 1 `threats.md` lacks the architecture-source line (O1) | T079 (notes) |
| §7 item 13: the non-claims and Q1's answer | T079 (notes) |
| §5a (1): "Agents can skip the reference files their instructions require: deliver the rules in the batch input, or check the reads structurally" | filed #433, under that exact title |
| §5a (2): "Agents can read files outside their declared read list: close the list, and check read scope structurally" | filed #434, under that exact title |
| §2: a follow-up for any rate above 10% | none owed: the highest rate was 1.3% |

### (c) `t146-fixes-pr1.md`, "Deferred" (as the W6 batch corrects its SA-3 and SA-4 rows)

| Item | Disposition |
|---|---|
| SA-3's remainder: values that reach no unit | filed #444 |
| The Q3 reader drop | folded into #444 |
| SA-6 | folded into #447 |
| SA-9 | folded into #449 |
| SA-12 | folded into #443 |
| SA-14 | folded into #448, as context |
| SA-15 | folded into #448 |
| SA-16 | filed #458 |
| SA-17 | folded into #449 |
| SA-18 | folded into #458 |
| T067's LOW and INFO findings | source (i) below |
| `_SRC_ATTR_KV_PATTERN`'s whitespace cost | folded into #454 |
| T065's O4: the fixture's stale `source_file` | folded into #441 |
| `tachi-pytest.yml`'s missing `tests/conftest.py` path | folded into #452 |
| U-2's colon-form title upgrade | filed #437 |
| For the architect at T070: SA-4's mode loss | fixed in PR 1 (W6 batch, P1-2) |
| For the architect at T070: SA-1's residual | filed #445 |
| For the architect at T070: the `https%3A//` edge | folded into #450, as the optional hardening |

### (d) The architect's P1 checkpoint (gitignored record)

| Item | Disposition |
|---|---|
| "Notes for other tasks", T080: SA-1's residual, as T064's spec | filed #445, whose expected behavior is that spec |
| T080: the `https%3A//` hardening | folded into #450 |
| T080: P1-3, unless it moves into PR 1 | not filed: the PM moved it into PR 1 (W6 ruling Q1), and the trip-wire didn't fire. Its writer half stays PR 2's (Track O, as the checkpoint planned) |
| T080: the read-back widening, with T067a L8, as one change | filed #446, one issue for both |
| T080: SA-3's remainder | filed #444 |
| T080: the list in T146's record | source (c) above |
| §1: P0-11 | folded into #453 |
| §1: P0-12 | `fail`'s `counts.open` folded into #450; the `module-signatures.md` half was done in W3 |
| §4: SA-4 through the renderers' `os.replace` | fixed in PR 1 (W6 batch, P1-2) |
| §4: FX-5's effort-estimate check, and D2's text | fixed in PR 1 (W6 batch, P1-4) |
| §4: T067b's early-`reconcile` warning (H2's option) | not filed: accepted as is, no code |
| §4: T067b's read-back of each copied value | PR 1 (W6, P1-4's standing rule) |
| §4: T067a's read-back of legacy prose | filed #446 |
| §4: T067b L8, a copied peer's `score-source` | fixed in PR 1 (W6 batch, P1-5) |
| §4: T067b M1, option (b) | not filed: not needed, option (a) stands |
| P1-8: a test docstring quotes D2's old rule ("T080, or with the W6 batch") | fixed in PR 1 (W6 batch) |

### (e) Session S1's handoff (`8fbfa9f`), "T080 follow-ups"

| Item | Disposition |
|---|---|
| `check-citation-urls.py` imports `yaml` at module level | folded into #452 |
| Older `tachi-pytest.yml` `paths:` gaps | folded into #452: `tests/conftest.py`, `asset-modifiers.md`, `extract-report-data.py` and the two `__init__.py` files |
| `stride-categories-shared.md`'s missing roster rows | folded into #453 |
| The adapter `VERSION` hashes (#369) | folded into #427, which joins #369's family and names the manifest's missing `risk-scorer.md` entry. The 14 manifest hashes match their sources at `401078a` (checked), and #369 owns the CI integrity check |
| `WIRED_BY_T047` in `test_contract_text_374.py` is now inert | folded into #451 |
| `CI_CD_GUIDE.md` lacks the f374 modules | not an issue: done here |
| P0-10 | not filed: fixed in W3 (`a41baeb`, ruling Q9) |
| P0-11 | folded into #453 |
| P0-12 | folded into #450 (the `counts.open` half) |
| W3's heading-capture ruling: the extractors' older lookups go to T080, "ranked above P0-10" (`w3-p0-fixes.md`) | filed #455 |

### (f) Session S2's handoff (`acdceef`), "T080 follow-ups"

| Item | Disposition |
|---|---|
| S1's list, and T146's "Deferred" list | sources (e) and (c) |
| From P1: SA-1's residual, the `https%3A//` hardening, P1-3, the read-back widening with L8, SA-3's remainder | #445, #450, not filed (in PR 1), #446 and #444, as in (d) |
| U-2's colon-form title | filed #437 |
| A list-form Section 7 with no baseline, a PM question | filed #438 |
| Merging correlation groups that share a member (an idea) | folded into #456 |
| T065's O4: the fixture's stale `source_file` | folded into #441 |

### (g) The current NEXT-SESSION.md, "T080", session L's three additions

| Item | Disposition |
|---|---|
| `test_tachi_parsers`' 5,000-deep JSON case fails on Python 3.12 and later | folded into #442 |
| The control analyzer's agent file still asks for scan limits in its reply (AW5-8's residual) | folded into #439 |
| The runbook's section 11 has no entry for the 2026-11-24 run | filed #459 |
| S-16's KB entry (Entry 27) with W5's true-max evidence | not an issue: written here |

### (h) The PM's W6 rulings

| Item | Disposition |
|---|---|
| Q1 (P1-3) | not filed: the fix moved into PR 1, and its fallback title stays unused |
| Q2 (P1-6) | nothing for T080 |
| Q3(a): reference sub-sections that neither run writes | no follow-up of its own: the template marking rides #435 |
| Q3(b): "no mapped threat" controls | filed #435, under the PM's title with the `enhancement:` prefix, covering the four body points |
| Q4: a first run's `threats.md` has no `delta_status` | filed #436, under the PM's title with the `defect(pipeline):` prefix, covering both halves and the acceptance. It replaces §7 item 7 |

### (i) The deferred review and scan findings

**T067a (the shared core):**

| Item | Disposition |
|---|---|
| M1, M2, M3 | fixed in PR 1 (T146) |
| L1: three fence scanners | folded into #447 (with EC-10) |
| L2: two readers of the baseline SARIF's vectors | folded into #447 (with EC-8) |
| L3: duplicated strict-JSON hooks | folded into #443 (with EC-13) |
| L4: one provenance stamp, two validators | folded into #443 |
| L5: registry constants that no shipped code reads, and a dead `prefix_for` | folded into #443 |
| L6: PEP 604 annotations in `tachi_scoring.py` | folded into #453 |
| L7: `self_check` and a non-object `relatedLocations` entry | folded into #450 |
| L8: a legacy rationale led by `**` or `---` | filed #446 |
| L9: the declared-paths snapshot grows until the check switches off | filed #448 |
| L10: negative narrative cases pin only that a problem exists | folded into #451 |
| N-a to N-e, the notes for part (b) | as T067b assessed them: L4 (#449), L5 (scorer site fixed in T146; controls site #447), H2 (fixed in T146), I1 (below) and L6 (#451) |
| The open question on legacy prose at the read-back | filed #446 |

**T067b (the renderers and contract surfaces):**

| Item | Disposition |
|---|---|
| H1, H2, M1 (option a), M2, M3 | fixed in PR 1 (T146) |
| L1: the renderers' copied scaffolding | folded into #443 (EC-1) |
| L2: P0-11's helper list in one command of three | folded into #453 |
| L3: four `.md`–`.sarif` pairs the scorer doesn't compare | folded into #450 |
| L4: escaped text inside code spans | folded into #449 |
| L5: plain `json.loads` on input SARIF | the scorer site fixed in PR 1 (T146, with T067a M3); the controls site folded into #447 (EC-5) |
| L6: literal U+202E in the controls tests | folded into #451 |
| L7: `tests/conftest.py` missing from `tachi-pytest.yml`'s `paths:` | folded into #452 |
| L8: a copied peer's `score-source` | fixed in PR 1 (W6 batch, P1-5) |
| L9: 45-plus renderer tests accept exit 0 or 5 | folded into #451 |
| I1: `module-signatures.md` cites a retired generator | not filed: a pointer in a frozen feature record, not shipped text. The file it names is gone, so the pointer reads as history, and the record's next amendment can repoint it |
| I2: two scorer lookups that aren't fence-aware | folded into #447 (EC-9) |
| I3: the controls renderer's docstring and help | folded into #453 |
| I4: the `CF` instruction | folded into #453 |
| I5: Step 1.5's bare `{input_file}` | folded into #453 |
| The open questions (H2's warning, the standing rule, M1's option (b), L8) | ruled at the P1 checkpoint: source (d) |

**T064 (the security advisory):**

| Item | Disposition |
|---|---|
| SA-6 | folded into #447 |
| SA-9 | folded into #449 |
| SA-12 | folded into #443 |
| SA-14 | folded into #448 |
| SA-15 | folded into #448 |
| SA-16 | filed #458 |
| SA-17 | folded into #449 |
| SA-18 | folded into #458 |

**T068 (the Step 7 scan):**

| Item | Disposition |
|---|---|
| O-4: pre-existing quadratic patterns in the extractors and the parser | filed #454, which also notes O-3's crash paths (one half is #388's) |
| O-1, beyond the brief: `evidence_path_problem` has no caller | folded into #443's dead-code item |

### (j) The Step 8 economy gate (`economy-check.md`)

| Item | Disposition |
|---|---|
| EC-1: the entry plumbing | folded into #443 |
| EC-2: the declared-paths copies' stale lookup | fixed in PR 1 (W6) |
| EC-3: one capped reader that follows no link | folded into #443, with SA-12 |
| EC-4: one forbidden-character walker | folded into #443, with SA-12 |
| EC-5: `_sarif_details`' own reader | folded into #447 |
| EC-6: the hand-kept pairs | folded into #443 |
| EC-7: the layer and zone chain | folded into #447 |
| EC-8: the renderer's `_sarif_vectors` | folded into #447 |
| EC-9: D3's two-step lookup | folded into #447 |
| EC-10: the three fence rules | folded into #447 |
| EC-11: `expected_file_problem` has no caller | folded into #443 |
| EC-12: `percent_encode` is `urllib.parse.quote` | folded into #443 |
| EC-13: the strict-JSON hooks | folded into #443 |

The timing is stated in the bodies: #443 is one change at PR 2's start, before PR 2's new entry scripts copy the plumbing again, and #447 is post-merge, item by item, with the oracle's re-run.

### (k) Other T080 pointers in tracked text (a search for "T080")

| Item | Disposition |
|---|---|
| ADR-050 Known limitations: a drift form's carried threat text (U-2) | #437 |
| ADR-050 Known limitations: the SARIF fallback reports no repeated member | filed #456 |
| ADR-050 Known limitations: the extractors find a section by substring | #455 |
| ADR-050 Known limitations: a flagged controls §2 cell (FR-K8.1's follow-up) | #432 |
| ADR-050 Known limitations: the rules' taxonomy links; spec W3 ruling 2c ("T080 files the alignment as a follow-up issue"); `contracts/sarif-result.md`'s taxa names; `sarif_common.taxonomy_name_for`'s docstring; S1's ASI01 rename note | filed #457 |
| Spec W3 ruling 2: a contracted rule `name` and `help` "could join T080's list of ideas" | folded into #457 |
| Spec W4 ruling R-F: merging groups that share a member | folded into #456 |
| Spec W4 example-defect table: "T080 needs no item of its own for the refresh" | not filed: it goes to #364 with T083's tail |
| ADR-050 Known limitations: SA-9, SA-15, SA-6 and SA-16 | #449, #448, #447 and #458 |
| `contracts/module-signatures.md`: SA-17, "a T080 note" | #449 |
| `w0-gate.md`: `check-citation-urls.py`'s `yaml` import | #452 |
| `w5-setup-pr1.md`, finding 1: T065's O4 class | #441 |
| ADR-050 Known limitations: S-16's follow-ups | #428 to #430 |
| `test_coverage_attestation_audit.py`: "ADR-037 (T080)" | not F-374's: an earlier feature's task number |

### (l) The architect's P2 checkpoint (W6, gitignored record), added after the first pass

| Item | Disposition |
|---|---|
| P2-1 (LOW): the escaped-pipe rule is stricter than GitHub's, but its words call it GitHub's | fixed in PR 1 (W6, the fix lane's text commit): the docstrings, `module-signatures.md`'s phrase and a test that pins the even-backslash form as a refusal |
| P2-2 (LOW): a Section 7 pipe can reach the controls agent's `matrix_row`, which can't hold one | filed #460, for PR 2 (Track O, beside the writer's pipe line) or the first patch. No issue in #427 to #459 covers it: #432 would remove the seam and #449 concerns the row's line breaks, so both are linked from it |
| P2-3(a): `contracts/part-files.md`'s `atomic_write` mode line | fixed in PR 1 (W6, the fix lane's text commit) |
| P2-3(b): the scoring skill's `score_source` lines | fixed in PR 1 (W6, the fix lane's text commit) |
| P2-3(b): the system-design README's copy, `docs/architecture/01_system_design/README.md:1662-1664` | fixed here (T080): `score_source` now says where a finding's scoring inputs came from, and a copied peer takes its primary's source (P1-5). The lines' count and the rest of the file are unchanged |
| P2-4 (INFO): the layer chain's Section 7 step, ruled right | not filed: a reading for the PM's records (T066, T079) |
| P2-5 (INFO): the ADR's W6 revision entry doesn't name W6's contract additions | not filed: one clause for the ADR lane at T080's commit |
| P2-6 (INFO, pre-existing): an unreadable output makes `plan` end in a traceback | filed #461. No issue in #427 to #459 covers it |

## Hygiene

- H1: no pytest, renderer or extractor ran. The lane used reads, greps, `git` queries, `gh` and one standard-library check of the adapter manifest's hashes, from the session scratchpad.
- H8, NFR-6: the titles and bodies hold no local path, no real target name and no finding or report content. The fixtures are synthetic.
- This lane changed four files in this worktree: this ledger, `docs/INSTITUTIONAL_KNOWLEDGE.md` (Entry 27), `docs/devops/CI_CD_GUIDE.md` and `docs/architecture/01_system_design/README.md` (lines 1662 to 1664). The two regenerated baseline files under `tests/fixtures/init-baseline-tree/` are T081's, and this lane left them alone. Nothing is committed, and nothing under `examples/` changed. The board cache that the issue script wrote is gitignored.
