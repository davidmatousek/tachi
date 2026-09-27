# Contract: manifest completeness test and manual-install loop (K1, K2, S-13; FR-K2.2–K2.5)

**Module:** `tests/scripts/test_install_manifest_completeness.py`. It is part of the W1 cut line and is gated by `.github/workflows/tachi-install-fidelity.yml` (PD-9).

**Revision 1 (2026-09-27).** This revision folds in:
- the architect's plan review: M6 (zsh), L8 (the e2e source copy) and L9 (the neutral D-1 sentence);
- the PM's plan review: RC-P1 (the cut line's workflow scope), RC-P5 (paths) and R-P7 (the `:71` wording).

Changed sections are marked **(rev. 1)**.

## Manifest reader (parity with `install.sh` `parse_manifest`)

```python
BEGIN, END = "<!-- BEGIN MANIFEST -->", "<!-- END MANIFEST -->"
def read_manifest(text: str) -> list[str]:
    lines = text.split("\n")                      # "\n" only, never splitlines()
    assert lines.count(BEGIN) == 1 and lines.count(END) == 1   # exact equality, exactly once
    entries, inside = [], False
    for line in lines:
        if line == BEGIN: inside = True; continue
        if line == END: inside = False; continue
        if inside and line != "" and not line.startswith("#"):
            entries.append(line)                  # no stripping, mirrors IFS= read -r
    return entries
```

Each entry is also checked for hygiene:
- no leading or trailing whitespace;
- no `..` segment;
- no leading `/` or `~`.

The reader must return at least one entry. Two checks were added in rev. 1:
- no entry is a path prefix of another entry, which keeps the installer's checked-set origins unambiguous (data-model §2);
- no line inside the block starts with `<!--`. The installer would copy such a line as an entry, while the manual loop drops it.

## Required set and assertions

| Test | Asserts |
|---|---|
| `test_skills_covered` | Every `.claude/skills/tachi-*` dir is covered (data-model §1 coverage relation). There must be at least 21 dirs |
| `test_commands_covered` | Every `.claude/commands/tachi.*.md` is covered. There must be at least 6 |
| `test_referenced_scripts_covered` | Every `scripts/<name>.py` matched by `(?<![\w./-])(?:\./)?scripts/[\w-]+\.py` in the pinned distributed globs is covered or on `EXCLUDED`. `EXCLUDED` is a dict mapping a path to a reason, initially empty. There must be at least 4 matches. It fails closed |
| `test_import_closure_covered` | For each required script, the local modules imported at module load (resolved by an `ast` walk to `scripts/<name>.py`) are covered, transitively. There must be at least 1 (`tachi_parsers`) |
| `test_distributable_imports_stdlib_only` (S-13) | Every import executed at module load in the four distributable scripts is in `sys.stdlib_module_names ∪ {"tachi_parsers"}`. That includes imports nested in module-level `if`, `try` or `with` blocks, but not imports inside function bodies. Only the top-level package name is checked. Skipped when `sys.version_info < (3, 10)` |
| `test_manifest_hygiene` | Markers occur exactly once, the entry-hygiene checks pass (including the two rev. 1 checks), and the entry count is at least 1 |
| `test_negative_matrix` (FR-K2.5) | For each category (a)–(d), remove one required entry from an **in-memory copy** of the block. The matching assertion must fail, and its message must name `INSTALL_MANIFEST.md` and the missing path. It also covers a leading-space entry, a duplicated BEGIN marker, a missing END marker **and (rev. 1) a nested entry pair** |
| `test_end_to_end_install` **(rev. 1)** | Build `tmp/src` **from the manifest**: copy `INSTALL_MANIFEST.md`, `scripts/install.sh`, and the working-tree source of every entry the test's own reader returns. From an empty `tmp/project`, run `/bin/bash tmp/src/scripts/install.sh` with `LC_ALL=C`. Every required path must then exist in the project. There is no `.git`, so the post-copy `git fetch --tags` never runs: no network call and no ref change. Why the copy is manifest-driven: a local tree can hold large untracked or ignored content (for example a 29 MB `.venv` with symlinks) that a whole-tree copy would drag in. Driving the copy from the manifest loses nothing: a required path missing from the manifest is then missing from `tmp/src` too, and the assertion still fails |
| `test_manual_install_loop` (RC-4) **(rev. 1)** | Extract the loop between the `<!-- BEGIN MANUAL INSTALL LOOP -->` and `<!-- END MANUAL INSTALL LOOP -->` markers in `README.md` and in both developer-guide blocks. All three must be byte-identical. **The block must contain no comment**: no line matches `(^|[ \t])#`, because interactive zsh does not treat `#` as a comment by default. Rewrite the loop's first line to `TACHI='<tmp/src>'`, run it with `bash` into an empty project, and assert the required set exists. Run it a second time into the same project, which must succeed with no nested `x/x/` directories |
| `test_manual_install_loop_zsh` **(rev. 1)** | When `shutil.which("zsh")` finds zsh: feed the rewritten block on **stdin** to `zsh -f -i`, which models a paste into a stock interactive shell, and assert the required set exists. Skipped when zsh is absent (ubuntu runners may lack it). The static no-comment assertion above is the portable guard |

Each failure message follows this shape: `INSTALL_MANIFEST.md is missing <path> (<category>). Add it to the block between the BEGIN/END MANIFEST markers.`

**Recorded once, not in CI:** `test_manual_install_loop` and its zsh variant are also run under macOS `/bin/bash` 3.2.57 and zsh 5.9, and the results go in `test-results/`. NFR-7 keeps README and docs off `tachi-pytest.yml`'s trigger.

**Plan-review evidence.** In the scratchpad, the original commented block fed to `zsh -f -i` printed `zsh: command not found: #`. It left `TACHI` unset and hit `sed: /INSTALL_MANIFEST.md: No such file or directory`, and it installed **0 files**. With `interactivecomments` set it installed 158 files. The same block ran twice under `/bin/bash` 3.2 with 158 files and no nesting.

## Workflow wiring for this module **(rev. 1, RC-P1, RC-P5)**

- **The cut-line commit.** `tachi-install-fidelity.yml` invokes **only this module**. The pre-existing extraction modules join after the cut line, in their own lock-step commit with PD-8's mmdc skip (PD-9, PD-20).
- **The module's `paths:`**, which land in the cut-line commit: `INSTALL_MANIFEST.md`, `.claude/skills/**`, `.claude/commands/tachi.*.md`, `.claude/agents/tachi/**`, `templates/tachi/**`, `scripts/*.py`, `scripts/install.sh`, **`README.md`** and **`docs/guides/DEVELOPER_GUIDE_TACHI.md`**. The last two are there because the loop test byte-compares their blocks. The rest are this test module, `tests/conftest.py`, `tests/scripts/conftest.py`, `pyproject.toml` and the workflow file.

## The manual-install loop (FR-K2.2; the same text in all three blocks) **(rev. 1)**

````markdown
<!-- BEGIN MANUAL INSTALL LOOP -->
```bash
TACHI=~/Projects/tachi
sed -n '/^<!-- BEGIN MANIFEST -->$/,/^<!-- END MANIFEST -->$/p' "$TACHI/INSTALL_MANIFEST.md" |
  grep -v -e '^<!--' -e '^#' -e '^$' |
  while IFS= read -r p; do
    case "$p" in
      */) mkdir -p "$p" && cp -R "$TACHI/$p." "$p" ;;
      *)  mkdir -p "$(dirname "$p")" && cp "$TACHI/$p" "$p" ;;
    esac
  done
```
<!-- END MANUAL INSTALL LOOP -->
````

- **No comment inside the block.** The `#` characters in `'^#'` are quoted, so they are not comments.
- **Surrounding prose.** Each block adds three plain sentences, which carry what the inline comment used to:
  1. "Set `TACHI` to your tachi clone's path (the default location is shown) and run this from your project root."
  2. "It copies every path between the `BEGIN MANIFEST` and `END MANIFEST` markers of `INSTALL_MANIFEST.md`, and it is safe to re-run."
  3. "**The manual path does not check for symlinked destinations**, so run it only into real directories." **(rev. 1)** This wording is true before and after K3 lands, so a TW-7 ship of Lane A without K3 needs no rewording (L9).
- **The developer guide's `:1016` block** is a single fence that mixes the clone, copy and verify steps. It is split into three fences (clone; the marker-delimited loop; verify) so that the HTML markers sit outside every fence.
- **Stale developer-guide text.** The verify counts (`:135`, `:137`, `:139`, `:1028`, `:1030`) are replaced by "compare against the manifest". The stale `--version v4.0.0` example becomes `vX.Y.Z`.

## Manifest content change (K1/K2)

These are added to the block:
- `.claude/skills/tachi-output-integrity/`
- `.claude/skills/tachi-misinformation/`
- `.claude/skills/tachi-human-trust-exploitation/`
- `scripts/populate-affected-assets.py`

The prose changes too:
- the counts become 21/21;
- the agent table gains three rows;
- the script notes and the script table cover 4 scripts;
- the dependency note reads "stdlib-only at import; PyYAML is imported lazily for the PDF coverage-attestation page";
- `:73` becomes "every other file in `scripts/` is tachi-internal";
- **(rev. 1, R-P7)** `:71`'s "silently fall through to LLM inline extraction" becomes: "If a script is missing, the report and infographic agents stop with `EXTRACTION SCRIPT MISSING` and name the missing files, and a pipeline step that runs `populate-affected-assets.py` fails at that step." The first clause was verified at `report-assembler.md:120-151` and `threat-infographic.md:141-160`. The populator's callers have no preflight, which is a follow-up candidate the spec did not adopt;
- the checklist item at `:140` reads "manual install blocks derive from this manifest; no edit needed".
