### Upgrading: update your tachi clone, then re-run `install.sh`

This release corrects what tachi's documentation says about where your data goes, adds an installed runbook for running tachi inside Claude Code's sandbox, and keeps every run's writes inside its output directory. Earlier documentation said that architecture descriptions never leave your machine. That was wrong. Your Claude Code model provider receives the architecture description, the files tachi reads and the findings on every run. If you set `GEMINI_API_KEY` and run `/tachi.infographic`, Google's Gemini API also receives image prompts built from derived threat-model content, including names and descriptions taken from your architecture. The README, `SECURITY.md` and the runbook list what those prompts carry by design. An AI agent following tachi's templates writes each prompt, and no code checks it against that list before it is sent (#401).

`install.sh` copies from your local tachi clone, so update the clone first. Then re-run the installer from your project root and restart Claude Code:

```bash
git -C ~/Projects/tachi pull
~/Projects/tachi/scripts/install.sh
```

Use your clone's path if it lives elsewhere. If you install with `--version`, pull first anyway, so that the updated `install.sh` is the one that runs.

**`/tachi.security-report`'s output directory must sit under your working directory.** The report is now compiled from a throwaway copy of the template inside the output directory, and Typst reads only files under the working directory, so the build stops with an error for an output directory outside it. Without `--output-dir`, the output directory is the target directory. The default target is inside your project, so a default run is unaffected; a run on a folder outside your project now stops the same way.

**Where a run writes.** A run now writes only under its output directory and the temporary directory (`$TMPDIR`), and never under the installed `templates/tachi/` tree. Intermediates are kept in `{out}/.tachi-build/`: the infographic extraction JSON, the Gemini request and response files and, after a failed compile, the report's build directory. The request file is the exact body sent to the Gemini API, and the key is not in it. These files are as sensitive as the rest of the run folder. `install.sh` writes no `.gitignore`, so if you commit run output, add `.tachi-build/` to your project's `.gitignore`. With `--output-dir`, `/tachi.security-report` writes its rendered diagrams and any corrected infographic copy there, and `/tachi.risk-score` writes both of its outputs there and leaves the input directory unchanged. If an earlier report failed to compile, delete `templates/tachi/security-report/report-data.typ` from your project: it holds that run's report data, and `install.sh` does not remove it.

**Running tachi isolated.** The new runbook, `docs/guides/ISOLATED_OPERATION_TACHI.md`, is installed into your project. It gives one session profile to save and pass with `claude --settings`, the probes to run before you rely on it, the write locations, transcript retention and where to report problems. Its header records what was validated live: macOS with Claude Code 2.1.330 in auto mode, with and without the image key, on the profile before its last ten deny rules; the published profile was then re-checked without the key. Linux and WSL2 are not yet run live. On macOS, Chromium cannot start inside Claude Code's sandbox, so under the profile `/tachi.security-report` builds no PDF for a run with Critical or High findings or a surfaced attack chain; §6 of the runbook gives a by-hand build to run after the session (not yet run live).

**Fixes:**

- **Report dispatch.** `/tachi.security-report` now dispatches tachi's own report assembler. It named `senior-backend-engineer`, a development agent that tachi does not install.
- **Custom report configuration.** A `report-config.typ` in the run folder no longer overwrites the installed default, so it no longer carries over into later reports.
- **MAESTRO detection on macOS.** `/tachi.infographic all` checked for MAESTRO data with `grep -P`, which macOS's grep does not support. It now uses `grep -E`.

**For forks.** CI now runs a privilege guard. A change to a tachi agent's tools, model pin or frontmatter keys, or to a command's frontmatter keys, fails until §8 of `docs/standards/CLAUDE_PERMISSIONS.md` changes in the same pull request.

The rest of #391 is not in this release; #396 and #399 track it.
