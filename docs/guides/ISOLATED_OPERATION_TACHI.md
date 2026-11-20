# Isolated operation runbook for tachi

## 0. Header

- Last validated: not yet validated
- Minimum Claude Code version: v2.1.285
- Owner: the tachi maintainer
- Platforms the claim covers: _To be completed in this feature's second runbook commit._
- Refresh triggers: re-validate this runbook and re-stamp it when one of these changes:
  - Claude Code's sandbox, auto-mode, `--settings` or retention behavior.
  - New guidance from the program that section 9 maps.
  - The tools, the model or the write set of any tachi agent or command.

## 1. What leaves your machine

_To be completed in this feature's second runbook commit._

## 2. Passivity

_To be completed in this feature's second runbook commit._

## 3. Session profile

Save the block below to a file and start each tachi session with `claude --settings <file>` ([CLI reference: flags](https://code.claude.com/docs/en/cli-reference#cli-flags)).

<!-- BEGIN TACHI SESSION PROFILE -->
```json
{
  "env": { "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1" },
  "permissions": {
    "deny": [
      "WebFetch",
      "WebSearch",
      "mcp__*",
      "Read(~/.ssh/**)",
      "Read(~/.aws/**)",
      "Read(~/.claude/.credentials.json)",
      "Read(//proc/**)",
      "Read(.env*)"
    ]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "autoAllowBashIfSandboxed": false,
    "network": {
      "allowedDomains": ["generativelanguage.googleapis.com"],
      "strictAllowlist": true,
      "tlsTerminate": {}
    },
    "credentials": {
      "envVars": [{ "name": "GEMINI_API_KEY", "mode": "mask", "injectHosts": ["generativelanguage.googleapis.com"] }],
      "files": [
        { "path": "~/.ssh", "mode": "deny" },
        { "path": "~/.aws", "mode": "deny" },
        { "path": "~/.claude/.credentials.json", "mode": "deny" }
      ]
    }
  },
  "autoMode": {
    "environment": [
      "$defaults",
      "Primary use: threat modeling with tachi. tachi reads an architecture description and a local checkout, writes only under the run's output directory, and never connects to, scans or modifies a running system.",
      "Host containment: Bash runs in Claude Code's sandbox with network limited to generativelanguage.googleapis.com; the cloud metadata endpoint is not reachable.",
      "Trusted internal domains: generativelanguage.googleapis.com, only for the optional /tachi.infographic image request.",
      "Sensitive data locations & audiences: the run's output directory and the architecture file hold confidential threat models. Audiences: the security team; Google's Gemini API for the derived infographic prompt only (the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description).",
      "Data retention: Claude Code transcripts are kept 30 days or more via cleanupPeriodDays."
    ],
    "hard_deny": [
      "$defaults",
      "Never use a tool (Bash, WebFetch, WebSearch, an MCP server or any other) to send tachi threat-model outputs, the architecture description, or files read from the analyzed repository to any network host other than generativelanguage.googleapis.com. Requests to that host are acceptable only from the /tachi.infographic image step and only with the derived infographic prompt."
    ]
  }
}
```
<!-- END TACHI SESSION PROFILE -->

_To be completed in this feature's second runbook commit._

## 4. Probe table

_To be completed in this feature's second runbook commit._

## 5. Write locations

tachi writes only under the run's output directory and the sandbox's per-user temporary directory; no write allowances are needed. The session profile in section 3 therefore sets no `sandbox.filesystem.allowWrite` entry.

One command is the exception. `/tachi.architecture` creates the architecture description that `/tachi.threat-model` reads. It writes that file (by default `docs/security/architecture.md`, or the path given with `--output`) and, when the file already exists, a copy of the previous version in `.archive/v{N}/` beside it. Both paths are listed at the end of the table.

Keep every output path under the working directory: `--output-dir` on `/tachi.threat-model`, `/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic` and `/tachi.security-report`, and `--output` on `/tachi.architecture`. Outside the working directory a write needs an allowance that the profile does not grant.

`/tachi.security-report` checks this in code. It builds the report in a throwaway copy of the template at `{out}/.tachi-build/security-report/`, and `typst --root .` resolves from the working directory, so the extractor stops with an error when the output directory lies outside it. The same command also needs its target directory under the working directory when infographic images are present, because Typst reads them under `--root .`. The other commands do not check the condition.

Notation in the table:

- `{out}` is the run's output directory. For `/tachi.threat-model` it is a timestamped subdirectory of the directory that `--output-dir` names, `docs/security/{timestamp}/` by default. For the other commands it is the directory that `--output-dir` names, which defaults to the directory the command reads from.
- `$TMPDIR` is the sandbox's per-user temporary directory.
- `{arch_path}` is the file `/tachi.architecture` writes, and `{arch_dir}` is the directory that contains it.
- `{timestamp}`, `{template}`, `{stem}`, `{finding-id}`, `{chain-id}` and `{N}` are filled in at run time. Braces with commas, as in `{md,sarif}`, list alternatives.

The table lists every path tachi writes.

| Path | Written by | Condition |
|---|---|---|
| `{out}/` | the main session of each run command (`/tachi.threat-model`, `/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic`, `/tachi.security-report`) | the directory does not exist yet |
| `{out}/architecture.md` | the main session of `/tachi.threat-model` (verbatim copy of the architecture file) | the architecture file exists |
| `{out}/threats.md` | `tachi-orchestrator`; updated in place by `scripts/populate-affected-assets.py`, which the orchestrator and `/tachi.threat-model` run and which `/tachi.risk-score` runs on its input file | always for `/tachi.threat-model`; for `/tachi.risk-score` only when the input is markdown, an architecture file is found and `{out}` is the input directory |
| `{out}/threats.sarif` | `tachi-orchestrator` | always |
| `{out}/attack-chains.md` | `tachi-orchestrator` | at least one cross-layer chain passes the filter |
| `{out}/threat-report.md` | `tachi-threat-report` | the report phase runs (the default; the orchestrator's `--skip-report` opt-out skips it) |
| `{out}/attack-trees/` | `tachi-attack-tree-delta` (`{finding-id}-attack-tree.md` and `.manifest.json`); `scripts/extract-report-data.py` (`{finding-id}-attack-tree.png`) | Critical or High findings exist (the manifest is written either way); the PNGs only when `mmdc` is on `PATH` |
| `{out}/attack-chains/` | `scripts/extract-report-data.py` (`{chain-id}-attack-chain.png`) | an attack chain is surfaced and `mmdc` is on `PATH` |
| `{out}/risk-scores.{md,sarif}` | `tachi-risk-scorer` | always |
| `{out}/compensating-controls.{md,sarif}` | `tachi-control-analyzer` | always |
| `{out}/threat-{template}-spec.md` | `tachi-threat-infographic` | each requested template |
| `{out}/threat-{template}.{jpg,png}` | `tachi-threat-infographic`, decoding the response with `python3` | `GEMINI_API_KEY` is set and the API returns an image |
| `{out}/.tachi-build/infographic-{template}.json` | `scripts/extract-infographic-data.py --output` | each template extraction; kept |
| `{out}/.tachi-build/gemini-{template}-request.json` | `tachi-threat-infographic` (Write tool) | `GEMINI_API_KEY` is set; kept (it is the exact payload sent to the Gemini host) |
| `{out}/.tachi-build/gemini-{template}-response.json` | `curl --output`, run by `tachi-threat-infographic` | `GEMINI_API_KEY` is set; kept |
| `{out}/security-report.pdf` | `typst compile`, run by `tachi-report-assembler` | the compile succeeds |
| `{out}/.tachi-build/security-report/` | `scripts/extract-report-data.py --build-dir` (a copy of `templates/tachi/security-report/`, a custom `report-config.typ` when one exists, and `report-data.typ`); removed by `--remove-build-dir` | every report run; removed after a successful compile and kept after a failed one (the parent `{out}/.tachi-build/` stays) |
| `{out}/threat-{stem}.{jpg,png}` | `scripts/extract-report-data.py`: a corrected copy of an infographic image whose bytes do not match its extension; with `--cleanup-mislabeled-images`, which no run recipe passes, it also deletes a redundant file that lies in `{out}` | such an image exists |
| `$TMPDIR` | `scripts/extract-report-data.py` (Python `tempfile`: Mermaid sources and rendered PNGs, removed on exit); headless Chromium started by `mmdc` (profile and caches) | attack trees or attack chains are rendered |
| `{arch_path}` | the main session of `/tachi.architecture` | always, unless a guided update ends with no changes |
| `{arch_dir}/.archive/v{N}/` | the main session of `/tachi.architecture` | an existing architecture file was found |

## 6. Platforms

_To be completed in this feature's second runbook commit._

## 7. Retention and provenance

_To be completed in this feature's second runbook commit._

## 8. Reporting routes

_To be completed in this feature's second runbook commit._

## 9. Program mapping

_To be completed in this feature's second runbook commit._

## 10. Privilege matrix

The privilege matrix lists each tachi agent's tools, model, shell command families, written paths and hosts, and each command's dispatches, written paths and child processes. It is section 8 of `CLAUDE_PERMISSIONS.md` in the tachi repository. That file is not installed into your project, so the link is pinned to a release:

[Agent and command privilege matrix](https://github.com/davidmatousek/tachi/blob/v4.48.2/docs/standards/CLAUDE_PERMISSIONS.md#8-agent-and-command-privilege-matrix) <!-- x-release-please-version -->

The pin moves only when tachi cuts a release. A post-release `main` install therefore sees the previous release's matrix, which can differ from the agents you installed. No matrix exists before the first release that carries section 8.

tachi's CI runs a guard (`scripts/check-agent-privileges.py`) that compares the agent and command files with the matrix. Scope: the guard covers `.claude/agents/tachi/**` and `.claude/commands/tachi.*.md`, not the adapter copies under `adapters/claude-code/agents/`.

## 11. Live-validation record

_To be completed in this feature's second runbook commit._
