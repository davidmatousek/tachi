# Architect P2 (pre-final) Read and `/aod.build` Step 5 Final Architecture Review: Feature 373

**Reviewer**: architect · **Date**: 2026-10-10 (about 16:20–17:00Z) · **Reviewed at**: `276dd28`, the PR head after W4 (T037, T038). Branch `373-adopter-install-output-fidelity`, draft PR #375, 40/40 tasks done.

## STATUS (Step 5): APPROVED_WITH_CONCERNS

- **Nothing architectural, security-related or production-related holds `/aod.deliver`.** The executable bundle is the one P1 approved: since `9c15a3b`, the last fully verified tip, only `.md` files and one records JSON under `specs/` changed (§5.1).
- **One edit is required before the squash-merge (§6), and it is docs only.** `CHANGELOG.md`'s Feature 373 entry makes two statements that are wrong against the shipped code and contradict the release notes. The fix is about four lines. It needs no re-review, only a grep check and green CI at the tip it creates.
- **P2 verdict on W4: PASS with one correction** (the CHANGELOG, ruling (a)). The ADR-014 note, the data-model N11 bullet, the dev-guide paragraph, the release notes, the spec NFR-7 edit, the #364 draft and the PR body all check out against the code. NFR-6 is clean in every public text.
- **Ruling (a):** the CHANGELOG must change. `release-notes-upgrading.md` stands as written.
- **Ruling (b):** **accept** the PM's "pull first, even with `--version`" refinement. It is technically correct and makes the upgrade run itself safer.
- **CI at `276dd28`: 10 of 10 green**, both `tachi pytest` legs included: ubuntu at 16:33:32Z, macOS at 16:56:31Z, run 38067671214 (§4). The §6 commit creates a new tip, and deliver needs green there too.

## 0. Rulings at a glance

| # | Item | Ruling |
|---|---|---|
| 1 | T037: ADR-014 F-373 note | **PASS.** Every claim checked against the shipped files (§1.2) |
| 2 | T037: data-model §2.2 N11 bullet | **CONFIRMED** in §2.2 (`data-model.md:68-73`) |
| 3 | T037: dev-guide `--follow-symlinks` paragraph | **PASS.** Byte-identical to README `:129-135` |
| 4 | T037: CHANGELOG `## Unreleased` entry | **Correction required** (§2, §6). Everything outside the two errors is accurate |
| 5 | T037: `issue-364-handoff.md` | **PASS.** The figures match P1 §1.4. Two optional wording fixes before posting (§1.2) |
| 6 | T037: PR body | **PASS**, accurate as of `9c15a3b`. Refresh it at deliver (§8) |
| 7 | T038: `release-notes-upgrading.md` | **PASS.** Notices 1–5 present; 6 and 7 rightly dropped (P1 §7.2) |
| 8 | T038: the PM's NFR-7 `paths:` edit | **CONFIRMED** (`spec.md:712`) |
| 9 | NFR-6 public hygiene | **CLEAN** in all five public W4 texts (§1.5) |
| 10 | Ruling (a): CHANGELOG vs release notes | **The CHANGELOG changes.** Two required fixes and two recommended alignments (§2) |
| 11 | Ruling (b): `--version` users pull first | **ACCEPT**, no change. One optional half-sentence for detached clones (§3) |
| 12 | CI at the final tip | **10/10 green at `276dd28`** (§4). Re-confirm at the E-1 tip |
| 13 | Step 5: hold deliver? | **No architectural hold.** Hold only the squash-merge until §6 lands and CI is green at that tip |

## Evidence base

- **The main tree was only read**: `git show/log/diff`, `grep`, Read and `gh`. The only write is this record. No pytest, extractor or `install.sh` ran anywhere (#365).
  - None was needed: W4 changes nothing executable.
  - P1's executions at `9c15a3b` cover the code, which is byte-identical at `276dd28`.
- **Scratch** (`…/scratchpad/final-arch/`) holds copies of the public texts for the NFR-6 scan:
  - the live PR body;
  - the CHANGELOG F-373 entry;
  - the lines W4 added to the ADR and the dev guide;
  - the release notes and the #364 draft.

  It also holds the README/dev-guide byte comparison.
- **Inputs:**
  - the P0 and P1 records;
  - the T036 code review (`.aod/results/code-reviewer-373.md`, final APPROVED_WITH_CONCERNS);
  - the K3 security review (`.aod/results/security-analyst-373-k3.md`: no CRITICAL or HIGH findings);
  - the PM's T038 handoff (`.aod/results/product-manager-373-t038.md`).

---

## 1. The P2 read of W4

### 1.1 What changed since P1

- **The W4 commits**, `1dc774e..276dd28`: `7e1c082` (the docs sweep), `75547e2` (CHANGELOG), `2e5cabf` (the #364 draft) and `276dd28` (the ADR note, the N11 bullet, the release notes, NFR-7, tasks).
- **Footprint:** 8 files, +167/−3, all `.md`.
- **Since `9c15a3b`** (N-1, P1's 10/10-green tip): the same `.md` set, plus P1's four contract amendments, `p1-architect-review.md` and `wave-04/results.json`. All are records. **No product code, test, workflow or manifest changed.**
- **Branch currency:** `origin/main` = local `main` = merge-base = `63438d7`. `main` has nothing the branch lacks.

### 1.2 Each artifact against the code

| Artifact | Verdict | What was checked |
|---|---|---|
| **ADR-014 F-373 note** (`docs/architecture/02_ADRs/ADR-014-…md:10-17`) | **PASS** | See the bullets below this table |
| **data-model §2.2 N11 bullet** | **CONFIRMED** | §1.3 |
| **Dev guide** (`DEVELOPER_GUIDE_TACHI.md`, +8 lines) | **PASS** | The paragraph and the flag gloss are byte-identical to README `:129-135` (`cmp`). The README carried them from earlier in the branch, so the "docs sweep of the README and developer-guide install sections" is complete. The text sits outside the manual-install `<details>` loop, and `manifest-completeness` is green at `276dd28` |
| **CHANGELOG F-373 entry** | **Correction required** | See the bullets below this table |
| **`release-notes-upgrading.md`** | **PASS** | See the bullets below this table |
| **spec NFR-7** | **CONFIRMED** | §1.4 |
| **`issue-364-handoff.md`** | **PASS**, with two optional fixes | See the bullets below this table |
| **PR body** (live) | **PASS** | See the bullets below this table |

**ADR-014 note:**
- **Placement.** It is appended as a dated note, and the 2026-03-23 text is not rewritten (P1 §7.3).
- **Model chain.** It matches `gemini-prompt-construction.md:227-232`: four `Verified:` lines (2 models × 2 ratios) and one `Retired models:` line.
- **A6.** It exists (`TestA6NoRetiredModelIDs`) and is gated (`tachi-install-fidelity.yml:161`).
- **Retired IDs.** They are absent from the render surface the note names: the templates, the `tachi-infographics` references, the agent and the Claude Code adapter. The note's scope is exactly FR-K14.6's: the Copilot, Cursor and generic adapters are out of scope (§7, #8).
- **Error table.** The 404/403 walk, the exhausted chain at Error, 429 not walked and the 60 s timeout match `threat-infographic.md:365-382`.
- **W0 date.** 2026-09-28 matches `w0-smoke.md`.
- **Hygiene.** It is generic.

**CHANGELOG F-373 entry:**
- **Accurate:**
  - K12 "every report tier": one shared helper (FR-K12.1/.2);
  - K13.1 "never blank" (FR-K13.1, SC-4);
  - P-11.1's phrase, verbatim in **Added**;
  - "Closes #373 and #370".
- **Wrong** (ruling (a)):
  - the report-data trigger in **Upgrading**;
  - the image fix in **Fixed** omits the rejected request.

**`release-notes-upgrading.md`:**
- The names match the manifest diff and the chain matches the shipped files (PM §2, re-checked).
- The notice-5 trigger matches `main.typ:129-130`, which stops only when the posture variables are missing.
- The `--version` mechanics match `install.sh` (§3).
- The images clause states the cause (spec `:241`, SC-5 baseline `:773`).
- P-11.1's phrase appears once, verbatim.

**`issue-364-handoff.md`:**
- **The figures** match P1 §1.4 and `oracle-diff.md`:
  - `agentic-app/sample-report` is 4/0/82/0 and `agentic-app` is 12/69;
  - the fallback set is 3 examples and the placeholder set 1;
  - `maestro-reference` grows from 86 to 88 pages;
  - funnel 5 tier-1 + 7 empty-tier; S-9 nonzero on 3 of 5;
  - K10 moves 0.
- **Optional fixes when posting:**
  1. `allow_list` is JSON-only. `report-data.typ` gains only the `risk-posture-level`/`risk-posture-label` pair, in kebab case. As written, "every infographic JSON … and every `report-data.typ` now carries … and an `allow_list` subtree" can be read as putting `allow_list` in the `.typ` too.
  2. "No `.pdf.baseline` other than `maestro-reference`'s page-count note above changed" can be read as saying that baseline changed. No `.pdf.baseline` changed anywhere (NFR-8).

**PR body:**
- It meets T037's R-T1 list: the changed examples, the 4b ledger, the live-render records, the goldens, TW-0..TW-7, PD-8 as #365-adjacent, both "Closes" lines and the `fix(373)` title.
- **Stale at the final tip:** "CI at the PR head (`9c15a3b`)". Refresh it at deliver (§8).
- **Recommended:** the K14 bullet should name the request-shape fix, to match the corrected CHANGELOG (§2).

### 1.3 The N11 bullet in data-model §2.2: CONFIRMED

- **Location.** `data-model.md:68-73` lies under "### 2.2 Destination containment" (`:58`) and before "### 2.3 Decision table" (`:75`). It is marked "(amended at W4, 2026-10-10)".
- **Content.** It mirrors `contracts/installer-cli.md:134-139`:
  - the directory-entry-only rule and the `elif` at the code's `[ "$manifest_entry" != "$entry_stripped" ]`;
  - no flag remedy;
  - the silent skip when `phys_dest` fails, covered by §2.1;
  - the bracket text;
  - provenance (`c194946`, the test and P1's probes).
- **Code references at the tip.** `install.sh:447` is the `elif` and `:448` is the line it prints. Both are exact.
- This closes P1 §8's carry-forward.

### 1.4 The PM's NFR-7 `paths:` edit: CONFIRMED

- `spec.md:712` adds `brand/**` and `schemas/**`, plus the "matches **every** manifest entry" sentence, with a dated PM marker.
- It matches the workflow's `&fidelity_paths` (`:9-10`). The "together with" clause is true: `adapters/claude-code/**` is at `:36` and the dev guide at `:14`.
- `INSTALL_MANIFEST.md` and `tachi-install-fidelity.yml` are unchanged from `8484a7b` to `276dd28`, so P1's and the PM's independent 37/37 checks still hold.
- This closes P1 §4's required spec edit (L-8).

### 1.5 NFR-6 public hygiene: CLEAN

- **Texts scanned:**
  - the CHANGELOG F-373 entry;
  - `release-notes-upgrading.md`;
  - the live PR body;
  - `issue-364-handoff.md`;
  - the lines W4 added to the ADR and the dev guide.
- **What the scan looked for:**
  - real-world target or project names;
  - private paths (`_internal/`, home directories, planning-doc IDs);
  - contributor handles;
  - finding-ID-shaped tokens;
  - URLs.
- **Hits:** only the project's own repo slug (in the PR body's `AOD_REPO` line), the internal ruling ID `P-10` and the attribution URL. All are acceptable.
- Tracked `examples/` names appear only as structural references, as the PR body itself states. No finding text, finding IDs or report content appear anywhere.

---

## 2. Ruling (a): the CHANGELOG's upgrade text vs `release-notes-upgrading.md`

**Ruling: not consistent enough. The CHANGELOG changes; the release notes stand as written.**

- The release notes were checked against the code and are right.
- The CHANGELOG is wrong on two of the PM's four C-1 points.
- PD-7 and T037 required the CHANGELOG to carry "PD-7's applicable notices". C-1's sync step ("before the W4 commit") did not happen before `276dd28`.

| C-1 point | CHANGELOG at `276dd28` | Release notes | Code and spec | Verdict |
|---|---|---|---|---|
| Notice-5 trigger | **Upgrading:** "A `report-data.typ` compiled outside `/tachi.security-report` now stops with a regenerate instruction …" | "an older or hand-built `report-data.typ`", and the command regenerates the file on every run | `main.typ:129-130` panics only when `risk-posture-level`/`-label` are **absent**. A freshly generated file compiled outside the command does not stop. The CHANGELOG's own **Fixed** bullet says this correctly ("built without that data") | **Wrong. Required (R-1)** |
| Images: the cause | **Fixed:** "moves off the preview and `gemini-2.5-flash-image` models (all shut down …)". The rejected request is never mentioned | "its image request was rejected, and the models it named are now shut down" | Spec `:241` and SC-5 `:773`: **every released request failed with HTTP 400**. The ADR-014 note says the same. The CHANGELOG implies images worked until the shutdowns, and its **Fixed** list omits K14's primary fix | **Incomplete and misleading. Required (R-2)** |
| `--version` advice | Silent | "pull first anyway" | §3 | Not a contradiction. **Recommended (R-4)** |
| P-11.1 phrase | Verbatim in **Added** | Verbatim | `README:135`, the dev guide and the refusal text | **Consistent** |
| (Architect) D-1 scope | **Upgrading:** "If any destination `install.sh` writes into is a symlink" | "is a symlink or passes through one" | The pre-flight checks every component, linked ancestors included (M9: "covers every symlinked destination component"). **Added** covers it with "at or above" | Imprecise. **Recommended (R-3)** |

**Suggested wording** (PM-consistent and generic per NFR-6; the editor may condense):
- **R-1** (Upgrading, last sentence): "Compiling an older or hand-built `report-data.typ` (one without the risk-posture variables) outside `/tachi.security-report` now stops with a regenerate instruction; `/tachi.security-report` regenerates the file on every run, so its own runs are unaffected."
- **R-2** (Fixed, the image bullet; prepend): "Infographic images are generated again: the previous release's image request put `aspectRatio` and `imageSize` directly under `generationConfig`, so the API rejected every request (HTTP 400) and no image was produced; they now sit under `generationConfig.imageConfig`." Keep the existing chain and walk sentences after it.
- **R-3** (Upgrading): "If a destination inside your project is a symlink or passes through one, `install.sh` now stops before writing anything and names it; …"
- **R-4** (Upgrading): "If you install with `--version`, pull first anyway, so that the updated `install.sh` is the one that runs."
- **Optional, same edit:**
  - "then restart Claude Code", as in the release notes;
  - one **Fixed** line for FR-K3.5: `install.sh --version` now warns, giving the command to run, when it cannot restore the clone's original ref, instead of failing silently (tip `:271-283`).

---

## 3. Ruling (b): `--version` users pull first (diverges from PRD M9's example)

**Ruling: ACCEPT. No change.**

- **The mechanics are correct.**
  - In v4.48.0 (`origin/main:scripts/install.sh:101-125`), `--version` runs `git checkout <tag>` inside the source clone and then copies from it.
  - The `MANIFEST_FILE` path is fixed at `:87`, but `parse_manifest` reads it at `:212`, after the checkout. So the **tag's** manifest is copied.
  - The process keeps running the script it started with: git replaces the file under it, and bash keeps reading its open descriptor.
  - **So M9's example route** ("`git fetch --tags`, then `install.sh --version vX.Y.Z`") delivers the new payload, but the upgrade run happens without D-1's protections. That run has no symlink pre-flight, and the old cleanup can delete through a link. It is the one run where an adopter with a linked `.claude/skills` is most exposed.
  - **Pulling first** makes the upgrade run itself D-1-protected. It also gives that run the loud ref restore (tip `:271-283`).
- **Authority.**
  - M9 is the PM's own ruling. Its parenthetical example was illustrative, and the refinement keeps M9's binding intent: update the clone first, and cover every symlinked component.
  - Architect confirmation of the technical claim is all that's needed.
  - No PRD edit is needed. The approved v1.2 is a historical record, and the divergence is recorded in the PM's T038 results and here.
- **C-2 (other upgrade text in W4):**
  - The README's "To install a specific version" block gives no update guidance, so it doesn't conflict.
  - W4 added no upgrade text to the README or dev guide. The dev guide gained only the byte-identical `--follow-symlinks` paragraph.
  - The CHANGELOG is the only other upgrade text, and R-4 aligns it.
- **Residual edge (optional, PM's call):**
  - `ORIGINAL_REF` is the branch name when the clone is on a branch (`rev-parse --abbrev-ref HEAD`). So a successful earlier `--version` run left the clone on its branch, and `git pull` works.
  - A clone left **detached** by v4.48.0's swallowed restore failure (`:114`, `2>/dev/null || true`; the defect in PRD §1) makes `git pull` error with "not currently on a branch".
  - Git's message is self-explanatory, so this is not required. A half-sentence such as "if `git pull` reports you are not on a branch, check out your branch first" would cover it.

---

## 4. CI at the final tip (`276dd28`)

**10 of 10 checks green** (`gh pr checks 375` at 16:56Z).

| Check | Run | State |
|---|---|---|
| `tachi install fidelity`: manifest-completeness, extraction-fidelity, report-posture | 38067671246 | success |
| `tachi catalog-drift` | 38067671231 | success |
| `tachi maestro coverage` | 38067671335 | success |
| `tachi mmdc preflight` | 38067671215 | success |
| `gitleaks (CI parity)` and the standalone gitleaks check | 38067671213 | success |
| `tachi pytest`, ubuntu leg | 38067671214 | **success** (16:33:32Z, 6m59s) |
| `tachi pytest`, macOS leg | 38067671214 | **success** (16:56:31Z, 29m50s) |

- **Corroboration.**
  - `1dc774e..276dd28` changes no executable file. The tip's code and tests are byte-identical to `9c15a3b` (10/10, run 38064601442).
  - They are also byte-identical to `1dc774e`, whose run 38066487952 is green on both legs: ubuntu at 16:15:44Z, macOS at 16:32:41Z.
  - That makes three consecutive 2-OS green cycles on the same executable content.
- **For deliver:** green is required at the **final** tip. §6's CHANGELOG commit creates a new tip, and every workflow re-runs on it, because PR path filters are evaluated against the whole PR diff. Expect one more 2-OS cycle of about 26 min.

---

## 5. Step 5: the final architecture review

### 5.1 Architecture

**Unchanged since P1, so P0, P1 and T036 stand.**

- **K3 (D-1):**
  - identity-based containment (`[ -ef ]`), deny by default;
  - copies-only opt-in, which never deletes through a link;
  - the always-refused classes: broken, looping, wrong-type, nested, and source-clone in both directions (N11).
- **Fixes closed:**
  - RC-1, RC-2 and RC-3;
  - the 12 review findings, including H-1 (`ENVIRON`) and M-1 (no early-exit reader under `pipefail`);
  - N-1, now deterministic.
- **The oracle** is 100% attributed (0 unclassified) and was independently re-derived at P1.
- **Goldens:** all 47 leaves are authorized (SC-8).
- **NFR-8:** no PNG or `.pdf.baseline` changed.
- **Contracts and the data model** match the code after P1's 13 amendments and this W4 N11 bullet.

### 5.2 Security

- **K3** (security-analyst):
  - no CRITICAL or HIGH;
  - SEC-K3-01 is closed by RC-1;
  - SEC-K3-03 (a leading-dash `--version`) is a LOW follow-up (#1). It is user-supplied and local, and the tag-existence check runs before the checkout.
- **K14 key handling** is header-only (NFR-5). Keeping the key out of argv is a LOW follow-up (#7, CWE-214).
- **K15:** the allow-list and the leaked-label prohibition were verified live, 7 of 7.
- **CI supply chain:**
  - the new workflow is `contents: read` and uses no secrets;
  - its actions are tag-pinned, as in every other workflow;
  - `setup-typst@v5` was already on `main` (`tachi-mmdc-preflight.yml`);
  - no dependency manifest changed.

### 5.3 Production readiness and release-level risk

- **Release urgency (P1 §7.1) stands, and is if anything understated.**
  - Adopters on v4.48.0 get no infographic images today.
  - Per spec SC-5 that is true since the release itself (HTTP 400), not only since the 2026-10-02 shutdown.
  - **Deliver promptly.** The §6 edit costs minutes plus one CI cycle.
- **Behavior changes in a `fix:` release** (C-8 kept `fix:`). Both fail closed and carry their remedies, and both are covered by notices 2 and 5:
  - D-1's stop on a symlinked destination (exit 1, the remedy in the message);
  - the `main.typ` stop on an older or hand-built `report-data.typ`.
- **The release-notes mechanism** (PD-7) is validated by the PM's simulation:
  - the pre-merge insert after `## [x.y.z]`;
  - the `head -1` grep backstop;
  - release-please's single-release parse still holds.
- **Branch currency is clean today.** KB 18's check must be repeated at deliver (§8).

### 5.4 Does anything hold `/aod.deliver`?

- **No architectural, security or production hold.**
- **Hold the squash-merge, not the start of deliver,** for:
  1. the §6 CHANGELOG correction;
  2. 10/10 CI green at the tip it creates.

---

## 6. Required edit before deliver

| # | Owner | File | Change | Check (no re-review) |
|---|---|---|---|---|
| E-1 | The orchestrator. It may delegate to SBE-A, T037's CHANGELOG author; a PM courtesy check is optional | `CHANGELOG.md`, the `## Unreleased` "Feature 373" entry | **R-1 and R-2 (required)**; R-3 and R-4 recommended in the same commit (§2). Commit on the branch as `docs(373): …` | (1) No sentence in the entry says that every `report-data.typ` compiled outside the command stops. (2) **Fixed** names the rejected HTTP 400 request as the reason no images were produced. (3) NFR-6 re-scan clean. (4) CI 10/10 at the new tip |

Nothing else is required. The optional items:
- the two #364 wording fixes (§1.2);
- the PR body's K14 request-shape clause and its CI line (§8);
- the ruling (b) half-sentence.

None of them gates deliver.

## 7. Follow-ups to file at deliver

- **File P1 §5's seven, as listed there**, after `export AOD_REPO=davidmatousek/tachi`, in generic wording:
  1. `--version` leading dash;
  2. the `## Section N:` heading form;
  3. free-text `baseline.source`;
  4. the em-dash project name;
  5. maestro-stack contrast;
  6. the cell-level grid;
  7. the Gemini key off argv.
- **Candidate #8 (new at P2; the PM decides whether to file):** the Copilot, Cursor and generic adapters still send the image request shape the API rejects, and name only shut-down image models.
  - Evidence:
    - `adapters/copilot/agents/threat-infographic.agent.md:591-661`;
    - `adapters/cursor/rules/threat-infographic.mdc:597-667`;
    - `adapters/generic/prompts/13-threat-infographic.md:552-622`.
  - It is pre-existing (identical on `origin/main`) and explicitly out of scope here (FR-K14.6, S-10), so it is not a defect of this feature.
  - But nothing tracks it, and the developer guide's FAQ (`:1782-1783`) tells readers the adapters are equivalent across platforms.
  - The fix: sync those three copies to the ADR-014 F-373 note, or mark them unmaintained and correct the FAQ. LOW.

## 8. Carry-forward for `/aod.deliver`

**Pre-merge, in order:**
1. E-1 committed and pushed.
2. CI 10/10 green at the resulting tip, both `tachi pytest` legs included.
3. Refresh the PR body:
   - the CI line names the final tip;
   - recommended: the K14 bullet gains the request-shape clause.
4. Re-verify the title `fix(373): adopter install + output fidelity fixes`, then `gh pr ready 375`.
5. KB 18: the branch is current, and `main` equals `origin/main` in a full-tree comparison. `git reset --hard` is blocked in this environment; use `git checkout -B main origin/main` instead.
6. No pytest or extractor runs in the main tree (#365). Check `git status` after every agent returns.

**Merge and release:**
1. Squash-merge, then confirm a release-please **patch** PR opens within about 30 s.
2. If one doesn't open, the empty release-marker commit must be **`fix(373): … — release marker`**, not the `feat` example in the git-workflow rule. A `feat` marker would turn C-8's patch into a minor release.
3. PD-7:
   - copy `release-notes-upgrading.md` to `$SCRATCH/upgrading.md`;
   - run any polish first;
   - insert it into the release-please PR body after the `## [x.y.z](…) (date)` line and a blank line, before `### Bug Fixes`, as the last action before merging that PR;
   - post-publish, run the `gh release edit` backstop if the `head -1` grep misses;
   - check the result verbatim with `gh release view` (SC-6).

**After merge:**
- File §7's follow-ups.
- Post the #364 comment (the text below the paste line of `issue-364-handoff.md`), with the optional fixes.
- SC-7 stays outside this feature.

## 9. Final state

- **Main tree** (`git status --short` at 16:57Z; HEAD `276dd28`):
  - `?? …/test-results/p2-architect-review.md` is this record, the only file this review created. Nothing else was edited and nothing was committed. The orchestrator commits.
  - `?? specs/373-adopter-install-output-fidelity/economy-check.md` is **not this review's**. It appeared during the review, probably from a parallel gate, and was left untouched.
- **Scratch:** `…/scratchpad/final-arch/` holds only the copies used for the NFR-6 scan and the byte comparison.
