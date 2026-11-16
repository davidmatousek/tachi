# Version marker `templates/tachi/VERSION` (Part B2)

**Tracked placeholder**: `templates/tachi/VERSION` is committed with the content `tachi_version: unknown`, so the path joins the installer's K3 pre-flight checked set (built with `find` over the source tree) and every copy path resets the value.

**Format**: exactly one line, `tachi_version: <value>`, trailing newline. At install `<value>` is `git describe --tags --always --dirty` of the source clone after any `--version` checkout (for example `v4.48.1`, `v4.48.1-2-g3ecba74`, `v4.48.1-2-g3ecba74-dirty`), git dir detected with `git -C "$SOURCE_DIR" rev-parse --git-dir` (worktrees and submodules); when the source has no git tree, `<manifest ".">-release-manifest` (for example `4.48.1-release-manifest`, labelled so it cannot be read as a describe string or sort above the release); otherwise `unknown`. The installer's existing `untagged` fallback is aligned to `unknown`. Never rendered as SemVer `+` build metadata.

**Writers**: `scripts/install.sh` removes any existing marker before the copy loop and writes the new line after it (`:585`), through the containment (`under()`, `[ -ef ]`) and symlink guards, before the EXIT trap restores the ref; the README manual-install loop (and the two developer-guide copies, byte-identical per the manifest completeness test) writes the same line after its copy. Installs that skip the line read `unknown` because the copied placeholder says so; a marker-writing install followed by a marker-skipping install reads `unknown` (tested). **Residual**: a downgrade performed with a pre-391 installer cannot reset the marker (ADR-049 Known limitations). `install.sh` runs a best-effort `git fetch --tags` at install time; the runbook mentions it for air-gapped installs.

**Readers**: `stamp-tachi-version.py` only. Agents never read it.

**Coordination**: #369's `adapters/*/VERSION` uses `source_version:`; this marker uses `tachi_version:` to match the frontmatter key; the two formats are documented side by side in #369's attestation doc.

**Release wiring**: none (D-9). The marker is written at install time from the live clone; `release-please-config.json` is unchanged for it. (The runbook's matrix link, AD-2, is the only new `extra-files` entry.)
