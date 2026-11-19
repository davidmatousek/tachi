# W1 audit rulings: T004 discrepancies

| Item | Value |
|---|---|
| Feature | 391 Isolated and Auditable Operation, Part A |
| Ruling | Architect, mid-W1, under `agent-assignments.md` §9 (row T012/T014: "the architect rules") |
| Inputs | `contracts/audit-write-set.md` (T004) §5 and §7; spec FR-007, FR-008, SC-005; plan AD-4, AD-9, AD-13; tasks T012 to T016, T020, T023, T025, T026; the PRD design note "Writes: relocate, not document" |
| Tree | HEAD `b39b767`. T014 (`a580e45`), T022 (`c068ddc`) and T024 (`cae659a`) landed while this ruling was written, so the extractor change in AR-1 goes into T012's commit, not T014's. Line numbers are at `b39b767`; agents, commands and skills are unchanged from `46aec8d` apart from the one-line T022 and T024 edits |
| Date | 2026-11-19 |
| Escalations | PM: none (no spec or PRD wording change). User: none blocking; three FYI items in section 4 |

## 1. Rulings

| AR | Discrepancy | Disposition | Absorbing task | Scope change (files, lines, behaviour) |
|---|---|---|---|---|
| AR-1 | D-2: the extractor writes PNGs, corrected images and the opt-in deletion in `{target_dir}` | Relocate (option a). In build mode every extractor write lands under `{out}` (the directory that holds `.tachi-build/`) or `$TMPDIR`; `--target-dir` is only read | T012 (extractor hunk and path text; T014 is closed), T015 (four cases) | `scripts/extract-report-data.py`: an `image_dir` keyword on three functions and a deletion rule; T012's path text; T015 cases. Detail in 2.1 |
| AR-2 | D-3: `/tachi.risk-score` rewrites the input `threats.md`; `risk-scorer.md` ignores the output directory | In scope; body-only fix | T013, plus one T020 listing step | `risk-scorer.md` L16, L398, L442-446, L456, L538-542 write to the prompt's output directory; `tachi.risk-score.md` Step 1.5 (L92-93, L103-107) skips the in-place populator when the output directory is not the input directory. Detail in 2.2 |
| AR-3 | D-4: Gemini request, response and decode locations unpinned | Pin under `{out}/.tachi-build/`, kept; not `$TMPDIR` | T013 | `gemini-prompt-construction.md:266` (first sentence) and `:299` (step 6); decode tool `python3`. Detail in 2.3 |
| AR-4 | D-5: C6 red on day one because of `echo` | Confirmed: `echo` joins `tachi-threat-infographic`'s §8 Bash families and the guard's allow-list; the key-check line is not edited | T023, T025, T026 | Day-one sets: orchestrator `{python3}`; report-assembler `{python3, test, typst}`; threat-infographic `{[, echo, python3, test}` (after T013). T026's reserved-word case asserts exactly `{[, echo}` for a fence of the `threat-infographic.md:348` shape. §8 cells backtick each family so `[` renders as text. `threat-infographic.md:348` belongs to the key-handling patch and prints a fixed message; editing it only to shrink the set is churn on a reviewed line |
| AR-5 | D-6: `Agent` is transitive | Declare it in the §8 legend; no new guard check in 391; two follow-ups | T023 (legend), T045 (follow-ups) | The agents table keeps the contract's seven columns; the legend gains a "Dispatch" paragraph. Detail in 2.4 |
| AR-6 | D-7: skill-reference fences and unfenced model-built commands sit outside C6 | Accept the audit's proposal | T023 | The Bash families column holds C6's fenced families only. A footnote declares, as declared-only: threat-infographic's `curl` (pinned form, `gemini-prompt-construction.md:255-264`) and its `python3` decode (AR-3); the extractor cleanup fence (`typst-artifacts.md:118-124`); the report assembler's unfenced PDF check (Step 3c). C6 unchanged (TW-A3); the `curl` fence stays in the skill reference |
| AR-7 | D-8: adapter copies carry no `tools:` and no `model:` | Accept; the remedy (repair hints point at `scripts/install.sh`) landed in T024 (`cae659a`) | T023 | Scope note: the copies under `adapters/claude-code/agents/` carry no `tools:` or `model:` key, six agents have no copy, the guard does not cover them, and the repair path is `scripts/install.sh`. State the inheritance consequence only with the Claude Code subagents docs citation. No adapter change (FR-014; #369) |
| AR-8 | D-9: the `{out}`-under-cwd precondition is disclosed for one command only | Accept; runbook only | T016 | The runbook's precondition covers every output path: `--output-dir` on the five run commands and `/tachi.architecture --output`. Outside the working directory a write needs an allowance the profile does not grant. Add: `/tachi.security-report` also needs `{target_dir}` under the working directory when infographic images are present, because Typst reads them under `--root .` (already true before 391). `tachi.security-report.md:15-18` (T012) stays the only command text change, since only there does code enforce the precondition |
| AR-9 | D-10: `{output_path}` is undefined in the infographic agent; the two `/tmp` names disagree | Accept | T013 | Use `{output_dir}`, the name the command passes (`tachi.infographic.md:153`), with one sentence in the agent's Script Invocation (`threat-infographic.md:164`) saying where it comes from. Both recipes (`threat-infographic.md:170`, `tachi.infographic.md:163`) write `{output_dir}/.tachi-build/infographic-{template_name}.json`. Also correct `threat-infographic.md:60` ("specified by the orchestrator": the `/tachi.infographic` command passes the template) so the agent text matches §8's Dispatches column |
| AR-10 | D-11: T012's same-commit list misses prose with the old path base | Accept | T012 | Add `typst-template-contract.md` L105-111, L260, L294-296, L310, L326, L342, L406; `brand-asset-guidelines.md` L48, L52, L57-59, L78; `docs/guides/DEVELOPER_GUIDE_TACHI.md:1994` (second compile-path sentence besides `:1609`); the fence is `typst-artifacts.md:118-124`. New text per 2.1 (c) |
| AR-11 | D-12: argparse `required=True` would trip the new recipes | Closed by T014 (`a580e45`) | none (T040 checks; T043 runs) | `_resolve_cli_mode` re-imposes the legacy flag triple with argparse's own message; `--build-dir` needs only `--target-dir` and refuses `--output`; `--remove-build-dir` takes no other flag. T043 runs the legacy-form callers (`test_extract_report_data.py`, `test_report_posture_contract.py`, `test_backward_compatibility.py`) in a scratch clone |
| AR-12 | D-13: gaps in the Architect's baseline | Accept, with the AR-1 and AR-2 tokens | T023 | The orchestrator also writes `{out}/attack-chains.md` (conditional); `tachi-attack-tree-delta` also writes `.manifest.json`; no `{target_dir}` write remains (section 3); the infographic Bash set includes `[` and `echo` and no `.env` sourcing; after T012 the report assembler names no deletion command (the extractor's `--remove-build-dir` removes the build directory) |
| AR-13 | D-1: `/tachi.security-report` dispatched `senior-backend-engineer` | Closed by T022 (`c068ddc`) | none | §8 commands table, Dispatches cell: `tachi-report-assembler` |

## 2. Detail

### 2.1 AR-1 (D-2): the extractor's image writes move under `{out}`

**Why relocation and not option (b).** FR-008 requires the report-assembler write sites, the extractor among them, to "relocate every write outside the output directory into it". The PRD's design note reads "Writes: relocate, not document" and counts the attack-tree and attack-chain PNGs in the output directory's write set. Option (b), running only with the default and scoping the sentence to it, satisfies neither FR-007 nor FR-008 as written: `--output-dir` is a documented option, and `tachi.security-report.md:256` shows the combination in which `{target_dir}` differs from `{out}`. Option (b) would need a spec and PRD wording change (PM), and T015 would pass trivially on a fixture whose target is its output directory.

**Why `{out}` and not the build directory.** With the default invocation every path stays byte-for-byte the path written today. Adopters keep the PNGs they get now, and the tracked sample-report PNGs and the legacy-mode tests are untouched. No new flag is needed: the build-directory guard requires the suffix `.tachi-build/security-report`, so `{out}` is exactly the build directory's grandparent. The committed order stays as it is: the build directory is recreated only after extraction succeeds.

(a) **Extractor** (`scripts/extract-report-data.py`, in T012's commit):
1. `render_mermaid_to_png` (:1027), `prepare_attack_chains` (:1170, which passes the value on to `_render_chain_diagrams`, directory at :1622) and `detect_images` (:1767) take an optional keyword `image_dir=None`. `None` means `--target-dir`, so legacy mode is unchanged byte for byte. The PNG directories become `image_dir/attack-trees` and `image_dir/attack-chains`, created with `parents=True` (:1058, :1623). The corrected copy goes to `image_dir` (:1848). Each emitted Typst path is the `os.path.relpath` from the template or build directory to the directory that holds that file; a correctly labelled infographic is still read from `--target-dir`.
2. Deletion rule for `--cleanup-mislabeled-images`, at both call sites (:1841, :1862): delete a file only when it lies in `image_dir` (resolved). Legacy mode, and build mode with `{out}` equal to the target, behave as today. Build mode with a different `{out}` deletes nothing and logs one stderr line, so the only copy of an infographic is never deleted outside `{out}`.
3. `main()` in build mode (:2652 to :2670): `image_dir = Path(build_real).parent.parent`, passed to the three calls at :2812, :2830 and :2841. Legacy mode passes nothing.
4. Module docstring and `--help` epilog, one sentence: in build mode the extractor writes only under the output directory (the directory that contains `.tachi-build/`) and `$TMPDIR`, and only reads `--target-dir`.

Keep `_render_single`'s two-argument signature (tests patch it). Nothing else changes.

(b) **Typst `--root .`**. Typst resolves `image()` paths against the template file that calls it (`typst-template-contract.md:111`), and those files live in the build directory. The extractor computes every path from there, so the PNGs read as `../../attack-trees/<file>` and `../../attack-chains/<file>`. Every referenced file must lie under the working directory: the guard guarantees it for `{out}`; for `{target_dir}` (correctly labelled infographics) and `brand/final/` it is a read precondition that predates 391 and that AR-8 discloses.

(c) **T012 text** (AR-10's lines): the extractor computes relative paths from the build directory, never a fixed `../../`; attack-tree and attack-chain PNGs live in `{out}/attack-trees/` and `{out}/attack-chains/`; infographic images are read from `{target_dir}`, or from a corrected copy in `{out}`; brand assets come from `brand/final/` under the working directory. The cleanup fence at `typst-artifacts.md:118-124` becomes the build-mode form, `--target-dir {target_dir} --build-dir {target_dir}/.tachi-build/security-report --cleanup-mislabeled-images`, followed by `--remove-build-dir {target_dir}/.tachi-build/security-report`. There `{out}` is the target, so the F-217 cleanup behaves as before. T012's agent recipe is unchanged.

(d) **T015** gains four cases (SBE-TA; the workflow wiring is unchanged):
1. Target and output in separate directories under the test's working directory (`--target-dir {tmp}/run`, `--build-dir {tmp}/out/.tachi-build/security-report`). `{tmp}/run` is hashed before and after and stays byte-unchanged.
2. A mislabeled infographic (a `.jpg` holding PNG bytes) in `{tmp}/run`: the corrected copy appears in `{tmp}/out` and the PDF compiles. The same run with `--cleanup-mislabeled-images` also leaves `{tmp}/run` unchanged.
3. One attack tree and one surfaced attack chain rendered through a stub `mmdc` placed first on `PATH` (it writes a small valid PNG to its `-o` argument; no Chromium; extraction alone is enough for this case). The PNGs land under `{tmp}/out/attack-trees/` and `{tmp}/out/attack-chains/`, none under `{tmp}/run`. No CI workflow installs `mmdc` (every `mmdc`-dependent test skips there), so this stub is the only CI evidence for W17 and W18.
4. The static fence assertion also reads `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` and `.claude/skills/tachi-report-assembly/references/typst-artifacts.md`: no `/tmp`, and no `--output` value or copy destination under `templates/tachi/`.

Effort: T012 +0.08 d (extractor 0.05, text 0.03); T015 +0.07 d.

### 2.2 AR-2 (D-3): `/tachi.risk-score` honours `--output-dir`

**Why in scope.** FR-007 is a MUST whose write list "comes from the FR-011 audit", and the plan makes the relocation audit-driven (Components: "Write relocation: E (audit) + D (edits)"). The fix is about a dozen lines of body text, and no gated test pins either file's text. Leaving it out would need a PM wording change to FR-007 and would leave an undetermined write location (the command and the agent body disagree) in a matrix whose purpose is audit. The defect predates 391; record it in `delivery.md` beside AD-13's.

Edits (SBE-D, one commit in T013's slot; frontmatter untouched):
1. `.claude/agents/tachi/risk-scorer.md` L16, L398, L442-446, L456, L538-542: write `risk-scores.md` and `risk-scores.sarif` to the output directory named in the prompt (the "Output directory:" line, passed at `tachi.risk-score.md:123`; the command defaults it to the input file's directory). The reads stay as they are: the baseline `risk-scores.md` lookups (L89, L388) and `architecture.md` (L332).
2. `.claude/commands/tachi.risk-score.md` Step 1.5, in the run condition (L92-93) and the skip list (L103-107): a third skip applies when `--output-dir` names a directory other than the input directory. The input directory then stays read-only, and the risk-scorer copies the `## Affected Assets` block as the prior `/tachi.threat-model` run wrote it. One sentence says to run without `--output-dir` to refresh the block in place. This hunk is separate from T024's line 42 edit, which has already landed.

Result: W12 is always `{out}/risk-scores.{md,sarif}`, and W13 is `{out}/threats.md` in place, only when `{out}` is the input directory. `/tachi.risk-score` no longer writes anywhere in `{target_dir}`.

**T020** (maintainer, W2; about 0.05 d inside TW-A1's budget) gains one listing. After the key-less full run, run `/tachi.risk-score <run-dir> --output-dir <alt>` and `/tachi.security-report <run-dir> --output-dir <alt>`, with `<alt>` under the working directory. With `{out}` set to `<alt>`, T020's existing method applies: nothing in `<run-dir>` is new or changed, and everything new lies under `<alt>` or `$TMPDIR`. This is the only runtime evidence for the risk-scorer change, because it is an LLM agent that no automated test can pin. It is also the live counterpart of T015's case 1.

**If the user declines the added file** (not recommended), three things follow:
- The runbook would have to say "`/tachi.risk-score --output-dir <dir>` still updates the input `threats.md` in place and may write `risk-scores.md` and `risk-scores.sarif` beside the input; run it without `--output-dir` for isolated operation".
- FR-007 would need a PM wording change.
- The follow-up title would be "risk-scorer ignores the output directory /tachi.risk-score passes, and Step 1.5 rewrites the input threats.md".

### 2.3 AR-3 (D-4): Gemini intermediates under `{out}/.tachi-build/`, kept

Edits (SBE-D, in T013's commit). The key-handling patch already pinned the request form and T005 leaves the file alone, so T013 is its only writer in W1:
1. `gemini-prompt-construction.md:266`, first sentence only:
   - `{request_file}` is `{output_dir}/.tachi-build/gemini-{template_name}-request.json`, written with the Write tool.
   - `{response_file}` is `{output_dir}/.tachi-build/gemini-{template_name}-response.json`, written by `curl --output`.
   - Both files are kept. The agent has no deletion family, the files are as sensitive as the rest of `{out}`, and the request file is the exact payload sent to the Gemini host. A retry on the next chain model overwrites both.
   - The fence keeps its placeholders.
2. Step 6 of Response Parsing (`:299`): decode with `python3` (standard library `json` and `base64`), reading `{response_file}` and writing `{output_dir}/threat-{template_name}.{ext}`. No other tool is used and nothing is written anywhere else.
3. Keep everything the tests pin:
   - `test_gemini_key_env_only.py` needs `**Request form (pinned)**`, `--config -`, the `header = "x-goog-api-key: $GEMINI_API_KEY"` line and `--data @`.
   - Keep the rest of `:266`: every line holding `?key=` or a `--header "x-goog-api-key` form must contain "never".
   - A1 needs `inlineData` and `mimeType` in Response Parsing, and the file must never contain the substring "resolution".

**Why not `$TMPDIR`.**
- The request file is written with the Write tool. A `$TMPDIR` path lies outside the working directory, where Claude Code's file tools need an extra permission, so it can prompt or be blocked under auto mode.
- The agent would first need a Bash call to learn the value.
- A model-built temporary path can fall back to `/tmp`, which is the failure the relocation removes.
- `{out}/.tachi-build/` already exists after the extraction step and is already a listed write location.

Python's own `tempfile` use inside the extractor stays in `$TMPDIR`; no agent names that path.

Effort: T013 +0.02 d.

### 2.4 AR-5 (D-6): declaring `Agent` in §8

T023:
- **Agents table.** It keeps the seven columns in `contracts/matrix-section.md` and gets no Dispatches column, because the guard parses that table and dispatch targets are declared-only data. `Agent` stays in the Tools cell of `tachi-orchestrator` and `tachi-threat-report` (C2 enforces it).
- **Legend.** It gains a "Dispatch" paragraph, written as prose or a list and not as a third table inside §8 (the guard parses §8's tables). Content:
  - `Agent` is transitive. An agent that holds it can start any subagent type available in the session: tachi's agents, and Claude Code's built-in types such as `general-purpose`. The started subagent runs with its own tools and model, not the dispatcher's.
  - Declared targets: `tachi-orchestrator` starts the six STRIDE agents, the eight AI agents and `tachi-threat-report`; `tachi-threat-report` starts `tachi-attack-tree-delta`.
  - Observed: `tachi-threat-report` has started built-in `general-purpose` subagents that ran Bash and Write. No tachi file instructs this.
  - The guard pins which agents hold `Agent`. It does not check which types they start, and tachi does not restrict them.
  - The commands' dispatches stay in the commands table's Dispatches column.

**Guard: no new check in 391.**
- C2 already turns CI red if any other agent gains `Agent`.
- The dispatch targets live in prose, which FR-012 and TW-A3 keep out of the guard.
- No static check can bound a choice made at run time.

B1 is already covered by `test-results/p0-b0-precheck.md` P0B0-1: a non-tachi instance is a recorded subagent with `pinned_model` null, never a dispatch. The W2 record (T020) notes the built-in subagent types seen, by type and count. The existing write listing already covers their writes.

## 3. Write rows after the rulings (for T016 and T023)

T016 and T023 take audit §5's rows with the rows below in their place. Tokens are as in audit §2: §8 and the runbook use `{template}`, while the agent and reference text say `{template_name}`.

| ID | Path after the rulings | Writer | Condition | Ruling |
|---|---|---|---|---|
| W10 | `{out}/threat-{template}.{jpg,png}` | `tachi-threat-infographic`, decoded with `python3` | key set and an image returned | AR-3 |
| W12 | `{out}/risk-scores.{md,sarif}` | `tachi-risk-scorer` | always | AR-2 |
| W13 | `{out}/threats.md`, in place | `/tachi.risk-score` main session (populator) | markdown input, an architecture file found, and `{out}` is the input directory | AR-2 |
| W16 | `{out}/.tachi-build/gemini-{template}-request.json`; `{out}/.tachi-build/gemini-{template}-response.json` | `tachi-threat-infographic` (Write; `curl --output`) | key set; kept | AR-3 |
| W17 | `{out}/attack-trees/{finding-id}-attack-tree.png` | `scripts/extract-report-data.py` | attack trees exist and `mmdc` is on `PATH` | AR-1 |
| W18 | `{out}/attack-chains/{chain-id}-attack-chain.png` | `scripts/extract-report-data.py` | a surfaced chain and `mmdc` on `PATH` | AR-1 |
| W19 | `{out}/threat-{stem}.{jpg,png}`, a corrected copy | `scripts/extract-report-data.py` | an image whose bytes do not match its extension | AR-1 |
| W20 | `{out}/threat-{stem}.{jpg,png}`, deleted | `scripts/extract-report-data.py --cleanup-mislabeled-images` | the flag is passed (no run recipe passes it), a byte-identical correct counterpart exists, and the file lies in `{out}` | AR-1 |

With these rows every write lies under `{out}` or `$TMPDIR`, apart from the `/tachi.architecture` carve-out (W23, W24). The runbook (T016) and ADR-049 (T029) can therefore state the confinement sentence without a qualifier, together with AR-8's precondition.

The report assembler's §8 Writes cell lists, in this order (T023 pins the final cell syntax):
- `{out}/security-report.pdf`
- `{out}/.tachi-build/security-report/`
- `{out}/attack-trees/`
- `{out}/attack-chains/`
- `{out}/threat-{stem}.{jpg,png}`
- `$TMPDIR`

ADR-049 adds one clause: in build mode the extractor only reads `--target-dir`.

## 4. Escalations and follow-ups

**PM.** No ruling needs a spec or PRD wording change: AR-1 and AR-2 make FR-007, FR-008 and SC-005 hold as written. T045's CHANGELOG entry (neutral wording) should note two `--output-dir` behaviour changes:
- `/tachi.security-report --output-dir` writes its rendered diagrams, and any corrected image copy, under that directory instead of the artifact directory.
- `/tachi.risk-score --output-dir` writes both outputs there and leaves the input directory unchanged.

**User.** Nothing blocking. Three FYI items:
1. File additions:
   - AR-2 adds `.claude/agents/tachi/risk-scorer.md` (body only) to Lane D's change set. The plan does not list this file; it comes in through the plan's audit-driven relocation.
   - AR-3 adds `gemini-prompt-construction.md` to T013.
   - AR-1 puts an extractor hunk into T012, because T014 closed while this ruling was written.
2. T020, the maintainer's W2 session, gains one listing step of about 0.05 d (2.2).
3. Agent effort grows by about 0.20 d on Lanes D and E: T012 +0.08 d, T013 +0.05 d, T015 +0.07 d. This stays inside the 1.66 d W1 window and crosses no trip-wire threshold. The orchestrator logs the actuals in the S1 handoff.

**Follow-ups for `delivery.md` (T045).**
1. Extend the listed guard follow-up: command bodies and the two dispatcher agents' bodies may name only `tachi-*` agents that have a §8 row. Audit §3.3 lists the dispatch forms to parse.
2. Title: "Bound the subagent types tachi-orchestrator and tachi-threat-report can start". The options, each to be confirmed live:
   - a per-type restriction of `Agent` in their tools;
   - a session-profile deny for built-in types;
   - a body instruction naming the permitted targets.
3. Record the risk-scorer output-directory defect (AR-2) as pre-existing, as for AD-13.

## 5. Checks for T040

| Ruling | Check |
|---|---|
| AR-1 | In build mode nothing is written under `--target-dir` (T015 cases 1 to 3 green in a scratch clone). Legacy mode's paths and `report-data.typ` are unchanged (no new failures against T003's pre-state in T043). The deletion rule is in place |
| AR-2 | Both body edits are present. Agent frontmatter is unchanged (guard C2 to C4 green). T020's `--output-dir` listing is recorded |
| AR-3 | The two file names and the decode tool are in the reference. `test_gemini_key_env_only.py` and `test_gemini_request_contract.py` are green in a scratch clone |
| AR-4 | C6 is green on the live tree with the three day-one sets |
| AR-5 | The legend has the Dispatch paragraph, and the agents table shape matches the contract |
| AR-8, AR-10, AR-12 | The runbook states the precondition, T012's path text matches 2.1 (c), and the §8 corrections are applied |
