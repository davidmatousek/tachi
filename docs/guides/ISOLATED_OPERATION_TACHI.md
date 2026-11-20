# Isolated operation runbook for tachi

## 0. Header

- Last validated: not yet validated
- Minimum Claude Code version: v2.1.285
- Owner: the tachi maintainer
- Platforms the claim covers: none yet. §6 lists the platforms this runbook targets, and §11 names the ones that ran in the live validation.
- Refresh triggers: re-validate this runbook and update the "Last validated" line when one of these changes:
  - A new Claude Code minor release, or a change to its sandbox, auto-mode, `--settings` or retention behavior.
  - A change to the session profile (§3).
  - A new tachi host or write location, or a change to the tools, the model or the write set of any tachi agent or command.
  - New guidance from the program that §9 maps.

## 1. What leaves your machine

Your Claude Code model provider receives the architecture description, the files tachi reads and the findings on every run. If you set `GEMINI_API_KEY` and run `/tachi.infographic`, Google's Gemini API (`generativelanguage.googleapis.com`) also receives image prompts made of tachi's fixed layout instructions and derived threat-model content, including names and descriptions taken from your architecture (the project name and assessment date; the names, types and short descriptions of components, trust zones, trust boundaries and data flows; finding IDs, descriptions, severities and risk scores; correlation groups of related findings and their descriptions; finding counts, severities and analysis coverage, overall and by component, zone, boundary, flow, threat category and MAESTRO layer; the overall risk posture; control-coverage and risk-reduction figures from compensating-control runs; counts of new, updated, unchanged and resolved findings since a baseline, with new findings marked; and, if a template cannot be loaded, a one-line system description). By design, tachi sends nothing else, but an AI agent following tachi's templates writes each prompt, and no code checks it against this list before it is sent. Claude Code's own operational traffic, such as usage metrics, error reports and feature-flag fetches, is separate from tachi; it is governed by Claude Code's [privacy and telemetry settings](https://code.claude.com/docs/en/data-usage#telemetry-services), and setting `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` turns these off.

The field-level specification of those prompts is the installed prompt sources: the five scaffolded templates in `templates/tachi/infographics/`, the executive-architecture prompt in `.claude/skills/tachi-infographics/references/executive-architecture.md`, the request form and fallback prompt in `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md`, and the baseline instruction in `.claude/commands/tachi.infographic.md`.

### The two hosts

A tachi run reaches two hosts. Claude Code's own traffic, below, is separate.

| Host | When | Who connects | In the profile's allow-list |
|---|---|---|---|
| Your model provider: `api.anthropic.com` on the Anthropic API, or your cloud provider's or gateway's endpoint | Every run | The Claude Code process, which runs outside the shell sandbox | No. The allow-list governs sandboxed commands, and this connection is not one |
| `generativelanguage.googleapis.com` | Only when `GEMINI_API_KEY` is set and `/tachi.infographic` runs. Without the key, tachi skips the image request and the pipeline continues | A sandboxed `curl` run by the `tachi-threat-infographic` agent | Yes. It is the profile's only allowed domain (§3) |

Sources: [network access requirements](https://code.claude.com/docs/en/network-config#network-access-requirements); [cloud provider and LLM gateway routing](https://code.claude.com/docs/en/network-config#cloud-provider-and-llm-gateway-routing); [what runs outside the sandbox](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox).

A sandbox does not change what reaches the model. Your prompts and the files Claude reads go to your provider with or without one ([sandbox environments](https://code.claude.com/docs/en/sandbox-environments#compare-sandboxing-approaches)). In auto mode, the permission classifier's checks also go to your provider, inside the session's model requests or as separate classifier requests. They add requests, not hosts ([server-side classifier review](https://code.claude.com/docs/en/permission-modes#server-side-classifier-review); [default classifier model](https://code.claude.com/docs/en/permission-modes#default-classifier-model)).

The allow-list works on hostnames. §9 gives the domain-fronting caveat.

Each image request is kept as `{out}/.tachi-build/gemini-{template}-request.json`, the exact body sent for that template's last attempt. The key is not in it. It travels only as a request header (`.claude/skills/tachi-infographics/references/gemini-prompt-construction.md`).

### Claude Code's own traffic

This traffic belongs to Claude Code, not to tachi. The session profile sets `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, which turns off everything in the first table below. Any non-empty value turns the variable on, `0` and `false` included. Unset it to allow the traffic again.

| Traffic | Where it goes | Its own switch |
|---|---|---|
| Usage metrics. They never include code, prompts or file paths | Anthropic and third-party logging infrastructure | `DISABLE_TELEMETRY=1`, which also stops feature-flag fetching |
| Error reports, after Claude Code redacts known patterns of secrets, paths and personal data | A third-party error tracking service | `DISABLE_ERROR_REPORTING=1` |
| Feature-flag fetches | `api.anthropic.com` | `CLAUDE_CODE_DISABLE_FEATURE_FLAGS=1` (v2.1.319 or later; older versions read `DISABLE_GROWTHBOOK`) |
| Auto-updates, release notes, session surveys, status and availability checks, and `/feedback` and Claude-drafted feedback, which can send conversation history | The hosts listed in network access requirements | Only the nonessential-traffic variable covers all of them |
| Artifact publishing | `claude.ai` | Off while the nonessential-traffic variable is set |

Sources: [telemetry services](https://code.claude.com/docs/en/data-usage#telemetry-services); [environment variables](https://code.claude.com/docs/en/env-vars); [network access requirements](https://code.claude.com/docs/en/network-config#network-access-requirements); [artifact availability](https://code.claude.com/docs/en/artifacts#availability).

The nonessential-traffic variable does not cover these:

| Traffic | Its own switch | In a session under the profile |
|---|---|---|
| The WebFetch domain safety check. It sends each requested hostname, not the URL or the page, to `api.anthropic.com`, on every provider | `skipWebFetchPreflight: true` in settings | WebFetch is denied, so no fetch reaches the check |
| Official plugin marketplace auto-install, usually at a machine's first interactive launch | `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL=1`, read at that moment | The profile does not set it. Set it in your environment before that first launch if you want the marketplace left unregistered |
| Gateway model discovery | Its own opt-in | Applies only behind an LLM gateway |

Sources: [default behaviors by API provider](https://code.claude.com/docs/en/data-usage#default-behaviors-by-api-provider); [WebFetch domain safety check](https://code.claude.com/docs/en/data-usage#webfetch-domain-safety-check); [environment variables](https://code.claude.com/docs/en/env-vars).

claude.ai connectors are fetched by default for claude.ai sign-ins, through `mcp-proxy.anthropic.com`. `ENABLE_CLAUDEAI_MCP_SERVERS=false` or `disableClaudeAiConnectors: true` stops that. The profile denies every MCP tool (`mcp__*`), so Claude cannot call a connector ([network access requirements](https://code.claude.com/docs/en/network-config#network-access-requirements)).

Some traffic stays on because Claude Code requires it: the model requests, the classifier checks, and sign-in and token refresh through `claude.ai` and `platform.claude.com` ([network access requirements](https://code.claude.com/docs/en/network-config#network-access-requirements)). On Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry and Claude Platform on AWS, metrics, error reports and `/feedback` reports are off by default. The WebFetch check and session surveys still run there ([default behaviors by API provider](https://code.claude.com/docs/en/data-usage#default-behaviors-by-api-provider)).

### Local tools

typst builds the PDF from the installed templates in `templates/tachi/security-report/`, which import only local files. mmdc renders the attack-tree and attack-chain diagrams through a headless browser that it starts on your machine (§10). tachi's four installed scripts in `scripts/` load no network library, and the only programs they start are mmdc runs. All of these run as sandboxed commands, child processes included, so under the profile none of them could reach a host other than the Gemini host ([sandboxing](https://code.claude.com/docs/en/sandboxing)).

Nothing is fetched or installed mid-run. Install typst, mmdc (with the browser it uses) and python3 before a run. If typst or mmdc is missing, `/tachi.security-report` stops with an install hint, and no tachi command installs anything. The claim rests on the offline render check recorded in §11, which renders the diagrams with no network access and compares the images byte for byte. It does not rest on a run that logged no denials. Such a run shows only that nothing it tried was refused.

### Install time

tachi's installer, `scripts/install.sh`, runs from your shell before any session. It makes one network call: a quiet, best-effort `git fetch --tags` in the tachi source clone, so that it can report the release it installed. On an air-gapped machine the fetch fails silently and the install still completes. Installing Claude Code and the prerequisites above is also done before a run, outside tachi.

## 2. Passivity

tachi reads an architecture description and a local checkout; it never connects to, scans or modifies a running system.

- **What it reads.** The architecture description you give it and, for commands that inspect code such as `/tachi.compensating-controls`, a checkout on your disk. It works on files only.
- **What it never does.** It sends no request to the systems it describes: no login, probe, scan or deployment. No tachi command, agent or skill instructs Claude to run the analysed project's code. §10 lists the shell commands tachi uses.
- **What it writes.** Only its own outputs, at the locations in §5.
- **What it sends.** The two flows in §1. Passive does not mean private: what tachi reads goes to your model provider.

The session profile states the same facts to auto mode's classifier, in its primary-use entry (§3).

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

### Launch details

Save the block to a file outside the project, for example `~/.tachi/session-profile.json`. Sandboxed commands can write to the working directory, so a copy inside the project could be changed before your next launch ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)). Start each tachi session from the project root, because `Read(.env*)` covers `.env` files at or under the working directory ([how deep a pattern matches](https://code.claude.com/docs/en/permissions#how-deep-a-pattern-matches)):

```
claude --settings ~/.tachi/session-profile.json
```

Claude Code applies the file above your user, project and local settings and below managed settings, for that session only ([settings precedence](https://code.claude.com/docs/en/settings#settings-precedence); [change a setting for one session](https://code.claude.com/docs/en/settings#change-a-setting-for-one-session)). The file must be a regular file of at most 2 MiB ([CLI reference: flags](https://code.claude.com/docs/en/cli-reference#cli-flags)). Starting `claude` without the flag applies none of the profile. tachi's agents run in the session's process and use its sandbox configuration, so the profile covers every agent ([sandbox scope](https://code.claude.com/docs/en/sandboxing#scope)).

The profile sets no permission mode. A new terminal session starts in auto mode where Claude Code offers it (v2.1.283 or later) and in Manual mode otherwise, unless `--permission-mode` or a `defaultMode` in one of your own settings files names another mode ([which mode a session starts in](https://code.claude.com/docs/en/permission-modes#which-mode-a-session-starts-in)). The status bar shows the active mode ([switch permission modes](https://code.claude.com/docs/en/permission-modes#switch-permission-modes)).

### Check the effective configuration

A session runs with the union of all settings scopes, not with the profile alone. Lists merge, so the profile adds entries and cannot remove another file's: your own `allowedDomains` entries and `WebFetch(domain:...)` allow rules still widen what sandboxed commands can reach. A scalar that the profile sets, such as `sandbox.enabled`, wins over your user, project and local files ([lists merge instead of overriding](https://code.claude.com/docs/en/settings#lists-merge-instead-of-overriding); [settings precedence](https://code.claude.com/docs/en/settings#settings-precedence)). The profile sets `allowUnsandboxedCommands` to `false`, which makes the sandbox admin-required. Claude Code then ignores a repository's `excludedCommands`, write allowances, extra allowed domains and weakening switches. It does not ignore your own `~/.claude/settings.json` ([repository settings under an admin-required sandbox](https://code.claude.com/docs/en/sandboxing#repository-settings-under-an-admin-required-sandbox)).

Under the profile, `/sandbox` does not open. It prints `Sandbox settings can't be changed here. Higher-priority settings override them.`, because the profile sets sandbox keys above the local level ([troubleshooting](https://code.claude.com/docs/en/sandboxing#sandbox-fails-with-sandbox-settings-cant-be-changed-here)). Check the configuration in three steps instead:

1. **Read the other scopes.** Start a session in the same project without the profile and open `/sandbox`. Its Config tab lists what your user, project and local files add: allowed domains, write paths, excluded commands, read re-openings and any weakening switch set to `true` ([get started](https://code.claude.com/docs/en/sandboxing#get-started)). Remove what you did not mean to keep.
2. **Read the profile session.** Start a session with the profile. `/status` lists the settings sources that loaded, and its `Setting sources` line should include `Command line arguments`. `claude doctor`, run from a terminal, lists settings entries that Claude Code rejected ([confirm what loaded](https://code.claude.com/docs/en/settings#confirm-what-loaded)). `/permissions` lists every rule and the file it comes from. Look there for `WebFetch(domain:...)` allow rules, which add hosts to the sandbox allowlist, and for narrow `Bash(...)` allow rules, which in auto mode skip the classifier ([manage permissions](https://code.claude.com/docs/en/permissions#manage-permissions); [network isolation](https://code.claude.com/docs/en/sandboxing#network-isolation); [suspend shell allow rules](https://code.claude.com/docs/en/auto-mode-config#suspend-shell-allow-rules)).
3. **Read the auto-mode rules.** From a terminal, run `claude --settings ~/.tachi/session-profile.json auto-mode config`. It prints the four rule lists with your settings applied. The profile's `environment` and `hard_deny` entries should follow the built-in ones, and the literal `"$defaults"` should not appear ([inspect the defaults and your effective config](https://code.claude.com/docs/en/auto-mode-config#inspect-the-defaults-and-your-effective-config)). If the profile's entries are missing, pass the same JSON inline, as `claude --settings "$(cat ~/.tachi/session-profile.json)" auto-mode config`, and start your sessions the same way: the docs list the `--settings` flag as inline JSON for `autoMode` and show no file form ([where the classifier reads configuration](https://code.claude.com/docs/en/auto-mode-config#where-the-classifier-reads-configuration)). The output does not show the server's built-in rules, which can differ from it while `/status` reports `Auto mode server` as `Enabled`.

Then run the probes under the profile (§4).

### TLS termination and the image key

Masking the image key needs TLS termination. The sandbox proxy substitutes the real key inside the request, so it has to read the request ([mask credentials](https://code.claude.com/docs/en/sandboxing#mask-credentials)). The profile therefore sets `sandbox.network.tlsTerminate`. The setting is experimental, and it lets the local proxy read the HTTPS requests of sandboxed commands, including the content of any request to the Gemini host. It adds no content filtering ([`sandbox.network.tlsTerminate`](https://code.claude.com/docs/en/settings-reference#sandbox-network-tlsterminate); [security limitations](https://code.claude.com/docs/en/sandboxing#security-limitations)). With `{}`, Claude Code makes an ephemeral CA for the session. Claude Code honors the setting and the `mask` entry only from user settings, managed settings and `--settings`, so a repository cannot switch either on.

If you do not accept that, deny the key: do not set `GEMINI_API_KEY`. tachi then skips the image request, and every other output is produced as usual (§1). This key-less run is the isolated default. If you remove `tlsTerminate` from your copy, remove the `credentials.envVars` entry with it. Masking fails without TLS termination: the sentinel reaches the server unchanged, so the image request fails authentication. `claude doctor` reports `TLS termination is unavailable` for the misconfiguration, and the docs do not say whether it reads a file passed with `--settings`.

### Secret files and the process environment

Read deny rules are the primary secret-file control. The Read tool runs outside the sandbox, so a `credentials.files` entry does not stop it and a permission rule does ([what runs outside the sandbox](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox)). Claude Code merges the paths of Read deny rules into the sandbox's own read denies, so sandboxed commands are blocked at the operating-system level as well ([`sandbox.filesystem.denyRead`](https://code.claude.com/docs/en/settings-reference#sandbox-filesystem-denyread); [permission rules and the sandbox](https://code.claude.com/docs/en/sandboxing#permission-rules)). Read deny rules also cover the file commands that Claude Code recognizes, such as `cat`, and shell redirections. They cover Grep and Glob on a best-effort basis, and they do not cover arbitrary subprocesses ([what Read and Edit rules cover](https://code.claude.com/docs/en/permissions#what-read-and-edit-rules-cover)).

The profile denies `~/.ssh`, `~/.aws`, Claude Code's login file `~/.claude/.credentials.json`, `.env*` files under the working directory and, on Linux, `/proc`. The `/proc` rule matters because the Read tool runs inside the Claude Code process. On Linux, a process's environment can be read through `/proc`, and `/proc/self` is the process that does the reading ([`proc_pid_environ(5)`](https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html); [`proc_self(5)`](https://man7.org/linux/man-pages/man5/proc_self.5.html)). That environment holds the real image key and any provider credential you set in the environment. On macOS there is no `/proc`, and the rule has no effect.

**Other credential stores.** The profile does not cover every store. For each of these that you keep, add a Read deny rule and a `credentials.files` entry in the home-anchored forms the block uses for `~/.ssh`: `~/.claude.json` (account details and your personal MCP server definitions, which can hold credentials), `~/.netrc`, `~/.git-credentials`, `~/.kube`, `~/.docker/config.json` and the configuration directories of your cloud CLIs ([protect credentials](https://code.claude.com/docs/en/sandboxing#protect-credentials); [file reference](https://code.claude.com/docs/en/claude-directory#file-reference)). Put them in your user settings. Lists merge with the profile's, and the block stays identical to the one published here.

If you set `CLAUDE_CONFIG_DIR`, the login file lives at `<that directory>/.credentials.json`. Write both entries for that path in the `~/` or `//` form, because the documented path forms expand no variables. On macOS, Claude Code normally keeps its login in the Keychain, which is not a file, and uses the file only as a fallback ([credential management](https://code.claude.com/docs/en/authentication#credential-management)).

### MCP servers, hooks and the status line

The profile denies every MCP tool with `mcp__*`. That removes the tools from Claude's context, including the claude.ai connectors that Claude Code fetches itself, which appear as `mcp__claude_ai_<server>__<tool>` ([tool name wildcards](https://code.claude.com/docs/en/permissions#tool-name-wildcards); [MCP rules](https://code.claude.com/docs/en/permissions#mcp)).

A deny rule does not stop a configured local MCP server from starting, and such a server runs outside the sandbox with your full access ([what runs outside the sandbox](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox)). List each server you have in `deniedMcpServers` in your user settings, as `{ "serverName": "<name>" }` entries, which stops it from loading, or confirm that you have none: `claude mcp list` shows every configured server ([`deniedMcpServers`](https://code.claude.com/docs/en/settings-reference#deniedmcpservers); [managing your servers](https://code.claude.com/docs/en/mcp#managing-your-servers)). The profile cannot carry that list, because its key set is closed.

Command hooks, plugin monitors, LSP servers, mods and helper commands such as the status line and `apiKeyHelper` also run outside the sandbox with your full access. They can receive the environment of the Claude Code process, which holds the real image key. Review them before a session that holds the key. §9 lists everything that runs outside the sandbox.

### The classifier

The `autoMode` block keeps Claude Code's built-in rules in every list (`"$defaults"`), adds facts about this machine to `environment` and adds one prohibition to `hard_deny`.

- **Trust comes only from `environment` entries.** They tell the classifier which hosts and locations are trusted, so a destination that they do not name stays a possible exfiltration target ([define trusted infrastructure](https://code.claude.com/docs/en/auto-mode-config#define-trusted-infrastructure)).
- **`hard_deny` only prohibits.** Its entries block the actions they describe even when you ask for them, and nothing in it grants access ([override the block and allow rules](https://code.claude.com/docs/en/auto-mode-config#override-the-block-and-allow-rules)).
- **The classifier reads commands, not their output.** In the requests Claude Code sends it, tool results are stripped. It sees your messages, the tool calls other than read-only lookups, and your CLAUDE.md content ([how auto mode evaluates actions](https://code.claude.com/docs/en/permission-modes#how-auto-mode-evaluates-actions)). It can refuse a command that would send tachi's content to another host. It cannot judge what a file or a command's output said.
- **Sandboxed commands reach it.** The profile sets `autoAllowBashIfSandboxed` to `false`, so sandboxed commands go through the regular permission flow, whatever the version default is (`true` before v2.1.324) and whatever a repository, local or user file sets ([`sandbox.autoAllowBashIfSandboxed`](https://code.claude.com/docs/en/settings-reference#sandbox-autoallowbashifsandboxed)). In auto mode they therefore reach the classifier and its `hard_deny` like any other command. Read-only commands, and commands that a narrow allow rule matches, can still skip it ([how auto mode evaluates actions](https://code.claude.com/docs/en/permission-modes#how-auto-mode-evaluates-actions); [suspend shell allow rules](https://code.claude.com/docs/en/auto-mode-config#suspend-shell-allow-rules)). In Manual mode, sandboxed commands prompt like other commands, apart from the built-in read-only set ([regular permissions mode](https://code.claude.com/docs/en/sandboxing#regular-permissions-mode); [read-only commands](https://code.claude.com/docs/en/permissions#read-only-commands)).
- **No extra host for a single command.** `strictAllowlist` also makes Claude Code refuse auto mode's per-command host lists, so no host outside `allowedDomains` opens for one command ([per-command allowed domains in auto mode](https://code.claude.com/docs/en/sandboxing#per-command-allowed-domains-in-auto-mode)).

### Key provisioning

The image key is optional (§1). To use it, inject `GEMINI_API_KEY` into the environment of the `claude` process from your secret manager, and nowhere else. The sandbox masks a variable that Claude Code inherits from its own environment ([mask environment variables](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)).

- Never put the key in a file the session can read: not a `.env` file, not a settings file, not a shell startup file. Never type it into a prompt, because prompts go to your model provider and into the plaintext transcript (§1, §7).
- Read the key from your secret manager in the command that starts `claude`, so it exists only in that process's environment. Replace `your-secret-manager-read-command` with the command that prints the key to standard output:

  ```
  GEMINI_API_KEY="$(your-secret-manager-read-command)" claude --settings ~/.tachi/session-profile.json
  ```

- A wrapper that runs `claude` as a child process, such as `op run`, masks the child's output by default and can disturb an interactive session. If you use one, try it before a real run. §11 records the exact form that worked in the live validation.
- Run the archiver (§7) under the same secret-injection wrapper as the session, with the same variables set. Its final scan compares what it writes with the values of secret-named variables in its own environment, so an archiver started from a shell that lacks them checks fewer values. It prints how many it checked.

**What the mask does and does not do.** The image key is masked for sandboxed commands: they see a placeholder, and the sandbox proxy substitutes the real value only on connections to `generativelanguage.googleapis.com`. The real value is still held by the Claude Code process, which runs outside the sandbox, and it can reach hooks, the status line and local MCP servers, which Claude Code starts outside the sandbox, unless you scrub the environment. The Read denies in the profile keep Claude's file tools away from that environment on Linux and from Claude Code's own login file; whatever a tool does read is written to the plaintext transcript. `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` is the documented switch that strips credentials from those subprocesses. The profile does not set it, and the docs do not say how it combines with a masked variable ([what the subprocess environment scrub removes](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes)).

**Everything else in the launch environment reaches sandboxed commands.** Sandboxed commands inherit the whole environment of the Claude Code process, and the mask covers one variable ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)). A provider credential that you set in the environment, such as `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`, therefore reaches them. There are two remedies. Launch from a minimal environment that lists only what the session needs:

```
env -i HOME="$HOME" USER="$USER" SHELL="$SHELL" PATH="$PATH" TERM="$TERM" \
  LANG="${LANG:-en_US.UTF-8}" TMPDIR="${TMPDIR:-/tmp}" \
  GEMINI_API_KEY="$(your-secret-manager-read-command)" \
  "$(command -v claude)" --settings ~/.tachi/session-profile.json
```

Add whatever else your setup needs, such as `TACHI_MMDC_PUPPETEER_CONFIG` on Linux (§6). Or add a `deny` entry for each such variable under `sandbox.credentials.envVars` in your user settings, which removes the variable from the environment of sandboxed commands ([protect credentials](https://code.claude.com/docs/en/sandboxing#protect-credentials)). Signing in with `/login` keeps your Claude Code credential out of the environment: it is stored in the macOS Keychain or in a file that the profile denies ([credential management](https://code.claude.com/docs/en/authentication#credential-management)).

The docs do not say whether a sandboxed command on macOS can read another process's environment, for example with `ps eww`. Until you have checked it on your machine, assume that it can.

### Model selection

**Which model runs tachi's agents.** tachi pins every agent to the `sonnet` model alias. An agent with an alias runs on the version the alias points to, with one exception: when your session itself runs on a Sonnet model, the agents run on that same version ([which version a model alias selects](https://code.claude.com/docs/en/sub-agents#which-version-a-model-alias-selects)). These change it ([choose a model](https://code.claude.com/docs/en/sub-agents#choose-a-model)):

- A model passed when an agent is started overrides the pin. No tachi command, agent or skill text passes one.
- `ANTHROPIC_DEFAULT_SONNET_MODEL` changes which model the alias points to ([model configuration: environment variables](https://code.claude.com/docs/en/model-config#environment-variables)).
- `CLAUDE_CODE_SUBAGENT_MODEL` alone leaves the pins in place. With `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` also set (v2.1.257 or later), every agent runs on that one model and the pins are ignored ([run every subagent on one model](https://code.claude.com/docs/en/sub-agents#run-every-subagent-on-one-model)). If your shell or user settings set both, tachi's pins stop applying, and nothing in tachi shows it.

The pin is the model Claude Code asks for, and the model that answers can differ. An organization's model allowlist can substitute another model, and a fallback can move a request when a model is unavailable or when a flagged request re-runs on another model ([when an allowlist blocks a subagent model](https://code.claude.com/docs/en/sub-agents#when-an-allowlist-blocks-a-subagent-model); [fallback model chains](https://code.claude.com/docs/en/model-config#fallback-model-chains); [automatic model fallback](https://code.claude.com/docs/en/model-config#automatic-model-fallback)). The session transcripts record the model that served each turn, and `/tasks` names the model a running agent uses (v2.1.242 or later; [check a subagent's model](https://code.claude.com/docs/en/sub-agents#check-a-subagents-model)). Program access applies only to the models your program covers, which the program's Help Center article lists ([Cyber Verification Program](https://support.claude.com/en/articles/14604842-cyber-verification-program)). The matrix linked in §10 records the pins, and its legend (§8.1 of the permissions standard) covers the rest.

### Settings sources

`--setting-sources` limits which settings files a session loads ([CLI reference: flags](https://code.claude.com/docs/en/cli-reference#cli-flags)). Do not use it by default.

- **Excluding `project` stops tachi from running.** The docs define the `project` source to include project skills, commands and subagents, and tachi installs its agents, commands and skills into your project. A session that leaves out `project` would not load them ([control filesystem settings with settingSources](https://code.claude.com/docs/en/agent-sdk/claude-code-features#control-filesystem-settings-with-settingsources)).
- **Excluding `user` is opt-in hardening, with costs.** It keeps your own user entries, such as excluded commands, write paths and extra allowed domains, out of the effective configuration. The costs:
  - Provider and authentication configuration that lives in user settings, such as `env`, `apiKeyHelper` and cloud credential helpers, is not read.
  - User-scope environment-variable masks are dropped, and user-scope `sandbox.filesystem` entries, `Edit` rules and Read deny rules are ignored when the sandbox configuration is built. User-scope `deny` entries under `sandbox.credentials` still apply ([protect credentials](https://code.claude.com/docs/en/sandboxing#protect-credentials); [configure sandboxing](https://code.claude.com/docs/en/sandboxing#configure-sandboxing)).
  - The retention sweep pauses when no enabled source sets `cleanupPeriodDays` ([retention sweep event](https://code.claude.com/docs/en/monitoring-usage#retention-sweep-event)).
  - A mode dialog that your user file suppressed can appear again. The docs state this for the bypass-permissions warning, which the profile does not use ([skip all checks with bypassPermissions mode](https://code.claude.com/docs/en/permission-modes#skip-all-checks-with-bypasspermissions-mode)).

The docs do not say whether a file passed with `--settings` still applies when `--setting-sources` leaves sources out. If you try the flag, repeat the effective-configuration check above.

### Your user settings

Keep the profile as published and put your own additions in `~/.claude/settings.json`: the extra credential-store rules, the `deniedMcpServers` entries and, for retention, `cleanupPeriodDays`, which stays at user scope and is never lowered (§7).

One more addition is optional. The profile applies to tachi sessions only. To sandbox every Claude Code session on the machine, merge the profile's `sandbox` object into your user settings. Merge it, do not replace the file: lists combine across scopes, so your own entries stay and the profile's are added ([lists merge instead of overriding](https://code.claude.com/docs/en/settings#lists-merge-instead-of-overriding)). Claude Code honors `mask` entries and `tlsTerminate` from user settings ([mask credentials](https://code.claude.com/docs/en/sandboxing#mask-credentials)). Two cautions. With the copy in place, sandboxed commands in every session reach only the Gemini host and whatever else your own files allow, so use it only where you want that. And the copy carries `autoAllowBashIfSandboxed: false`, so your other sessions in Manual mode prompt for sandboxed commands. Leave that key out of your copy if you want the version default in those sessions: the profile sets it for tachi sessions either way.

### Forms and scope

- **Path forms.** In permission rules, avoid the single-slash `/path` form. It anchors at the profile file's directory, not at the filesystem root. The `~/`, `//` and working-directory-relative forms are fine. Sandbox path lists use the opposite convention, where `/path` is absolute, so a path copied between the two changes its meaning ([where a pattern anchors](https://code.claude.com/docs/en/permissions#where-a-pattern-anchors); [sandbox path prefixes](https://code.claude.com/docs/en/settings-reference#sandbox-path-prefixes)).
- **Keep the bare `WebFetch` deny.** `WebFetch(domain:*)` in `deny` also denies every host to sandboxed commands, the Gemini host included ([allow or deny every fetch](https://code.claude.com/docs/en/permissions#allow-or-deny-every-fetch)).
- **Local sessions only.** In an Anthropic-hosted cloud session, `failIfUnavailable` lets the session start with a warning, and the `sandbox.filesystem` and `sandbox.network` rules are not enforced ([`sandbox.failIfUnavailable`](https://code.claude.com/docs/en/settings-reference#sandbox-failifunavailable)). The `env` key also keeps Claude Code's artifact publishing off (§1).

## 4. Probe table

Run these probes first, inside a session that you started with the profile. Ask Claude to run each line. What you type at the `!` prompt usually runs outside the sandbox, so typing a line yourself does not test it ([confirm commands run inside the sandbox](https://code.claude.com/docs/en/sandboxing#confirm-commands-run-inside-the-sandbox)). The profile turns the unsandboxed retry off ([turn off the retry with strict sandbox mode](https://code.claude.com/docs/en/sandboxing#turn-off-the-retry-with-strict-sandbox-mode)). If a prompt still offers to run a probe outside the sandbox, decline it.

| Probe | Pass | Layer that should refuse |
|---|---|---|
| `touch ~/sandbox-probe` | Fails with `Operation not permitted` (macOS) or `Read-only file system` (Linux, WSL2). If it succeeds, delete `~/sandbox-probe` and stop: the sandbox is not confining writes, so check the effective configuration (§3) | Sandbox, filesystem |
| `curl --noproxy '*' https://example.com` | Fails with `Could not resolve host`, because the command has no route around the sandbox proxy | Sandbox, network |
| `curl -sS https://example.com` | Fails without reaching `example.com`. The result names the host as blocked and no prompt appears, which shows that `strictAllowlist` is in force ([hosts outside your allowed domains](https://code.claude.com/docs/en/sandboxing#hosts-outside-your-allowed-domains)) | Sandbox proxy |
| A planted `.env`: from another terminal, create `.env` in the project root holding only `PROBE=not-a-secret`. Then ask Claude to read it with the Read tool and to run `cat .env`. Delete the file afterwards | Both are refused, and no file content appears in either result | The permission rule `Read(.env*)`; for `cat`, the same rule or the sandbox's read denies ([what Read and Edit rules cover](https://code.claude.com/docs/en/permissions#what-read-and-edit-rules-cover)) |
| WebFetch: ask Claude to fetch `https://example.com` with WebFetch | Denied. Claude has no WebFetch tool or the call is refused, and no page content comes back ([allow or deny every fetch](https://code.claude.com/docs/en/permissions#allow-or-deny-every-fetch)) | The permission rule `WebFetch` |
| Secret-store rules (a configuration check): run `/permissions` | The list holds the profile's deny rules, among them `Read(//proc/**)` and `Read(~/.claude/.credentials.json)`, and no startup warning names an invalid rule ([manage permissions](https://code.claude.com/docs/en/permissions#manage-permissions)) | Configuration |
| Linux and WSL2, seccomp filter (a check: `/sandbox` does not open under the profile, so run it in a session started without the profile): run `/sandbox` | No Dependencies tab appears beside the other tabs. If one lists the seccomp filter, install it with `npm install -g @anthropic-ai/sandbox-runtime`, restart Claude Code and check again before the first session with the profile ([set up Linux and WSL2](https://code.claude.com/docs/en/sandboxing#set-up-linux-and-wsl2)) | Configuration |

**Record which layer refused each line.** A refusal by a permission rule or by the auto mode classifier is not a sandbox result. If one stops a `touch` or `curl` line, approve the action under `/permissions`, on the Recently blocked tab, and ask Claude to retry it, so the sandbox gets to answer ([review denials](https://code.claude.com/docs/en/auto-mode-config#review-denials)).

**Never plant a real secret.** A probe that fails open writes what it reads into the plaintext transcript ([plaintext storage](https://code.claude.com/docs/en/claude-directory#plaintext-storage)). Use a dummy value, and never point a probe at a real credential file such as Claude Code's login file. The rules for those paths are checked by configuration, in the table above.

### Optional on Linux: the `/proc` rule

This check reads a dummy variable, never a real secret. Run it only in a session whose environment holds no key and no provider credential. If you sign in through an environment variable, skip it. Sandboxed commands inherit the environment of the Claude Code process ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)), so start the session from a cleaned environment that holds one dummy variable (`<file>` is your saved profile):

```
env -i HOME="$HOME" USER="$USER" SHELL="$SHELL" PATH="$PATH" TERM="$TERM" \
  LANG="${LANG:-en_US.UTF-8}" TMPDIR="${TMPDIR:-/tmp}" TACHI_PROBE_DUMMY=not-a-secret \
  "$(command -v claude)" --settings <file>
```

Then ask Claude to do each of these:

1. Use the Read tool on `/proc/self/environ`. Pass: the call is refused with a permission message, and no line of the environment appears. A refusal here comes from the permission rule `Read(//proc/**)` ([how path patterns match](https://code.claude.com/docs/en/permissions#how-path-patterns-match)).
2. Run the line below, where `<CLAUDE_PID>` is the process ID of the `claude` process. From another terminal, `pgrep -n -f -- '--settings <file>'` prints it. Pass: it prints `not-readable`. A result of `readable` means that a sandboxed command can read the environment of the Claude Code process, which holds the real key when you provide one. Do not provide the key on that machine unless a boundary surrounds the whole Claude Code process (§9).

   ```
   test -r /proc/<CLAUDE_PID>/environ && echo readable || echo not-readable
   ```

   The docs state that the subprocess scrub isolates Bash commands from host process environments on Linux. They only imply that the default Linux sandbox does the same, so this line is the check ([what the subprocess environment scrub removes](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes); [`sandbox.enableWeakerNestedSandbox`](https://code.claude.com/docs/en/settings-reference#sandbox-enableweakernestedsandbox)).

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

This runbook targets macOS, Linux and WSL2. Native Windows is not supported for isolated operation. The header names the platforms that ran in the live validation, and §11 records the result for each.

### macOS

The sandbox uses the built-in Seatbelt framework, so nothing needs installing ([get started](https://code.claude.com/docs/en/sandboxing#get-started)). The `Read(//proc/**)` rule in the profile has no effect there, because macOS has no `/proc`.

### Linux and WSL2

Install the sandbox's two packages, `bubblewrap` and `socat`, with your distribution's package manager. On Ubuntu and Debian, run `sudo apt-get install bubblewrap socat`. On Fedora, run `sudo dnf install bubblewrap socat`. WSL2 is required, because WSL1 does not run the sandbox ([set up Linux and WSL2](https://code.claude.com/docs/en/sandboxing#set-up-linux-and-wsl2)). Also install the optional seccomp filter and check it as §4 describes. Without the filter the sandbox does not block Unix-socket connections, such as a container runtime's socket or, on WSL2, the socket that launches Windows programs ([`sandbox.network.allowAllUnixSockets`](https://code.claude.com/docs/en/settings-reference#sandbox-network-allowallunixsockets)).

**Diagram rendering.** On Linux and WSL2 a sandboxed command cannot create user namespaces, so Chromium, which `mmdc` starts to render the attack-tree and attack-chain diagrams, exits with `No usable sandbox!` ([Chromium fails inside the sandbox on Linux](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux)). tachi's recipe starts Chromium without its own sandbox:

1. Create a file outside the project that holds exactly this JSON, and check before each use that it holds nothing else. It sets the flags that Chromium starts with:

   ```json
   {"args": ["--no-sandbox"]}
   ```

2. Set `TACHI_MMDC_PUPPETEER_CONFIG` to the absolute path of that file, in the environment that starts `claude`, for example `export TACHI_MMDC_PUPPETEER_CONFIG="$HOME/.tachi/puppeteer-no-sandbox.json"`. Sandboxed commands inherit that environment ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)). When the variable is set, `scripts/extract-report-data.py` passes `-p <path>` to both `mmdc` runs. It stops with an error when the value is empty, is a relative path or does not name an existing regular file.

The trade-off: with `--no-sandbox`, the renderer processes LLM-authored diagrams derived from the analysed repository with Claude Code's sandbox as its only boundary. Chromium's own sandbox is off ([Chromium fails inside the sandbox on Linux](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux)). The profile still confines the renderer's writes and network like those of any sandboxed command.

Do not work around the failure in any other way. Never add `excludedCommands`, `allowNestedUserNamespaces`, `enableWeakerNestedSandbox` or a write allowance: the profile forbids them, and each gives up isolation ([Chromium fails inside the sandbox on Linux](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux); [security limitations](https://code.claude.com/docs/en/sandboxing#security-limitations)). Running a step outside the isolated session is outside this runbook, and it is not an isolated-operation step.

### Native Windows

Not supported for isolated operation. The sandbox runs on macOS, Linux and WSL2 only. The profile sets `failIfUnavailable`, so on native Windows Claude Code exits at startup instead of running commands unsandboxed ([sandboxing overview](https://code.claude.com/docs/en/sandboxing); [`sandbox.failIfUnavailable`](https://code.claude.com/docs/en/settings-reference#sandbox-failifunavailable)). To use the profile on a Windows machine, run Claude Code inside a WSL2 distribution.

### What "validated" covers

"Validated" is the maintainer's own record of a live run. It is not a statement by Anthropic about this runbook. It means that the maintainer ran the profile in §3, the probes in §4 and a full tachi run, with and without the key, on the platform, Claude Code version and permission mode that the header names, and recorded the result in §11. A platform, version or mode that §11 does not list is not validated, and a step that did not run there is marked "not yet run live". §11 also records any step that was scoped out on a platform, for example diagram rendering on Linux, and any fallback that was applied. A change that one of the header's refresh triggers names ends the claim until the runbook is validated again.

## 7. Retention and provenance

Claude Code writes a transcript of every session, and the transcripts of tachi's agents are kept with it. The transcripts are plain text. Anything that passes through a tool is written to them: the architecture description, the files read, command output and the findings. They can also hold the system prompt, the tool definitions and the instruction files that Claude Code loaded. They are not encrypted, and file permissions are the only protection ([application data](https://code.claude.com/docs/en/claude-directory#application-data); [plaintext storage](https://code.claude.com/docs/en/claude-directory#plaintext-storage)). Treat them as sensitive as the threat model itself. They are the record of what ran: each turn records the model that served it, and §3 ("Model selection") says how to read which model ran.

**Retention.** Claude Code deletes transcripts once they are older than `cleanupPeriodDays`. The default is 30 days and the minimum is 1, and `0` fails validation ([`cleanupPeriodDays`](https://code.claude.com/docs/en/settings-reference#cleanupperioddays); [cleaned up automatically](https://code.claude.com/docs/en/claude-directory#cleaned-up-automatically)). The 30-day default meets the retention floor that §9 maps. Keep the key at user scope, in `~/.claude/settings.json`, and never lower it. The profile does not set it, so the profile neither protects nor lowers retention.

Any settings file can lower the key: your user file, your project's `.claude/settings.json` and `.claude/settings.local.json`, a file passed with `--settings`, or managed settings. The highest-ranked source that sets the key wins ([settings precedence](https://code.claude.com/docs/en/settings#settings-precedence)). Before each session, look for a lower value:

```
grep -n cleanupPeriodDays ~/.claude/settings.json .claude/settings.json .claude/settings.local.json
```

`/status` shows whether managed settings are in effect ([confirm what loaded](https://code.claude.com/docs/en/settings#confirm-what-loaded)). If any file lowers the key, raise it again, or archive the transcripts you need by copying them out of `~/.claude/projects/` before you start another session. Claude Code deletes old transcripts in a background sweep that starts after a session starts, so the copy has to finish first. The docs do not say whether a session that lowers the value also deletes the transcripts of other projects, so assume that it does ([retention sweep event](https://code.claude.com/docs/en/monitoring-usage#retention-sweep-event)). Keep any copy as protected as the original.

### The run archive and the run manifest

`scripts/archive-run-transcripts.py` copies one finished session to a directory outside `~/.claude/projects/`, where Claude Code's retention sweep works, and writes `run-manifest.json` beside the copy. It needs Python 3.9 or later and no packages. It makes the copy that the retention advice above calls for, and it records how the run was produced.

**Run it.** Run it from your own shell, in the project root, after the session has ended, and start it the way you started the session: under the same secret-injection wrapper, with the same variables set (§3). For a session that held the image key:

```
GEMINI_API_KEY="$(your-secret-manager-read-command)" \
  python3 -I -B scripts/archive-run-transcripts.py --latest --output-dir docs/security/<timestamp>
```

For a session that ran without the key, leave the variable out. `--latest` takes the newest session of this project, and `--session <id>` takes a named one. `--output-dir` names the run's output directory (§5), so that the manifest records a hash of every file in it. `--dest <dir>` overrides the destination. The `-I -B` flags stop a file planted beside the script from shadowing a standard-library module in a shell that holds your secrets, and a plain `python3` start restarts the script under them. The archiver is not part of the isolated session. Its default destination is in your home directory, which a sandboxed command cannot write, so it is not one of tachi's run commands and §5 does not list that destination.

**What it copies, and where.** It finds the project's transcripts under `~/.claude/projects/`, or under the directory that `CLAUDE_CONFIG_DIR` names, by matching their working directory to the project ([application data](https://code.claude.com/docs/en/claude-directory#application-data)). It copies the main transcript and the whole session directory beside it, which holds the subagent transcripts, their metadata files and the persisted tool results, byte for byte. The default destination is `~/.tachi/runs/<project>/<YYYY-MM-DD>-<session>/`. Directories are owner-only (mode 0700) and files are mode 0600.

**When it refuses.** The archiver exits 1 and writes nothing when the destination is inside a git work tree and git does not ignore every path the run would write there; when the destination is not empty (an identical, finished archive of the same session is a no-op, and anything else needs a new `--dest`); when the session looks live, meaning a file of it changed in the last 120 seconds, unless you pass `--allow-live`; when the destination is a symbolic link, or a link on its path leads into a work tree; and when the destination lies under Claude Code's projects directory, where the sweep could delete it. It exits 2 when it cannot work at all, for example when it finds no transcript for the project, or needs git for the work-tree check and cannot find it. It recognizes git work trees only: Mercurial, Subversion and Jujutsu work trees are not recognized, so keep `--dest` outside them.

**The archive is sensitive.** The copy is a full, unredacted transcript. It holds your architecture description, the files that were read, command output and the findings, and anything a tool printed, which can include a secret. It is owner-only, and the archiver refuses a destination that git could commit, but never commit it, attach it to a ticket or share it whole. Retention is yours: the archiver never deletes an archive, and nothing in tachi limits how long it lives. Keep it as protected as the original. A backup or indexing tool that reads `~/.tachi` picks the archive up too.

**The manifest.** `run-manifest.json` holds structure only: identifiers, counts, host names and hashes, never message text, tool input or output, command lines or URLs. It records:

- the tachi version of the install (`tachi_version`, from `templates/tachi/VERSION`, and `unknown` when the install recorded none), the session id, the Claude Code versions seen, the start, end and archive times, and a SHA-256 hash of every archived file;
- for the main session and for each subagent instance, the models that served its turns as a count of turns per model id (`served_model_histogram`), with its agent type, its spawn depth and its pin (`pinned_model`), which is the alias as your installed agent file writes it. A subagent type that the installed roster does not name, such as a built-in `general-purpose` instance, is listed too, with `pinned_model: null`. The archiver does not resolve the alias and does not compare it with the served model;
- every dispatch of a tachi agent at any depth with its outcome (`recorded`, `dispatch-failed` or `not-recorded`), and the installed tachi agents that were never dispatched, so a run in which the orchestrator analysed inline shows what never ran as an agent;
- the permission modes seen;
- the hosts that URLs in Bash commands and WebFetch calls named (`egress_observed`), and the calls that Claude Code denied, by host and kind: sandbox, classifier or permission rule (`egress_denied`);
- with `--output-dir`, a hash of every file in the run's output directory.

The run manifest records the model that actually served each turn. `pinned_model` is the alias that tachi asked for, and `served_model_histogram` counts the turns that each model id actually answered, so compare the two (§3, "Model selection").

**What it does not show.**

- `egress_observed` records what the session asked for, not what the network did. It sees only URLs, and it cannot see the child processes of a tool, such as a diagram renderer or a headless browser.
- `denial_detection` says whether an empty `egress_denied` can be read as "none denied". It reads `validated` only for Claude Code versions whose denial markers were checked against a recorded run. For every other version it reads `not-validated`, and an empty list proves nothing.
- The manifest is not signed. `pinned_model`, the agent roster and `tachi_version` are read from your project's files when the archiver runs, so a session that could write those files could have changed them. Treat the manifest as an aid to an audit, not as proof.

**Before you share the manifest.** The manifest is built to hold no secret. A final scan refuses to write it when a value that looks like a key, or the value of a secret-named environment variable (raw, or re-encoded as hex, base32, base64, percent-encoding or JSON escaping), reaches it. The scan skips variable values shorter than 8 characters, so the manifest's structure, not the scan, is what keeps a secret out. The archiver prints how many variables it compared, and warns when there were none. The manifest still names hosts, file names and session ids, so read it before you share it.

## 8. Reporting routes

Send each kind of problem to the party that can act on it. Keep the session transcripts first (§7). They are plain text and hold whatever passed through a tool, including your architecture, the files read and the findings, so share only what the recipient asks for ([application data](https://code.claude.com/docs/en/claude-directory#application-data); [plaintext storage](https://code.claude.com/docs/en/claude-directory#plaintext-storage)).

| What you observed | Where to report it |
|---|---|
| **Out-of-scope model behaviour** in a run: an agent probing its sandbox or network isolation, or acting outside its task, such as trying a host other than the two in §1 | Your Anthropic account team, which the program's containment guidance names for this ([Agent containment best practices for CVP participants](https://support.claude.com/en/articles/17317514-agent-containment-best-practices-for-cvp-participants)). If you have no account team, use the program's own channel: your program page in the [Verification Portal](https://portal.anthropic.com/programs) and your program terms ([Cyber Verification Program](https://support.claude.com/en/articles/14604842-cyber-verification-program)). Anthropic's [Responsible Disclosure Policy](https://www.anthropic.com/responsible-disclosure-policy) names `usersafety@anthropic.com` for model safety concerns |
| **A suspected breach or misuse involving your program grant** | Anthropic, within 72 hours, or within 24 hours for a security incident, at `security@anthropic.com` or your account team contact. The program's security requirements apply this to individual grants too ([Cyber Verification Program Security Requirements](https://support.claude.com/en/articles/17202708-cyber-verification-program-security-requirements)) |
| **A block on work your tier should allow** | The program's [false-positive report form](https://claude.com/form/cyber-block-false-positive-report-cvp-rejection-appeal), linked from the program announcement ([Expanding the Cyber Verification Program](https://www.anthropic.com/news/cyber-verification-program)) |
| **A defect or vulnerability in tachi**, including behaviour that traces to tachi's instructions, scripts or templates | tachi's private advisory route, [Report a vulnerability](https://github.com/davidmatousek/tachi/security/advisories/new), as [`SECURITY.md`](https://github.com/davidmatousek/tachi/blob/main/SECURITY.md#reporting-a-vulnerability) describes. Do not open a public issue |
| **A false positive or a missed threat** in a threat model | A public [GitHub issue](https://github.com/davidmatousek/tachi/issues), as `SECURITY.md` describes |
| **A defect in Claude Code itself**, such as a sandbox bypass | Anthropic, not tachi (`SECURITY.md`, Out-of-scope) |

The Anthropic pages and addresses in this table were retrieved on 2026-11-19. One observation can need two reports: an agent that leaves its task because of a tachi instruction goes to the program's channel and to tachi's advisory route.

## 9. Program mapping

Anthropic publishes containment guidance for people who use its most capable models through the Cyber Verification Program ([Agent containment best practices for CVP participants](https://support.claude.com/en/articles/17317514-agent-containment-best-practices-for-cvp-participants), dated 2026-10-06, retrieved 2026-11-19). This section paraphrases each item and marks how far this runbook goes. Read the guidance itself for the full text. The mapping is tachi's own reading, not a statement by Anthropic. The guidance gives recommendations. The program's security requirements are a separate document and are not mapped here; §8 gives their reporting route.

**Markers.**

- **Profile**: covered by the session profile (§3).
- **Boundary**: needs a process-level boundary, one around the whole Claude Code process. Claude Code documents three: the [sandbox runtime](https://code.claude.com/docs/en/sandbox-environments#sandbox-runtime), a [dev container](https://code.claude.com/docs/en/devcontainer) and a [virtual machine](https://code.claude.com/docs/en/sandbox-environments#virtual-machine) ([compare them](https://code.claude.com/docs/en/sandbox-environments#compare-sandboxing-approaches)).
- **Operator**: yours to do or to keep, outside the session profile.
- **tachi**: covered by tachi's own design.

A row carries two markers when the profile covers part of an item.

### The sandbox covers shell commands only

The profile's sandbox covers shell commands only, with the processes they start. Claude's file and web tools, hooks and MCP servers run outside it ([sandboxing](https://code.claude.com/docs/en/sandboxing)). The full list of what runs outside ([what runs outside the sandbox](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox)):

- Claude's file and web tools, such as Read, Edit, Write, WebFetch and WebSearch. Permission rules govern them instead. The profile's deny rules cover the web tools and the secret paths (§3).
- MCP servers. The profile denies every MCP tool, but a configured local server still starts and runs outside the sandbox (§3).
- Command hooks, plugin monitors, LSP servers, mods, and helper commands such as the status line and `apiKeyHelper`. They run with your full access.
- Commands you type yourself at the `!` prompt ([strict sandbox mode](https://code.claude.com/docs/en/sandboxing#turn-off-the-retry-with-strict-sandbox-mode)).
- The Claude Code process itself, which keeps the credentials for its own model requests ([subprocess environment scrub](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes)).

To put all of these behind one boundary, run Claude Code inside a process-level boundary.

**Domain fronting.** The allow-list works on hostnames. By default the sandbox proxy decides from the hostname a client supplies, without inspecting TLS. Code inside the sandbox could therefore use domain fronting or a similar technique to reach a host that is not on the list. The caveat covers the one host the profile allows. The profile's `tlsTerminate` terminates TLS for key masking only: the docs say it adds no content filtering, and they do not say it removes this caveat. If your threat model needs more, run a custom proxy that terminates and inspects TLS ([security limitations](https://code.claude.com/docs/en/sandboxing#security-limitations); [custom proxy configuration](https://code.claude.com/docs/en/sandboxing#custom-proxy-configuration)). The allow-list limits where sandboxed commands connect, not what they send to an allowed host. What tachi sends there rests on its design (§1).

### The guidance, item by item

tachi's work falls in the guidance's first category, local work that needs no internet access. Every item there is mapped. Three items from the network-testing category also apply to local work, and they follow.

| Guidance item | Paraphrase | Marker | In a tachi session under the profile |
|---|---|---|---|
| Sandbox and network isolation (1) | Run inside a virtual machine or a dedicated physical host | Boundary | The profile sandboxes shell commands on your own host. It is not a virtual machine |
| Sandbox and network isolation (2) | Block egress except to the model API | Profile, for shell commands. Boundary, for the rest | Sandboxed commands reach only the Gemini host. The allow-list is strict, there is no unsandboxed retry, and the session stops if the sandbox cannot start. WebFetch, WebSearch and every MCP tool are denied. The Gemini host stays allowed when you run without the key. Everything in the list above runs outside the sandbox |
| Sandbox and network isolation (3) | Reach the model API only through a local proxy, with the key added from outside the sandbox | Boundary, for the model connection. Profile, for the image key | The Claude Code process connects to your provider itself and holds its own credentials. A provider credential set in the environment is inherited by sandboxed commands (§3). For the image key, sandboxed commands see a placeholder, and the sandbox proxy adds the real key only on connections to the Gemini host ([mask credentials](https://code.claude.com/docs/en/sandboxing#mask-credentials)) |
| Sandbox and network isolation (4) | Tell the model not to use the internet | Profile, in part | The profile gives auto mode's classifier a rule against sending tachi's content to any other host. tachi's agent instructions do not yet say it themselves ([#360](https://github.com/davidmatousek/tachi/issues/360)) |
| Sandbox and network isolation (5) | Install every tool before the run, so nothing is fetched mid-run | tachi | See §1. Under the profile, a fetch to any other host would be refused |
| Pre-engagement validation (1) | Before live runs, probe the sandbox: review its configuration, then run a supervised escape attempt with no internet access | Operator | The probe table and the effective-configuration check (§3, §4) review the profile's settings. They are not an escape test. Run one yourself before you rely on the setup |
| Pre-engagement validation (2) | Confirm the agent has the tools it needs, and look for tasks it cannot complete | Operator | `/tachi.security-report` checks for typst, and for mmdc when diagrams exist, before it starts |
| Transcript retention and review (1) | Keep transcripts and egress logs for at least 30 days | Operator, for transcripts. Boundary, for an egress log kept off the host | Claude Code keeps transcripts for `cleanupPeriodDays`. Its 30-day default meets the floor, and the runbook keeps it at user scope, outside the profile (§7). The sandboxing docs describe no separate log of refused connections: a refused connection fails the command, and the command's output is in the transcript. An egress log kept off the host needs a proxy or firewall that you run |
| Transcript retention and review (2) | Review the transcripts of runs with denied or unexpected outbound requests, scan a sample automatically, and report out-of-scope behaviour | Operator | tachi ships no review tooling. Report through §8. The program's escape-score signal is not available in Claude Code ([getting started](https://support.claude.com/en/articles/17316076-agent-containment-best-practices-getting-started-private-beta)) |
| Use Claude Code's auto mode | Use auto mode, and describe the environment in `autoMode.environment` instead of turning the mode off | Profile | The profile keeps the built-in rules (`"$defaults"`), states facts about the machine and adds one prohibition. From v2.1.257 the built-in rules block common containment-escape actions ([what the classifier blocks by default](https://code.claude.com/docs/en/permission-modes#what-the-classifier-blocks-by-default)), and the runbook's minimum version is above that. If auto mode is unavailable, the session starts in Manual mode, and the header records the mode that ran |
| Explicit scope-setting | State the scope in the model's instructions as intent, not as a claim about the environment | Profile, in part | As for isolation item (4). The profile's rule is phrased as intent. Its environment entries are facts for the classifier, which the program's notes treat as separate from instructions ([sandboxing notes](https://support.claude.com/en/articles/17316105-agent-containment-best-practices-sandboxing-private-beta)) |
| Brokered tool use | Reach targets through observable tools, separate read-only tools from state-changing ones, and supervise the second group more closely | tachi, and Profile | 14 of tachi's 21 agents can only read. The writers and the shell-capable agents are listed in §10, and CI fails when an agent's declared tools change. tachi's commands run in your main session with its full toolset (§10). Under the profile, sandboxed commands stay in the regular permission flow: the classifier reviews them in auto mode, and Manual mode prompts for them (§3) |
| High-consequence targets | Keep autonomous agents away from live high-consequence systems, and stay passive where live access cannot be avoided | tachi | tachi is passive (§2) |

The two remaining network-testing items, scoping egress to in-scope targets and supervising runs that reach a target, assume a target on the network. A tachi run has none. In an interactive run you are the supervisor, and tachi sets no turn or time limit on its agents.

**Interactive use.** A tachi run is usually an interactive session. For interactive work the program's notes still recommend a sandbox, and either Manual mode, with a person reviewing each tool use, or auto mode with a person approving actions that reach outside the repository ([sandboxing notes](https://support.claude.com/en/articles/17316105-agent-containment-best-practices-sandboxing-private-beta)). The profile supplies the sandbox and auto mode. In auto mode the classifier, not a person, reviews those actions, and file reads outside the working directory run without a prompt after a one-time question in terminal sessions ([the first read outside the working directories](https://code.claude.com/docs/en/permission-modes#the-first-read-outside-the-working-directories)). For a person in that loop, use Manual mode. The block answer to that question sets [`permissions.blockReadsOutsideWorkingDirectories`](https://code.claude.com/docs/en/settings-reference#permissions-blockreadsoutsideworkingdirectories), which also keeps sandboxed commands out of your home directory, where typst, mmdc or its browser may be installed. It is not part of the profile or of the live validation.

**Where tachi differs from the notes.** The program's auto-mode notes recommend full model IDs, not aliases, for every agent stage, so that you can check before launch that each model supports auto mode ([auto-mode notes](https://support.claude.com/en/articles/17316089-agent-containment-best-practices-auto-mode-private-beta)). tachi pins the `sonnet` alias by design, and §3 says how to see and change what it resolves to. The same notes suggest classifier rules of your own, such as one against tampering with the session's setup. The profile adds none. If you add rules, put them in user or managed settings, because the classifier ignores `autoMode` in a project's settings files ([where the classifier reads configuration](https://code.claude.com/docs/en/auto-mode-config#where-the-classifier-reads-configuration)).

**Prompt injection.** It is not a listed practice, but the guidance flags it for agents that read content written outside your organization, such as third-party code in a checkout ([getting started](https://support.claude.com/en/articles/17316076-agent-containment-best-practices-getting-started-private-beta)). tachi's own hardening against it is tracked in [#360](https://github.com/davidmatousek/tachi/issues/360). Under the profile, an injected instruction meets the same limits as any other.

New program guidance is one of this runbook's refresh triggers (header).

## 10. Privilege matrix

The privilege matrix lists each tachi agent's tools, model, shell command families, written paths and hosts, and each command's dispatches, written paths and child processes. It is section 8 of `CLAUDE_PERMISSIONS.md` in the tachi repository. That file is not installed into your project, so the link is pinned to a release:

[Agent and command privilege matrix](https://github.com/davidmatousek/tachi/blob/v4.48.2/docs/standards/CLAUDE_PERMISSIONS.md#8-agent-and-command-privilege-matrix) <!-- x-release-please-version -->

The pin moves only when tachi cuts a release. A post-release `main` install therefore sees the previous release's matrix, which can differ from the agents you installed. No matrix exists before the first release that carries section 8.

tachi's CI runs a guard (`scripts/check-agent-privileges.py`) that compares the agent and command files with the matrix. Scope: the guard covers `.claude/agents/tachi/**` and `.claude/commands/tachi.*.md`, not the adapter copies under `adapters/claude-code/agents/`.

## 11. Live-validation record

_Recorded after the live validation run._
