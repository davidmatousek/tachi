# W3 reviews: full-diff review of both branches (T044)

T044 has two parts: the code review (part 1, below) and the architect's final checkpoint (part 2), which reads part 1. Structure only: no transcript text, session ids, home paths or account details.

## T044 part 1: code review (2026-11-20)

| Item | Value |
|---|---|
| Task | T044 part 1 (`tasks.md`), with the scope of the architect's B1-stop ruling §6.1 (T044 row) and `NEXT-SESSION.md` ("Decisions S2a took", "What L changes" item 4) |
| Reviewer | code-reviewer |
| Part A | `391-isolated-auditable-operation` at `b2385ca`: `git diff main...b2385ca`, 84 paths (main `39af1ce`) |
| part-b | `391-isolated-auditable-operation-part-b` at `f34e0ed`: `git diff b2385ca...f34e0ed`, merge base `b71a0d7`, 17 paths (B2 and the seven TW-B1 stop commits) |
| Later commits | While this review ran, Part A gained `183fb2f` (runbook citation links, T041 FR-009) and part-b gained `a828584` (the BX'''' merge of Part A). The review is of the pinned tips; section 5 checks the delta |
| Method | Read-only git in the main tree. Every execution ran in scratch clones of the pinned tips (`git clone --no-hardlinks`, `log -1` checked, clean after each run) or in scratch sandboxes built from them. No pytest and no extractor in the main tree |
| Verdict | **APPROVED_WITH_CONCERNS**: 0 CRITICAL, 2 WARNING, 6 SUGGESTION, 2 INFO. No finding blocks the merge. The two WARNINGs are small fixes; land them before T046/T047, or defer each to a follow-up by an explicit architect ruling |

### 1. Findings

| ID | Severity | Branch | File:line | Finding | Recommendation | Owner |
|---|---|---|---|---|---|---|
| CR-1 | WARNING | Part A | `scripts/check-agent-privileges.py:427-442` (`:440`), used at `:602` (agents) and `:788` (commands) | `split_frontmatter` ends the frontmatter at the first line whose stripped text is `---` or `...`, so an indented `---` inside a block-scalar value, or a `...` line, closes the guard's view early. Keys after that line are invisible to C2, C3, C4 and C5. Reproduced on a copy of the guard's inputs: an agent whose `description` is a literal block scalar holding an indented `---`, followed by `permissionMode: bypassPermissions`, leaves the guard at exit 0, while a YAML reader of the block up to the column-0 `---` lists `permissionMode`. A `...` line before the same key also gives exit 0. Not checked against Claude Code: a `---yaml` first line in the allow-listed document keeps it classified as having no frontmatter. Claude Code's own delimiter rule was not checked. Needs a crafted change, and the key stays visible in the diff, so this is not CRITICAL. But it is a parser difference of the kind the guard already refuses for duplicate keys, and it undercuts ADR-049's "cannot ride along" consequence | Make the guard fail closed whichever rule Claude Code uses. Inside the frontmatter body, an indented line whose stripped text is `---` or `...`, or a `...` closer, is exit 2 (as a duplicate key is). So is a first non-blank line that starts with `---` and is not exactly `---`, at least for the allow-listed document. Add red cases for an agent and a command to `test_agent_privilege_guard.py` | SBE-W3A |
| CR-2 | WARNING | part-b | `README.md:153`, `:157`; `docs/guides/DEVELOPER_GUIDE_TACHI.md:131`, `:1036` | The manual-loop marker line runs `git -C "$TACHI" describe`. When `$TACHI` is a tachi copy that is not a git clone but sits inside another git work tree (a release archive unpacked into a project, or a home directory kept in git), the line writes that repository's describe value. Reproduced in a scratch sandbox: a host repository tagged `v9.9.9-host` with a non-git tachi copy inside it gave `tachi_version: v9.9.9-host`. The value passes the readers' rule, so the stamp copies it into `threats.md` as the wrong provenance, with no warning. `install.sh:644` handles this case with `rev-parse --show-cdup`, and a test covers it. `README.md:157` says the line gives `unknown` "when git cannot describe `$TACHI`, for example because it is not a git clone", which does not hold for a nested copy | Keep the line single, byte-identical in its three copies and comment-free. Run the describe only when `git -C "$TACHI" rev-parse --show-cdup` prints nothing, and write `unknown` otherwise. Empty output means the repository root, or not a repository, where describe then fails to `unknown`. Add a bash and a zsh case to `test_tachi_version_marker.py`. Alternatively, state the limit in the `:157` sentence and in ADR-049 D10 | SBE-B2 |
| CR-3 | SUGGESTION | Part A | `scripts/extract-report-data.py:947-972`; preflight calls `:1069`, `:1651` | W3-L4, carried. A bad `TACHI_MMDC_PUPPETEER_CONFIG` ends the run with an uncaught `RuntimeError`: exit 1, a traceback, then a message that names the variable. It fails closed (see 2.2). Also: the check runs only when a diagram is rendered, after `detect_images` (`:2914`), which may already have written a corrected infographic copy under `{out}` (confinement holds). Exit 1 is documented as "missing required artifact" (`:46`). A symlink to a regular file is accepted | No change in 391. Follow-up: when the variable is set, check it once at startup in both modes. Print one line and exit 2, as `_exit_build_dir_error` does, and name the case in the docstring's exit codes and the epilog. The bad-value tests assert only `returncode != 0`, so they stay valid | SBE-W3A |
| CR-4 | SUGGESTION | part-b | `.github/workflows/tachi-pytest.yml:34`, `:41`, `:337` | The `py39-floor` comments say the job "re-runs the F-391 modules" and that its list is "the F-391 subset" of the matrix list. The matrix list holds four F-391 modules, and the job runs the two Part B ones. The guard states Python 3.9 or later (its docstring, ADR-049 D1), and stock macOS `python3` is 3.9.6, yet no CI job runs the guard suite on 3.9. Under 3.9.6 in a scratch clone of `b2385ca`, the guard suite, the profile contract, manifest completeness and coverage attestation gave 388 passed and 1 pre-existing skip | Either add `test_agent_privilege_guard.py`, and optionally `test_isolated_profile_contract.py`, to `py39-floor` in lock-step, or reword the two comments to "the Part B modules" | SBE-TB |
| CR-5 | SUGGESTION | part-b | `scripts/install.sh:573-588`; `tests/scripts/test_tachi_version_marker.py` | No automated case reaches `marker_guard`'s refusals. They are the only guard when `--version` names a tag older than the placeholder, because the pre-flight then has no `VERSION` to classify. Checked by hand in a scratch sandbox, with a source tree without the placeholder and without a git tree. A symlinked marker gave exit 1 with the "symbolic link" message, the link target unchanged and nothing written. A directory at the marker path gave exit 1 with the "not a regular file" message, nothing written. A plain project gave exit 0 and `tachi_version: 4.48.2-release-manifest` | Add the two refusal cases (one runnable check for the safety branch, code-economy §1) | SBE-TB |
| CR-6 | SUGGESTION | Part A | `.claude/agents/tachi/report-assembler.md:164`, `:194`, `:218` | "Quote a path that contains spaces" is given for Step 2c only. Steps 3a and 3d use the same `{output_path}` unquoted, and the pre-391 Step 3a quoted the PDF path. The frontmatter is unchanged on every branch | Add the sentence to 3a and 3d, or quote the placeholders in the three fences. C6 reads quoted words as before | SBE-W3A |
| CR-7 | SUGGESTION | part-b | `docs/standards/CLAUDE_PERMISSIONS.md:377` | The `/tachi.threat-model` "Bash it instructs" cell reads `` `python3`, `python3 scripts/stamp-tachi-version.py` ``. Every other cell in the column lists command families. The guard does not read the column, and the cell syntax accepts the token | Keep the cell at `python3` and name Step 2.6's script in the §8.4 notes, or define the column's tokens in §8.2 | SBE-B2 |
| CR-8 | SUGGESTION | part-b | `tests/scripts/test_threats_schema_contract.py:33-34` | The docstring says that `cli-contracts.md` has exit codes 1 and 2 the other way round and that T040 reconciles it. The contract now matches the script and the tests | Drop the sentence | SBE-TB |
| CR-9 | INFO | Part A (records) | `specs/391-isolated-auditable-operation/contracts/version-marker.md:7` | "writes the new line after it (`:585`)" is stale. On part-b the write is `scripts/install.sh:675-676` (block `:670-680`), and the pre-loop reset is `:590-597` | Update the pointer, or drop the line number | SBE-B2 |
| CR-10 | INFO | Part A | `scripts/extract-report-data.py` (`_materialize_build_dir`; the PNG directories under `{out}`) | T042 W3-H1 marked an optional code hardening for T014: in build mode, refuse a symlinked `{target_dir}/report-config.typ` and symlinks under `{out}`. Today the copy and the PNG writes follow links. Under the session profile the sandbox binds each write by its real path. The by-hand build is covered by the runbook text added in `c535aa9` | Concur with T042: a follow-up, not 391 | SBE-W3A |

### 2. Rulings on the carried items

**2.1 X-7 went past the literal ruling: the code is right.** The writer (`install.sh:659-668` on part-b) spells out the letters and digits instead of using ranges. It writes `unknown` for an empty value, a first character that is not a letter or digit, any character outside letters, digits and `. _ + ~ -`, and more than 128 characters. The reader (`stamp-tachi-version.py:80`) accepts `[A-Za-z0-9][A-Za-z0-9._+~-]{0,127}` on a one-line file. Both define the same language, ASCII only, and no locale can widen the bash list. With B1 stopped, the stamp script is the only reader. So `contracts/version-marker.md:5` ("aligned with the rule") holds for the installer. Closing the three extra differences was right: each one wrote a marker that the reader then turned into `unknown`, and now the file and the stamped value agree. The tests cover all five out-of-rule tags and the 128-character control. The README line is a second writer without the filter; the reader maps its out-of-rule values to `unknown`, except CR-2's case, which passes the rule.

**2.2 `TACHI_MMDC_PUPPETEER_CONFIG` and the uncaught `RuntimeError`: do not change it in 391.** It fails closed. The run exits non-zero before any `mmdc` call. No `report-data.typ` is written, because the build directory is recreated only after extraction succeeds (`extract-report-data.py:3017`). The message names the variable. The report assembler stops on any non-zero exit (its Step 2d). The pre-existing mmdc-missing preflight uses the same channel. A clean message is worth having, but it is a product-file change after T043's gated run. Recommendation: the follow-up in CR-3. A docstring-only line adds little, because Step 2d already stops on any non-zero exit.

**2.3 X-8 and the archiver's `DeprecationWarning` (3.13 and later): nothing of either remains on either branch.**
- X-8 (`c46b6a8`) touched only the archiver, its manifest schema and its suite. All three are removed from part-b (`40f0a58`, `bc943c6`), and `git ls-tree` finds no B1 path at `f34e0ed`.
- A `git grep` of both tips for the archiver tokens, `XAUTHORITY` and `GIT_COMMITTER` excluded the feature records, the system-design README and `docs/product/**`. It finds only pre-existing, unrelated text: a run-manifest file name in a Feature 373 record, and a test environment in `test_template_git_clone_timeout.py`.
- The warning class is gone too. An AST scan of the five installed scripts at `f34e0ed`, the guard and the SARIF generator finds no positional `maxsplit`, `count` or `flags` in `re.split`, `re.sub` or `re.subn`.
- Under Python 3.14.4 with `-W error -X dev`, the guard's `--self-test` and a stamp run with `--check` both exit 0. All six scripts compile with `DeprecationWarning` and `SyntaxWarning` as errors.

**2.4 Left to the architect (part 2):** the AD-12 deviation, F3 and F7 (`w2-live.md` §7) and W3-L6 (T042). On F3's code side: AR-21's eight bare names and AR-21a's two rules are in the published block. `test_isolated_profile_contract.py` pins them exactly: a removal, `Monitor(*)`, a case change and `Agent(isolation:remote)` or `Agent(isolation:worktree)` each turn it red.

### 3. Confirmations for the architect's B1-stop ruling (§3.9 and the §6.1 T044 row)

Each check ran on the pinned tips (`b2385ca...f34e0ed`, merge base `b71a0d7`) and again on the new tips (`183fb2f...a828584`). Both runs gave the same result.

| Check | Result |
|---|---|
| B1 files in the part-b tree (`scripts/archive-run-transcripts.py`, `schemas/run-manifest.yaml`, the archiver suite, `tests/fixtures/transcripts/`) | 0 |
| Paths in the 3-dot diff | 17, identical to the list in §1.1 (compared line by line) |
| Runbook and ADR-019 | 3-dot diff empty. The runbook blob on `f34e0ed` equals the merge base's, Part A's text when BX''' merged (Part A changed it again later in `c535aa9`). On `a828584` it equals Part A's `183fb2f`. ADR-019 has one blob on every tip |
| ADR-019 Note that ships | Part A's, FR-015's "otherwise" wording ("recorded in Claude Code's transcripts, not in the agent files"), on both branches |
| ADR-049 (E1 to E8) | "Ten decisions"; D10 is the version stamp; no D11 and no run-archive decision; Known limitation 6 in the E5 wording; no item 7; FR range `FR-011 to FR-015, FR-020, FR-021` in both places; AD list without AD-6; the version-stamp cross-reference line |
| `INSTALL_MANIFEST.md` | "5 Python files" at `:15` and `:65`; 5 rows in the Script Files table; 5 `scripts/*.py` lines in the machine-parseable block; no archiver row or line |
| `tachi-pytest.yml` | Parses as YAML; `paths:` 74 entries, and `push` reuses the anchor; matrix list 23 modules; `py39-floor` 2, a subset in the same order; every module in `paths:`; no `archive` token |
| B1 tokens (§3.9's fourth command) | 0 on the 3-dot diff, and 0 on `main...b2385ca` and `main...f34e0ed` (the T046 and T047 form) |
| Stamp script S1 and S2, test docstring (§3.4, §3.5) | Applied as written |
| The seven stop commits | `be2e890`, `dfcf93e`, `efaaf70`, `140d93d`, `f7f8ce4`, `40f0a58`, `bc943c6`: subjects as §7 items 2 to 8, in §2.2's order, each touching only its own files |

### 4. What was reviewed, and how

**Part A code.**
- `check-agent-privileges.py` was read in full, and C1 to C8 behave as its docstring and `cli-contracts.md` state.
  - It fails closed: a strict YAML subset, duplicate keys refused, and any internal error is exit 2.
  - The self-test compares each mutation with an unmutated baseline. Its "already red" status cannot hide a blind check on a green tree.
  - C6 behaves as documented: separators, reserved words, `$(`, backticks and process substitution on the raw line, and stand-ins for quoted metacharacters. A heredoc body would be read as commands and turn red (fail closed).
  - Apart from CR-1, no gap was found.
- In `extract-report-data.py`, every hunk was read:
  - the build-directory guard (an anchored symlink walk, run twice);
  - the recreate-after-extraction order, and the idempotent removal;
  - `image_dir` as the build directory's grandparent, and the `{out}`-only cleanup gate;
  - legacy mode unchanged, and the CLI mode resolution.
  T042 already ran the guard against 12 path forms, and those were not repeated here.
- The three importers set `sys.dont_write_bytecode` before importing `tachi_parsers`.

**Bodies, skills, `.gitignore`.**
- Frontmatter: the three agent files that change (`report-assembler.md`, `threat-infographic.md`, `risk-scorer.md`) have the same frontmatter hash on main, Part A and part-b.
- Agent bodies:
  - The infographic body's claim about `--output` matches the script: the option is required, and the script creates the parent directory.
  - The prompt lines that the bodies rely on are in the commands: "Write all output files to:" and "Output directory:".
- Commands:
  - `/tachi.security-report` dispatches `tachi-report-assembler`.
  - The repair hints name `install.sh`, run from the project root. The adapter copies keep their old hint (AD-13, #369, carried).
  - `grep -P` became `grep -E` in `/tachi.infographic`, which also works with BSD grep.
- The skill references match the extractor's relative bases, and `.gitignore` ignores `.tachi-build/`.

**Tests.** Read for structure and for the cases the brief names:
- the AR-21 and AR-21a controls, with their negative controls;
- the guard's red, green and infra cases, and its self-test cases;
- write confinement, including X-1's puppeteer cases;
- SC-A4 in manifest completeness;
- the coverage-attestation build-directory change, which no longer writes into the templates tree;
- the B2 marker and schema-contract suites.

CR-5 and CR-8 are the only test findings.

**Workflows.**
- `tachi-permissions-verify.yml`: the anchor gains the four guard inputs, and a `python3` presence step comes before `--self-test`.
- `tachi-install-fidelity.yml`: the anchor covers every input of the write-confinement suite and of the SC-A4 cases.
- `tachi-pytest.yml`: the list and `paths:` move in lock-step on Part A (21 modules) and on part-b (23 modules, plus `py39-floor`).

**Machine-checked doc parts.**
- The runbook §5 table and §8.5 of `CLAUDE_PERMISSIONS.md` are byte-identical, all 23 rows, at `b2385ca` and at `183fb2f`.
- The profile block is unchanged across `b71a0d7`, `b2385ca` and `183fb2f`: 18 deny rules, the contract test's 19 key paths.
- The matrix-link line carries the release marker and is pinned to the current release (ADR-049 Known limitation 2).
- §8's agents and commands tables match the files and the extractor's write set.

**part-b code.**
- `install.sh`, with the marker block: passes `bash -n` under Bash 3.2.57, and `shellcheck` reports 0 findings at any severity on both tips. The block uses no Bash 4 feature.
- `stamp-tachi-version.py`:
  - keeps every byte outside the inserted line;
  - writes an `O_EXCL` temp file, then renames it over the target;
  - replaces a symlink at the target and never writes through it;
  - turns any internal error into exit 2.
- `generate-threats-sarif.py` takes `semanticVersion` from the input file, with `schemas/output.yaml` as the fallback. It is not installed.
- Schema 1.5 is additive, and Step 2.6 sits between Step 2.5 and Step 3.
- The populator edits only the Affected Assets block, so a later `/tachi.risk-score` keeps the stamp.

**Python floor (installed scripts, stdlib, 3.9 or later).**
- An AST and API scan under Python 3.9.6 covered the guard, the five installed scripts, the SARIF generator and the seven test modules. It found no `match`, no `zip(strict=)`, no `hashlib.file_digest`, no `datetime.UTC`, no PEP 604 outside annotations and no `fromisoformat`.
- Every file compiles under 3.9.6.
- B2's modules run on 3.9 in CI (`py39-floor`). For Part A, the floor rests on T043's X-5 record and on this review's run on 3.9.6 (see CR-4).

**Code economy.**
- No over-build was found.
- The guard's own strict YAML subset is justified: the job is stdlib-only and installs nothing, and the parser fails closed.
- The stamp script's byte-level edit and atomic write protect a user's file (carve-out §1).
- The build-directory explanation appears in six places (docstring, epilog, flag help, agent body, skill references, template README). That is prose duplication, and it is acceptable.
- The safety carve-outs are intact. The one gap is CR-5's untested guard branches.

### 5. Runs in scratch clones, and the delta to the new tips

| Tip | Run | Result |
|---|---|---|
| Part A `b2385ca`, Python 3.9.6 | `test_isolated_profile_contract.py`, `test_agent_privilege_guard.py`, `test_install_manifest_completeness.py`, `test_coverage_attestation.py` | 388 passed, 1 skipped (`sys.stdlib_module_names` needs 3.10; pre-existing) |
| Part A `183fb2f`, Python 3.9.6 | the first three modules above; guard `--self-test` | 372 passed, 1 skipped; guard pass |
| Part A `b2385ca`, Python 3.14.4, `-W error -X dev` | guard `--self-test` | exit 0 |
| part-b `f34e0ed`, Python 3.14.4, `-W error -X dev` | stamp, then `--check`, on a copy of an example `threats.md` | stamped, exit 0; then already stamped, exit 0 |

- T043's gated record is for Part A at `b71a0d7`. From `b71a0d7` to `b2385ca`, only the runbook (`c535aa9`) and records change, and no code. So the runbook-reading suites above extend that record to the reviewed tip.
- `183fb2f` changes runbook prose only (citation links). The profile block and the §5 table are unchanged, and the guard and the suites stay green.
- `a828584` is a merge of Part A, and every check in section 3 holds on it.

### 6. Verdict

**APPROVED_WITH_CONCERNS.** 0 CRITICAL, 2 WARNING (CR-1, CR-2), 6 SUGGESTION (CR-3 to CR-8) and 2 INFO (CR-9, CR-10).
- Both branches do what the plan, the contracts and the TW-B1 stop ruling say. Every §3.9 check holds, and the Python floor and Bash 3.2 constraints hold.
- The carried items are ruled in section 2.
- CR-1 and CR-2 are small fixes; land each before T046/T047, or defer it by an explicit architect ruling.

`git status --short` of the main tree after this review:

```
?? .aod/revision-context.md
?? specs/391-isolated-auditable-operation/test-results/w3-reviews.md
```

`.aod/revision-context.md` was there before the review. This file is the review's only change to the working tree. The working notes are in the gitignored `.aod/results/`.

## T044 part 2: architect final checkpoint (2026-11-20)

| Item | Value |
|---|---|
| Task | T044 part 2 (`tasks.md`), after part 1; the last step of gate G3 (`agent-assignments.md` §4) |
| Reviewer | architect |
| Tips | Part A `183fb2f`; part-b `a828584` (the BX'''' merge; merge base `183fb2f`). Part 1 reviewed `b2385ca` and `f34e0ed`, and the delta to these tips is runbook prose and records |
| Inputs | Part 1 and its working notes; the architect's W3 rulings (W3-1 to W3-8, W3-3a) and the B1-stop ruling; `tw-b1-w2.md`, `w3-recheck.md`, `security-b1.md` (T042), `w3-sweeps.md` (T041), `w3-gated-suite.md`, `w2-live.md` and `security-a.md` §5; the PM's ruling on K2's refusal |
| Method | Read-only git in the main tree. Execution only in a fresh scratch clone of `183fb2f` and in scratch shell sandboxes. CR-1 was reproduced in the clone, and the fail-closed rule in section 1 was tried there: the guard and its `--self-test` stayed green, the guard's test module gave 154 passed, and each of the four planted shapes gave exit 2. CR-2's corrected line ran under bash 3.2.57 and zsh 5.9 against a root clone, a dirty clone, a linked worktree, a plain copy and a plain copy inside another repository. No pytest and no extractor ran in the main tree |
| Verdict | **CHANGES_REQUESTED.** The W3 list in sections 1 to 3 lands before T045 and T046. The architect's working notes give each change exactly. G3 closes on the conditions in section 6, and a change that matches its text needs no further architect review |

### 1. Rulings on the code-review findings

| ID | Ruling | Owner and change | Runnable proof |
|---|---|---|---|
| CR-1 | **Fix in W3 (Part A).** This is a gap in a privilege control. In the scratch clone, the guard stayed at exit 0 for four shapes: a `permissionMode` key after an indented `---` in a block scalar; the same key after a `...` line; an `allowed-tools: Bash` key hidden the same way in a command file; and a `---yaml` first line on the allow-listed document, over a full agent block. Until the fix lands, D1's key-set rule and ADR-049's "cannot ride along" consequence do not hold for a crafted change | SBE-W3A: in `split_frontmatter`, only a line that is exactly `---` closes the block. Any other line in the block whose stripped text is `---` or `...` is exit 2, and so is a first line that starts with `---` but is not `---`. The rule fails closed whatever delimiter rule Claude Code applies, as the duplicate-key rule does. No current agent, command or document trips it, on either tip or on `main`. `--self-test` and its five mutations stay as they are | SBE-TA: four cases in the guard module's exit-2 list, one per shape, in the same commit as the code |
| CR-2 | **Fix in W3 (part-b).** The line writes a wrong provenance value with no warning, in the feature whose purpose is that value, and a one-line fix keeps every constraint on the line | SBE-B2: the marker line, in all three copies, byte-identical and without `#`, runs `git describe` only when `git -C "$TACHI" rev-parse --show-cdup` prints nothing, as `install.sh` decides, and writes `unknown` otherwise. README `:157` then says when `unknown` is written. ADR-049 D10 stays true as written | SBE-TB: a nested-copy case for the manual loop, bash and zsh, in the same commit as the line; the README phrase quoted in the neighbouring docstring follows the new sentence |
| CR-3 | **Follow-up**, one issue with W3-L4 (section 7). The extractor fails closed: a non-zero exit, no `mmdc` call and no `report-data.typ` | T045 | none |
| CR-4 | **Fix the wording in W3 (part-b); the coverage is a follow-up.** The job runs only the Part B modules, so its comments say so. A Python 3.9 CI leg for Part A's guard and installed-script modules is a follow-up: X-5 covers them for 391, and a Part A module does not belong in a Part B job | SBE-TB: `tachi-pytest.yml` `:34`, `:337` and the step name say the Part B modules | CI parses the workflow; no module list changes |
| CR-5 | **Fix in W3 (part-b).** Code-economy §1: these refusals are the only guard for a `--version` tag older than the placeholder | SBE-TB: two cases, each from a source without the placeholder and without a git tree: a symlinked marker, and a directory at the marker path. Each gives exit 1 and its message, leaves a link target unchanged and writes nothing | the two cases |
| CR-6 | **Fix in W3 (Part A).** Feature 391 dropped the quotes that `main`'s Step 3a put around the PDF path | SBE-W3A: Steps 3a and 3d of `report-assembler.md` gain the sentence that Step 2c already has, "Quote a path that contains spaces." Only prose changes, with no fence and no frontmatter, so C6 and the write-confinement fence scan read the same fences | the guard and the write-confinement suite in the T043 re-run |
| CR-7 | **Fix in W3 (part-b)** | SBE-B2: the `/tachi.threat-model` "Bash it instructs" cell goes back to `python3`, and the §8.4 notes say that Step 2.6 runs `python3 scripts/stamp-tachi-version.py`, which replaces `{out}/threats.md` with a stamped copy through a temporary file beside it | the guard on part-b |
| CR-8 | **Fix in W3 (part-b)** | SBE-TB: drop the stale sentence at `test_threats_schema_contract.py:33-34`; the contract matches the script | none |
| CR-9 | **Fix in W3 (records, Part A)** | Orchestrator: `contracts/version-marker.md` drops the `:585` pointer and records CR-2's rule for the manual-loop line | none |
| CR-10 | **Follow-up** (section 7). Concur with T042 and part 1: the runbook's "Check first" bullet covers the by-hand build, and under the profile the sandbox binds each write to its real path | T045 | none |

### 2. Findings of this checkpoint

Part 1 reviewed each branch's own diff. These four come from reading Part A's text as part-b ships it, and from the S2b addendum to the W2 record.

| ID | Finding | Owner and change |
|---|---|---|
| A-1 | ADR-049 D8 calls the three extraction and population scripts "the three installed scripts that agents and commands run". On part-b, `/tachi.threat-model` also runs the stamp script at Step 2.6, so the count is wrong there. The stamp script imports only the standard library, so D8's guarantee itself holds | SBE-D (Part A): name the three scripts without a count. The new text names no Part B file, so T046 step (3) stays at zero |
| A-2 | Runbook §1 says "tachi's four installed scripts". Part-b installs five. What the sentence says about network libraries and child programs holds for all five | DEVOPS-R (Part A): "tachi's installed scripts". The runbook stays identical on both branches, as the B1-stop check requires |
| A-3 | Runbook §10 says "two agents ran command families outside their rows". The tracked record says all three Bash-capable agents did | DEVOPS-R: "all three Bash-capable agents", and "the infographic agent wrote helper scripts" |
| A-4 | Runbook §11's "What the agents did beyond their rows" still says the infographic agent "decoded images through heredocs and helper scripts", the reading that section 4 corrects, and it names two agents | DEVOPS-R: the bullet takes section 4's facts and the three-agent count |

### 3. The carried items

| Item | Ruling |
|---|---|
| W3-L4 | Follow-up, in one issue with CR-3 |
| W3-L6 | SEC-A's fallback rules stay in `security-a.md` §5.2. No run has measured them, and they leave `cmdline` and `fd` readable. DEVOPS-R adds one sentence to runbook §6 (Linux and WSL2), in the paragraph that lists the forbidden workarounds, which already carries its docs links: never remove a deny rule from the profile to make a step work, `Read(//proc/**)` among them, because on Linux it keeps Claude's Read tool away from the Claude Code process's environment (§3). If a step fails while the rule is in place, stop and report it as a tachi defect (§8). The measurement goes into the Linux validation follow-up that T045 already files, as an acceptance item: run a diagram render and a process substitution under the broad rule, and apply SEC-A's fallback only if one of them fails. That adds no new issue |
| The PM's optional §3 sentence | Fix in W3. DEVOPS-R appends the PM's text (`pm-w3-k2-391.md` §3.1) to the "No extra host for a single command" bullet, which already carries its docs link |
| O-1 | Dropped. `scope.md:16` says where the harness runs, and the data-handling bullet follows on the next line. O-3 is already applied (runbook `:505` at `183fb2f`), and O-2 stands as T041 recorded it |
| The AD-12 deviation | Accepted as recorded. Runbook §11's opening paragraph, `w2-live.md` §1 and `w3-recheck.md` say that Claude drove the sessions at the maintainer's instruction and that the maintainer directed the runs. T045 records it in `delivery.md`. No text change |
| X-7 and the extractor's `RuntimeError` | Concur with part 1, §2.1 and §2.2 |

### 4. The D7 sentence (W3-7)

**Confirmed.** ADR-049 D7 at Part A says that in the live validation the agent decoded each image with a `python3` heredoc, as the instructions say, and built the specifications and the Gemini request files with two helper scripts, so the request files did not come from the Write tool. That corrects the W3-7 text, which put the heredocs and the helper scripts together in the decode. The instructions name `python3` and the standard library, and D7's own previous sentence says so, so "as the instructions say" reads correctly in place.

One records addition. The tracked `w2-live.md` says that the agent wrote two helper scripts and simplified specs. It does not say what the scripts produced or how the images were decoded. The orchestrator adds a dated, structure-only line to the S2b addendum there, so the ADR's statement rests on a tracked record. If the structure census cannot show which tool wrote the request files, D7 drops that clause instead, and A-4's bullet says only that the agent wrote two helper scripts.

### 5. The W3 list

| Item | Result |
|---|---|
| X-4: ADR-049 D3, D5, D7 and Mitigation bullet 3 | Landed in `d57dee6`. D5 and Mitigation bullet 3 read as ruled. D3 carries W3-8's "declare … they do not bound a run". D7 is as in section 4 |
| W3-8: §8.1, runbook §5 and §10 | §8.1 (`36f262b`) and runbook §5 read as ruled. §8.1 names two agents as examples, not as a count, and stays as it is. §10 takes A-3 |
| AR-21, AR-21a and the re-check | The block is the re-checked one at `b2f5e54`, `b71a0d7`, `183fb2f` and `a828584`: 3,156 bytes, SHA-256 `36df2a9a…`, 18 deny rules. The contract, `data-model.md` and `w1-audit-rulings.md` carry AR-21 and AR-21a, and the contract test pins all ten names |
| The header's "Last validated" line | Matches `w3-recheck.md`: the profile that ran, with its full SHA-256; "adds ten deny rules"; and a key-less re-check covering startup, the rule list, the tool inventory, a refused isolated Agent call, the sandbox probes and one `/tachi.threat-model` run. §11 also lists the `.env` probe, which the header leaves out. That understates, and needs no change |
| F1's macOS scoping and the by-hand build | The header, §1, §6, the §9 row "Pre-engagement validation (2)" and §11 scope `/tachi.security-report` out on macOS for runs with diagrams. The by-hand build carries T042's "Check first" bullet and the wider "What it gives up" (W3-H1), the `&&` chain (W3-L1) and the Linux stop (W3-L5) |
| F2 and F7 | §3's "Shell startup files and the Keychain (macOS)" block, the two appended sentences and §4's "Environment names" row are in place. The messaging-variable sentence states only the docs' reach rule and says that their use was not tested. §6 and §9 carry the inbox sockets |
| ADR-019's Note against what ships | One blob on both tips (`506cc3e0`): Part A's Note, in FR-015's "otherwise" wording ("recorded in Claude Code's transcripts, not in the agent files"). B1 does not ship, so no manifest wording ships either |
| The B1 stop commits | Re-run at the current tips: 0 B1 files on part-b; 17 paths; the runbook and ADR-019 3-dot diff empty; 0 B1 tokens on the 3-dot diff and on `main...` each tip; T046 step (3)'s grep on `main...` Part A gives 0 |

### 6. Gate G3

- **T042:** cleared. W3-H1 and W3-M1 are fixed in the runbook (`c535aa9`), together with W3-L1, W3-L2, W3-L3 and W3-L5. W3-L4 is a follow-up, and section 3 rules W3-L6.
- **T043:** PASS at `b71a0d7` and `f34e0ed`. The delta to `183fb2f` and `a828584` changes runbook prose and records only, and only three suites read the runbook: the profile contract, the guard and manifest completeness. The orchestrator ran them at `183fb2f` (373 passed, guard pass), and `a828584` holds the same runbook blob, with part-b's own files unchanged since `f34e0ed`. For that delta alone, those runs suffice. The W3 list changes code on both tips, though, so G3's own rule applies: T043 re-runs in full on both final tips, after BX''''', recorded as a dated addendum to `w3-gated-suite.md` and `wave-03/results.json`. The pass rule is unchanged.
- **ADR-019:** matches what ships.
- **Before the push:** the orchestrator re-runs the B1-stop §3.9 checks on part-b, which still give 17 paths, because every part-b fix is in a listed file. It also re-runs T046 step (3)'s grep on Part A, which must still give 0.
- **G3 closes** when the list has landed as specified, CI is green on #392 and #396 at the final tips, and the T043 re-run passes. The orchestrator records the fix commits and the re-run result in one dated line under this section. A change that departs from its text comes back to the architect.

**Order.**
1. On Part A, one push: CR-1's code and cases in one commit, CR-6, A-1, DEVOPS-R's runbook commit, and the records.
2. In the part-b worktree: CR-2's line with its case in one commit, then CR-7 and SBE-TB's other changes.
3. DEVOPS-E merges Part A into part-b (BX'''''). No Part A change touches a line that part-b changes, so the merge is clean. Then one push.
4. The tester re-runs T043.

About 0.2 d inside W3. Of that, about 0.06 d is Part B agent time for the TW-B2 log, below its 0.5 d re-invoke line.

### 7. Follow-ups for T045

Three new issues:
1. CR-3 and W3-L4: when `TACHI_MMDC_PUPPETEER_CONFIG` is set, `extract-report-data.py` checks it once at startup in both modes, prints one line and exits 2, as the build-directory errors do; its exit-code docstring and epilog name the case.
2. CR-10 (the code half of T042's W3-H1): in build mode, the extractor refuses a symlinked `{target_dir}/report-config.typ` and symlinks under `{out}`.
3. CR-4, the coverage half: a Python 3.9 CI leg for Part A's guard and installed-script modules (X-5's 12), on `main`, or in `py39-floor` once Part B merges.

W3-L6's Linux measurement joins the Linux validation follow-up that T045 already files, so it adds no new issue.

### 8. Verdict

**CHANGES_REQUESTED.**
- **To W3:** CR-1, CR-2, CR-4 (wording), CR-5 to CR-9, A-1 to A-4, the W3-L6 sentence, the PM's sentence and the D7 records line.
- **Follow-ups:** three, for CR-3 with W3-L4, CR-10 and CR-4's coverage half.
- **Dropped:** O-1.
- **D7:** confirmed.

Nothing found here changes the profile block, the §5 table or a write location.

`git status --short` of the main tree after this checkpoint:

```
?? .aod/revision-context.md
?? specs/391-isolated-auditable-operation/test-results/w3-reviews.md
```

`.aod/revision-context.md` was there before the review. This file is still the only change to the working tree, now with this section appended. The architect's working notes are in the gitignored `.aod/results/`.
