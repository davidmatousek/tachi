# W1 scratch adopters at v4.48.4 (T141)

**Date:** 2026-11-22. **Base:** W1's base, `9457a3e`. **Input:** T141, split from T022 (TL-T2).

**Result:** two scratch adopters, `<adopter A>` and `<adopter B>`, hold tachi v4.48.4 as `scripts/install.sh --version v4.48.4` installs it. Both are ready for T021: (a) runs in `<adopter A>` and (b) in `<adopter B>`.
- Both installs exited 0, reported `Version:  v4.48.4` and `Copied:   38 item(s)`, and wrote nothing to stderr.
- Both match the tag's own tree exactly: 166 files, byte-identical. The two adopters equal each other.
- No tachi command, no Claude Code session, and no pytest, extractor or renderer ran in either adopter or in any tracked tree.

## 1. Method

The steps follow README Quick Start steps 1 and 2 and the developer guide's Step 2 and Step 3.

1. **Clone (README step 1, one-time).** A full `git clone` of the public repository into `<tachi clone>`: a new directory beside the adopters, outside every tracked tree.
   - It is a clone, not the main checkout or a lane worktree, because `--version` runs `git checkout <tag>` in the source repository and restores it on exit. Run from a tracked tree, it would have switched that tree's HEAD (H5, H9).
   - It comes from the public repository, because the local repository has no `v4.48.4` tag: its newest tag is v4.48.3. The public repository has the tag, and it resolves to `b040fa1`, the commit that T001 froze as the code baseline.
2. **Adopters.** Each is a fresh `git init -b main` with a one-line README and one commit, under a repo-local generic identity.
3. **Install (README step 2, per adopter).** From each adopter's root, with `<tachi clone>/scripts/install.sh --version v4.48.4`.
   - `<tachi clone>`'s `main` already sat on the tag's commit, so the installer that ran is the tag's own. Its `install.sh` and `INSTALL_MANIFEST.md` are also byte-identical to W1's base.
   - The two installs ran one after the other, because each checks out the tag in the same clone. The clone was restored to `main` and was clean after each.
   - `install.sh` was the only writer into the adopters. The adapter directory was never copied (R-17).
4. **Verify** as in section 4, then **one commit per adopter**, "Install tachi v4.48.4". It stages the seven top-level directories the manifest places, by explicit path.

Not done, by design: any tachi command or Claude Code session (T021 starts them, and README step 3's restart is theirs), and `pre-commit install` (the gitleaks hook is opt-in for adopters and is not part of the install).

## 2. Installed version marker

- `install.sh` writes no version file into the project. It reports the version once, in its summary line: `Version:  v4.48.4`. That is `git describe --tags --always` in `<tachi clone>` while the tag is checked out.
- `v4.48.4` is a lightweight tag on `b040fa1`, the "release 4.48.4" commit.
- The only placed file that names the version is `docs/guides/ISOLATED_OPERATION_TACHI.md`, line 537: a link whose ref segment is `v4.48.4`, with the `x-release-please-version` marker. Apart from that link, nothing in the project records which version was installed, so the "Install tachi v4.48.4" commit message and this record are the marker.
- **Warnings:** none. stderr was empty for both installs. The courtesy warning for a missing `mmdc` did not fire, since `mmdc` is on the PATH.

## 3. What install.sh placed

38 manifest entries became 166 files and 15,086,027 bytes, the same in both adopters. One file is executable (`scripts/extract-infographic-data.py`, as in the tag). There are no symlinks.

| Top-level directory | Files | Contents |
|---|---|---|
| `.claude/` | 89 | `agents/tachi/` 22; `commands/` 6 (the six `tachi.*` commands); `skills/` 61 files in 21 `tachi-*` skill directories |
| `schemas/` | 21 | The whole directory: the 8 listed schemas, plus `README.md`, `attack-chain.yaml`, `coverage-checklists.yaml` and `taxonomy/` |
| `templates/` | 33 | `templates/tachi/` only: `output-schemas/` 7 files, `infographics/` 6 entries, `security-report/` 19 entries |
| `scripts/` | 4 | `extract-infographic-data.py`, `extract-report-data.py`, `populate-affected-assets.py`, `tachi_parsers.py` |
| `adapters/` | 6 | `adapters/claude-code/agents/references/` only |
| `brand/` | 11 | The whole directory: `final/` has 6 logo PNGs, plus the brand guidelines, two concept images and two posters |
| `docs/` | 2 | `docs/guides/DEVELOPER_GUIDE_TACHI.md` and `docs/guides/ISOLATED_OPERATION_TACHI.md` |

## 4. Verification

**A. The developer guide's Step 3 (Verify)**, checked against `INSTALL_MANIFEST.md` at the tag. The result is the same in both adopters.

| Documented check | Found | Outcome |
|---|---|---|
| `ls .claude/agents/tachi/` against the manifest's Agent Files table | 22 files: all 21 listed agents, plus `_TACHI_AGENT_BEST_PRACTICES.md` | pass (section 5) |
| `.claude/agents/tachi/orchestrator.md` exists (the guide's "Tachi says it is not installed" check) | present | pass |
| `ls .claude/commands/` | exactly the six `tachi.*` files the manifest lists | pass |
| `ls schemas/` against the Schema Files list | all 8 listed schemas present, 12 entries in all | pass (section 5) |
| `ls templates/tachi/output-schemas/` (the guide says 7 templates) | 7 | pass |
| `ls templates/tachi/infographics/` | 6 entries | pass |
| `ls templates/tachi/security-report/` (the guide says `main.typ`, `theme.typ`, `shared.typ` and page templates) | 19 entries; the three named files are present | pass |
| `ls adapters/claude-code/agents/references/` (the guide says 6 reference docs) | 6 | pass |
| `ls brand/final/` | 6 logo PNGs | pass |

**B. A comparison with the tag's own tree.** This is stronger than `ls`: `git ls-tree` on the tag, against the files on disk.
- The file set equals the tag's tree under the 38 manifest entries: 166 and 166, none missing and none extra (the project's own README aside).
- Every installed file's blob hash equals the tag's, so the contents are byte-identical. The executable bit matches.
- `adapters/claude-code/agents/` holds only `references/`, so no adapter agent copy was installed (R-17).
- At the git level, before the install commit, `git status --porcelain --ignored` showed exactly the seven manifest top-level directories, untracked, and nothing ignored. After the commit it showed nothing.

**C. Adopter A against adopter B.** The seven installed subtrees have identical git object ids, and the file counts and byte totals agree.

**D. Prerequisites the README names** (for later runs, not for the install): `typst` 0.14.2 and `mmdc` 11.12.0, both on the PATH.

## 5. Observations (documentation nuances, not install faults)

- **The agent count.** The manifest says 21 agents and its table lists 21, but `.claude/agents/tachi/` holds 22 files. The 22nd, `_TACHI_AGENT_BEST_PRACTICES.md`, lands because the manifest says to copy the whole directory. "21" counts agents, not files.
- **The schema list.** It names 8 schemas. The whole directory is copied, so a literal `ls schemas/` comparison finds extras and no gaps.
- **No stored version.** See section 2: the version is printed once and not kept in the project.
- **The interpreter.** `python3` on this shell's PATH is 3.12.11. T021's runs reach `python3` through the commands' fences, so they use whichever interpreter is first on the PATH of the session that starts them.

## 6. For T021 and the orchestrator

- T021(a) goes in `<adopter A>` and T021(b) in `<adopter B>`. The real paths are in the lane's private results file, not here (H8).
- Each adopter's last commit, "Install tachi v4.48.4", is the pristine install. `git status` is clean there, so anything a run adds or changes shows against it.
- `<tachi clone>` sits beside the adopters, restored to `main` and clean. A reinstall from it checks out the tag again, so never run two installs at once.
- Claude Code needs a new session in each adopter to see the commands (README step 3).
- This lane edited no tracked tree. Its only tracked file is this record.

## 7. Environment

| Item | Value |
|---|---|
| Host | macOS 26.6.2, arm64 |
| Installer shell | bash 5.3.9 (Homebrew), which the script's `env bash` shebang resolved to |
| git | 2.52.0 |
| Source | The public repository, full clone: `main` at `b040fa1`, with the v4.48.4 tag on the same commit |
| Network use | One `git ls-remote` and one `git clone` of the public repository, and the installer's own `git fetch --tags` in `<tachi clone>` |
