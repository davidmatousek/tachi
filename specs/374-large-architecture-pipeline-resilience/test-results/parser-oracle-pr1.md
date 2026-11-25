# Lane P's data-layer oracle (T058, W2)

**Date:** 2026-11-23. **Pinned ("before"):** `e9bd0e1`, W2's base. It predates every lane-P change and holds gate G1's records. **After:** `ddc53cc`, the integration tip: T033 (the decoder), T048, T142 and its `properties.id` follow-up, T032 (the drift forms), T057 (both controls formats) and T143. **Method:** F-373's C-4, reused as written (`specs/373-adopter-install-output-fidelity/test-results-prestate.md`, whose appendix holds `snapshot.sh`, and `oracle-diff.md`). **Python:** 3.11.13. **Where it ran:** scratch clones only, one fresh clone per run, never a tracked tree (H1).

## Result: PASS. The extractors' data layer is byte-identical across the two SHAs, so no diff is unattributed

| Question | Result |
|---|---|
| Runs | 84 per snapshot: 12 shipped examples × (6 infographic templates + the report data). 84/84 exit 0 in all four snapshots (two per SHA), about 42 s each |
| Diff, `e9bd0e1` to `ddc53cc` | **0 of 168 files** (72 infographic JSON, 12 `report-data.typ`, 84 stderr), compared after F-373's normalization. stderr is 15,171 bytes at both SHAs: 52 `Warning:` lines in 10 distinct lines, the same multiset |
| Unattributed diffs | 0. There is no diff to attribute |
| Determinism | Two runs per SHA, and the normalized trees are byte-identical. The raw files differ only in `metadata.generation_timestamp` (N1) and `metadata.source_file` (N2, the clone path), in the 12 `executive-architecture` payloads |
| Could the oracle have seen a change? | Yes. A positive control through the same entry points shows T033's decode in the after clone only: 1 JSON leaf and 3 `report-data.typ` lines (section 3.1) |
| Why lane P's other changes don't move the data | They are unreachable from both extractors (T032's drift readers, T048, T142, T143), or they have no read site (T057's three keys). Section 3 gives the evidence |
| PDF baselines and PNGs | None regenerated and none committed. `examples/**` is clean in the main checkout and in the worktree. The four `--output` clones each re-rendered the same 48 tracked PNGs (#365). The `--build-dir` clones stayed clean |

## 1. Method (F-373's C-4)

**(a) Snapshot, diff, attribute.**

- **Snapshot.** F-373's `snapshot.sh`, extracted from its appendix with `sed -n '261,464p'` and run unmodified. For each tracked `examples/**/threats.md` directory it runs `extract-infographic-data.py` once per template (6) and `extract-report-data.py` once, both in `--output` mode, and keeps every run's output and stderr. No Typst compile ran, so no PDF exists. There are 12 directories, the same 12 at both SHAs, and no file under `examples/` differs between the SHAs, so only the code varies. Five examples run at tier 1 and seven at tier 3.
- **Normalization** is F-373's N1 (`generation_timestamp`) and N2 (an absolute path through a `/tachi/` segment becomes `<REPO>/`). Each clone sits in a directory named `tachi`, because N2 skips a path with no such segment (F-373 section 6).
- **One fresh clone per run.** The report extractor's `--output` mode renders attack-tree and attack-chain PNGs into the target directory, which is `examples/` of the clone (#365), so a second run in the same clone would start from changed PNGs. The two runs at each SHA are the determinism check that F-373 made at its pre-state.
- **Diff.** `diff -rq` over the normalized trees, 168 files each. F-373 classified every changed leaf, line and warning to a named K-item and reported anything unmatched as `UNCLASSIFIED`. Here no file changed, so there was nothing to classify. Section 3 does the attribution from the other side: for each lane-P change it asks whether an extractor can reach it, and where the change is visible.

**(b) Golden regeneration:** none was authorized and none was needed. **(c) PDF baselines:** untouched. 10 are tracked and 0 differ between the SHAs.

**Checks added to the method.** A clean diff proves little unless the instrument could have shown a change, so five checks sit beside it:

1. *Import closure.* An AST walk of each extractor's imports (lazy ones included), restricted to `scripts/`.
2. *Static reachability.* From the names each extractor imports from `tachi_parsers`, follow name references through function bodies, plus module-level code, and list which lane-P functions are reached.
3. *Reader level.* Call the readers that lane P changed, at both SHAs, over the shipped examples, the way the extractors call them.
4. *Static pin.* Scan every tracked text file under `examples/` for the decoder's closed set of references.
5. *Positive control.* A synthetic input, outside any clone, that the changed code must change.

## 2. Result per example

For every row, all 6 infographic JSON files, the `report-data.typ` and all 7 stderr files are identical at the two SHAs.

| Example | Tier | Findings | Notes |
|---|---|---|---|
| `agentic-app` | 3 | 81 | One GFM `\|` (`threats.md:230`), which D3 leaves undecoded |
| `agentic-app/sample-report` | 1 | 85 | One GFM `\|` (`threats.md:315`). Pre-fix controls format. 6 stage-ID and 2 row-count warnings, as at the pinned SHA |
| `agentic-app/test-output/2026-03-25T12-53-57` | 3 | 38 | |
| `ascii-web-api` | 3 | 11 | |
| `consumer-agent-app/sample-report` | 1 | 19 | Section 7 is a numbered list under `## Section 7: ...`, a T032 drift form. The extractors warn 7 times that they find no Recommended Actions table, at both SHAs. Pre-fix controls format |
| `free-text-microservice` | 3 | 15 | |
| `maestro-reference` | 1 | 110 | Section 7 lists I-17 twice (lines 536 and 556), unchanged. Pre-fix controls format |
| `mermaid-agentic-app` | 3 | 19 | |
| `microservices` | 3 | 23 | |
| `mobile-banking-app/sample-report` | 1 | 31 | Pre-fix controls format |
| `predictive-ml-app/sample-report` | 1 | 43 | Section 7 is a numbered list, a T032 drift form. 7 no-table warnings, at both SHAs. Pre-fix controls format |
| `web-app` | 3 | 16 | |

All 52 warning lines are data-shape properties of these fixtures and were present at the pinned SHA.

## 3. Attribution by cause

| Cause | Task | Reachable from an extractor? | Data-layer diff | Section |
|---|---|---|---|---|
| Shared reference decoder | T033 | Yes: `parse_markdown_table`, `_find_table_with_column`, the controls recommendation and evidence text, the attack-chain text, the report's executive narrative, and both extractors' own table readers | 0 | 3.1 |
| Drift forms | T032 | Only the split of `parse_threats_findings` into `_findings_from_section_7_rows`, which keeps its `[]`-with-a-warning behavior. `parse_reference_set`, the numbered-list reader and the `## Section 7:` heading reader are not reachable | 0 | 3.2 |
| Controls formats | T057 | Yes: `parse_compensating_controls_md` and `_resolve_k8_fields`. The three new keys have no read site | 0 | 3.3 |
| Correlation groups | T048 | No | 0 | 3.4 |
| SARIF fallback reader; persisted-controls reader | T142, T143 | No | 0 | 3.4 |
| Everything else between the SHAs | other lanes | No | 0 | 3.5 |

### 3.1 T033, the decoder

- **Static pin.** Of 434 tracked files under `examples/`, 349 are text (85 binaries skipped). None holds one of the decoder's eight closed references (`&amp;`, `&lt;`, `&gt;`, `&#124;`, `&#96;`, `&#123;`, `&#10;`, `&#35;`, read from `tachi_parts.ESCAPE_REFERENCES`). This is what `test_no_shipped_example_holds_a_reference_the_decoder_would_change` pins. The only two `\|` are the two lines T033 names, and the data of both examples is identical.
- **Positive control.** A synthetic copy of the `web-app` example, with references appended to two Section 7 cells, ran through both clones' extractors (the baseball-card template and the report data). The appended text was `x &lt;b&gt; &amp; c &#124; d &amp;lt; e` in one cell and ``y &#96;code&#96; &#123;{z}&#125; &#35;h`` in the other. The before clone keeps both verbatim. The after clone gives `x <b> & c | d &lt; e` and ``y `code` {{z}&#125; #h``. Exactly 1 JSON leaf (`top_findings[1].threat`) and 3 `report-data.typ` lines changed. `&amp;lt;` decodes once, so there is no double decode, and `&#125;`, which is outside the closed set, stays as written. The stderr of both runs is identical.
- So the zero diff over the shipped examples is the expected outcome of an input with nothing to decode, and the oracle does detect the decoder.

### 3.2 T032, the drift forms

- **Reader level.** `parse_reference_set` over the 12 examples. Ten read identically at both SHAs. Two change, as T032 intends: `consumer-agent-app/sample-report` and `predictive-ml-app/sample-report` go from `ReferenceSetError` to readable in the list form (19 and 37 open findings). They are the only two examples whose Section 7 isn't a table, and they are the source of the 14 `could not find Recommended Actions table` warnings in the extractors' stderr, which are identical at both SHAs. The extractors keep `parse_threats_findings`'s `[]` with a warning, as T032 requires (`test_the_wrapped_parser_keeps_its_empty_list_and_warning_for_the_extractors`).
- **`maestro-reference`'s repeated I-17.** The reader returns `duplicates == ["I-17"]` at both SHAs and keeps the first row (line 536; the repeat is at line 556). This is the "duplicate reference-set ID, first row wins" case. Its warning is the stage's (`lists I-17 more than once; the first row is used`), not an extractor's: no extractor run at either SHA names I-17 or says "duplicate" (0 of 84 stderr files at each). So no data-layer diff was attributed to it, and none could be.

### 3.3 T057, the controls formats

- **Reader level.** `parse_compensating_controls_md` over the 5 controls files, called as the extractors call it (composites joined from `risk-scores.md`). 0 leaves removed or changed, and 864 added: 288 findings × 3 keys (`maestro_layer`, `control_category`, `carried_forward`). Every shipped controls file is the pre-fix format (header `Threat ID | CF | Component | ...`, with no `MAESTRO Layer` or `Control Category` column). So `maestro_layer` and `control_category` are `""` on all 288 findings, and `carried_forward` is `False` (every CF cell is a dash). The stderr of those calls is identical.
- **Read sites.** Neither extractor mentions `control_category` or `carried_forward`. Every `maestro_layer` read in them is on rows the extractors build from the threats.md MAESTRO table, or on attack-chain members, never on controls findings. The commit that carries T057 changed `scripts/tachi_parsers.py` and its tests only, so bringing the extractors' readers in line needed no extractor edit.

### 3.4 T048, T142 and T143

`parse_correlation_groups` and `_assign_correlation_groups` (T048), `parse_sarif_member_set` and `_load_sarif` (T142), and `parse_controls_assessment_inputs`, `_controls_item` and `_controls_input` (T143) are not reachable from either extractor, by the static reachability walk. The infographic extractor keeps its own Section 4a reading in `deduplicate_findings` (the report extractor reads no Section 4a), so these functions cannot move the extractors' data until a stage or an extractor calls them.

### 3.5 Everything else between the two SHAs

- Each extractor loads exactly three scripts: itself, `tachi_parsers` and `tachi_parts`. `tachi_parts`' changes are in part intake (`_prose`, `_evidence_entry` and an import), and `tachi_parsers` uses none of those names. `sarif_common`, `tachi_scoring_rules` and `tachi-stage` are never loaded. `tachi_parsers` mentions `sarif_common` in docstrings only.
- The only commit that touched an extractor is T033's. The other changed paths outside `scripts/`, `tests/` and `specs/` are agents, commands, risk-scoring skill references, the ADR and the two `output-schemas` templates. Neither extractor reads any of them. Their other inputs (`templates/tachi/infographics/`, `templates/tachi/security-report/`, `schemas/taxonomy/`) have no changed file.

## 4. Cross-check in `--build-dir` mode

`--help` documents a second report-extractor mode, `--build-dir`, that "only reads TARGET_DIR" and renders its PNGs under the output directory. Run in two more fresh clones over the same 12 examples: 12/12 exit 0, 12/12 `report-data.typ` identical across the SHAs (even before normalization, because the paths are relative), 12/12 stderr identical. `git status` in both clones shows nothing, so `examples/**` stays clean in the clone itself. Against `--output` mode at the same SHA, the only differences (242 lines across 12 files) are image and brand path fields, with 0 unclassified.

## 5. H1 and H2

- No pytest, extraction or render ran in a tracked tree. The only invocation there was each extractor's `--help`, which extracts and renders nothing and left no file. Every other run was in a scratch clone. The one pytest run was `tests/scripts/test_tachi_parsers.py` in a scratch clone of the tip: 443 passed, so every test that this record cites passes.
- `git status` after each run. The four `--output` clones: 48 modified tracked PNGs each, the same 48 (`agentic-app/sample-report` 15, `mermaid-agentic-app` 12, `maestro-reference` 9, `mobile-banking-app/sample-report` 8, `consumer-agent-app/sample-report` 4), and no other entry. That is #365 happening in throwaway clones. The two `--build-dir` clones, and the positive-control runs against a directory outside any clone, left nothing.
- Main checkout and worktree: `git status --short -- examples` is empty in both, and the worktree holds only this record. Nothing was committed, pushed, stashed or switched. No PDF baseline was regenerated and no PNG was committed.

## 6. What this oracle can't see

- T032's list and heading readers, T048, T142 and T143 are not called by either extractor, so this oracle can't move on them. Section 3.2 covers T032's at reader level. For all four, `test_tachi_parsers.py` is the coverage, including its shipped-sample cases for Section 4a and the shipped SARIF files. The stage-level consumers get their own oracles (T066, T121).
- No shipped example is in K8's controls format, so T057's K8 half is covered by T057's own cases, not by this oracle. `test_every_shipped_controls_file_reads_as_the_pre_fix_format` pins that every shipped file is pre-fix.
- The snapshot ran on Python 3.11 only. The `--build-dir` cross-check covers the report data and not the infographic JSON, which has no such mode.

## 7. Re-running

```bash
# the directory that holds each clone must be named tachi (N2)
git clone --quiet <repo> <before clone> && git -C <before clone> checkout --quiet e9bd0e1
git clone --quiet <repo> <after clone>  && git -C <after clone>  checkout --quiet ddc53cc
sed -n '261,464p' specs/373-adopter-install-output-fidelity/test-results-prestate.md > snapshot.sh
PATH=<python 3.11 bin>:$PATH bash snapshot.sh <before clone> <out dir>/before
PATH=<python 3.11 bin>:$PATH bash snapshot.sh <after clone>  <out dir>/after
diff -rq <out dir>/before/norm <out dir>/after/norm      # empty: byte-identical
git -C <after clone> status --short                      # the PNG churn, if any (#365)
```

For a determinism check, repeat each snapshot in a second fresh clone. For T066 and T121, prefer `extract-report-data.py --build-dir out/<slug>/.tachi-build/security-report` over `--output`, so that the clone's `examples/` stays clean.
