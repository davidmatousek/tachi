# P0 architect checkpoint (T040): end of W1

**STATUS: APPROVED_WITH_CONCERNS.** Of the 10 checks, 7 pass and 3 pass with concerns. None fails.

- **W2 entry:** approved. No finding blocks the live session.
- **Part B past W1:** approved.
- **Before BX′ and H1:** the four fixes in section 4.1 land: two contract folds (records only), three corrections to the T048 text that landed during this review, and T037's manual-loop write case.
- **The Part B PR:** clears once the W1 fixes land, the Part B items in section 4.2 land before T043 and T044, and the PR's own gates pass (T043, T044, T051 if B1 ships, and #364 for T038b).

| Item | Value |
|---|---|
| Gate | T040 / P0 (`tasks.md:168`; `agent-assignments.md:302`) |
| Reviewer | `architect` |
| Date | 2026-11-19 |
| Read at | Part A at `2c5fe08` (code tip `8273669`, followed by the G1 record). Part B at BX `8d390ce` (part-b with Part A merged in). T048's W1 part landed on part-b during the review (`7838f48` to `77bbec8`, five docs-only commits). It was read as well, and section 2.10 rules on it. |
| Method | Read-only on both branches: `git log`, `git diff` and `git show`. Two things ran, both in scratch clones of `2c5fe08` and `8d390ce` and nowhere else: the guard (`scripts/check-agent-privileges.py`, plain and `--self-test`), and one run of Part A's installed-script test modules under Python 3.9.6. No test, extractor or script ran in the main tree. Both clones were clean afterwards. |
| Precedence | As at P0-B0, section 5 governs where it differs from `contracts/cli-contracts.md`, `contracts/run-manifest.md`, `contracts/version-marker.md`, `data-model.md` or `plan.md` AD-6. This holds until F-1 and F-2 fold it into those files. |

## 1. The checklist

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Audited write set (T004, `contracts/audit-write-set.md`) against what shipped (AR-1 to AR-3, AR-14) | **PASS** | **AR-1:** `image_dir` on the three extractor functions (`scripts/extract-report-data.py:1038`, `:1192`, `:1831`, and the chain renderer at `:1631`). Deletion is confined by `_lies_in` (`:1777`) inside `_maybe_delete_mislabeled` (`:1789`). Build mode sets `image_dir` to the build directory's grandparent (`:2771`); legacy mode passes none (`:2775`). **AR-2:** `.claude/agents/tachi/risk-scorer.md:16`, `:398`, `:442`, `:456`, `:538`, and `.claude/commands/tachi.risk-score.md:93-94`, `:104-112`. Frontmatter is unchanged (C2 to C4 green). **AR-3 and AR-9:** `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md:266`, `:299`; `.claude/agents/tachi/threat-infographic.md:60`, `:164`, `:170-172`. **AR-14:** the two lines precede `sys.path.insert` in all three installed entry scripts (`extract-report-data.py:64-66`, `extract-infographic-data.py:27-29`, `populate-affected-assets.py:59-61`). **Tests:** T015's cases and AR-14's three cases (`tests/scripts/test_write_confinement.py:457-778`, `:833`). The static fence scan covers both skill references (`:881-887`). **Tables:** §8.5 (`docs/standards/CLAUDE_PERMISSIONS.md:396-418`) and the runbook's §5 table (`docs/guides/ISOLATED_OPERATION_TACHI.md:323-345`) are identical row for row (21 rows), and C7 passes on both tips |
| 2 | §8's placement and slug (T023) | **PASS** | **Placement:** `## 8. Agent and command privilege matrix` (`CLAUDE_PERMISSIONS.md:299`) sits after §7.5 and before `## Cross-references` (`:438`). Every §1 to §7 heading is byte-identical to `main`; only line numbers moved, by the 7-line header note. **Slug:** `8-agent-and-command-privilege-matrix`, pinned at `tests/scripts/test_isolated_profile_contract.py:72` and `:1087`. **Runbook link:** `ISOLATED_OPERATION_TACHI.md:471` carries the `x-release-please-version` marker, and the runbook is in `release-please-config.json` `extra-files`. **Shape:** the table shapes match `contracts/matrix-section.md`, and the Dispatch paragraph (AR-5) is at `:317` |
| 3 | AD-13's tool coverage after T012 (T022) | **PASS** | **Declared tools:** {Read, Glob, Grep, Bash, Write} (`.claude/agents/tachi/report-assembler.md:4-9`). **Steps:** Read for the skill references (`:56-67`) and artifact checks; Bash for `test` (`:124-126`), `python3` (`:157-162`, `:217-219`) and `typst` (`:193-195`). No step names any other tool. **Dispatch:** `.claude/commands/tachi.security-report.md:163` dispatches `tachi-report-assembler`. Observation in 2.3 |
| 4 | RC-P1's dispatch definition applied in T002, before T002 ran | **PASS** | **Definition:** RC-P1 (`.aod/results/architect-plan-391.md:49-54`, carried into `plan.md:175` and `:231`) was signed in `85df048` on 2026-11-16. **Run:** the spike ran on 2026-11-18 (`w0-spike.md:11`), and its record landed in `864121b` on 2026-11-19. **Checks:** check (f) passed at depths 1 to 3, and `Agent` blocks were found inside subagent transcripts (`w0-spike.md:28-36`). This confirms P0-B0 check 1. **Carried:** P0B0-4(i)'s structure addendum was never appended, so T051 records the same facts (section 6) |
| 5 | The extractor-owned build directory (T012/T014): the path-shape guard, `--remove-build-dir`, and no `rm` in recipes | **PASS with concern** | **Guard:** `extract-report-data.py:2466-2522`. It runs again right before deletion (`:2525-2550`) and on removal (`:2553-2567`). **Modes:** `:2680-2722`. **Recipes:** `report-assembler.md:157-162`, `:193-195`, `:217-219`, and `typst-artifacts.md:118-125`. **No `rm`:** no `rm`, `rmdir` or `unlink` appears in any tachi agent, command, skill or template, or in the runbook (repository search: 0 hits). **Tests:** `test_write_confinement.py:516`, `:588`, `:602`. **Concern (2.5):** the AD-9 variable check (`:947-972`) has no committed test |
| 6 | C6 green from day one on the live tree (T025/T026), including AR-4 | **PASS** | **Guard:** C1 to C7 PASS on both tips, and `--self-test` exits 0 on Part A (M1 to M5 detected). **Families:** the found families equal the day-one sets exactly: orchestrator {`python3`}; report-assembler {`python3`, `test`, `typst`}; threat-infographic {`[`, `echo`, `python3`, `test`}. AR-4's line (`threat-infographic.md:350`) is unedited. **Tests:** the reserved-word skip on the infographic agent (`tests/scripts/test_agent_privilege_guard.py:1017`), the bracket as the family (`:1049-1054`), a command after `then` still caught (`:981`), and the live tree green (`:508-531`). **CI:** green on `8273669` (`tachi-permissions-verify.yml:130-140` runs `--self-test`). **AR-4's "exactly {`[`, `echo`}":** met in substance. The three cases together go red if a reserved word becomes a family or if the word after `then` is dropped |
| 7 | Step 2.6's placement and the one-commit rule (T039) | **PASS** | **Placement:** `## Step 2.6` (`.claude/commands/tachi.threat-model.md:195` on part-b) comes after Step 2.5's sequencing note (`:185-193`) and before `## Step 3` (`:224`). **Body:** one `bash` fence holding exactly the command (`:207`), and the failure clause per P0B0-9(c) (`:217-222`). **`orchestrator.md`:** untouched (an empty diff from `2c5fe08` to `8d390ce`). **One commit:** `f76e238` holds the script, Step 2.6 and the `INSTALL_MANIFEST.md` whitelist line, with P0B0-7's row, counts and failure sentence (`INSTALL_MANIFEST.md:15`, `:65`, `:74`, `:78`, `:136`, reviewed by hand). The contract test is T039's separate SBE-TB commit (`1793c21`), as the task assigns it |
| 8 | The re-install test (T037; P0B0-10) | **PASS** | **Re-install case:** `tests/scripts/test_tachi_version_marker.py:337-355`. A writing install runs first. The precondition is asserted: the marker holds a describe value, not the placeholder. The skipping install is the loop's copy step for `templates/tachi/`, built directly and not read from the README (`:212-221`, P0B0-10 (a)). The result reads `unknown`. **Case 3:** `:362-370`. **Pending:** the README manual-loop write case was to land after T048 (`:506`). T048's marker line has landed (`77bbec8`), so F-4 |
| 9 | The B1 manifest contract (T032, after the T034 fixes) and the B2 contract (T038a) | **PASS with concern** | **B1 rulings:** P0B0-1 to P0B0-11 are applied and tested (`tests/scripts/test_archive_run_transcripts.py:1205-1409`, `:2023-2065`; the stdlib check at `:3124`). **T034 fixes:** H-1 to L-8 are fixed, with one regression group per finding (`:3219-3991`); L-3 is fixed in part (section 3, row 2). **B1 code:** the schema example obeys turns = histogram + synthetic turns (`schemas/run-manifest.yaml:423`). `requestedModel` stays out of v1 behind its marker (`scripts/archive-run-transcripts.py:1352`). `tachi_version` comes from the marker (`:1393`). **B2:** `schemas/output.yaml` is at 1.5, with the six keys, `tachi_version` and the consumer guidance, and the reference, template and SARIF specification agree (`test_threats_schema_contract.py`). CF-21 measured churn, so the flag is not built (`t038a-measurement.md`). `semanticVersion` comes from the input's `schema_version`, with a fallback (`scripts/generate-threats-sarif.py:47-59`, `:584`). **Concerns (2.9):** contracts not folded; the generator's sourcing is untested |
| 10 | T029's ADR-049 text (Part A) | **PASS with concern** | **Size:** no trim (2.10). **Decided items:** every item the Part A text states as decided has landed, except three statements that rest on T020, which has not run (`docs/architecture/02_ADRs/ADR-049-privilege-contract-and-write-confinement.md:82`, `:104`, `:182`). **Part B text:** T048's text, which landed during this review, needs three corrections (2.10, F-3) |

## 2. Notes on the checks

### 2.1 Write set

The relocation leaves no write outside `{out}`, `$TMPDIR` and the `/tachi.architecture` carve-out:

- W25 to W27 are gone.
- W14 to W16 are pinned.
- W17 to W20 now land under `{out}`.
- W12 and W13 follow `--output-dir`.

The runbook therefore states the confinement sentence without a qualifier, together with AR-8's precondition (`ISOLATED_OPERATION_TACHI.md:304-312`).

AR-2's live listing (`/tachi.risk-score` and `/tachi.security-report` with `--output-dir <alt>`) is T020's and cannot be checked before W2.

One sentence in the extractor's module docstring (`extract-report-data.py:22-28`) is hard to read. It lists the build-mode writes after "only reads DIR:", so they read as reads. The `--help` epilog (`:2601-2609`) says it correctly. The fix is optional (4.3).

### 2.3 Report-assembler tools

Since T012, `tachi-report-assembler` runs every step through Bash: the extractor copies the config, writes `report-data.typ` and removes the build directory. No step uses the `Write` tool any more. That is coverage with one unused tool, not a gap, and AD-13 holds.

Dropping `Write` would narrow the agent to sandboxed writes, which is the least-privilege direction. It is a frontmatter change, though, and that touches the §8 row, C2 and T028's install assertion. 391 changed only the dispatch body (AD-13), so this is a follow-up (4.4).

### 2.5 The AD-9 variable

`_mmdc_puppeteer_args` (`extract-report-data.py:947-972`) validates `TACHI_MMDC_PUPPETEER_CONFIG` before any render starts. It accepts an absolute path to a regular file, and anything else stops the run. Its output becomes part of a child process's argv. The checks were run only in a scratch harness during T014 (23 checks) and were never committed. The plan's test table has no row for them, and the live Linux run in W2 would be the only evidence. Input validation at a trust boundary ships with a runnable check (`.claude/rules/code-economy.md` §1), so X-1 adds one to a module that is already gated.

### 2.9 B1 and B2

**B1.** The archiver's behaviour matches the contracts as amended by P0-B0 and T034. The contract files themselves still carry the pre-review text:

- the `<dest>/.probe` check;
- exit codes and a refusal list without H-1 to L-6;
- `turns: 41` in the example;
- the five-word name list;
- the "Readers" line of the version marker.

F-1 and F-2 fold in section 5's text. For T048, the archiver text followed the shipped script rather than the contracts (`.aod/results/sbe-d-t048-w1.md`, judgment call 8). The fold is still due: T042, T043, T044 and T051 read the contracts in W3, from a new session.

**B2.** The PM L-5 premise ("tracked twins reproduce unchanged") holds only in part (`t038a-measurement.md`):

- `examples/agentic-app/sample-report/threats.sarif` says 1.7, for an input that declares 1.4. A regeneration now writes 1.4.
- `examples/consumer-agent-app/sample-report/threats.sarif` keeps 1.8 after T038b corrects its input to 1.4.

No test compares either file, and neither moves in 391. Both go on the L-5 follow-up list (section 3, row 7).

The generator's input-first sourcing is new logic with no test (X-6). The header comment of `schemas/output.yaml` (`:12-14`) says the generator takes its version from that file; it does so only as the fallback (X-9).

### 2.10 ADR-049

**Size.** The Part A text is 25.9 KB, in the range of ADR-041 (21 KB) and ADR-042 (26.5 KB). Each of its nine sections is a decision with its rationale. The facts it repeats from §8.1, §8.6 and the runbook were checked against those files and agree. Trimming it now would buy a re-review and a new wording sweep for no change in content. **Ruling: no trim.**

After T048 the file is 36.2 KB on part-b, still well inside the repository's ADR range. The same ruling holds.

**Decided and landed:**

- D1: the guard, its CI step, the red cases in `tachi-pytest.yml`, and T028's install assertion in the install-fidelity workflow.
- D2 to D4: the C1 rules and §8.1.
- D5 and D6: T012, T014 and runbook §5.
- D7: T013.
- D8: AR-14.
- D9: T022.
- Known limitations 1 to 5, each checked. For example, no workflow runs `test_coverage_attestation.py`, and the runbook states the link lag beside the link.

**Resting on T020.** Three statements depend on the live run:

- D5's "a sandboxed run needs no `allowWrite` entry" (`:82`);
- D7's decode with `python3` (`:104`);
- the Mitigation bullet that describes the maintainer's live listing in the present tense (`:182`).

They stay as written for now. X-4 reconciles them with the W2 record at T021, and T044 checks the result.

**T048's text (part-b, `7838f48` to `77bbec8`).** Three corrections are needed (F-3):

1. **A false clause.** D11's last bullet says the generator's sourcing means "tracked SARIF files reproduce unchanged" (`:138` on part-b). That is false for `agentic-app/sample-report` (2.9).
2. **P0B0-1's sentence is missing.** P0B0-1 asked T048 to say that the manifest lists every subagent instance, tachi or not, and that a non-tachi instance has `pinned_model: null`. Neither the runbook (`ISOLATED_OPERATION_TACHI.md:418` on part-b) nor ADR-049 D10 (`:123`) says so. An auditor who sees `pinned_model: null` on the `general-purpose` instances needs that sentence.
3. **An incomplete refusal list.** D10's list (`:121`) leaves out the refusal of a destination that is itself a symbolic link (T034 L-2). The runbook includes it (`:411`).

The rest of T048's W1 part matches the shipped code and the rulings:

- `-I -B`;
- archiving after the session, under the same wrapper;
- the unrecognized tree types;
- the sensitivity paragraph;
- the D-1 wording, which never says the pin was honored;
- Known limitations 6 and 7;
- the byte-identical marker lines.

## 3. Deferred items: rulings

| # | Item | Ruling | Owner | Branch | Blocks W2 |
|---|---|---|---|---|---|
| 1a | T039 `--check` exit codes (1 = drift, 2 = error), the reverse of `cli-contracts.md:27` | **Accept the code; amend the contract (F-2).** 0 / 1 / 2 is the house convention of the guard and the archiver (1 = finding, 2 = infrastructure). Step 2.6 reacts to any non-zero exit | SBE-B2 | Part A (records) | No |
| 1b | T039 writes the value quoted | **Accept.** The contract already writes `tachi_version: "<value>"`, so no contract change is needed. The marker file stays unquoted, `tachi_version: <value>` | — | — | No |
| 1c | T039 keeps `--json` | **Accept.** The contract and the house conventions list it | — | — | No |
| 1d | The marker regex rejects `/` (the same rule as the archiver), while `install.sh` accepts `/` | **Align the writer to the readers (X-7).** Drop `/` from the installer's filter (`scripts/install.sh:661`), so a tag the readers would read as `unknown` is written as `unknown`. State the grammar in `version-marker.md` (F-2). No practical effect today: release tags are `vX.Y.Z`, and the readers fail safe | SBE-B2 (+ SBE-TB, one case) | part-b | No |
| 2 | B1 deferral L-3: a token rule on recorded path strings (`transcripts[].path`, `artifacts[].path`) | **Accept the deferral. No token rule in v1, and no follow-up.** The paths are relative, symbolic links are never followed (`archive-run-transcripts.py:1454-1472`), each string is JSON-escaped and passes the final scan with encoded forms, and the stem rule now covers `--latest`. A sentinel or re-encoding would break the path-to-hash mapping an auditor checks against the archive | — | — | No |
| 3 | B1 deferral M-1: an optional cap on long host labels | **Accept the deferral. No cap.** The encoded-form scan closes the channel T034 found. A cap would drop real labels. T048 has already stated the residual (the manifest's structure, not the scan, keeps a secret out) | — | — | No |
| 4 | P0B0-1(5) against P0B0-4(f): `permission_modes_seen` from every transcript or from the main one only | **No disagreement in substance; P0B0-1(5) governs.** The field holds the distinct modes of the `permission-mode` entries in every archived transcript. P0B0-4(f) recorded where those entries were observed (only main transcripts carry them on 2.1.328), and it still governs the empty case (`[]`, stated in the `--json` summary). The code (`archive-run-transcripts.py:1062-1073`) and the tests (`test_archive_run_transcripts.py:1409-1421`, `:2882-2895`) are right. Reading every transcript is also the better audit choice: a subagent that ran in another mode would show. F-1 folds the wording | SBE-B1 | Part A (records) | No |
| 5 | The archiver's name list: `AUTH` also matches `GIT_AUTHOR_*` | **W3, low (X-8).** The result fails closed: a false refusal at worst, never a leak. A value fragment of 8 or more characters from a name in `GIT_AUTHOR_NAME` that also appears in a manifest string would refuse a clean run, and a refusal costs a new `--dest` (P0B0-5). Exclude `GIT_AUTHOR_*`, `GIT_COMMITTER_*` and `XAUTHORITY` by name, as `PWD` and `SSH_AUTH_SOCK` already are (`:217`), and add one case | SBE-B1 (+ SBE-TB) | part-b | No |
| 6 | No test for `generate-threats-sarif.py`'s `semanticVersion` sourcing | **W3 (X-6).** Add three cases to `test_threats_schema_contract.py`: an input declaring 1.4 gives 1.4, an input with no `schema_version` gives `schemas/output.yaml`'s value, and the fenced-frontmatter form. No new workflow path is needed (the generator is already in `&hardening_paths`) | SBE-TB | part-b | No |
| 7 | SARIF twin: `examples/agentic-app/sample-report` carries 1.7, but its input declares 1.4 | **Yes, add it to the L-5 follow-up**, together with the consumer-agent-app twin's 1.8, as one follow-up. Suggested title: "Correct the tracked SARIF twins whose semanticVersion disagrees with their input's schema_version". It stays out of 391, which moves no tracked SARIF baseline. The ADR sentence that says otherwise is F-3 | PM (T045) | Part A (records) | No |
| 8 | `generate-threats-sarif.py` imports the private `_extract_frontmatter_text` | **Accept. No public wrapper.** It is one caller, in a maintainer tool that is not installed (`INSTALL_MANIFEST.md` lists six scripts, and this is not one of them). The import carries a comment that says why. A public alias would add API to an installed shared module for no adopter. Revisit when a third caller appears (rule of three) | — | — | No |
| 9 | Guard (low): `--self-test` exits 2 instead of 1 when a planted unlisted agent sorts before `agent-autonomy.md`, or when the allow-listed document already has frontmatter | **W3 (X-2).** CI is red either way and every C1 finding is listed, so this is a diagnosis defect, not an escape. Apply the fix in `.aod/results/sbe-ta-t026.md` §4: pick M1's target only among agents with a row, and count a mutation whose finding is already red in the baseline as "already red". Add the `Evil.md` and planted-document trees to `test_self_test_stays_valid_on_a_drifted_tree` (`test_agent_privilege_guard.py:1136`) | SBE-E (+ SBE-TA) | Part A | No |
| 10 | T023 extras: Category 1's "no network egress" line, Category 4's wildcard sentence, §7.2's "adopters lose the baseline" | **Accept, and send them to the PM as information only.** Each corrects a claim in the same document that the five FR-003 corrections make false, or that is false on its face: the `gh` rules call the GitHub API; the wildcard sentence contradicted the corrected §7.4; adopters receive no baseline. FR-003's five corrections are a minimum. No requirement or PRD wording changes. T041's FR-003 check lists all eight edits, and T045 names them in `delivery.md` | PM | Part A | No |
| 11 | `py39-floor` runs on `ubuntu-24.04`, not `ubuntu-latest` | **Ratify.** The rule's intent, a Python 3.9 run on Linux in CI, holds, and `ubuntu-latest` (26.04) has no 3.9 build. The job documents its expiry and its upgrade path, a container or uv, and never a return to `ubuntu-latest` (`.github/workflows/tachi-pytest.yml:322` and the comment above it). Record it as a deviation in `delivery.md` | DEVOPS-E | part-b | No |
| 12 | The zsh SC-A4 path skips in CI and is covered locally on macOS only | **Accept for 391.** It is the same CI posture as F-373's existing zsh loop case (`test_install_manifest_completeness.py:732-734`). T043 records the zsh cases as passed, not skipped, on both tips (X-5). CI coverage of zsh, on a macOS runner or with zsh installed on the Ubuntu job, is an optional follow-up | PM (T045, optional) | — | No |
| 13 | Stale docs: four lines describe `report-posture` as posture-only (`docs/devops/CI_CD_GUIDE.md:629`, `docs/architecture/00_Tech_Stack/README.md:88` and `:287`, `docs/devops/environment-variables.md:183`) | **W3 (X-3).** Each line also names `test_write_confinement.py`. `environment-variables.md:183` names both readers of `TACHI_REQUIRE_TYPST` | DEVOPS-E | Part A | No |
| 14 | Stale count: `tasks.md:171` (T043) says "18 modules" | **Records fix.** Amend it to "21 on Part A, 24 on part-b" in the commit that marks T040 complete. T043 runs the list as it stands at each tip | DEVOPS-E (records) | Part A (records) | No |

## 4. Fixes

### 4.1 Must fix in W1 (before BX′ and H1)

| ID | Fix | Owner | Branch |
|---|---|---|---|
| F-1 | **B1 contract fold.** One records commit applies section 5.1 to `contracts/cli-contracts.md` (archiver paragraph), `contracts/run-manifest.md`, `data-model.md` (RunManifest and archive states) and an amendment note on `plan.md` AD-6 | SBE-B1 | Part A |
| F-2 | **B2 contract fold.** One records commit applies section 5.2 to `contracts/cli-contracts.md` (stamp paragraph), `contracts/version-marker.md` and `data-model.md` (VersionMarker) | SBE-B2 | Part A |
| F-3 | **T048 corrections**, one commit per file, as T048 requires: ADR-049 D11's SARIF clause and D10's refusal list and `pinned_model: null` sentence; the same sentence in runbook §7 (exact text in 5.3) | SBE-D | part-b |
| F-4 | **T037's README manual-loop write case**, now that T048's marker line has landed (`77bbec8`). The case extracts the README block, runs it under bash and `zsh -f -i` against a tagged local source, and asserts the describe value; the brief is in `.aod/results/sbe-d-t048-w1.md`, "T037's README manual-loop case". The module is already wired | SBE-TB | part-b |

BX′ then merges the Part A records (F-1, F-2) into part-b. None of the four touches code that W2 runs.

### 4.2 W3 (before T043 and T044)

| ID | Fix | Owner | Branch |
|---|---|---|---|
| X-1 | A committed test of `TACHI_MMDC_PUPPETEER_CONFIG`, in `test_write_confinement.py`, which already has the stub `mmdc`. Cases: unset gives no `-p`; an absolute regular file gives `-p <path>` at both call sites; empty, relative, missing and directory values exit non-zero, name the variable and start no render. No wiring change | SBE-TA | Part A |
| X-2 | The guard's `--self-test` classification, and the two drifted-tree cases (row 9) | SBE-E, SBE-TA | Part A |
| X-3 | The four stale `report-posture` lines (row 13) | DEVOPS-E | Part A |
| X-4 | At T021, check ADR-049 D5's last sentence, D7's decode and Mitigation bullet 3 against the W2 record. If T020 is honest-stopped, Mitigation bullet 3 says the live validation has not run, and the runbook header keeps "not yet validated". T044 checks the result | SBE-D | Part A |
| X-5 | T043 runs Part A's installed-script modules under Python 3.9 in its scratch clone. Part A has no 3.9 CI leg, and the split path ships the extractor's AR-1 changes without one. This checkpoint's run is the baseline: 12 modules, 667 passed. T043 also records the zsh manual-loop cases as passed | tester (T043) | both |
| X-6 | Tests for the generator's `semanticVersion` sourcing (row 6) | SBE-TB | part-b |
| X-7 | Align the installer's marker filter with the readers (row 1d) | SBE-B2, SBE-TB | part-b |
| X-8 | Exclude the git identity names and `XAUTHORITY` from the secret-name scan (row 5) | SBE-B1, SBE-TB | part-b |
| X-9 | `schemas/output.yaml:12-14`: say that the generator reads the input's `schema_version` first and falls back to this file | SBE-B2 | part-b |

### 4.3 Optional (low; T044 may take or drop them)

- The extractor's docstring sentence (2.1). SBE-D, Part A.
- Runbook §5's opening line on part-b: "tachi writes only…" could become "A tachi run writes only…". Runbook §7 (`:407` on part-b) and ADR-049 D10 already scope the archiver out of §5, so this only adds a cross-reference. SBE-D, part-b.
- §8.4: the `/tachi.threat-model` "Bash it instructs" cell now holds a family (`python3`) and a full invocation (`python3 scripts/stamp-tachi-version.py`). `contracts/matrix-section.md` asked for the stamp to be named, and the guard does not read the column, so the cell can stay as it is.
- The part-b ADR-019 Note: "is evidenced by the run manifest" holds when the operator archives the run. "Can be evidenced" is more exact. T044 checks the ADR-019 wording anyway.

### 4.4 Follow-ups for `delivery.md` (T045, PM)

1. The SARIF twins (row 7).
2. Drop `Write` from `tachi-report-assembler`. No step has used it since 391 (2.3); the change needs a §8 row, C2 and T028 edit.
3. Optionally, zsh install-loop coverage in CI (row 12).
4. After Part B reaches `main`, add the archiver and the stamp to `REQUIRED_SCRIPT_NAMES` (P0B0-8).
5. Manifest v2 with `requested_model_histogram` (P0B0-3(d)).
6. The existing list stands:
   - the guard on skill frontmatter;
   - the guard on command dispatch targets;
   - bounding what `Agent` can start;
   - the pre-existing AD-13 and AR-2 defects.

## 5. Fold text

Each entry gives the file, the text it replaces, and the text that replaces it. Line numbers are at `2c5fe08`.

### 5.1 B1 (F-1)

1. **`contracts/cli-contracts.md:16`.** Show the invocation as `python3 -I -B scripts/archive-run-transcripts.py (--session SESSION_ID | --latest) …`, and add: "A plain `python3` start re-executes itself under `-I -B` (T034 H-3)."
2. **`contracts/cli-contracts.md:20`.** Replace the sentence that starts "Refusals (exit 1, reason on stderr):" and ends "…resolving into a work tree." with:

   > Refusals (exit 1, reason on stderr):
   > - a destination inside a git work tree, unless git ignores every path the run writes there. The paths are each copied source file, `run-manifest.json` and `.run-manifest.json.tmp`, asked as real paths in one batched `git check-ignore --stdin -z -n -v` from the toplevel, and any other outcome refuses. The repository named by the operator's `GIT_DIR` or `GIT_WORK_TREE` is asked too;
   > - a non-empty destination, unless it is a finished archive of the same session: `run-manifest.json` present and parsed, with `session_id` and `transcripts[]` (path, bytes, sha256) equal to the source, gives exit 0, a no-op. Hash-equal transcripts without the manifest give exit 1, "incomplete archive" (P0B0-5);
   > - a destination that is a symbolic link, or a symbolic link on its path that resolves into a work tree;
   > - a destination under `<config>/projects` (elsewhere under `<config>` it is accepted with a warning);
   > - a live session (any file of the session tree changed within the window) without `--allow-live`.
   >
   > Every git call is `git -c core.fsmonitor=false …` with an allowlisted environment (T034 H-2). The archive's own `.gitignore` (`*`) is written first. Mercurial, Subversion and Jujutsu work trees are not recognized. `--latest` skips stems that fail the session-id pattern. Parse failures (exit 1, no manifest) also include a line nested too deeply, a non-ASCII `version` and a timestamp out of range once its offset is applied. The run prints how many secret-named values the final scan compared (`secret_scan` in `--json`), and warns when the count is zero.
3. **`contracts/run-manifest.md:13`.** In the example's `main` object, `"turns": 41` becomes `"turns": 42` (P0B0-4(d)).
4. **`contracts/run-manifest.md:33`.** Append:

   > **Turns** (P0B0-4(d)): a turn is one model response, the non-synthetic assistant lines that share a `message.id` (a line without one is its own turn). In every object, `turns` equals the histogram total plus `synthetic_turns`. A group whose lines disagree on `message.model` fails the run.
   >
   > **Instances** (P0B0-1): `subagents[]` lists every subagent instance, tachi or not, and `pinned_model` is `null` for any type the installed roster lacks. An `Agent` or `Task` call that names a non-tachi type is not a dispatch.
   >
   > **Dispatch states** and fail-closed cases follow P0B0-2 (a) to (g).
   >
   > **Unknown entry types and keys** are counted in the `--json` and stderr summaries, not in the manifest (P0B0-4(e)).
   >
   > **`permission_modes_seen`** holds the distinct values of the `permission-mode` entries in every archived transcript. On Claude Code 2.1.328 only the main transcript carries them. The field is `[]` when there are none, and the `--json` summary says so.
   >
   > **`tachi_version`** is read from `templates/tachi/VERSION` under `--project-dir`, with the stamp's rule; absent or malformed reads `unknown` (P0B0-6).
   >
   > **The final scan** follows `schemas/run-manifest.yaml` (`redaction.final_scan`).
5. **`data-model.md:34`.** Replace "final secret scan (known key formats + values of env vars named `*KEY*`, `*TOKEN*`, `*SECRET*`, `*PASSWORD*`, `*CREDENTIAL*`, hash fields excluded)" with:

   > final secret scan per `schemas/run-manifest.yaml` (`redaction.final_scan`). It applies 20 key-format rules with boundaries, and it checks the values of environment variables whose names contain KEY, TOKEN, SECRET, PASSWORD, PASSWD, PASSPHRASE, PWD, CREDENTIAL, PRIVATE, AUTH, DSN or DATABASE_URL. `PWD`, `OLDPWD` and `SSH_AUTH_SOCK` are excluded by name. Each value is stripped, split into pieces when it holds whitespace, JSON or a URL password, and matched raw and as hex, base32, base64, base64url, percent-encoded and JSON-escaped text. Values under 8 characters, and date, timestamp, version and IP shapes, are skipped (P0B0-11 as amended at T034). Hash fields are excluded, and the run reports how many values it compared.
6. **`data-model.md:30` and `:37`.**
   - `permission_modes_seen`: "distinct values of the `permission-mode` entries in every archived transcript".
   - `subagents[]`: "one per subagent instance, tachi or not".
   - The re-archive state: "`no-op` only when `run-manifest.json` is present and matches the source (P0B0-5); hash-equal transcripts without it are `refused` (incomplete archive)".
7. **`plan.md:175` (AD-6).** Add an italic amendment note at the start, in the form AD-4 uses:

   > *Amended at T040 (architect, 2026-11-19): the destination rule asks git about every path the run writes, not `<dest>/.probe` (T034 H-1), and the archive carries its own `.gitignore`. git runs with `core.fsmonitor` off and an allowlisted environment (H-2). The archiver re-executes itself under `-I -B` (H-3). A re-archive is a no-op only when the manifest is present (P0B0-5). The roster is the installed agent files' `name:` values (P0-B0 O-2). `contracts/cli-contracts.md` holds the full rule.*

### 5.2 B2 (F-2)

1. **`contracts/cli-contracts.md:25`.** The signature becomes `python3 scripts/stamp-tachi-version.py --threats PATH [--marker templates/tachi/VERSION] [--check] [--json]`.
2. **`contracts/cli-contracts.md:27`.**
   - Replace the `--schema-version-from-template` sentence with: "`--schema-version-from-template` is not built. CF-21 measured churn (`test-results/t038a-measurement.md`), so `schema_version` stays model-authored and declared-only, and the flag is rejected as an unknown argument (exit 2)."
   - Delete "`--schema-version-from-template` reads the single source `schemas/output.yaml`."
   - Replace "`--check` exits 2 if the file would change. Exit 0 stamped or unchanged, 1 I/O or no frontmatter." with: "Exit 0: stamped, already stamped, or `--check` finds nothing to change. Exit 1: `--check` finds the field missing, different or not in the written form, and nothing is written. Exit 2: any error (an unreadable or unwritable file, not a regular file, no frontmatter, a bad argument). This follows the house convention of the guard and the archiver (1 = finding, 2 = infrastructure). Step 2.6 reacts to any non-zero exit."
   - The quoted value and `--json` stay as written.
3. **`contracts/version-marker.md:9`.** Replace the Readers line with: "**Readers**: `stamp-tachi-version.py` (Step 2.6) and `archive-run-transcripts.py` (the manifest's `tachi_version`), with one rule: exactly one line, `tachi_version: <value>`, where `<value>` matches `[A-Za-z0-9][A-Za-z0-9._+~-]{0,127}`. Anything else, or no file, reads `unknown`. Agents never read it."
4. **`contracts/version-marker.md:5` (Format).** Append: "The installer writes `unknown` for any describe value outside the readers' rule. Its character filter is aligned with the rule in W3 (X-7)."
5. **`data-model.md`, VersionMarker.** "Reader: …" becomes "Readers: `stamp-tachi-version.py` (Step 2.6 of `/tachi.threat-model`) and `archive-run-transcripts.py` (P0B0-6)."

### 5.3 T048 corrections (F-3, part-b)

1. **ADR-049 D11, "What is not written", last sentence.** Replace "so tracked SARIF files reproduce unchanged." with:

   > so a regenerated SARIF file agrees with the frontmatter of the file it was generated from. Two tracked SARIF files do not: `examples/agentic-app/sample-report/threats.sarif` says 1.7 for an input that declares 1.4, and `examples/consumer-agent-app/sample-report/threats.sarif` keeps 1.8 when its input is corrected to 1.4. They stay as they are, because this feature moves no tracked SARIF baseline; correcting them is a follow-up.
2. **ADR-049 D10, "Manifest", after the `pinned_model` sentence, and runbook §7's second manifest bullet (`ISOLATED_OPERATION_TACHI.md:418` on part-b).** Add:

   > A subagent type that the installed roster does not name, such as a built-in `general-purpose` instance, is listed too, with `pinned_model: null`.
3. **ADR-049 D10, "Refusals".** Replace "and for a symbolic link that resolves into a work tree" with:

   > and for a destination that is itself a symbolic link or has a symbolic link on its path that resolves into a work tree

Run the Wording sweep over the changed lines.

## 6. Conditions and carry-forwards

- **BX's CI.** At review time `tachi-pytest.yml` was still running on `8d390ce` and on `77bbec8`. The other workflows were green on both. DEVOPS-E confirms both runs green before BX′. Part A's `tachi-pytest.yml` is green on `8273669` and on `2c5fe08`.
- **W2 (T020) checks carried from the rulings, unchanged:**
  - AR-2's `--output-dir` listing;
  - AR-14's "no Python cache path";
  - AR-15 stages B and C;
  - AR-16's Manual-mode check;
  - AR-18's `/sandbox` message and probe row;
  - P0B0-1's built-in subagent types, by type and count.

  The runbook's profile block extracts to 2,908 bytes with SHA-256 `43496fb7d4fca098983a70648def8f1da2a2d1843528b5ca4c14444e32564279`, the value AR-20 predicted for the GL diff.
- **T051.** It records, from the W2 archives, the structure facts that P0B0-4(i)'s addendum would have given:
  - the key that holds the mode in `permission-mode` entries;
  - assistant lines against distinct `message.id` values;
  - `Task`-named `tool_use` blocks;
  - `tool_result` blocks with `is_error`.
- **H1.** The S1 handoff records the per-lane actuals (inputs to G-B2) and this checkpoint's F and X lists. T048's W1 part is done; its W4 part (the CHANGELOG's Part B lines) is not.
- **AD-14 at the cut line.** T046 step (3)'s search over `main...391-isolated-auditable-operation`, excluding the feature records, the system-design README and `docs/product/`, returns zero hits.

## 7. Runs behind this record

| Run | Tree | Result |
|---|---|---|
| `python3 -I -B scripts/check-agent-privileges.py` | scratch clone, `2c5fe08` | C1 to C7 PASS, exit 0. Counts: 21 agents, 3 Bash-capable, 6 commands, 21 paths |
| `… --self-test` | scratch clone, `2c5fe08` | C8 PASS: M1 to M5 detected, exit 0 |
| `python3 -I -B scripts/check-agent-privileges.py` | scratch clone, `8d390ce` | C1 to C7 PASS, exit 0 |
| `--json` families | scratch clone, `2c5fe08` | found = allowed for all three Bash-capable agents |
| Python 3.9.6 run with `TACHI_REQUIRE_TYPST=1`, 12 modules: `test_write_confinement.py`, `test_report_posture_contract.py`, the seven extraction-fidelity modules, `test_agent_privilege_guard.py`, `test_isolated_profile_contract.py`, `test_coverage_attestation.py` | scratch clone, `2c5fe08` | 667 passed. The clone was clean afterwards |
| T046 step (3) search | `main...2c5fe08` | 0 hits |
| Session-profile block extraction | `docs/guides/ISOLATED_OPERATION_TACHI.md` at `2c5fe08` | 2,908 bytes, the SHA-256 above |
