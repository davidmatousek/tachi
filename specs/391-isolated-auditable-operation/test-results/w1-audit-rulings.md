# W1 audit rulings: T004 discrepancies

| Item | Value |
|---|---|
| Feature | 391 Isolated and Auditable Operation, Part A |
| Ruling | Architect, mid-W1, under `agent-assignments.md` §9 (row T012/T014: "the architect rules") |
| Inputs | `contracts/audit-write-set.md` (T004) §5 and §7; spec FR-007, FR-008, SC-005; plan AD-4, AD-9, AD-13; tasks T012 to T016, T020, T023, T025, T026; the PRD design note "Writes: relocate, not document" |
| Tree | HEAD `b39b767`. T014 (`a580e45`), T022 (`c068ddc`) and T024 (`cae659a`) landed while this ruling was written, so the extractor change in AR-1 goes into T012's commit, not T014's. Line numbers are at `b39b767`; agents, commands and skills are unchanged from `46aec8d` apart from the one-line T022 and T024 edits |
| Date | 2026-11-19 |
| Escalations | PM: none (no spec or PRD wording change). User: none blocking; three FYI items in section 4 |
| Addendum | AR-15 to AR-20: T016's profile review (architect, 2026-11-19, tree `3da1ec4`), against `contracts/session-profile.md` as amended at T006 and the public Claude Code docs read that day. Detail in sections 2.6 to 2.11; escalations in 2.12 |

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
| AR-14 | T015 finding (no audit row): a stock `python3 scripts/<entry>.py` makes CPython cache the imported `tachi_parsers` as bytecode, in `scripts/__pycache__/` or under the interpreter's cache prefix. That write lies outside `{out}` and `$TMPDIR` | Option (d), none of (a) to (c): each installed entry script turns bytecode writing off when run as a script, before its sibling import. No recipe, profile, §8 or runbook text changes | T015: one follow-on commit on `1be9716` (SBE-D the three scripts, SBE-TA the module); T015 closes with it | `scripts/extract-report-data.py` before :64, `scripts/extract-infographic-data.py` before :27, `scripts/populate-affected-assets.py` before :59, two lines each; `tests/scripts/test_write_confinement.py` :34-37, :349, :371, :380, :400, plus three cases. T023 and T016: no follow-up. Detail in 2.5 |
| AR-15 | T049 placement (`test-results/security-a.md` §5.5; no audit row): do `Read(//proc/**)`, `Read(~/.claude/.credentials.json)` and the matching `credentials.files` entry join the baseline profile or only the runbook's extension note? | **Baseline.** All three join the block; `Read(~/.claude.json)` and the `CLAUDE_CONFIG_DIR` caveat stay in the extension note. A pre-ruled Linux fallback ladder replaces another architect round trip | T016 (first commit copies the block; second commit: §5.6 claim text and the note), T017 (pins the lists), T020 (re-extracted profile; stage A as SEC-A §6 with the three strings removed), T021 (ladder) | `contracts/session-profile.md` block and disclosures; `data-model.md` SessionProfile. No new key path. The pre-staged W2 profile is replaced before T020. Detail in 2.6 |
| AR-16 | Profile defect: `sandbox.autoAllowBashIfSandboxed` is unset. Its default was `true` before v2.1.324 (runbook minimum v2.1.285), and a repository's value still applies under an admin-required sandbox, so whether auto mode's classifier and the FR-6 `hard_deny` see sandboxed Bash depends on the version and on other files | Pin `"autoAllowBashIfSandboxed": false` | T016, T017 (one key path, value pinned), T020 (one Manual-mode check) | Block +1 key path (19); disclosure "Classifier coverage". Detail in 2.7 |
| AR-17 | Profile defect: nothing in the profile acts on MCP. FR-005 has the profile cover MCP servers, yet coverage rested on an adopter step that no test pins. The claude.ai connectors that a claude.ai-authenticated session fetches by default are model-invocable egress that the sandbox does not reach | Add `"mcp__*"` to `permissions.deny`; keep the `deniedMcpServers` instruction for the process residual | T016, T017 | `permissions.deny` +1 rule. No new key path. Detail in 2.8 |
| AR-18 | Profile defect: the contract had adopters check the effective configuration on the `/sandbox` Config tab, but `/sandbox` does not open while `--settings` sets `sandbox.enabled` or `allowUnsandboxedCommands`. On Linux and WSL2 the optional seccomp filter, which blocks Unix sockets, can be missing without any profile-visible sign | Re-route the check: the other scopes from a session without the profile; `/status`, `/permissions` and `auto-mode config` inside it; a proxied-`curl` probe for `strictAllowlist`; a Linux/WSL2 seccomp-filter step | T016 (second commit), T020 (two steps change) | Disclosures "Effective configuration" and "Linux and WSL2"; probe table +1 row. Detail in 2.9 |
| AR-19 | Profile defect (LOW): the named negatives missed documented weakening keys (`allowAppleEvents` is the one gap in the docs' own list of six); the test pinned key paths but not the values or the members of the security lists | 21 named negatives in full key-path form; scalar values and list members pinned | T017 | Contract-test paragraph; `data-model.md`. Detail in 2.10 |
| AR-20 | Profile defect (LOW): prose items in the contract were inaccurate, incomplete or Part B text: the `--setting-sources` costs, the list of what runs outside the sandbox, the model-selection and retention sentences (both named Part B tools), the probe table's pass criteria, and four missing disclosures | Corrected in the contract | T016 (second commit), T048 (the two Part B clauses) | Contract prose only; the block's `autoMode` entries are unchanged. Detail in 2.11 |

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

### 2.5 AR-14 (T015 finding): tachi's scripts write no bytecode cache

Lines are at `1be9716`.

**What happens today.** This was reproduced in scratch copies of the four installed scripts. Each entry script ran from the project root with `--help` and with `PYTHONDONTWRITEBYTECODE` unset:
- **The import.** The three installed entry scripts import `tachi_parsers` at module level (`extract-report-data.py:66`, `extract-infographic-data.py:29`, `populate-affected-assets.py:61`), so every run of any of them caches it. CPython never caches the script it runs as `__main__`, so `tachi_parsers` is the only module concerned.
- **Python 3.12** wrote `scripts/__pycache__/tachi_parsers.cpython-312.pyc` for each script.
- **macOS's own `/usr/bin/python3`** (3.9.6, the floor the plan cites) wrote nothing under `scripts/`. Its `sys.pycache_prefix` is `~/Library/Caches/com.apple.python`, so the cache went there, under the project's absolute path. `PYTHONPYCACHEPREFIX` can move it anywhere.
- **The callers.** The recipes run these three scripts in 10 fenced lines across 7 files:
  - `orchestrator.md:685`;
  - `report-assembler.md:158` and `:218`;
  - `threat-infographic.md:169`;
  - `tachi.threat-model.md:126` (inside the orchestrator's dispatch prompt) and `:170`;
  - `tachi.risk-score.md:99`;
  - `tachi.infographic.md:160` (inside the dispatch prompt);
  - `typst-artifacts.md:119` and `:123`.

  `tachi.security-report.md` runs no script.
- **No change elsewhere:**
  - `generate-threats-sarif.py`, `generate-risk-scores-sarif.py`, `populate-maestro-coverage.py` and `sarif_common.py` also import a sibling. They are not installed (`INSTALL_MANIFEST.md:77`), and no recipe runs them.
  - On part-b (`ceea019`), `stamp-tachi-version.py` and `archive-run-transcripts.py` import only the standard library. Step 2.6 (`tachi.threat-model.md:207` there) therefore stays as written, and AD-14 is not touched.

**Ruling.** In each of the three installed entry scripts, insert two lines immediately before `sys.path.insert(0, str(Path(__file__).resolve().parent))` (`extract-report-data.py:64`, `extract-infographic-data.py:27`, `populate-affected-assets.py:59`):

```python
if __name__ == "__main__":
    sys.dont_write_bytecode = True  # no bytecode cache for the import below (feature 391, FR-007)
```

- **Mechanism.** `sys.dont_write_bytecode` is the documented, settable form of `-B`. Set before the import, it stops both kinds of cache. Reproduced on both interpreters: with the two lines, no cache of `tachi_parsers` was written, neither in the project nor under a cache prefix.
- **The `__main__` condition** keeps the flag out of processes that load a script by path, as the tests do (`importlib.util.spec_from_file_location` with a module name). The scripts start no Python child (the extractor's pools are thread pools), so nothing escapes the condition.
- **Nothing else changes:** no flag, output or exit code, and `tachi_parsers.py` stays untouched. AR-1's sentence in the extractor's docstring and epilog (`extract-report-data.py:23-24`, `:2600-2602`) becomes true as written.

**Why not the listed options.**
- **(a) `python3 -B` in the recipes.** That is 10 lines in 7 files, two of them inside dispatch prompts. The property would hold only while every agent and main session copies the flag on every run, and T020 can only sample that. (d) holds for every invocation form, including a paraphrased command and a person running a script by hand. Neither (a) nor (d) touches C6 (the family stays `python3`) or C7.
- **(b) `PYTHONDONTWRITEBYTECODE=1` in the profile's `env`.** It covers only sessions started with the profile, so FR-007 and SC-005 stay false for every other run. It also adds a key path to the closed set (`contracts/session-profile.md`, T017).
- **(c) Disclosure.**
  - FR-007 and SC-005 would need a qualifier, which is a PM wording change. Section 3's "without a qualifier" would no longer hold.
  - No fixed C7 row can name a location that depends on the interpreter, and one form of that location lies in the home directory.
  - tachi's own `.gitignore:217` ignores `__pycache__/`, but `scripts/install.sh` writes no `.gitignore`. In an adopter project the cache would show up as untracked files in a `scripts/` directory the adopter may share.
- **Precedent.** (d) follows the same principle as the H-3 fix (`test-results/security-b1.md`): the script guarantees the property, not its invocation.
- **No `-I`.** `-I` is not added anywhere. It addresses import shadowing (H-3), and the three scripts put their own directory back at the front of `sys.path` before the sibling import anyway.

**Out of scope.** The interpreter's own standard-library cache lies outside the project and serves every Python program. T020 observes it live, as it does Typst's and Chromium's own caches (decision 5 of the T015 result).

**T015 follow-on.** One commit on `1be9716`: SBE-D writes the three scripts and SBE-TA the module. The wiring is unchanged, because the scripts match `scripts/*.py` in `&fidelity_paths` (`tachi-install-fidelity.yml:60`). T015 is marked complete only once this commit lands.
1. **Children run the recipe form.** Drop `"-B"` at `:371`, `:380` and `:400`. At `:349`, remove `PYTHONDONTWRITEBYTECODE` from the child environment with `env.pop`, so that a developer's shell setting cannot mask a regression. Rewrite the interpreter note at `:34-37` to match.
2. **Three new cases**, one per installed entry script. In a project that holds a copy of that script and `tachi_parsers.py`:
   - Run `scripts/<entry> --help` from the project root, with `PYTHONPYCACHEPREFIX` set to a test-owned directory.
   - Assert exit 0, no `scripts/__pycache__/`, and no `<stem>.cpython-*.pyc` under that directory for any module in the project's `scripts/`.
   - Do not assert on the standard library, which the interpreter also caches under the prefix (the dry run showed this with and without the two lines).

   With the prefix set, the case fails on any interpreter when the two lines are missing. That includes macOS's `/usr/bin/python3`, whose default cache lies outside `tmp_path`.
3. **Non-vacuity**, recorded in the T015 result. Remove the two lines from one script in the scratch clone. That script's case goes red. On an interpreter without a cache prefix, the nine snapshot tests that needed the suppression also go red. Then restore the lines.

Effort: SBE-D +0.02 d and SBE-TA +0.03 d, inside the W1 window. No trip-wire threshold is crossed.

**Other tasks.**
- **T023: no follow-up edit.**
  - The Writes column gets no `__pycache__` entry, the Bash families stay as AR-4 set them, and the commands table keeps the recipe forms.
  - If the in-flight draft already lists `scripts/__pycache__/` (the third option in T015's finding), drop it before the commit.
- **T016: no follow-up.** §5 states the confinement sentence without a qualifier and gets no extra row. "No write allowances are needed" stands.
- **T017, T025, T026: none.** The key set, C6 and C7 are unchanged.
- **T029** (ADR-049, not yet written): one clause in the write-confinement section saying that the installed scripts write no bytecode cache when run as scripts, whatever cache location the interpreter uses.
- **T020:** the existing write listing is the live check, and it must show no `scripts/__pycache__/`. A Python cache path in the denial record means an unguarded Python run; record it as a finding.
- **T045** (optional; the PM sets the wording): "tachi's scripts no longer leave a `scripts/__pycache__/` directory in the project."

**Escalations.**
- **PM:** none. FR-007, FR-008 and SC-005 hold as written.
- **User:** nothing blocking. FYI: `scripts/extract-infographic-data.py` and `scripts/populate-affected-assets.py` join Lane D's change set, which the plan does not list, as AR-2 did for `risk-scorer.md`.

**Check for T040.**
- The two lines precede `sys.path.insert` in the three installed entry scripts.
- In a scratch clone, T015 is green with no bytecode suppression and with the three cases, and its non-vacuity run is recorded. T043 runs it on both tips.
- T020's listing shows no Python cache path.

### 2.6 AR-15 (T049): the SEC-A rules go in the baseline

The docs cited in 2.6 to 2.11 are the public Claude Code pages under `https://code.claude.com/docs/en/`, read as raw Markdown on 2026-11-19, named here by page and section.

**Why baseline and not the extension note.**
- The exposure comes from the profile's own key route. The runbook provisions `GEMINI_API_KEY` into the Claude Code process environment, and the Read tool runs in that process, outside the sandbox (SEC-A D1, D2). The same rule covers adopters who authenticate through `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`, so it matters in key-less sessions too. It is not an extra store that an adopter chose to keep.
- The block is the only text that T017 pins and T020 runs. A note marked "required" is neither tested nor present in a copied profile.
- The anchoring is right. In a permission rule `//proc/**` is absolute, while `/proc/**` would anchor at the profile file's directory and match nothing (SEC-A §5.3; permissions, "Where a pattern anchors").
- No key path is added.
- The cost is bounded. On macOS, `Read(//proc/**)` and its merged sandbox read deny name a path that does not exist. On Linux, the merge's effect on sandboxed tools is the one open question (SEC-A N8), and the ladder below settles it without another review.

**The `credentials.files` entry stays, although it duplicates the merge.** Within the profile, a `deny` file entry and a merged Read deny give the same sandbox read block (settings reference, `sandbox.credentials.files`). The entry is kept for two documented reasons:
- The runbook offers an always-on copy of the `sandbox` block for user settings. That copy carries `credentials.files` but not `permissions`, so without the entry the login file would stay readable to sandboxed commands in those sessions.
- With `--setting-sources` excluding `user`, Claude Code still applies the user file's credential `deny` entries but ignores its Read deny rules when it builds the sandbox (sandboxing, "Protect credentials" and "Configure sandboxing"). The always-on copy then keeps the login file denied.

No `/proc` line goes under `sandbox.*`. SEC-A §5.4 holds, and `/proc` is not a credential file.

**`~/.claude.json` stays in the extension note**, with `~/.netrc`, `~/.git-credentials`, `~/.kube`, `~/.docker/config.json` and cloud-CLI configs. It holds account details and personal MCP server definitions, which are adopter configuration rather than an exposure the profile creates. For `CLAUDE_CONFIG_DIR`, SEC-A §5.2 applies.

**Claim text.** Because the rules are in the baseline, the runbook uses SEC-A §5.6 as written (T016's second commit, or T021) and keeps "can" in the hooks clause.

**Linux fallback ladder.** It is pre-ruled: T021 applies it from T020's stage C without another architect review. In every row, T021 changes the contract, the runbook block and T017's pinned deny list in one commit, then re-runs B1 to B3 and C on Linux.

| Stage C on Linux | Disposition |
|---|---|
| Passes with `Read(//proc/**)` | Keep it |
| Fails with it | Swap it for `Read(//proc/*/environ)` and `Read(//proc/*/task/*/environ)` (SEC-A §5.2). Record how long one sandboxed command takes to start, because the per-thread pattern expands to one entry per thread |
| C1 to C3 pass with both forms, and only C4 (diagram rendering) fails | Keep `Read(//proc/**)`. Scope Linux attack-tree and attack-chain rendering out under the profile through the AD-9 platform statement. A credential leak would be silent, while a missing image is visible |
| C1, C2 or C3 fails with both forms | Remove the `/proc` rules. The runbook says that on Linux the Read tool can read the Claude Code process environment, so key-ful operation and environment-variable authentication are not claimed protected there (SEC-A §5.8, row 1). It recommends `/login`, whose credentials file the profile denies, and names `permissions.blockReadsOutsideWorkingDirectories` as the documented opt-in where toolchains live outside the home directory |
| T020 runs on macOS only | The Linux rules ship unchecked, and the header says so (SEC-A §5.8, last row) |

**For T020.** SEC-A §6 stands, with three changes:
- Stage A uses a scratch copy of the re-extracted profile with the three SEC-A strings removed. It keeps the AR-16 and AR-17 changes.
- SEC-A §6.1's step "open the `/sandbox` Config tab" cannot run under the profile (AR-18). Record the message `/sandbox` prints instead.
- On Linux, show the OS-level merge with a read that the permission layer cannot analyse. Run it only in the key-less session with the cleaned environment: `python3 -c "print(open('/proc/self/environ','rb').read().count(b'TACHI_SEC_A_PROBE='))"`. Stage B expects an error from the sandbox (permission denied, or no such file where `/proc` is hidden); `1` means the merge did not reach the sandbox, which is recorded (the content is the dummy). In stage B, A3's `tr … < /proc/<pid>/environ` names its input as a redirection, which the permission layer now refuses, so A3 there uses the same `python3` form with `<CLAUDE_PID>`.

**T017** pins `permissions.deny` and `credentials.files` by member, as sets (AR-19). That answers SEC-A's hand-off, which asked whether the test pins the deny array or the files length: it pins both.

**Public probe table.** Adopters check the SEC-A rules by configuration (`/permissions` lists them and no startup warning names them), never by reading `/proc` or the login file. A probe that fails open writes the secret into a plaintext transcript (SEC-A D7, §6.0), so the live probes stay in the maintainer's run.

### 2.7 AR-16: pin `autoAllowBashIfSandboxed` to `false`

**What the docs state.**
- Auto-allow "approves a command automatically, with no prompt, when the command runs inside the sandbox". It "works independently of your permission mode setting, with three exceptions: plan mode, an auto mode command that carries per-command allowed domains, and server-side classifier review of sandboxed commands in auto mode" (sandboxing, "Sandbox modes"). In auto mode without server-side review, a sandboxed command under auto-allow never reaches the classifier.
- For `sandbox.autoAllowBashIfSandboxed`: "Default: `false`. Before v2.1.324, the default was `true`" (settings reference). The runbook's minimum is v2.1.285.
- Under an admin-required sandbox, "deny entries and the `autoAllowBashIfSandboxed` value" in a repository's files still apply (sandboxing, "Repository settings under an admin-required sandbox"). Picking a mode in `/sandbox` writes the key to the project's `.claude/settings.local.json` (sandboxing, "Get started").
- A key set with `--settings` "overrides the same key in your project and user settings files, and a key you leave out keeps its value from those files" (settings, "Settings precedence").

**Why it is a defect.** Three statements depend on the classifier seeing sandboxed commands:
- FR-006's `hard_deny` names Bash.
- The runbook must say that the classifier reads commands.
- D-6 says that `allowUnsandboxedCommands: false` from `--settings` stops a repository's settings from loosening the sandbox.

Without the pin, all three fail in one documented combination: no server-side review, together with auto-allow on. Server-side review is absent behind an LLM gateway or proxy that drops it, on a platform without it, or with `CLAUDE_CODE_AUTO_MODE_SERVER=0`. Auto-allow is on under a pre-v2.1.324 default, a user file or a repository file. In that combination sandboxed Bash runs without classifier review, including a `curl` that sends arbitrary content to the Gemini host, which the allowlist admits. The pin makes all three statements hold again.

With server-side review on, sandboxed commands are reviewed either way. The profile's non-essential-traffic switch makes that review the default from v2.1.282, so T020's likely configuration behaves the same, and the PRD's R-1 test (whether auto mode lets the Gemini request through) still holds.

**Cost.** In Manual mode, the pre-ruled fallback, each sandboxed command outside the read-only set prompts. That gives a person the review in the one mode that has no classifier, which suits an isolated session. The always-on copy carries the key, and the disclosure says that the adopter may leave it out of that copy.

**Not adopted.**
- `autoMode.classifyAllShell: true`, which would suspend narrow Bash allow rules from other scopes in auto mode. Sandboxed commands stay bound by the one-host allowlist, the effective-config check now names narrow Bash allow rules, and the spec does not require it.
- Pinning the weakening switches to `false` to override a user-scope `true`. FR-005's AC requires a profile text with no excluded-commands, write-allowance or nested-user-namespaces entry. These keys stay named negatives, and the effective-config check covers them.

**For T020.** One check of a few minutes, run before the write listing: start the profile once with `--permission-mode default` and ask Claude to run `touch ./tachi-mode-probe` in the scratch project. A prompt confirms the regular permission flow. Delete the file afterwards. Under the profile, `/sandbox` cannot show the mode (AR-18).

### 2.8 AR-17: deny every MCP tool in the profile

**What the docs state.**
- `"mcp__*"` "matches every MCP tool across all servers", and "A tool matched by a bare-name glob deny rule is removed from Claude's context" (permissions, "Tool name wildcards"). Deny rules apply before the classifier, in every mode.
- Connectors that Claude Code fetches itself appear as `mcp__claude_ai_<server>__<tool>` (permissions, "MCP"). Claude Code fetches them unless a setting turns them off (settings reference, `disableClaudeAiConnectors`, default `false`).
- Local MCP servers run outside the sandbox with full access (sandboxing, "What runs outside the sandbox"). `deniedMcpServers` stops a matching server from loading (settings reference).

**Why it is a defect.**
- FR-005 makes MCP part of what the profile covers, and the `hard_deny` names "an MCP server" among the tools.
- The contract's only MCP control was a runbook instruction. A copy-paste adopter can skip it, and no test pins it.
- In a claude.ai-authenticated session, every connector (mail, documents, chat) is a route off the machine that the model can invoke, and neither the sandbox nor `allowedDomains` reaches it.

One deny entry closes the tool route in every mode. No tachi agent or command uses an MCP tool (the Tools column in §8.3).

**What stays.** The runbook keeps "list each configured server in `deniedMcpServers`, or confirm there are none". The instruction now addresses the remaining residual: a local server process still starts and runs outside the sandbox. The rule's name contains `_` and `*`, so the startup check for unknown tool names exempts it (permissions, "Tool name wildcards").

**Not adopted.**
- `allowedMcpServers: []`. An empty list blocks servers only while no other file sets the key, so its effect would depend on other files.
- `disableClaudeAiConnectors`. The deny already covers the connectors' tools, and the spec asks for no more.

### 2.9 AR-18: the effective-configuration check, and the Linux seccomp filter

**What the docs state.**
- "When `sandbox.enabled`, `sandbox.autoAllowBashIfSandboxed`, or `sandbox.allowUnsandboxedCommands` is set above the local settings level, `/sandbox` prints `Sandbox settings can't be changed here. Higher-priority settings override them.` and its panel stays closed". The docs add: "Managed settings and `--settings` rank above local settings" (sandboxing, troubleshooting). The profile set two of these keys before AR-16, so its Config tab was never reachable.
- With `strictAllowlist` on, "Claude Code refuses per-command lists", and the proxy refuses an unlisted host in every permission mode (sandboxing, "Per-command allowed domains in auto mode" and "Hosts outside your allowed domains").
- The seccomp filter "is optional and adds Unix domain socket blocking". The sandbox starts without it, and only the Dependencies tab of `/sandbox` reports that it is missing (sandboxing, "Set up Linux and WSL2"). Without it the sandbox does not block Unix-socket calls (settings reference, `sandbox.network.allowAllUnixSockets`). On WSL2, the launch of a Windows program goes over a Unix socket (same Linux section).

**Why it is a defect.**
- FR-005 requires the runbook to have adopters check the effective configuration. As written, the instruction pointed at a view that the profile itself closes.
- AD-12's step "confirm `--settings` honours `strictAllowlist` from a file" relied on the same view (`test-results/profile-prestage.md` §7, last paragraph).
- On Linux and WSL2, the isolation claim also depends on the seccomp filter, which nothing in the profile or the probe table checks. Without the filter, sockets such as a container runtime's are open to sandboxed commands.

**Fix** (contract disclosures and probe table):
- Read the other scopes from a session in the same project started without the profile. Its `/sandbox` Config tab shows what those files add, which is the part of the union that the profile cannot remove.
- In the profile session, read `/status`, `/permissions` and `auto-mode config`.
- Confirm `strictAllowlist` with the new `curl -sS https://example.com` row.
- Confirm `tlsTerminate` with the key-ful run. Without it the sentinel reaches the server unchanged and authentication fails (sandboxing, "Mask credentials"). `claude doctor` reports `TLS termination is unavailable` for that misconfiguration; the docs do not say whether it reads a `--settings` file, so T020 records what it shows.
- On Linux and WSL2, install the filter and check the Dependencies tab before the first session with the profile.

**For T020.** Record the `/sandbox` message, whose text also confirms that the profile ranks above local settings. Run the new probe row. On the Linux VM, record whether the filter was present.

### 2.10 AR-19: named negatives and pinned values

The closed key set already rejects every key outside the 19 paths. The named negatives are the non-vacuity cases that prove it.

The contract named 13 keys and left out `sandbox.allowAppleEvents`, the one key missing from the docs' own list of six weakening keys; the docs say it "removes code-execution isolation". The list now holds 21 keys, in full key-path form:
- every key that the sandboxing page names as weakening or loosening the sandbox: the list of six, and the table of loosening settings that an admin-required sandbox ignores in repository files;
- `sandbox.credentials.allowPlaintextInject`, which would let the proxy put the real image key into a plain-HTTP request;
- the profile's own forbidden keys: `permissions.allow`, `permissions.defaultMode`, `autoMode.allow` and `autoMode.soft_deny`.

Short forms such as `defaultMode` become `permissions.defaultMode`; the meaning is unchanged.

**Values.** A set of key paths says nothing about `"enabled": false` or an extra deny rule. T017 therefore also pins the seven scalars and the members of the three security lists, compared as sets. That answers SEC-A's hand-off to T017. T017's task text lists 13 negatives, but the contract's list governs, because T017 asserts "the exact key paths of `contracts/session-profile.md`".

### 2.11 AR-20: contract prose corrections

Each item changes the contract's prose, which T016's second commit copies.

1. **`--setting-sources` costs** (T006 §3.2 and §10, item 2):
   - "retention default" becomes "the retention sweep pauses when no enabled source sets `cleanupPeriodDays`";
   - "auto-mode re-prompt" becomes "a mode dialog that the user file suppressed can appear again (documented for the bypass-permissions warning)";
   - "user-scope masks" becomes "user-scope environment-variable masks".
2. **What runs outside the sandbox.** The docs list command hooks, local MCP servers, plugin monitors, LSP servers, mods, and helper commands such as the status line and `apiKeyHelper` (sandboxing, "What runs outside the sandbox"). The contract named three of them.
3. **Part B text in Part A (AD-14).**
   - The model-selection sentence said "the manifest or transcripts", and the retention sentence said "archive with B1". The Part A forms now say "the session transcripts" and "raise it again, or copy the transcripts you need out of `~/.claude/projects/`". The Part B forms are T048's.
   - The model-selection statement also takes T006 §2.2's `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` caveat, so it agrees with §8.1 of `CLAUDE_PERMISSIONS.md` (T023). The words "states only" no longer rule that caveat out.
4. **Probe table.**
   - The expected outputs come from the docs ("Confirm commands run inside the sandbox").
   - Claude runs each line; a line typed at `!` runs outside the sandbox.
   - A permission-rule or classifier refusal of `touch` or `curl` is not a sandbox result.
   - It gains the `strictAllowlist` row (AR-18), and the SEC-A rules are checked by configuration (AR-15).
5. **Four new disclosures.**
   - `strictAllowlist` also refuses auto mode's per-command host lists.
   - `WebFetch(domain:*)` in `deny` is no substitute for the bare `WebFetch` deny, because it also denies every host to sandboxed commands, the Gemini host included (permissions, "Allow or deny every fetch").
   - The profile is for local sessions. An Anthropic-hosted cloud session starts with a warning and does not enforce the `sandbox.filesystem` and `sandbox.network` rules (settings reference, `sandbox.failIfUnavailable`).
   - The `env` key keeps artifact publishing off (artifacts, "Availability"). Without it, FR-004's two-host statement would also have to name claude.ai as a destination.
6. **The audiences sentence** now records the T005 ruling as done.

Considered and left as written:
- The primary-use entry's "writes only under the run's output directory" leaves out `$TMPDIR` and the `/tachi.architecture` carve-out. It is PRD FR-6's passivity wording, and the classifier allows file operations in the working directory by default, so it should cause no denial. If T020 records a denial traced to this entry, T021 takes a wording change to the PM.
- The `environment` slot names ("Primary use", "Data retention") are cosmetic (T006 §10, item 3).
- No byte of the `hard_deny` sentence or of the audiences entry changed. Both still match PRD FR-6 and `field-list.md` §10.3, checked by script.

### 2.12 AR-15 to AR-20: escalations, effects and the runbook's write table

**PM: FYI, no wording change.** PRD FR-5 lists the deny rules and the sandbox keys. The contract now adds `mcp__*`, the two SEC-A Read denies, the credentials-file entry and `autoAllowBashIfSandboxed: false`. FR-005's text already covers each addition: MCP servers in the deny list, read denies for secret paths, and the classifier statements of FR-006. D-6 is the architect's decision, and T049 already routed the key set to this review. A PRD sync at delivery is optional.

**User: nothing blocking.** FYI:
1. The pre-staged `~/.tachi/391-w2/session-profile.json` (SHA-256 `e3fdf5bf…`, 2658 bytes) no longer matches the contract. Before T020 it must be replaced by the block extracted from the runbook (`test-results/profile-prestage.md` §8). The amended block, extracted the same way with its trailing newline, is 2908 bytes with SHA-256 `43496fb7d4fca098983a70648def8f1da2a2d1843528b5ca4c14444e32564279`. The GL diff should reproduce that value once T016 lands, if the runbook keeps the block's bytes.
2. T020 gains a Manual-mode check (AR-16), a probe row (AR-18) and one Linux `python3` probe (AR-15), and one existing step changes. That is about 0.03 d inside TW-A1.

**Runbook §5 (review item 3).** T016's first commit copies §8.5 of `CLAUDE_PERMISSIONS.md` exactly:
- the heading `## 5. Write locations`;
- the header row `| Path | Written by | Condition |`;
- the 21 rows, verbatim.

The rows reflect the earlier rulings:
- AR-1: the attack-tree and attack-chain PNGs and the corrected image copy under `{out}`, and the deletion limited to `{out}`.
- AR-2: `risk-scores.{md,sarif}` always under `{out}`, and `threats.md` rewritten in place only when `{out}` is the input directory.
- AR-3: the two Gemini intermediates under `{out}/.tachi-build/`, kept, and the decode with `python3`.
- AR-14: no bytecode-cache row.

A script check found that the 21 path tokens equal the union of the Writes cells in §8.3 and §8.4, and that none names `__pycache__`, `templates/` or `/tmp`. C7 is therefore green on a verbatim copy. AR-8's precondition sentence and the `/tachi.architecture` carve-out go beside the table.

**No effect on** §8 of `CLAUDE_PERMISSIONS.md`, T023, T025, T026 or ADR-049.

Effort: T016 none beyond the copy; T017 +0.02 d (values, members, eight more negatives); T020 +0.03 d.

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
| AR-15 | The runbook block carries both SEC-A Read denies and the credentials-file entry. The second commit carries SEC-A §5.6 and the extension note. T020's stage B and C results are recorded, and any ladder row that fired (2.6) is applied in the contract, the runbook and T017 together |
| AR-16 | `autoAllowBashIfSandboxed` is `false` in the block, and T020's Manual-mode check is recorded |
| AR-17 | `mcp__*` is in the block, and the runbook keeps the `deniedMcpServers` instruction for the process residual |
| AR-18 | The runbook's effective-config check names no `/sandbox` view inside the profile session. The `strictAllowlist` probe row and the Linux and WSL2 seccomp step are present. T020 recorded the `/sandbox` message |
| AR-19 | T017 asserts the 19 paths, the scalar values, the three member sets and the 21 negatives, and goes red on a mutated copy |
| AR-20 | The second commit's prose matches 2.11. The runbook's Part A text names neither the manifest nor the archiver |

## 6. W3 addendum: AR-21 (architect, 2026-11-20, S2b)

AR-21 is the architect's ruling W3-3, made against the Part A branch at `858ac85` and the public Claude Code docs read on 2026-11-20. It began as finding F3 of the live validation (T020), the three MCP resource tools that sit outside `mcp__*`, and widened after a pass over the whole public tools reference. It applies AR-17's principle, that model-invocable egress outside the sandbox is closed in the profile, to the other built-in tools that run in the Claude Code process.

**PM:** FYI only. PRD FR-5's list is a floor (AR-15) and the `hard_deny` sentence is unchanged, so no PRD change is needed. **User:** nothing blocking. The maintainer's re-check (6.3) is the one action, and it comes before T046.

### 6.1 Ruling

| AR | Discrepancy | Disposition | Absorbing task | Scope change (files, lines, behaviour) |
|---|---|---|---|---|
| AR-21 | Profile defect: eight built-in tools run in the Claude Code process, outside the sandbox, and can move content off the machine or into another session. Most need no permission prompt. tachi uses none of them, and the profile denied none: AR-17's `mcp__*` does not match the three MCP resource tools, whose names do not start with `mcp__` | Add the eight to `permissions.deny` by bare name: `ListMcpResourcesTool`, `ReadMcpResourceTool`, `ReadMcpResourceDirTool`, `SendMessage`, `ListAgents`, `Monitor`, `RemoteTrigger`, `ShareOnboardingGuide`. Not adopted: `disableClaudeAiConnectors`, `crossSessionInbound`, a user-scope fix | T021 (the block, the runbook text, these records), T017's test in the same commit as the block (SBE-TA), T042 (review), the maintainer's re-check before T046 | `permissions.deny` +8 rules (16). No new key path: the closed set stays at 19. The published block differs from the one the live run used, which ends the "Last validated" claim under refresh trigger 2 until the re-check runs. Detail in 6.2 and 6.3 |

### 6.2 AR-21: deny eight built-in tools that run past the sandbox

**The eight, by family.** Each runs in the Claude Code process, as the Read tool does, so the sandbox, `allowedDomains` and `strictAllowlist` do not reach it.
- MCP resources: `ListMcpResourcesTool`, `ReadMcpResourceTool` and `ReadMcpResourceDirTool`. They list and read the resources of every connected server. Their names do not start with `mcp__`, so AR-17's rule misses them. The first two are in the tools reference; the third was observed on Claude Code 2.1.330.
- Messaging between your sessions: `SendMessage` and `ListAgents`. The feature is on by default, including with feature-flag fetching off (v2.1.248 or later), and the docs' recipe for turning it off is to deny both tools.
- `Monitor`: Claude Code itself opens a WebSocket watch to a `ws://` or `wss://` address. The docs' list of hosts denied to a watch does not include `allowedDomains`.
- `RemoteTrigger`: creates and runs cloud scheduled tasks on claude.ai, which need only a claude.ai login.
- `ShareOnboardingGuide`: uploads `ONBOARDING.md` and returns a share link (Team and Enterprise).

**Why it is a defect.**
- Most of the eight need no permission prompt, and a deny rule applies before the classifier, in every mode.
- tachi uses none of them. A grep over `.claude/agents/tachi/`, `.claude/commands/tachi.*.md` and `.claude/skills/tachi-*/` finds only the English word "Monitor" in mitigation text. A deny rule therefore removes nothing a run needs, and R6 checks that.
- The pass covered the whole tools reference, not only the three tools the live run noticed. `Artifact`, `PushNotification` and `SendUserFile` stay because the profile's non-essential-traffic variable turns off the publishing and Remote Control that they need. `Workflow` and `Agent` stay because they run under the same sandbox and rules. Everything else in the table is local or needs a cloud session or the desktop app.

**Form.** A bare tool name in a deny rule removes the tool from Claude's context, which the live run also showed for `WebFetch`. The docs describe no warning for a deny rule that names an absent tool, and R3 checks that on the version in use.

**Not adopted**, one reason each.
- `disableClaudeAiConnectors`: it would add a key path and cover only the claude.ai connectors, while the deny rules close the model's route to resources on every server.
- `crossSessionInbound`: it governs messages that arrive, not egress, so it earns no key path. The runbook text (T021) discloses it as an optional setting for the adopter's project-local settings.
- A user-scope fix: the eight are model-invocable and run in the Claude Code process, so AR-17's principle puts them in the profile. User scope is for process residuals, such as a local server starting.

**Key set.** No key path is added: the closed set stays at 19, and the scalars and the 21 named negatives are unchanged. In the contract, only the `permissions.deny` members change, plus one invariant and the two Disclosures bullets.

**Owners.**
- DEVOPS-R (T021): the runbook block, with the contract's block identical to it; the runbook text that follows (§1, §3, §4, §9); and the records (`contracts/session-profile.md`, `data-model.md` line 53, this addendum).
- SBE-TA: `tests/scripts/test_isolated_profile_contract.py`, landed in the same commit as the block edit. The test pins the block, so either change alone turns CI red. It gains the eight members, a check that each is present exactly as written, and negative controls (each name removed, one scoped form, one case change).
- Maintainer: the re-check in 6.3, before T046.
- T042: reviews the amended block.

### 6.3 The bounded re-check

A changed profile ends the "Last validated" claim (refresh trigger 2 in the runbook's header), and the published block differs from the one the live run used. A deny-only change cannot widen anything, but it could remove something a run needs. The re-check therefore covers the profile layer plus one command with a deep dispatch tree. It is required before T046 and is the maintainer's to run, and Claude may drive it with the deviation recorded. It runs key-less in the W2 scratch adopter and takes about 0.03 d.

| Step | What it covers |
|---|---|
| R1 | Extract the committed block. Record its bytes and SHA-256 |
| R2 | Run `claude --settings <file> auto-mode config` and compare as W2's GL-3 did: `environment` 21 to 26, `hard_deny` 1 to 2, `allow` and `soft_deny` unchanged |
| R3 | Launch with the validated wrapper form (W3-5), key-less. Pass: no startup warning names a rule, `/status` sources include Command line arguments, and `/permissions` lists the 16 profile denies. If a warning names one of the eight, drop only that name from the block and the test, then repeat R3 |
| R4 | Take the tool inventory, names only. Pass: no `mcp__` tool and none of the eight names, loaded or deferred. Also record which `isolation` values the `Agent` tool offers. Anything other than `worktree` goes back to the architect, because no deny rule can remove that without removing `Agent` |
| R5 | Run probes P1 to P3 and the planted `.env` row |
| R6 | Run `/tachi.threat-model` once on the W2 input, key-less. It must pass |

The record is a dated addendum in `test-results/w2-live.md`, or a short W3 record, plus runbook §11.

### 6.4 Check for T040

| Ruling | Check |
|---|---|
| AR-21 | The runbook block and the contract block are identical and carry 16 `permissions.deny` rules, with the eight tool names bare and in the architect's order. The contract says "sixteen rules" and carries the AR-21 invariant, and `data-model.md` lists the same 16. The contract test pins the members, the key set is still 19 paths, and the test goes red on a mutated copy. The re-check's R1 to R6 are recorded before T046 |
