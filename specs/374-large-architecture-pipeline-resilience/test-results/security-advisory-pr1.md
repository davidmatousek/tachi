# Security advisory for PR 1: part validation and path handling (T064, W3)

**Date:** 2026-11-23. **Reviewer:** security-analyst, lane SEC. **Tip reviewed:** `1493efb`, the W3 preview integration (PR 1's W2 tip plus every W3 lane commit so far). Two W3 pieces were still landing: the scorer renderer's P0-5 and P0-6 changes, and T054's retirement of the old SARIF generator. Neither changes part validation or path handling, so this record stands for the final W3 tip unless one of them touches the functions named below.

**Status: advisory, nothing blocks PR 1.** No CRITICAL and no HIGH finding. **2 MEDIUM, 11 LOW and 5 INFO.** The two MEDIUM findings and the one-line LOW fixes are worth landing before PR 1 merges (T146). The rest go to T080.

**Scope.** The five files T064 names, as production code (C-9, TL-T5). This overrides the knowledge-system supplement's "no application code" framing, as F-373 and F-391 did.
- `scripts/tachi_parts.py`, `scripts/tachi-stage.py`, `scripts/sarif_common.py` (the resolver), `scripts/render-risk-scores.py` and `scripts/render-compensating-controls.py`.
- Also read, because the planner and both renderers take part of their character and path decisions from them: `tachi_parsers.parse_controls_assessment_inputs`, and `tachi_scoring_rules.read_baseline_scores`, `resolve_baseline` and `check_run_file`.
- Not reviewed: PR 2's writers, the agent specs and #360's prompt-injection surface, `tachi_scoring.py`'s arithmetic, `populate-affected-assets.py`, the command texts' shell quoting, and the old SARIF generator (T054 retires it).

**Method.** Reading, then probes, all in scratch clones of `1493efb` (H1). No tracked tree was run, and the lane's `git status` stayed clean (H2). Fixtures are synthetic (H8).
- **Characters.** Every Unicode scalar value was run through `forbidden_character`, and the 29 `str.isspace()` characters through the P0-1 guard.
- **Escapers.** A property fuzz of `escape_prose` and `escape_cell`: 1,500 adversarial strings against the decoder's round trip, the next run's outline reader and `match_heading(outside_fences=True)`, and 250 of them against an independent GFM parser (pandoc). A mutation check weakened the guard three ways. Each mutant was caught by the prose-shape check and by pandoc, and two of them by the outline reader too, so the probe could have seen a regression.
- **Parts and paths.** 43 hostile parts through `classify_part`; 43 path cases in a scratch tree (symlinks to a file and to a directory, a FIFO, a hard link, a symlinked prefix, a colon, control and bidi characters in names); 10 `self_check` cases.
- **End to end.** 24 probes through the existing test harness (`plan`, synthetic parts, `reconcile`, render) for the scorer and the controls stage: baseline cells, a hostile `threats.md`, declared paths, a symlinked canonical output and `.tachi-build`, file modes, CRLF and BOM inputs, evidence file names, a symlinked SARIF fallback and a poisoned controls baseline. 24 passed. Each prints what it saw, so a pass is an observation and not an assertion.

---

## 1. The seven questions

### 1. P0-1's guard, item 1's intake strip and the dedent nit: all three CONFIRMED

- **The guard.** `_LINE_START_GUARD` (`tachi_parts.py:667`) leaves no `#` or `~` at the start of a prose line after any whitespace but a newline.
  - No miss across the 29 `str.isspace()` characters, with zero, one or two of them before each marker.
  - 1,500 adversarial strings against three oracles, and 250 of them against a fourth, with zero failures. The three are the decoder round trip (`decode_references(escape_prose(x)) == x`, and the same for cells), `_outline` and `match_heading(outside_fences=True)`. The fourth is pandoc's GFM parser (no skeleton heading lost, no fenced block, no table forged).
  - The mutation check: with the pre-P0-1 guard, with spaces and tabs only, and with `#` alone, the probe fails 40, 10 and 34 prose-shape cases of 700, so it has power. The spaces-and-tabs mutant is not seen by `_outline` (which strips only spaces and tabs) and is seen by pandoc, through a line that starts with a carriage return and then `~~~` (pandoc drops the CR and reads a fence). The real guard covers that line, because a carriage return at a line start is whitespace to it.
  - A direct pandoc check shows that a no-break space or an ideographic space before `~~~` or `##` is not block syntax, where a space or a tab is. So W3's widening to any whitespace is for tachi's own readers that strip every whitespace character, as the ruling says, and not for GitHub-style rendering.
- **A dependency to state in D3.** `(?m)^` anchors after the line feed only. A carriage return, `U+2028`, `U+0085`, VT, FF or FS to US *between* two lines is not a line start for the guard, and the guard doesn't claim it is (probe: a CR and a `U+2028` between two lines come out unchanged). CommonMark counts a lone carriage return as a line ending, so text, CR, `## H` would be a heading on a spec-conformant renderer. It is safe because those characters never reach the guard: step 10 refuses them in a part, the intake refuses them in an input, and `_check_staged` scans the whole file for them. The ADR lane should say so, because the guard is then no second line for forged line breaks.
- **Item 1's strip.** `_prose` (`:951-977`) cuts, dedents and strips, then runs step 10. Edge `U+2028`, VT, FF, FS, no-break and ideographic spaces are dropped without a flag. The same characters inside a value reject the part, and a closed value is never stripped (a `zone` with an edge VT is rejected). No forbidden character reaches an output through the strip.
- **The dedent nit.** `'        return x\n    def f():'` is kept as `'return x\ndef f():'`. Cosmetic, no security effect, accepted at W1.

### 2. P0-4's forbidden set: CONFIRMED as the contract's set, with one extension (SA-7)

- **The set** (`:877`) is 77 code points: `U+0000-0008`, `U+000B-001F`, `U+007F-009F`, `U+061C`, `U+200E-200F`, `U+2028-202E` and `U+2066-2069`.
- **It is complete for its three classes.**
  - Terminal controls: C0, DEL and C1.
  - Line breaks: every boundary of `str.splitlines()`, YAML 1.1 and JavaScript (`\r`, VT, FF, FS to RS, NEL, LS, PS). `\n` and tab stay allowed, as designed.
  - Trojan Source (CVE-2021-42574): `U+202A-202E` and `U+2066-2069`, with the three directional marks.
- **Not in it:** 151 other format characters. The one with a live argument is the Unicode tag block (`U+E0001`, `U+E0020-E007F`): invisible, ASCII-bearing, and accepted by step 10 today. SA-7 recommends adding `U+E0000-E007F` only. Variation selectors (`U+FE0F` is everywhere in emoji text) and the joiners (legitimate in several scripts) should stay out.

### 3. The baseline-cell outcome: recommend dropping the row to Input Issues, in the shared reader

Keep exit 2 for `threats.md` and `threats.sarif`, which are primary inputs. For a baseline, drop the row.

- **Why drop.**
  1. **Availability, by the design's own rule.** S-12(d) says an unreadable baseline "never stops the run", and a single unreadable row already goes to Input Issues and is scored fresh. A human-edited owner cell that carries a pasted `U+200E` (a copy from a document or a chat can bring one along) is the same kind of unreadable. Exit 2 holds a CI gate until someone edits an archived run directory, and a contributor who can commit a baseline can hold it indefinitely.
  2. **One partition (D2).** Today the planner routes the finding as carried, and the renderer refuses after the agents ran (probe A, five characters: plan 0, reconcile 0, render exit 2). A drop in `read_baseline_scores`, which both sides call, makes the planner send the finding to the agent and the renderer score it fresh. No wasted run, and the partition stays one.
  3. **The sink guarantee is unchanged.** The row is not read, so none of its text reaches any output. The issue names the finding, the field and the code point, never the character (`_quote` already uses `repr`).
  4. **The loss is bounded and visible.** One finding's owner, SLA, disposition and review date reset, and the old baseline file is untouched. It must be loud: a stage-record warning (`baseline-row-dropped`, with the count and the first five IDs, so the run exits 5), the Input Issue, and a line in the summary. An attacker who can edit the baseline can edit those cells directly, so the drop gives no new capability.
- **How.** An additive keyword on `read_baseline_scores` (default off, so the controls stage's *scored input*, which is primary, still refuses). `_scorer_routing`, `_prepare_baseline` and the baseline half of `parse_controls_assessment_inputs` pass it on. A row whose text holds a forbidden character becomes an `InputIssue(finding_id, field, "forbidden-character", ...)` and is left out of `rows` and `resolved_rows`. A baseline SARIF vector with one is ignored, with an issue.
- **Test.** A two-run case: baseline owner with `U+200E`; the plan sends that finding to the agent; the render exits 5 with the issue and the warning; the output holds no such character and the owner is `Unassigned`; the planner's agent set equals the renderer's.
- **Considered and not recommended:** stripping the character (it changes a carried value and can join words, which the carry-identity rule forbids). **If the team prefers fail-closed,** keep exit 2 but move it into the same reader call so `plan` refuses too (SA-3). What it must not stay is a refusal that only the renderer makes.

### 4. The planner-side P0-4 gap: yes, refuse at plan time. For the controls baseline it is a defect (SA-1)

- **For `threats.md` and SARIF text it is a cost, not a hole.** Batch inputs are written with `json.dumps` (ASCII), so a `U+202E` reaches the agent as the six characters `\u202e` and an ESC as `\u001b` (probe B). The renderer then refuses the same value (plan 0, reconcile 0, render exit 2). Failing at plan saves a whole agent run, hours at W5's scale. Refuse the values the renderer refuses, with the same message, from one predicate (SA-3).
- **For the controls stage's carried results it is a defect.** The planner copies each UNCHANGED finding's persisted result into its unit row, and the agent copies it back verbatim. A forbidden character in it makes the copy `invalid` on every attempt, and `reconcile` re-dispatches the same batch until exit 4 (probe K, SA-1). Here the fix is not a refusal. A persisted result that isn't a valid part item is left out of the carry, and the finding is scanned fresh.

### 5. FX0-1b's first question: the listed-rows scope is enough today. Check every row once the check moves into the reader

- **Today.** Every read of `baseline.rows` and `resolved_rows` in the scorer renderer is by a listed finding's ID (`:787`, `:1167`, `:1254-1255`). `ids_in_any_row` holds allow-listed IDs and no text. Probe A2 puts `U+200E` in the owner cell of a finding the run no longer lists: exit 0, and no such character in either output.
- **Recommendation.** With the Q3 reader drop the check covers every row the reader returns at no extra cost, and a finding that returns next run is covered the first time. If the refusal stays in the renderer, keep the listed-only scope: checking every row would refuse runs for text that no output reads.

### 6. The evidence-URI guard: sufficient for the evidence URI as built, and the primary URI has none (SA-11)

- **What protects an evidence URI.** Two layers do the work: `resolve_file` builds it from an `lstat` walk and `percent_encode`, and the controls renderer's `_check_sarif` (`:1816`) requires each related location to equal the resolver's URI. `self_check`'s `path_problem` call (`sarif_common.py:1298`) is a third.
- **What the third layer adds.** It refuses a scheme, a leading slash, `..` and a backslash (probe). On an encoded URI most of `path_problem`'s checks are vacuous, because `percent_encode` already writes `%5C`, `%60` and `%3A`. The live ones are the leading slash and `..`. It does not catch `%2e%2e` or `%2E%2E`, which is the marker's stated limit and is safe while the emitter encodes `%` as `%25`.
- **Sinks that lack it.**
  1. **The primary `artifactLocation.uri` of every result, in both files.** `self_check` compares it with the run's URI and never tests it. A primary URI of `https://...`, `/etc/passwd` or `../x` passes (probe). The scorer's SARIF has no other path, so for that file the guard covers nothing. Both renderers take the URI from the resolver, so this is defence in depth, and the primary URI is the one GitHub uses for alert identity.
  2. **The evidence `message.text`** carries the unencoded canonical path (`EVIDENCE_MESSAGE`). It is JSON-escaped and the forbidden-character scan covers it, but `path_problem` doesn't.
  3. **`format_architecture_source_line`** (`sarif_common.py:509`) writes a path into `threats.md` after `path_problem` alone (SA-8).
- **Sinks that have it:** the resolver, `check_run_file`, `_flag_run_dir`, `expected_file_problem`, the part validator (syntax) and the controls renderer (filesystem).

### 7. The declared-paths check, symlinks, `os.replace` and TOCTOU

- **Declared paths (exit 5).** It reports an undeclared file when the snapshot exists (probe C1: `evil.sh` after the plan is listed, exit 5). It is detective by design (ADR-050 D4, KB 17). Three limits: one odd name disables it (SA-5), it sees `--out` and nothing else (SA-14), and exit 5 is also the code for every ordinary warning, so it doesn't say which happened.
- **Symlinks.** None is followed on a write path. A symlink at a canonical output name is replaced and its target is untouched (probe D: the target kept its content). A symlinked `.tachi-build` makes `plan` exit 2 (D2). Parts, plans and pointers are read with `O_NOFOLLOW` after an `lstat` walk. The resolver refuses a symlink at any component, a FIFO and a directory, and takes an absolute path only through an ancestor that is the working directory by identity. The derived SARIF siblings are the exception (SA-10). A hard link to an outside file passes, which no check can see.
- **`os.replace`.** Sound: the temp file is created `O_EXCL` in the target's directory, the replace is atomic per file, and a half-applied pair is what `fail` undoes. One regression: the replaced file loses its mode (SA-4).
- **TOCTOU between plan and render.** Digest-pinned inputs are read and hashed in one pass by `_read_plan_input`, and a renderer then re-reads one of them to parse it (SA-6). The architecture file is a known limit (P0 record). The part files are re-validated at render and not pinned (SA-15). A swap between a check and the next `open` needs write access to `--out`, and with it an attacker has the canonical files. No race gives more than that.

---

## 2. Findings

Each finding gives where, what I saw, the fix, the owner and the effort. FX0 owns `tachi_parts`, `tachi_parsers`, `tachi_scoring_rules` and the scorer renderer. R2 owns the controls renderer. R3a owns `tachi-stage.py` and `sarif_common.py`.

### MEDIUM

**SA-1. A forbidden character in a baseline controls result reaches the agent, and its batch fails on every attempt.**
- **Where.** `tachi-stage.py` `_controls_baseline` (`:596-621`) and `_controls_units` (`:687-688`). `tachi_parsers.py` `_controls_input` (`:1955-1996`) checks the closed values only, and `parse_controls_assessment_inputs` (`:2046`) says narrative and evidence text is "re-validated where it is used". The use is the agent's verbatim copy into a part.
- **Saw (probe K).** One `U+202E` in one persisted summary of a baseline `compensating-controls.md`, with all 11 findings UNCHANGED. `plan` exits 0 with an empty stderr, and that finding's unit carries the value. An agent that copies the carried result, as the contract tells it to, writes a part that step 10 rejects. `reconcile` re-dispatches the batch unchanged: exit 3, exit 3, then exit 4 with all 11 findings of the batch exhausted. A re-run repeats it, because the baseline doesn't change.
- **Impact.** A deterministic denial of the controls stage by anyone who can edit the baseline file, and three dispatches of a whole batch before it shows. The same holds for any persisted value that fails the part validator's other item checks: a `matrix_row` with the wrong cell count, or a `recommendation_body` that lacks a key.
- **Fix.** Give `tachi_parts` a public `check_item(stage, item)` that runs the stage's `_PAYLOADS` validator on a deep copy and returns the `PartError` detail or `None`. Call it in `parse_controls_assessment_inputs` on each assembled item. A failing item goes to `errors` and is left out, which the planner already treats as "scanned fresh" with a warning. Then the docstring's promise, "an item that comes back could be a part's", is true.
- **Owner and effort.** FX0 (`tachi_parts`, `tachi_parsers`), R3a (the planner's warning and a test). 0.15 d.
- **Tests.** `test_tachi_parsers.py`: a persisted item with `U+202E`, with a `\r`, with a `matrix_row` of 10 cells and with a keyless `recommendation_body` each lands in `errors`. `test_tachi_stage.py`: the plan warns, and the unit carries no `evidence`.

**SA-2. One unusable evidence path ends the controls render with exit 2, after every agent has run, and a retry can't fix it.**
- **Where.** `render-compensating-controls.py` `_evidence_path` (`:961-974`), the only caller of the filesystem check. `tachi_parts.evidence_path_problem` (`:428`) is written for this and has no caller in any script. The part validator checks syntax only (`:1013`).
- **Saw (probe I).** A cited file that is a symlink, and one that doesn't exist, each give exit 2: "evidence 1 of S-2 names a file that is not usable under the target". Nothing is written, which is the right failure. Re-running the command re-dispatches every agent, and the same citation tends to come back.
- **Impact.** A hallucinated path is the commonest LLM failure, and F-374 exists to make large runs survive. At W5's ~150 dispatches one bad citation discards all of them. A hostile repo can plant a symlink where the agent is likely to cite (`README.md`). It is an availability finding. Nothing unsafe is ever written.
- **Fix.** Move the check to where retry exists. `reconcile` runs `evidence_path_problem(file, plan.refs.target)` on each evidence entry of a `done` controls part and treats a failing part as `invalid`, so the existing retry (cost 1) re-dispatches that batch only. R2 keeps its render-time check as the backstop, since the target can change in between.
- **Owner and effort.** R3a (`reconcile`), FX0 (a `read_part` hook or a helper in `tachi_parts`), R2 (keeps the backstop). 0.15 d.
- **Tests.** `test_tachi_stage.py`: a done part citing a missing, a symlinked and a directory path reconciles as pending, then as exhausted at the third attempt. `test_render_compensating_controls.py`: the backstop still exits 2.

### LOW

**SA-3. P0-4's intake lives only in the renderers, so a plan dispatches work that the render then refuses.** (Q3 to Q5)
- **Where.** `render-risk-scores.py` `_refuse_forbidden_inputs` (`:474`, called at `:699`) and `_refuse_forbidden_baseline` (`:491`, `:714`). `render-compensating-controls.py` `_refuse_forbidden` (`:490`). The planner's `_unit_row` (`:224`) and `_sarif_unit_row` (`:250`, lone surrogates only), and `_scorer_routing` (`:477-510`).
- **Saw (probes A, B).** Five characters in a baseline owner, and a `U+202E` in a `threats.md` threat: `plan` exit 0, parts valid, `reconcile` exit 0, render exit 2 with a clean message that names the finding and the field and never the text.
- **Fix.** Hoist the shared predicate (SA-12): `tachi_parts.first_forbidden(value)`, then one `tachi_scoring_rules` function that walks what the renderer takes from `threats.md` (every field of each open and resolved finding, each finding's layer, and the Section 1 and 2 names). The planner calls it after `parse_reference_set` and exits 2 with the same message. Add the Q3 reader drop for baselines.
- **Owner and effort.** FX0 (the helper, the reader), R3a (the call), R1/R2 (switch to it). 0.25 d with Q3. **Test:** an agreement test that runs one hostile `threats.md` through the planner and the renderer and requires the same field, character and exit code.

**SA-4. `atomic_write` gives a replaced file the default mode, not the mode it had.**
- **Where.** `tachi_parts.py:1558`, used by both renderers' staged write and `os.replace`, and by `architecture-source`'s in-place edit of `threats.md`.
- **Saw (probe E).** `risk-scores.md` at `0600` before the render, `0644` after (umask 022).
- **Impact.** A threat model is sensitive. An in-place write keeps an existing file's mode and a replace does not, so an adopter's `chmod 600` is undone on the next run. Directory permissions usually govern, hence LOW.
- **Fix.** When the target exists, copy its permission bits to the temp file before the replace. The docstring's "the mode an ordinary write would" is true for a new file only. Ownership can't be kept without privilege, so say so. FX0. 0.03 d. **Test:** a `0600` target keeps `0600`.

**SA-5. One odd file name in `--out` switches the declared-paths check off.**
- **Where.** `tachi-stage.py:374` skips the whole snapshot when any name fails `path_problem`. ADR-050 D4 says the check is skipped "above 20,000 entries" only.
- **Saw (probe C).** A top-level `note:final.txt` (a colon in the first component) and a name with a backslash each give `out_snapshot: null`. A planted `evil.sh` is then not reported: `undeclared_paths` is empty, with one warning `declared-paths-skipped`, and the render still exits 5, as it does when the check finds a file.
- **Impact.** The check is the one detective control for an agent that writes an unexpected file under `--out`, and a repository can commit such a name. macOS writes names with a carriage return into customised folders.
- **Fix.** Keep the snapshot. Key an unrecordable name by a stable placeholder (`unrecordable:` and the SHA-256 of the name), and report it through the existing `undeclared-paths-unrecordable` warning when it is new or changed. Name the skipped case in the summary line, so exit 5 says why. R3a, with the two renderers' identical `_undeclared` (SA-12). 0.05 d. **Test:** an odd name present at plan time doesn't hide a planted `evil.sh`.

**SA-6. Inputs are read twice, with the parse and the digest on different reads.**
- **Where.** The scorer renderer's `_prepare_baseline` (`:800`) re-reads `baseline_risk_scores` after `_read_plan_input` (`:227`) verified it. The controls renderer's `_members_from_markdown` (`:635`) does the same for `risk_scores`. The planner's `_scorer_routing` (`:498` then `:500`) parses one read and hashes another, and `_controls_scored_input` (`:585-586`) hashes one and parses another.
- **Saw (probe F).** The baseline file is opened twice in one render.
- **Impact.** It needs a concurrent writer. The stamp's `input_digest` would then describe bytes other than the ones parsed. If the planner's routing and the renderer's then differ, one direction ends the render ("the parts hold no item", exit 4) and the other ignores the agent's item. I did not construct either race, so this is provenance, not a demonstrated safety gap.
- **Fix.** An additive `text` keyword on `read_baseline_scores`, as `_sarif_vectors(inputs[...])` already takes verified bytes. Callers pass what they hashed. FX0, with call sites in R1, R2 and R3a. 0.1 d. T080.

**SA-7. Unicode tag characters pass step 10 and reach both output files.** (Q2)
- **Where.** `tachi_parts.py:877`.
- **Saw (parts probe, probes G and H).** Tag characters in a narrative field are accepted by `classify_part` and written into `risk-scores.md`. In a cited file name they reach Sections 3 and 7 and the SARIF URI, percent-encoded. They render as nothing and carry ASCII to any later agent that reads the file, and the report stage's agent has Bash.
- **Fix.** Add `U+E0000-E007F` to `_FORBIDDEN_CHARACTERS`. The parts, the intake and both backstops follow the one definition. Update the contract list in `part-file-contract-shared.md` (T010's drift test), D3 step 10, and the tests. FX0, the contract lane and the ADR lane. 0.03 d.

**SA-8. `path_problem` and `forbidden_character` are two definitions of an unsafe character.**
- **Where.** `tachi_parts.py:212` refuses `Cc` only.
- **Saw (path battery).** A path with `U+2028`, `U+2029`, `U+200E`, `U+061C` or `U+202E` passes `path_problem`, relative or absolute, and `forbidden_character` refuses all five. It reaches `format_architecture_source_line` (the body line of `threats.md`), the typed `--out`, `--threats`, `--risk-scores` and `--target` checks, `check_run_file`, and the resolver (an existing file with such a name resolves, and its canonical path is raw in Sections 3 and 7 and in `message.text`).
- **Impact.** No raw character reaches disk: `_check_staged`'s whole-file scans refuse it with exit 4, and the message then reads as a defect and not as a refusal.
- **Fix.** `path_problem` returns `control-char` when `forbidden_character(value)` is not `None`, as well as for any `Cc`. FX0. 0.02 d. **Test:** each of the five.

**SA-9. Inline link and image syntax passes every escaper.**
- **Where.** `escape_cell` and `escape_prose` (`tachi_parts.py:782-800`) escape `& < > |`, the backtick, `{{` and a line-start `#` or `~`.
- **Saw (probes G, H).** A threat text of `[text](https://example.invalid/...)` and `![x](...)` appears verbatim in `risk-scores.md` and in the SARIF `message.text`. A cited file name `docs/[x](https:/...).md` is a live link in Section 7's Assessment Inputs table. The Section 3 "Detected in" line is a code span and inert.
- **Impact.** Hostile repository text can put a clickable link or an image beacon into a report that GitHub renders (images are proxied, scripts are stripped). It is no worse than v4.48.x, and `<` is escaped, so raw HTML and `<url>` autolinks are already out. Bare URLs link anyway.
- **Disposition.** A ruling, not a code defect. Escaping `[` would be a tenth reference and breaks ordinary text such as `a[0]` only if mishandled. Record it under Known limitations, or have the PM ask for the tenth reference. ADR lane, T080.

**SA-10. The derived input paths are opened through symlinks.**
- **Where.** `tachi-stage.py:455-467` (the `threats.sarif` beside `threats.md`) and `:574-577` (the `risk-scores.sarif` beside `risk-scores.md`), both through `_read_threats` (`:209`), a plain `open`.
- **Saw (probe O).** A `threats.sarif` that is a symlink to a file outside the run directory is planned (33 units) and recorded as the input path.
- **Impact.** The baseline files, `source_file`, the architecture file and the parts are all read without following a link. These two are derived paths in a directory a hostile repository may fill, and git stores symlinks. The content must parse as SARIF to have any effect, and parse errors don't echo content, so the exposure is small. `--threats` is typed by the operator and can stay as it is.
- **Fix.** Check a derived path with `tp.path_guard_problem(path, os.path.dirname(path))` before the read, or use the no-follow reader (SA-12). R3a. 0.05 d. **Test:** a symlinked sibling is refused with a warning, and the plan falls back or fails by the existing rules.

**SA-11. `self_check`'s URI guard covers the evidence URI only, and as written.** (Q6)
- **Where.** `sarif_common.py:1293-1303`, and the marker at `:1296`.
- **Saw (`self_check` probe).** Refused: a scheme, a leading slash, `..` and a backslash in an evidence URI. Passed: a primary URI of `https://evil.invalid/x`, `/etc/passwd` and `../x`, and `%2e%2e` or `%2E%2E` in an evidence URI.
- **Fix.** Run `path_problem(uri)` on the primary URI too, and `urllib.parse.unquote` each URI before the check, which retires the marker. Keep R2's equality check. R3a. 0.03 d. **Test:** each passed case above is refused.

**SA-12. Security-relevant helpers are copied across files.**
- **Where.** `_first_forbidden` is identical in both renderers (`render-risk-scores.py:401`, `render-compensating-controls.py:464`). The no-follow reader exists four times (`tachi_parts._read_regular_file`, both renderers' `_read_text_file`, `tachi_scoring_rules._read_bytes`). `_walk` and `_undeclared` are in both renderers and in `tachi-stage.py` (`_walk`, `_undeclared_paths`), and `_relative` is in both renderers.
- **Why it matters.** SA-1, SA-3, SA-5 and SA-10 each need a change in these. With copies, a fix lands in one and a stale copy stays. W1 already moved `is_declared_path` and `retry_history` into `tachi_parts` for this reason, and the Rule of Three is met.
- **Fix.** Promote `first_forbidden`, the no-follow reader and the walk and undeclared check into `tachi_parts`. FX0, with call-site edits in R2 and R3a. 0.15 d. Best taken with SA-3.

**SA-13. `parse_affected_assets` splits lines with `splitlines()`.**
- **Where.** `sarif_common.py:162`. Every other reader splits on `\n`, and the module's own `_line_spans` says why (NFR-10).
- **Impact.** A `U+2028`, VT, FF, FS to RS, NEL or CR inside the block makes a phantom row. No effect today: S-13 compares the block with the architecture file's tags, or keeps only closed-set tags.
- **Fix.** `split("\n")`. R3a. 0.01 d.

### INFO

- **SA-14. The declared-paths check sees `--out` only.** An agent's Write tool reaches whatever the permission profile allows, and a changed file that fits the grammar (a rewritten `plan.json`, another batch's `inputs/*.json`) is not "undeclared". The digests (the plan against `--plan-digest`, each batch input against the plan) catch those two. The profile, not these scripts, is the confinement. ADR-050 D4 already frames the check as detective.
- **SA-15. Parts are not pinned between `reconcile` and render.** Render re-validates each part, so the content is valid either way, and any agent can write any batch's part. Two renders of one plan could differ if a late write lands between them. Recording each accepted part's SHA-256 in the plan is a plan-schema change, so not for PR 1.
- **SA-16. Evidence snippets and summaries are not checked against the cited file.** R2 resolves the path and never reads it. A prompt-injected controls agent can put text from elsewhere under a legitimate file name, such as a file reached through a symlink in the target. Requiring the snippet's first line to occur at `file:line` (after the dedent and strip) would also remove hallucinated evidence. It belongs with #360, so T080.
- **SA-17. `matrix_row` may hold `\n`.** Step 9 counts cells on `|` only. Probe J: the newline is written as `&#10;`, and a forged `## 4. Recommendations` is not a heading in the output. Reject `\n` in a row if you want the contract to say "one line".
- **SA-18. Error messages echo bounded, escaped hostile text** (`repr` and `ascii`) to the transcript that the orchestrating model reads. No script change. #360.

---

## 3. Checked and sound

So T070 need not repeat them.

- **`load_json` and the part limits.** `O_NOFOLLOW`, regular file and size cap before any parse. BOM, strict UTF-8, duplicate keys, `NaN` and `Infinity`, integers over 20 digits, nesting over 8 and surrogates (in the loader) are each refused. A FIFO at a part path is refused by the `lstat` walk, and a late swap to one by `O_NONBLOCK` and `fstat`.
- **Closed values and identifiers.** ASCII `fullmatch` allow-lists for every ID. A closed value is checked and never cut. The planned set must equal the part's, and the closed key sets reject every renderer-owned key.
- **The part's evidence `file`.** Absolute, parent, scheme, drive-letter, backslash, dot-only, NUL and over-length values are refused. A bidi mark, `U+2028` or a control character in it is refused by step 10.
- **The resolver.** A symlink at any component, a FIFO, a directory, an absolute path outside the working directory, a protocol-relative path and a `file:` URL are refused. A symlinked prefix of the base is accepted by identity, and a case variant takes the volume's spelling.
- **Write paths.** A symlink at a canonical output name is replaced and not followed. A symlinked `.tachi-build` is refused. The temp file is `O_EXCL` in the target's directory. `fail` moves only the stage's canonical names, only regular files, never overwrites, and puts back only a digest-matching pre-image.
- **The P0-4 intake.** All five tested characters refused for listed baseline rows and `threats.md` fields, naming the finding and field. An unlisted baseline row never reaches output (A2). CRLF `threats.md`, a CRLF baseline and a BOM baseline are not falsely refused (probes L, M, N).
- **The whole-file backstops.** Both renderers scan the raw markdown and every decoded SARIF string and key before any replace.
- **Frontmatter and messages.** `_quoted` writes `null` for anything not printable. Stage-record warnings and defect messages replace non-printable characters. The `_quote` of issue details uses `repr`.
- **`_check_staged` and the move.** The staged files are read back from disk and checked before either replace. A render that fails a check leaves earlier outputs in place (probe I: nothing written).

---

## 4. Dispositions

| Finding | Severity | Owner | Effort | When |
|---|---|---|---|---|
| SA-1 persisted controls result unchecked | MEDIUM | FX0, R3a | 0.15 d | PR 1 (T146) |
| SA-2 evidence path fails at render | MEDIUM | R3a, FX0, R2 | 0.15 d | PR 1 (T146) |
| SA-3 intake only in the renderers, plus Q3's reader drop | LOW | FX0, R3a, R1/R2 | 0.25 d | PR 1 (T146), with SA-12 |
| SA-7 tag characters | LOW | FX0, contract, ADR | 0.03 d | PR 1 (T146), one line |
| SA-4 file mode on replace | LOW | FX0 | 0.03 d | PR 1 (T146) |
| SA-5 snapshot skipped on one name | LOW | R3a | 0.05 d | PR 1 (T146) |
| SA-8 `path_problem` set | LOW | FX0 | 0.02 d | PR 1 (T146) |
| SA-10 symlinked derived inputs | LOW | R3a | 0.05 d | PR 1 (T146) |
| SA-11 primary URI and decoding | LOW | R3a | 0.03 d | PR 1 (T146) |
| SA-13 `splitlines` | LOW | R3a | 0.01 d | PR 1 (T146) |
| SA-6 double read | LOW | FX0 and callers | 0.1 d | T080 |
| SA-9 inline link syntax | LOW | ADR lane, PM | 0.02 d | T080, or Known limitations |
| SA-12 duplicated helpers | LOW | FX0, R2, R3a | 0.15 d | with SA-3, else T080 |
| SA-14 to SA-18 | INFO | none | none | T080 notes |

The PR 1 set is about 0.75 d with SA-12 taken alongside SA-3. The two MEDIUM findings and SA-3 are the ones I would not leave for after the merge.

---

## 5. Notes for T070 and the ADR lane

- **T070.** Re-check SA-1 and SA-2 as landed, and that the Q3 drop leaves the controls stage's scored input refusing. Probe K is the model for SA-1's test: a poisoned baseline, a verbatim-copy part, three attempts.
- **ADR lane.** (1) D3: the guard's dependency on step 10, the intake and the backstop for line breaks (Q1). (2) D3 step 10 and the contract list if SA-7 is taken. (3) D4's declared-paths bullet: the skip conditions as built or as fixed (SA-5). (4) Known limitations: inline links (SA-9), the declared-paths limits (SA-14) and parts not pinned (SA-15). (5) D7: the primary URI check once SA-11 lands.
- **T068 (the Step 7 scan).** Name `tachi_parts.py`, `tachi_scoring.py`, `tachi_scoring_rules.py`, `tachi-stage.py`, `render-risk-scores.py`, `render-compensating-controls.py` and the changed `sarif_common.py`. Expect SA-1 to SA-13 as known.
- **The probes** are throwaway. Probe K and probe I are worth turning into the tests above, and the guard fuzz is worth keeping as a stdlib-only test with pandoc as an optional extra oracle.
