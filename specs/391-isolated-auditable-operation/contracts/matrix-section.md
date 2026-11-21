# `CLAUDE_PERMISSIONS.md` §8 — Agent and command privilege matrix (Part A3)

**Placement**: appended after §7.5 and before `## Cross-references` (today lines 279-281). §3, §4 and §5 headings stay byte-exact: the AC-2 cross-check slices `## 4.`..`## 5.` and `tachi-permissions-verify.yml` greps the §3/§4 headings. The guard parses §8 between `## 8.` and `## Cross-references`; the §8 heading's exact GitHub slug is asserted by the guard or the profile test because the runbook links to it.

**Header statement**: §1–§7 describe the repository's development-time settings, which are not installed; §8 is the adopter-facing matrix.

**Enforcement legend** (printed above the tables): `tools:` is enforced by Claude Code at runtime; `model:` applies unless an invocation passes a model, which tachi's commands never do (the legend states only what is confirmed: the effect of `ANTHROPIC_DEFAULT_SONNET_MODEL` and `CLAUDE_CODE_SUBAGENT_MODEL` on subagents is stated only once the Lane R task confirms it; until then the legend says the manifest or transcripts record what served); the Bash, Writes and Hosts columns are declarations that only the adopter's sandbox and permission rules enforce; Bash that a command instructs an agent to run is declared-only.

**Agents table columns**: Agent · Tier (read-only / writer / Bash) · Tools (set) · Model · Bash families (exact first tokens; `—` for none) · Writes (paths under `{out}`; `$TMPDIR` for extractor children) · Hosts (model provider; Gemini host for threat-infographic with a key). Starting content: the Architect's privilege baseline (`.aod/results/architect-391.md` §10) corrected by the Lane E audit.

**Commands table columns**: Command · Frontmatter keys (today `{description}`; values recorded once `allowed-tools`/`model` are set) · **Dispatches** (the tachi agent it invokes; `/tachi.security-report` → `tachi-report-assembler` after AD-13; `/tachi.threat-model` → `tachi-orchestrator`, which dispatches the threat agents and the report agent at depth 2) · Bash it instructs (declared-only; `/tachi.threat-model` gains `stamp-tachi-version.py` at Step 2.6) · Writes · Child processes.

**Child-process note**: `mmdc` and headless Chromium are spawned by `extract-report-data.py` and are invisible to transcripts and permission rules; Python `tempfile` and Chromium write to `$TMPDIR`.

**Scope note**: the guard covers `.claude/agents/tachi/**` and `.claude/commands/tachi.*.md`; it does not cover `adapters/claude-code/agents/` (the repair path points at `install.sh`; the adapter roster is #369's).

**Link from the runbook**: `https://github.com/davidmatousek/tachi/blob/v<release>/docs/standards/CLAUDE_PERMISSIONS.md#8-…` with an `x-release-please-version` marker on that line, which carries exactly one version string (the runbook joins `release-please-config.json` `extra-files`); stated beside the link: post-release `main` installs see the previous release's matrix, and no matrix exists before the first release that carries §8.
