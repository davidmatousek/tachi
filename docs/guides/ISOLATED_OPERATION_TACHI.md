# Isolated operation runbook for tachi

## 0. Header

- Last validated: 2026-11-20, on macOS 26.6.2 (arm64), Claude Code 2.1.330, auto mode (one Manual-mode check), key-less and keyed, tachi build `v4.48.2-103-gfe5125a`, with the session profile at SHA-256 `43496fb7d4fca098983a70648def8f1da2a2d1843528b5ca4c14444e32564279`. The published profile adds ten deny rules (§3). A key-less re-check on 2026-11-20 covered its startup, its rule list, the tool inventory, a refused isolated Agent call, the sandbox probes and one `/tachi.threat-model` run (§11).
- Minimum Claude Code version: v2.1.285
- Owner: the tachi maintainer
- Platforms the claim covers: macOS, except `/tachi.security-report` on runs with diagrams (§6). Linux and WSL2: not yet run live. §6 lists the platforms this runbook targets, and §11 names the ones that ran in the live validation.
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

This traffic belongs to Claude Code, not to tachi. The session profile sets `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, which turns off everything in the first table below. Any non-empty value turns the variable on, `0` and `false` included. Unset it to allow the traffic again ([environment variables](https://code.claude.com/docs/en/env-vars)).

| Traffic | Where it goes | Its own switch |
|---|---|---|
| Usage metrics. They never include code, prompts or file paths | Anthropic and third-party logging infrastructure | `DISABLE_TELEMETRY=1`, which also stops feature-flag fetching |
| Error reports, after Claude Code redacts known patterns of secrets, paths and personal data | A third-party error tracking service | `DISABLE_ERROR_REPORTING=1` |
| Feature-flag fetches | `api.anthropic.com` | `CLAUDE_CODE_DISABLE_FEATURE_FLAGS=1` (v2.1.319 or later; older versions read `DISABLE_GROWTHBOOK`) |
| Auto-updates, release notes, session surveys, status and availability checks, and `/feedback` and Claude-drafted feedback, which can send conversation history | The hosts listed in network access requirements | Only the nonessential-traffic variable covers all of them |
| Artifact publishing | `claude.ai` | Off while the nonessential-traffic variable is set |
| Remote Control, and the phone notifications and file delivery that need it | Anthropic-hosted infrastructure | Unavailable while the nonessential-traffic variable is set. A desktop notification stays on the machine |

Sources: [telemetry services](https://code.claude.com/docs/en/data-usage#telemetry-services); [environment variables](https://code.claude.com/docs/en/env-vars); [network access requirements](https://code.claude.com/docs/en/network-config#network-access-requirements); [artifact availability](https://code.claude.com/docs/en/artifacts#availability); [tools reference](https://code.claude.com/docs/en/tools-reference); [Remote Control](https://code.claude.com/docs/en/remote-control).

The nonessential-traffic variable does not cover these:

| Traffic | Its own switch | In a session under the profile |
|---|---|---|
| The WebFetch domain safety check. It sends each requested hostname, not the URL or the page, to `api.anthropic.com`, on every provider | `skipWebFetchPreflight: true` in settings | WebFetch is denied, so no fetch reaches the check |
| Official plugin marketplace auto-install, usually at a machine's first interactive launch | `CLAUDE_CODE_DISABLE_OFFICIAL_MARKETPLACE_AUTOINSTALL=1`, read at that moment | The profile does not set it. Set it in your environment before that first launch if you want the marketplace left unregistered |
| Gateway model discovery | Its own opt-in | Applies only behind an LLM gateway |

Sources: [default behaviors by API provider](https://code.claude.com/docs/en/data-usage#default-behaviors-by-api-provider); [WebFetch domain safety check](https://code.claude.com/docs/en/data-usage#webfetch-domain-safety-check); [environment variables](https://code.claude.com/docs/en/env-vars).

claude.ai connectors are fetched by default for claude.ai sign-ins, through `mcp-proxy.anthropic.com`. `ENABLE_CLAUDEAI_MCP_SERVERS=false` or `disableClaudeAiConnectors: true` stops that. The profile denies every MCP tool (`mcp__*`) and the three built-in tools that list and read MCP resources, so Claude can neither call a connector nor read its resources. The connectors still connect unless one of those two switches is set ([network access requirements](https://code.claude.com/docs/en/network-config#network-access-requirements)).

Some traffic stays on because Claude Code requires it: the model requests, the classifier checks, and sign-in and token refresh through `claude.ai` and `platform.claude.com` ([network access requirements](https://code.claude.com/docs/en/network-config#network-access-requirements)). On Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry and Claude Platform on AWS, metrics, error reports and `/feedback` reports are off by default. The WebFetch check and session surveys still run there ([default behaviors by API provider](https://code.claude.com/docs/en/data-usage#default-behaviors-by-api-provider)).

### Local tools

typst builds the PDF from the installed templates in `templates/tachi/security-report/`, which import only local files. mmdc renders the attack-tree and attack-chain diagrams through a headless browser that it starts on your machine (§10). On macOS the browser cannot start inside the sandbox (§6). tachi's installed scripts in `scripts/` load no network library, and the only programs they start are mmdc runs. All of these run as sandboxed commands, child processes included, so under the profile none of them could reach a host other than the Gemini host ([sandboxing](https://code.claude.com/docs/en/sandboxing)).

Nothing is fetched or installed mid-run. Install typst, mmdc (with the browser it uses) and python3 before a run. If typst or mmdc is missing, `/tachi.security-report` stops with an install hint, and no tachi command installs anything. The claim rests on the offline render check recorded in §11, which renders the diagrams with no network access and compares the images byte for byte. It does not rest on a run that logged no denials. Such a run shows only that nothing it tried was refused. §11 states how the check withheld network access.

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
      "ListMcpResourcesTool",
      "ReadMcpResourceTool",
      "ReadMcpResourceDirTool",
      "SendMessage",
      "ListAgents",
      "Monitor",
      "RemoteTrigger",
      "ShareOnboardingGuide",
      "Workflow",
      "Agent(isolation:*)",
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

1. **Read the other scopes.** Read the sandbox keys in your user settings (`~/.claude/settings.json`), your project's `.claude/settings.json` and its `.claude/settings.local.json`: allowed domains, write paths, excluded commands, read re-openings and any weakening switch set to `true`. `/status` shows whether managed settings are in effect ([confirm what loaded](https://code.claude.com/docs/en/settings#confirm-what-loaded)). A session started in the same project without the profile lists the same under `/sandbox`, in its Config tab, only when one of those scopes turns the sandbox on. Otherwise both panels read `Sandbox is not enabled` and list nothing ([get started](https://code.claude.com/docs/en/sandboxing#get-started)). Remove what you did not mean to keep.
2. **Read the profile session.** Start a session with the profile. `/status` lists the settings sources that loaded, and its `Setting sources` line should include `Command line arguments`. `claude doctor`, run from a terminal, lists settings entries that Claude Code rejected ([confirm what loaded](https://code.claude.com/docs/en/settings#confirm-what-loaded)). `/permissions` lists every rule and the file it comes from. Look there for `WebFetch(domain:...)` allow rules, which add hosts to the sandbox allowlist, and for narrow `Bash(...)` allow rules, which in auto mode skip the classifier ([manage permissions](https://code.claude.com/docs/en/permissions#manage-permissions); [network isolation](https://code.claude.com/docs/en/sandboxing#network-isolation); [suspend shell allow rules](https://code.claude.com/docs/en/auto-mode-config#suspend-shell-allow-rules)).
3. **Read the auto-mode rules.** From a terminal, run `claude --settings ~/.tachi/session-profile.json auto-mode config`. It prints the four rule lists with your settings applied. The profile's `environment` and `hard_deny` entries should follow the built-in ones, and the literal `"$defaults"` should not appear ([inspect the defaults and your effective config](https://code.claude.com/docs/en/auto-mode-config#inspect-the-defaults-and-your-effective-config)). If the profile's entries are missing, pass the same JSON inline, as `claude --settings "$(cat ~/.tachi/session-profile.json)" auto-mode config`, and start your sessions the same way: the docs list the `--settings` flag as inline JSON for `autoMode` and show no file form ([where the classifier reads configuration](https://code.claude.com/docs/en/auto-mode-config#where-the-classifier-reads-configuration)). The output does not show the server's built-in rules, which can differ from it while `/status` reports `Auto mode server` as `Enabled`. The live validation needed no inline form: the file form applied (§11).

Then run the probes under the profile (§4).

### TLS termination and the image key

Masking the image key needs TLS termination. The sandbox proxy substitutes the real key inside the request, so it has to read the request ([mask credentials](https://code.claude.com/docs/en/sandboxing#mask-credentials)). The profile therefore sets `sandbox.network.tlsTerminate`. The setting is experimental, and it lets the local proxy read the HTTPS requests of sandboxed commands, including the content of any request to the Gemini host. It adds no content filtering ([`sandbox.network.tlsTerminate`](https://code.claude.com/docs/en/settings-reference#sandbox-network-tlsterminate); [security limitations](https://code.claude.com/docs/en/sandboxing#security-limitations)). With `{}`, Claude Code makes an ephemeral CA for the session. Claude Code honors the setting and the `mask` entry only from user settings, managed settings and `--settings`, so a repository cannot switch either on.

If you do not accept that, deny the key: do not set `GEMINI_API_KEY`. tachi then skips the image request, and every other output is produced as usual (§1). This key-less run is the isolated default. If you remove `tlsTerminate` from your copy, remove the `credentials.envVars` entry with it. Masking fails without TLS termination: the sentinel reaches the server unchanged, so the image request fails authentication ([mask credentials](https://code.claude.com/docs/en/sandboxing#mask-credentials)). `claude doctor` reports `TLS termination is unavailable` for the misconfiguration, and the docs do not say whether it reads a file passed with `--settings`.

### Secret files and the process environment

Read deny rules are the primary secret-file control. The Read tool runs outside the sandbox, so a `credentials.files` entry does not stop it and a permission rule does ([what runs outside the sandbox](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox)). Claude Code merges the paths of Read deny rules into the sandbox's own read denies, so sandboxed commands are blocked at the operating-system level as well ([`sandbox.filesystem.denyRead`](https://code.claude.com/docs/en/settings-reference#sandbox-filesystem-denyread); [permission rules and the sandbox](https://code.claude.com/docs/en/sandboxing#permission-rules)). Read deny rules also cover the file commands that Claude Code recognizes, such as `cat`, and shell redirections. They cover Grep and Glob on a best-effort basis, and they do not cover arbitrary subprocesses ([what Read and Edit rules cover](https://code.claude.com/docs/en/permissions#what-read-and-edit-rules-cover)).

The profile denies `~/.ssh`, `~/.aws`, Claude Code's login file `~/.claude/.credentials.json`, `.env*` files under the working directory and, on Linux, `/proc`. The `/proc` rule matters because the Read tool runs inside the Claude Code process. On Linux, a process's environment can be read through `/proc`, and `/proc/self` is the process that does the reading ([`proc_pid_environ(5)`](https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html); [`proc_self(5)`](https://man7.org/linux/man-pages/man5/proc_self.5.html)). That environment holds the real image key and any provider credential you set in the environment. On macOS there is no `/proc`, and the rule has no effect. The live validation ran on macOS only, so the Linux `/proc` rule is not yet run live (§11).

**Other credential stores.** The profile does not cover every store. For each of these that you keep, add a Read deny rule and a `credentials.files` entry in the home-anchored forms the block uses for `~/.ssh`: `~/.claude.json` (account details and your personal MCP server definitions, which can hold credentials), `~/.netrc`, `~/.git-credentials`, `~/.kube`, `~/.docker/config.json` and the configuration directories of your cloud CLIs ([protect credentials](https://code.claude.com/docs/en/sandboxing#protect-credentials); [file reference](https://code.claude.com/docs/en/claude-directory#file-reference)). Put them in your user settings. Lists merge with the profile's, and the block stays identical to the one published here.

If you set `CLAUDE_CONFIG_DIR`, the login file lives at `<that directory>/.credentials.json`. Write both entries for that path in the `~/` or `//` form, because the documented path forms expand no variables. On macOS, Claude Code normally keeps its login in the Keychain, which is not a file, and uses the file only as a fallback ([credential management](https://code.claude.com/docs/en/authentication#credential-management)). Sandboxed commands can query the login Keychain; whether they can read Claude Code's own sign-in item was not tested (see the block below).

**Shell startup files and the Keychain (macOS).** Claude Code runs each sandboxed command with bash or zsh: the shell that `CLAUDE_CODE_SHELL` names, else `$SHELL` when that is bash or zsh, else the first working zsh, then bash. A launch environment without `SHELL` therefore gets zsh where zsh exists ([environment variables](https://code.claude.com/docs/en/env-vars)). The shell runs inside the sandbox, so whatever its startup files do happens there. zsh, the macOS default, reads `~/.zshenv` for every command, after the launch, so `env -i` cannot stop it ([zsh: Startup/Shutdown Files](https://zsh.sourceforge.io/Doc/Release/Files.html)).

- **Startup files.** A startup file that loads a credential, from the Keychain or a secret manager, puts it in the environment of every sandboxed command, whatever you left out of the launch environment. In the live validation one did exactly that under zsh. The measured sessions ran with bash (§11).
- **The Keychain.** On macOS, sandboxed commands can query your login Keychain. In the live validation a sandboxed command reached it, and an item whose access list trusts `/usr/bin/security` is read without a prompt.
- **What the profile cannot do.** The profile cannot stop this: permission rules govern the commands Claude issues, not what a shell's startup file or a child process does, and no sandbox setting in the docs removes a system service that the sandbox allows by default.
- **What to do.** Keep credential loading out of the startup files that your session's shell reads for every command: for zsh, `~/.zshenv`. Or launch with `SHELL=/bin/bash`, as the form under "Key provisioning" does. `CLAUDE_CODE_SHELL=/bin/bash` is the documented alternative ([environment variables](https://code.claude.com/docs/en/env-vars)), and it is not yet run live. Then check the names in a sandboxed command's environment with the "Environment names" row in §4. For a Keychain item that you cannot move, run Claude Code inside a process-level boundary (§9).
- **Not tested.** Whether a sandboxed command can read the item that holds Claude Code's own sign-in was not tested.

### MCP servers, hooks and the status line

The profile denies every MCP tool with `mcp__*`. That removes the tools from Claude's context, including the claude.ai connectors that Claude Code fetches itself, which appear as `mcp__claude_ai_<server>__<tool>` ([tool name wildcards](https://code.claude.com/docs/en/permissions#tool-name-wildcards); [MCP rules](https://code.claude.com/docs/en/permissions#mcp)). MCP resources are read through built-in tools whose names do not start with `mcp__`: `ListMcpResourcesTool` and `ReadMcpResourceTool`, which the tools reference lists, and `ReadMcpResourceDirTool`, which it does not list and which Claude Code 2.1.330 offered in the live validation. The profile denies all three by name ([tools reference](https://code.claude.com/docs/en/tools-reference)).

A deny rule does not stop a configured local MCP server from starting, and such a server runs outside the sandbox with your full access ([what runs outside the sandbox](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox)). List each server you have in `deniedMcpServers` in your user settings, as `{ "serverName": "<name>" }` entries, which stops it from loading, or confirm that you have none: `claude mcp list` shows every configured server ([`deniedMcpServers`](https://code.claude.com/docs/en/settings-reference#deniedmcpservers); [managing your servers](https://code.claude.com/docs/en/mcp#managing-your-servers)). The profile cannot carry that list, because its key set is closed.

Command hooks, plugin monitors, LSP servers, mods and helper commands such as the status line and `apiKeyHelper` also run outside the sandbox with your full access ([what runs outside the sandbox](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox)). They can receive the environment of the Claude Code process, which holds the real image key. Review them before a session that holds the key. §9 lists everything that runs outside the sandbox.

**Built-in tools that reach past the sandbox.** Besides the MCP resource tools, five built-in tools run in the Claude Code process, outside the sandbox, and can send content off the machine or into another session. The sandbox, `allowedDomains` and `strictAllowlist` do not govern them, and most need no permission prompt. tachi uses none of them, and the profile denies each by its bare name ([tools reference](https://code.claude.com/docs/en/tools-reference); [tool name wildcards](https://code.claude.com/docs/en/permissions#tool-name-wildcards)).

- `SendMessage` and `ListAgents` message your other Claude Code sessions and list them with their names and working directories. Cross-session messaging is on by default, including with feature-flag fetching off (v2.1.248 or later), and it goes over a local socket. Denying both tools is the documented way to turn it off ([turn off cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging#turn-off-cross-session-messaging)).
- `Monitor` has Claude Code itself open a WebSocket watch to a `ws://` or `wss://` address. The docs name the hosts that a watch is denied: private, link-local and metadata addresses, `sandbox.network.deniedDomains` and a managed-only allowlist. `allowedDomains` is not among them, and in auto mode the classifier decides ([WebSocket source](https://code.claude.com/docs/en/tools-reference#websocket-source)).
- `RemoteTrigger` creates and runs cloud scheduled tasks on claude.ai. They run as cloud sessions with network policies of their own, the tool needs only a claude.ai sign-in, and the docs tie it to no non-essential-traffic switch ([routines](https://code.claude.com/docs/en/routines)).
- `ShareOnboardingGuide` uploads `ONBOARDING.md` and returns a share link, on Team and Enterprise plans ([tools reference](https://code.claude.com/docs/en/tools-reference)).

`Artifact` and Remote Control, which `PushNotification` and `SendUserFile` need, are off while `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set ([artifact availability](https://code.claude.com/docs/en/artifacts#availability); [Remote Control](https://code.claude.com/docs/en/remote-control)), and the profile sets it (§1).

**The Agent tool's `remote` option.** On Claude Code 2.1.330 the Agent tool also offers a `remote` isolation value, which it describes as launching the agent in a cloud environment; the subagent docs describe only `worktree` ([supported frontmatter fields](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields)). A cloud session runs outside your machine and does not enforce your local session's restrictions ([errors](https://code.claude.com/docs/en/errors#cloud-sessions-cannot-be-created-from-a-restricted-session)). Its network follows its cloud environment's access level: a new environment starts at Limited, with package registries, GitHub and cloud SDKs, and Full reaches any domain ([cloud environments: network access](https://code.claude.com/docs/en/cloud-environments#network-access)). A cloud session started from a repository without a GitHub remote uploads a bundle of the repository; the docs do not say whether a remote subagent does the same ([from terminal to cloud](https://code.claude.com/docs/en/claude-code-on-the-web#from-terminal-to-cloud)). The profile denies every Agent call that sets an isolation value (`Agent(isolation:*)`), a documented rule form ([match by input parameter](https://code.claude.com/docs/en/permissions#match-by-input-parameter)). `Agent` stays available, and tachi's dispatches, which set no isolation value, are unaffected. The profile also denies the Workflow tool, which starts subagents through a script whose launch options the docs do not describe; tachi does not use it. An organization Owner can turn cloud sessions off for the whole organization (`allow_remote_sessions`) ([`--cloud` requirements](https://code.claude.com/docs/en/claude-code-on-the-web#from-terminal-to-cloud)). Check the profile's side of this with the "Tool inventory" row in §4.

Messages from your other sessions can still arrive in a tachi session. To drop them, set `"crossSessionInbound": "refuse"` in the project's `.claude/settings.local.json`; from project or local settings, `refuse` applies over every other source ([turn off cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging#turn-off-cross-session-messaging)). The profile does not set it: it controls messages coming in, not what leaves, and with `SendMessage` denied the session cannot answer them.

### The classifier

The `autoMode` block keeps Claude Code's built-in rules in every list (`"$defaults"`), adds facts about this machine to `environment` and adds one prohibition to `hard_deny`.

- **Trust comes only from `environment` entries.** They tell the classifier which hosts and locations are trusted, so a destination that they do not name stays a possible exfiltration target ([define trusted infrastructure](https://code.claude.com/docs/en/auto-mode-config#define-trusted-infrastructure)).
- **`hard_deny` only prohibits.** Its entries block the actions they describe even when you ask for them, and nothing in it grants access ([override the block and allow rules](https://code.claude.com/docs/en/auto-mode-config#override-the-block-and-allow-rules)).
- **The classifier reads commands, not their output.** In the requests Claude Code sends it, tool results are stripped. It sees your messages, the tool calls other than read-only lookups, and your CLAUDE.md content ([how auto mode evaluates actions](https://code.claude.com/docs/en/permission-modes#how-auto-mode-evaluates-actions)). It can refuse a command that would send tachi's content to another host. It cannot judge what a file or a command's output said.
- **Sandboxed commands reach it.** The profile sets `autoAllowBashIfSandboxed` to `false`, so sandboxed commands go through the regular permission flow, whatever the version default is (`true` before v2.1.324) and whatever a repository, local or user file sets ([`sandbox.autoAllowBashIfSandboxed`](https://code.claude.com/docs/en/settings-reference#sandbox-autoallowbashifsandboxed)). In auto mode they therefore reach the classifier and its `hard_deny` like any other command. Read-only commands, and commands that a narrow allow rule matches, can still skip it ([how auto mode evaluates actions](https://code.claude.com/docs/en/permission-modes#how-auto-mode-evaluates-actions); [suspend shell allow rules](https://code.claude.com/docs/en/auto-mode-config#suspend-shell-allow-rules)). In Manual mode, sandboxed commands prompt like other commands, apart from the built-in read-only set ([regular permissions mode](https://code.claude.com/docs/en/sandboxing#regular-permissions-mode); [read-only commands](https://code.claude.com/docs/en/permissions#read-only-commands)).
- **No extra host for a single command.** `strictAllowlist` also makes Claude Code refuse auto mode's per-command host lists, so no host outside `allowedDomains` opens for one command ([per-command allowed domains in auto mode](https://code.claude.com/docs/en/sandboxing#per-command-allowed-domains-in-auto-mode)). An agent can still attach such a list in auto mode, even one naming only `generativelanguage.googleapis.com`, and Claude Code then refuses the call before it runs; in the live validation the infographic agent did this once and continued without the list (§11).

### Key provisioning

The image key is optional (§1). To use it, inject `GEMINI_API_KEY` into the environment of the `claude` process from your secret manager, and nowhere else. The sandbox masks a variable that Claude Code inherits from its own environment ([mask environment variables](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)).

- Never put the key in a file the session can read: not a `.env` file, not a settings file, not a shell startup file. Never type it into a prompt, because prompts go to your model provider and into the plaintext transcript (§1, §7).
- Read the key from your secret manager in the command that starts `claude`, so it exists only in that process's environment ([mask environment variables](https://code.claude.com/docs/en/sandboxing#mask-environment-variables)) and never in an argument list. Replace `your-secret-manager-read-command` with a command that prints the key to standard output and exits with a non-zero status on any error, because the guard below stops an empty or failed read but not an error message printed with status 0. This is the argument-free form, not yet run live:

  ```
  (
    K="$(your-secret-manager-read-command)" && [ -n "$K" ] || { echo "no key; not starting" >&2; exit 1; }
    SHELL=/bin/bash GEMINI_API_KEY="$K" exec "$(command -v claude)" --settings ~/.tachi/session-profile.json
  )
  ```

- A wrapper that runs `claude` as a child process, such as `op run`, masks the child's output by default and can disturb an interactive session. If you use one, try it before a real run. §11 records the exact form that worked in the live validation.

**What the mask does and does not do.** The image key is masked for sandboxed commands: they see a placeholder, and the sandbox proxy substitutes the real value only on connections to `generativelanguage.googleapis.com`. The real value is still held by the Claude Code process, which runs outside the sandbox, and it can reach hooks, the status line and local MCP servers, which Claude Code starts outside the sandbox, unless you scrub the environment. The Read denies in the profile keep Claude's file tools away from that environment on Linux and from Claude Code's own login file; whatever a tool does read is written to the plaintext transcript. `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` is the documented switch that strips credentials from those subprocesses. The profile does not set it, and the docs do not say how it combines with a masked variable ([what the subprocess environment scrub removes](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes)). Assume that processes of your own user that run outside the sandbox can read the real value from the Claude Code process's environment for the whole session, whichever launch form you use: on Linux through `/proc/<pid>/environ`, and on macOS with `ps eww` (see the `ps` measurements below). Only a process-level boundary (§9) keeps them out.

**Everything else in the launch environment reaches sandboxed commands.** Sandboxed commands inherit the whole environment of the Claude Code process, and the mask covers one variable ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)). A provider credential that you set in the environment, such as `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`, therefore reaches them. Claude Code adds variables of its own as well. Two of them, `CLAUDE_CODE_MESSAGING_SOCKET` and `CLAUDE_CODE_MESSAGING_TOKEN`, let a command post into the session's own inbox ([the session's inbox socket](https://code.claude.com/docs/en/cross-session-messaging#the-sessions-inbox-socket)). A sandboxed command reaches that socket only through the sandbox's Unix-socket settings, which the profile forbids, or where the sandbox does not block Unix sockets, as on Linux and WSL2 without the seccomp filter (§6). The live validation saw both variables in sandboxed commands and did not test their use.

There are two remedies for the credentials. Launch from a minimal environment that lists only what the session needs ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)). The block below is the form that ran in the live validation (§11). It reads the key first, into a shell variable that is never exported, and stops on an empty key. The subshell keeps the variable out of your interactive shell, and `exec` leaves no shell behind to hold it. It passes `SHELL` explicitly, because a launch environment without it gets zsh where zsh exists (see "Shell startup files and the Keychain" above). Replace `your-secret-manager-read-command` with a command that prints the key and exits non-zero on error, and for a key-less session drop the `K` line and the `GEMINI_API_KEY` argument:

```
(
  K="$(your-secret-manager-read-command)" && [ -n "$K" ] || { echo "no key; not starting" >&2; exit 1; }
  exec env -i HOME="$HOME" USER="$USER" SHELL=/bin/bash PATH="$PATH" TERM="$TERM" \
    LANG="${LANG:-en_US.UTF-8}" TMPDIR="${TMPDIR:-/tmp}" GEMINI_API_KEY="$K" \
    "$(command -v claude)" --settings ~/.tachi/session-profile.json
)
```

For the instant between `env` starting and `env` starting `claude`, the key is one of `env`'s arguments. No sandboxed command exists yet, so nothing the session runs can see it, but a process already running on the machine can: on macOS, any local user's, through `ps` (on macOS 26.6.2 `/bin/ps` is setuid root); on Linux, any user's, unless `/proc` is mounted with `hidepid=1` or higher. If endpoint monitoring or audit logging on this machine records process arguments, it would record the key and keep it past that instant (not tested), so use the argument-free form at the top of this section instead. Sources: [proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html); [proc_pid_cmdline(5)](https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html).

Add whatever else your setup needs, such as `TACHI_MMDC_PUPPETEER_CONFIG` on Linux (§6). The other remedy is a `deny` entry for each such variable under `sandbox.credentials.envVars` in your user settings, which removes the variable from the environment of sandboxed commands ([protect credentials](https://code.claude.com/docs/en/sandboxing#protect-credentials)). On a host that other users share, use the argument-free form at the top of this section, which puts the key in the child's environment and never in an argument list, together with that second remedy. That combination has not been run live. Signing in with `/login` keeps your Claude Code credential out of the environment: it is stored in the macOS Keychain or in a file that the profile denies ([credential management](https://code.claude.com/docs/en/authentication#credential-management)). On macOS that does not settle whether the credential is out of reach of sandboxed commands, which can query the Keychain; whether they can read Claude Code's own sign-in item was not tested (see "Shell startup files and the Keychain" above).

The docs do not say whether a sandboxed command on macOS can read another process's environment, for example with `ps eww`. In the live validation on macOS 26.6.2 the sandbox refused to run `/bin/ps` at all, so that route was closed to sandboxed commands, and outside the sandbox `ps eww` showed no process environment for the two processes it probed. A later check on the same macOS version did read one outside the sandbox: `ps eww` printed the environment of a process of the same user, a Claude Code 2.1.327 process, and of an ordinary process, but not of a protected system binary (variable names counted, no values printed). So the live probe's result does not generalise, and it answers sandboxed `ps` only. Other routes were not tested, so until you have checked your machine, assume that a process of your own user outside the sandbox can read the Claude Code process's environment, and that another route can.

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
  - Provider and authentication configuration that lives in user settings, such as `env`, `apiKeyHelper` and cloud credential helpers, is not read ([CLI reference: flags](https://code.claude.com/docs/en/cli-reference#cli-flags)).
  - User-scope environment-variable masks are dropped, and user-scope `sandbox.filesystem` entries, `Edit` rules and Read deny rules are ignored when the sandbox configuration is built. User-scope `deny` entries under `sandbox.credentials` still apply ([protect credentials](https://code.claude.com/docs/en/sandboxing#protect-credentials); [configure sandboxing](https://code.claude.com/docs/en/sandboxing#configure-sandboxing)).
  - The retention sweep pauses when no enabled source sets `cleanupPeriodDays` ([retention sweep event](https://code.claude.com/docs/en/monitoring-usage#retention-sweep-event)).
  - A mode dialog that your user file suppressed can appear again. The docs state this for the bypass-permissions warning, which the profile does not use ([skip all checks with bypassPermissions mode](https://code.claude.com/docs/en/permission-modes#skip-all-checks-with-bypasspermissions-mode)).
  - Your user-scope permission rules and `deniedMcpServers` entries do not load at all ([CLI reference: flags](https://code.claude.com/docs/en/cli-reference#cli-flags)). In the live validation, a session with `user` left out listed only `Command line arguments` among its settings sources. The extra credential-store Read denies from "Other credential stores" therefore no longer cover the Read tool. Only their `sandbox.credentials` deny entries still apply, as the cost about environment-variable masks above says.

The docs do not say whether a file passed with `--settings` still applies when `--setting-sources` leaves sources out. In the live validation it did: with `--setting-sources project,local` the file applied in full, its deny, sandbox and auto-mode rules were in force, and the `touch` probe and the proxy `curl` probe in §4 were refused. A non-blocking auto-mode notice reappeared, and the user's MCP servers and status line dropped with the user source. If you try the flag, repeat the effective-configuration check above.

### Your user settings

Keep the profile as published and put your own additions in `~/.claude/settings.json`: the extra credential-store rules ([protect credentials](https://code.claude.com/docs/en/sandboxing#protect-credentials)), the `deniedMcpServers` entries ([`deniedMcpServers`](https://code.claude.com/docs/en/settings-reference#deniedmcpservers)) and, for retention, `cleanupPeriodDays` ([`cleanupPeriodDays`](https://code.claude.com/docs/en/settings-reference#cleanupperioddays)), which stays at user scope and is never lowered (§7).

One more addition is optional. The profile applies to tachi sessions only. To sandbox every Claude Code session on the machine, merge the profile's `sandbox` object into your user settings. Merge it, do not replace the file: lists combine across scopes, so your own entries stay and the profile's are added ([lists merge instead of overriding](https://code.claude.com/docs/en/settings#lists-merge-instead-of-overriding)). Claude Code honors `mask` entries and `tlsTerminate` from user settings ([mask credentials](https://code.claude.com/docs/en/sandboxing#mask-credentials)). Two cautions. With the copy in place, sandboxed commands in every session reach only the Gemini host and whatever else your own files allow, so use it only where you want that. And the copy carries `autoAllowBashIfSandboxed: false`, so your other sessions in Manual mode prompt for sandboxed commands. Leave that key out of your copy if you want the version default in those sessions: the profile sets it for tachi sessions either way.

### Forms and scope

- **Path forms.** In permission rules, avoid the single-slash `/path` form. It anchors at the profile file's directory, not at the filesystem root. The `~/`, `//` and working-directory-relative forms are fine. Sandbox path lists use the opposite convention, where `/path` is absolute, so a path copied between the two changes its meaning ([where a pattern anchors](https://code.claude.com/docs/en/permissions#where-a-pattern-anchors); [sandbox path prefixes](https://code.claude.com/docs/en/settings-reference#sandbox-path-prefixes)).
- **Keep the bare `WebFetch` deny.** `WebFetch(domain:*)` in `deny` also denies every host to sandboxed commands, the Gemini host included ([allow or deny every fetch](https://code.claude.com/docs/en/permissions#allow-or-deny-every-fetch)).
- **Local sessions only.** In an Anthropic-hosted cloud session, `failIfUnavailable` lets the session start with a warning, and the `sandbox.filesystem` and `sandbox.network` rules are not enforced ([`sandbox.failIfUnavailable`](https://code.claude.com/docs/en/settings-reference#sandbox-failifunavailable)). The `env` key also keeps Claude Code's artifact publishing off (§1).

## 4. Probe table

Run these probes first, inside a session that you started with the profile. Ask Claude to run each line. What you type at the `!` prompt usually runs outside the sandbox, so typing a line yourself does not test it ([confirm commands run inside the sandbox](https://code.claude.com/docs/en/sandboxing#confirm-commands-run-inside-the-sandbox)). The profile turns the unsandboxed retry off ([turn off the retry with strict sandbox mode](https://code.claude.com/docs/en/sandboxing#turn-off-the-retry-with-strict-sandbox-mode)). If a prompt still offers to run a probe outside the sandbox, decline it.

| Probe | Pass | Layer that should refuse |
|---|---|---|
| `touch ~/sandbox-probe` | Fails with `Operation not permitted` (macOS) or `Read-only file system` (Linux, WSL2) ([confirm commands run inside the sandbox](https://code.claude.com/docs/en/sandboxing#confirm-commands-run-inside-the-sandbox)). If it succeeds, delete `~/sandbox-probe` and stop: the sandbox is not confining writes, so check the effective configuration (§3) | Sandbox, filesystem |
| `curl --noproxy '*' https://example.com` | Fails with `Could not resolve host`, because the command has no route around the sandbox proxy ([confirm commands run inside the sandbox](https://code.claude.com/docs/en/sandboxing#confirm-commands-run-inside-the-sandbox)) | Sandbox, network |
| `curl -sS https://example.com` | Fails without reaching `example.com`. The result names the host as blocked and no prompt appears, which shows that `strictAllowlist` is in force ([hosts outside your allowed domains](https://code.claude.com/docs/en/sandboxing#hosts-outside-your-allowed-domains)) | Sandbox proxy |
| A planted `.env`: from another terminal, create `.env` in the project root holding only `PROBE=not-a-secret`. Then ask Claude to read it with the Read tool and to run `cat .env`. Delete the file afterwards | Both are refused, and no file content appears in either result | The permission rule `Read(.env*)`; for `cat`, the same rule or the sandbox's read denies ([what Read and Edit rules cover](https://code.claude.com/docs/en/permissions#what-read-and-edit-rules-cover)) |
| WebFetch: ask Claude to fetch `https://example.com` with WebFetch | Denied. Claude has no WebFetch tool or the call is refused, and no page content comes back ([allow or deny every fetch](https://code.claude.com/docs/en/permissions#allow-or-deny-every-fetch)) | The permission rule `WebFetch` |
| Secret-store rules (a configuration check): run `/permissions` | The list holds the profile's deny rules, among them `Read(//proc/**)` and `Read(~/.claude/.credentials.json)`, and no startup warning names an invalid rule ([manage permissions](https://code.claude.com/docs/en/permissions#manage-permissions)) | Configuration |
| Environment names (a configuration check): ask Claude to run `python3 -c 'import os; print("\n".join(sorted(os.environ)))'` | It prints names, never values. Apart from Claude Code's own variables and the sandbox's proxy and CA-bundle variables, only the names you launched with appear, and no credential name ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)) | Configuration |
| Tool inventory (a configuration check): ask Claude to list its tools, loaded and deferred, by name, and run `/permissions` | No tool whose name starts with `mcp__` appears, and none of the tools that the profile denies by name (§3), `Workflow` among them. `Agent` is present, and `/permissions` lists `Agent(isolation:*)` ([manage permissions](https://code.claude.com/docs/en/permissions#manage-permissions)) | Configuration |
| Linux and WSL2, seccomp filter (a check, not yet run live: `/sandbox` does not open under the profile, so run it in a session started without the profile): run `/sandbox` | No Dependencies tab appears beside the other tabs. If one lists the seccomp filter, install it with `npm install -g @anthropic-ai/sandbox-runtime`, restart Claude Code and check again before the first session with the profile ([set up Linux and WSL2](https://code.claude.com/docs/en/sandboxing#set-up-linux-and-wsl2)) | Configuration |

**Record which layer refused each line.** A refusal by a permission rule or by the auto mode classifier is not a sandbox result. If one stops a `touch` or `curl` line, approve the action under `/permissions`, on the Recently blocked tab, and ask Claude to retry it, so the sandbox gets to answer ([review denials](https://code.claude.com/docs/en/auto-mode-config#review-denials)).

**Never plant a real secret.** A probe that fails open writes what it reads into the plaintext transcript ([plaintext storage](https://code.claude.com/docs/en/claude-directory#plaintext-storage)). Use a dummy value, and never point a probe at a real credential file such as Claude Code's login file. The rules for those paths are checked by configuration, in the table above.

### Optional on Linux: the `/proc` rule

This check is not yet run live. It reads a dummy variable, never a real secret. Run it only in a session whose environment holds no key and no provider credential. If you sign in through an environment variable, skip it. Sandboxed commands inherit the environment of the Claude Code process ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)), so start the session from a cleaned environment that holds one dummy variable (`<file>` is your saved profile):

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

The table lists every path tachi's instructions write. An agent can write other files inside the sandbox's writable set: in the live validation the infographic agent wrote helper scripts under `{out}/.tachi-build/`, still under `{out}` (§11).

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

Claude Code itself writes an empty `.claude/.cc-writes/` directory in the shell's working directory: at the project root on the first sandboxed command, and in a subfolder after the shell has changed directory. It is not a tachi write, so the table has no row for it.

## 6. Platforms

This runbook targets macOS, Linux and WSL2. Native Windows is not supported for isolated operation. §11 records the platforms that ran in the live validation and the result for each. The header names the platforms that the claim covers.

### macOS

The sandbox uses the built-in Seatbelt framework, so nothing needs installing ([get started](https://code.claude.com/docs/en/sandboxing#get-started)). The `Read(//proc/**)` rule in the profile has no effect there, because macOS has no `/proc`.

**Diagram rendering.** On macOS, Chromium, which `mmdc` starts to render the attack-tree and attack-chain diagrams, cannot start inside Claude Code's sandbox: it is refused the Mach service registration it needs. The Linux `--no-sandbox` recipe does not change this, so do not set `TACHI_MMDC_PUPPETEER_CONFIG` for it on macOS. Under the profile no diagram renders, and `/tachi.security-report` stops without a PDF for any run with Critical or High findings or a surfaced attack chain. A run with neither needs no diagrams, so no Chromium, and may build its PDF under the profile; that case has not run live either (§11). No setting in the Claude Code docs fixes this without weakening the profile. [`sandbox.network.allowMachLookup`](https://code.claude.com/docs/en/settings-reference#sandbox-network-allowmachlookup) lets commands look services up, while Chromium fails to register one. It was not tried, and the profile forbids it, as it forbids the keys listed under Linux and WSL2 below.

**Building the report by hand.** The by-hand build is the report assembler's own Steps 2c, 3a and 3d (`.claude/agents/tachi/report-assembler.md`). Run it from a plain terminal in the project root after the session, with `{out}` the run's output directory. The lines are chained, so a failed extraction stops before the compile, and a failed compile keeps the build directory for debugging, as the assembler does:

```
python3 scripts/extract-report-data.py --target-dir {out} --build-dir {out}/.tachi-build/security-report \
  && typst compile {out}/.tachi-build/security-report/main.typ {out}/security-report.pdf --root . \
  && python3 scripts/extract-report-data.py --remove-build-dir {out}/.tachi-build/security-report
```

- **Check first.** The session's sandbox can write to your project, including `scripts/` and `templates/`, and this step runs both with your full access, outside the sandbox ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)). Compare `scripts/` and `templates/tachi/security-report/` with the tachi release you installed from, or restore them from it. Read `{out}/report-config.typ` if it exists: a report configuration can pull any file under the project root into the PDF, `.env*` files included. Run `find {out} -type l`, which should print nothing, because the build follows symlinks in `{out}`. Run the build only when all three checks are clean.
- **From what.** The run folder `{out}`, including `{out}/report-config.typ` if it exists, plus the installed `scripts/` and `templates/tachi/security-report/` and the files that Typst reads under `--root .`, the brand logos in `brand/final/` included.
- **Writes.** Under `{out}` and `$TMPDIR`: the report rows of the table in §5.
- **It runs no model and sends nothing to a provider.** The extractor does all the data extraction and writes `report-data.typ`, so the result is what the agent would build, as long as `scripts/` and `templates/` are unmodified.
- **Leave `TACHI_MMDC_PUPPETEER_CONFIG` unset.** If your shell exports it, unset it first. The variable exists for sandboxed Linux sessions. Outside a sandbox, `mmdc` starts Chromium with Chromium's own sandbox on.
- **What it gives up.** It runs outside Claude Code's sandbox, so nothing confines the renderer's writes or network, and the project's own scripts and templates run with your full access. The offline render check (§11) shows that rendering needs no network, so disconnecting the machine from the network for this step loses nothing. Run it from a shell whose environment holds no key and no provider credential. It also uses whatever the session left in the project.
- **Status.** Not yet run live. It runs outside the isolated session, and §11 records it as such. The same build can be used on Linux and WSL2 if the `--no-sandbox` recipe fails there; that is also not yet run live. If Chromium cannot start there either, stop. Do not add `--no-sandbox` outside Claude Code's sandbox.

### Linux and WSL2

Install the sandbox's two packages, `bubblewrap` and `socat`, with your distribution's package manager. On Ubuntu and Debian, run `sudo apt-get install bubblewrap socat`. On Fedora, run `sudo dnf install bubblewrap socat`. WSL2 is required, because WSL1 does not run the sandbox ([set up Linux and WSL2](https://code.claude.com/docs/en/sandboxing#set-up-linux-and-wsl2)). Also install the optional seccomp filter and check it as §4 describes. Without the filter the sandbox does not block Unix-socket connections, such as a container runtime's socket, the inbox sockets that your Claude Code sessions listen on ([cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging#the-sessions-inbox-socket)) or, on WSL2, the socket that launches Windows programs ([`sandbox.network.allowAllUnixSockets`](https://code.claude.com/docs/en/settings-reference#sandbox-network-allowallunixsockets)).

**Diagram rendering.** On Linux and WSL2 a sandboxed command cannot create user namespaces, so Chromium, which `mmdc` starts to render the attack-tree and attack-chain diagrams, exits with `No usable sandbox!` ([Chromium fails inside the sandbox on Linux](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux)). tachi's recipe starts Chromium without its own sandbox:

1. Create a file outside the project that holds exactly this JSON, and check before each use that it holds nothing else. It sets the flags that Chromium starts with:

   ```json
   {"args": ["--no-sandbox"]}
   ```

2. Set `TACHI_MMDC_PUPPETEER_CONFIG` to the absolute path of that file, in the environment that starts `claude`, for example `export TACHI_MMDC_PUPPETEER_CONFIG="$HOME/.tachi/puppeteer-no-sandbox.json"`. If you launch with the `env -i` form under "Key provisioning", add the variable to that command instead, because `env -i` drops exported variables. Sandboxed commands inherit that environment ([what the sandbox restricts](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts)). When the variable is set, `scripts/extract-report-data.py` passes `-p <path>` to both `mmdc` runs. It stops with an error when the value is empty, is a relative path or does not name an existing regular file.

The trade-off: with `--no-sandbox`, the renderer processes LLM-authored diagrams derived from the analysed repository with Claude Code's sandbox as its only boundary. Chromium's own sandbox is off ([Chromium fails inside the sandbox on Linux](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux)). The profile still confines the renderer's writes and network like those of any sandboxed command.

Do not work around the failure in any other way. Never add `excludedCommands`, `allowNestedUserNamespaces`, `enableWeakerNestedSandbox` or a write allowance: the profile forbids them, and each gives up isolation ([Chromium fails inside the sandbox on Linux](https://code.claude.com/docs/en/sandboxing#chromium-or-rootless-podman-fails-inside-the-sandbox-on-linux); [security limitations](https://code.claude.com/docs/en/sandboxing#security-limitations)). Do not remove a deny rule from the profile to make a step work, `Read(//proc/**)` among them: on Linux it keeps Claude's Read tool away from the Claude Code process's environment, which holds the real image key (§3). If a step fails while the rule is in place, stop and report it as a tachi defect (§8). Running the step in a Claude Code session without the profile, or with a weakening key, is outside this runbook. The by-hand build under macOS runs no model; it is also outside the isolated session, and §11 records it as such.

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
- MCP servers. The profile denies every MCP tool and the built-in tools that list and read MCP resources, but a configured local server still starts and runs outside the sandbox (§3).
- Command hooks, plugin monitors, LSP servers, mods, and helper commands such as the status line and `apiKeyHelper`. They run with your full access.
- Commands you type yourself at the `!` prompt ([strict sandbox mode](https://code.claude.com/docs/en/sandboxing#turn-off-the-retry-with-strict-sandbox-mode)).
- The Claude Code process itself, which keeps the credentials for its own model requests ([subprocess environment scrub](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes)).

To put all of these behind one boundary, run Claude Code inside a process-level boundary.

**What sandboxed commands can still reach.** A sandboxed command can still reach the environment of the Claude Code process, except the masked key; whatever the shell's startup files load; on macOS, your login Keychain; and Claude Code's own variables, among them its messaging socket and token (§3). A process-level boundary keeps these out.

**Domain fronting.** The allow-list works on hostnames. By default the sandbox proxy decides from the hostname a client supplies, without inspecting TLS. Code inside the sandbox could therefore use domain fronting or a similar technique to reach a host that is not on the list. The caveat covers the one host the profile allows. The profile's `tlsTerminate` terminates TLS for key masking only: the docs say it adds no content filtering, and they do not say it removes this caveat. If your threat model needs more, run a custom proxy that terminates and inspects TLS ([security limitations](https://code.claude.com/docs/en/sandboxing#security-limitations); [custom proxy configuration](https://code.claude.com/docs/en/sandboxing#custom-proxy-configuration)). The allow-list limits where sandboxed commands connect, not what they send to an allowed host. What tachi sends there rests on its design (§1).

### The guidance, item by item

tachi's work falls in the guidance's first category, local work that needs no internet access, apart from the model connection and the optional image request (§1). Every item there is mapped. Three items from the network-testing category also apply to local work, and they follow.

| Guidance item | Paraphrase | Marker | In a tachi session under the profile |
|---|---|---|---|
| Sandbox and network isolation (1) | Run inside a virtual machine or a dedicated physical host | Boundary | The profile sandboxes shell commands on your own host. It is not a virtual machine. On macOS, sandboxed commands can still query your login Keychain (§3) |
| Sandbox and network isolation (2) | Block egress except to the model API | Profile, for shell commands. Boundary, for the rest | Sandboxed commands reach only the Gemini host. The allow-list is strict, there is no unsandboxed retry, and the session stops if the sandbox cannot start. WebFetch, WebSearch, every MCP tool and the built-in tools and Agent options in §3 that reach past the sandbox are denied. The Gemini host stays allowed when you run without the key. Everything in the list above runs outside the sandbox |
| Sandbox and network isolation (3) | Reach the model API only through a local proxy, with the key added from outside the sandbox | Boundary, for the model connection. Profile, for the image key | The Claude Code process connects to your provider itself and holds its own credentials. A provider credential set in the environment is inherited by sandboxed commands (§3). For the image key, sandboxed commands see a placeholder, and the sandbox proxy adds the real key only on connections to the Gemini host ([mask credentials](https://code.claude.com/docs/en/sandboxing#mask-credentials)). On macOS, Claude Code keeps its sign-in in the Keychain, and whether sandboxed commands can read that item was not tested (§3) |
| Sandbox and network isolation (4) | Tell the model not to use the internet | Profile, in part | The profile gives auto mode's classifier a rule against sending tachi's content to any other host. tachi's agent instructions do not yet say it themselves ([#360](https://github.com/davidmatousek/tachi/issues/360)) |
| Sandbox and network isolation (5) | Install every tool before the run, so nothing is fetched mid-run | tachi | See §1. Under the profile, a fetch to any other host would be refused |
| Pre-engagement validation (1) | Before live runs, probe the sandbox: review its configuration, then run a supervised escape attempt with no internet access | Operator | The probe table and the effective-configuration check (§3, §4) review the profile's settings. They are not an escape test. Run one yourself before you rely on the setup |
| Pre-engagement validation (2) | Confirm the agent has the tools it needs, and look for tasks it cannot complete | Operator | `/tachi.security-report` checks for typst, and for mmdc when diagrams exist, before it starts. On macOS under the profile, the mmdc check passes but the browser cannot start, so the command stops without a PDF. §6 gives the by-hand build |
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

Only the Tools column is enforced. The shell command families and write paths record what tachi's instructions say, not what a run is limited to: in the live validation all three Bash-capable agents ran command families outside their rows, and the infographic agent wrote helper scripts that no row lists, all under the run's output directory (§11).

tachi's CI runs a guard (`scripts/check-agent-privileges.py`) that compares the agent and command files with the matrix. Scope: the guard covers `.claude/agents/tachi/**` and `.claude/commands/tachi.*.md`, not the adapter copies under `adapters/claude-code/agents/`.

## 11. Live-validation record

This record is structure only. It holds no transcript excerpts, session ids, home paths or key material. It has two parts: the key-less re-check of the published profile, first, and the live run before it, which used the profile that §3 published before it gained ten deny rules. The sessions of both were real interactive Claude Code sessions in a terminal, driven by Claude at the maintainer's instruction. The maintainer directed the runs and recorded the results.

### Re-check of the published profile

**Passed on 2026-11-20: R1 to R6, with R4a, on the published 18-rule profile.** A change to the profile ends the "Last validated" claim (the second refresh trigger in the header), so the maintainer re-checked the profile that §3 now publishes. The re-check was key-less, on macOS 26.6.2 (arm64) with Claude Code 2.1.330, in auto mode, in the scratch project and with the installed build of the live run below (`v4.48.2-103-gfe5125a`). It used the launch form from §3, key-less, with `SHELL=/bin/bash` and the profile passed as a file to `--settings`. The user-scope additions that §3 recommends were not applied for it. Claude drove each session, as in the live run.

| Step | Result |
|---|---|
| R1 | Passed. The profile block extracted from the published runbook is 3,156 bytes, SHA-256 `36df2a9a98e301d783a06ff605d1be7f9548e10f805084b3fe225ff89eef9644`, with 18 deny rules. The same extraction of the live run's runbook gives its 2,908 bytes and `43496fb7d4fca098983a70648def8f1da2a2d1843528b5ca4c14444e32564279`. The two differ only by the ten deny rules after `mcp__*` |
| R2 | Passed. `claude --settings <file> auto-mode config` equalled the built-in lists followed by the profile's entries, in order (`environment` 21 to 26 entries, `hard_deny` 1 to 2, `allow` and `soft_deny` unchanged), identical to the live run's output |
| R3 | Passed. `claude --settings <file> doctor` reported no installation issues and no rejected or skipped rule, auto-update disabled by the non-essential-traffic variable, and Remote Control off because feature-flag evaluation is disabled. In the session, no startup warning named a rule and auto mode was on. `/status` listed User settings and Command line arguments as the settings sources, with `Auto mode server: Enabled`, and `/permissions` showed an empty Allow list and exactly the 18 profile rules under Deny, `Agent(isolation:*)` and `Workflow` among them |
| R4 | Passed. The session listed its tools without calling one. No `mcp__` tool and none of the nine bare names (the eight built-in tools that §3 denies by name, and `Workflow`) appeared, loaded or deferred, and `Agent` was present. The Agent tool still lists the `isolation` values `worktree` and `remote`, because a parameter rule removes no schema value |
| R4a | Passed. Asked to start one subagent with `isolation: "worktree"` and a one-word prompt, the session's Agent call was refused before it ran, with the message that permission to use Agent with `isolation:*` had been denied. No subagent ran, and `git worktree list` in the project showed only the main worktree. The layer was the permission rule from the command-line settings. The `remote` value was never requested |
| R5 | Passed. The `touch`, `curl --noproxy` and proxy `curl` probes of §4 were refused as in the live run, and a planted dummy `.env` was refused through the Read tool (by the permission settings) and through `cat` (before it ran, by the permission rule from the command-line arguments). The dummy file was removed afterwards |
| R6 | Passed. `/tachi.threat-model` ran key-less into a fresh output directory, so with no baseline: 1 Critical, 11 High, 5 Medium and 0 Low findings, and 17 SARIF results, in about 6 minutes. The dispatch tree was the orchestrator, then the report agent, then the attack-tree agent, all finished. None set an isolation value, so the new parameter rule left tachi's dispatches untouched. As in the live run, the orchestrator analysed inline instead of dispatching the STRIDE agents. The write listing (a hash of every path except `.git/`, before and after) showed 21 new paths, 0 changed and 0 deleted, all under the run's output directory |

**The first attempt, on the 16-rule profile.** A first re-check ran on the profile as it stood before the Agent tool's `remote` isolation value was known (3,110 bytes, SHA-256 `0880db3b3d75ad84e95b12a6127aeac345999b6366edb2bb1e6a4725d46b78d2`, 16 deny rules). R1 to R3 passed. R4's inventory showed no `mcp__` tool and none of the eight tool names, but the Agent tool's `isolation` parameter accepted `worktree` and `remote`. R4's stop condition applied, and that session ended without R5 or R6. The profile then gained `Agent(isolation:*)` and `Workflow` (§3), and the re-check restarted at R1 on the 18-rule profile recorded above.

**What it supports.** The published profile is validated for what the re-check covered: startup and the rule list, the tool inventory, a refused isolated Agent call, the sandbox and `.env` probes, and one key-less `/tachi.threat-model` run with the deepest dispatch tree. The rest of the live validation, including the keyed pipeline, the mask and the Gemini client's trust of the proxy's CA, ran in the live run, on the earlier profile. The ten added rules only deny: they name tools that tachi does not use, and Agent calls that set an isolation value, which tachi's dispatches never do. Nothing in the re-check changes blocker F1: on macOS, `/tachi.security-report` still cannot render diagrams under the profile (§6). The subsections below record the live run.

### Result in brief

- **Passed:** the probe table in §4 and two added probes, with the planted classifier denial; the macOS secret-store probes; write confinement; the key mask and the Gemini client's trust of the proxy's CA; the offline render check; auto mode with non-essential traffic off; the Manual-mode check; and `--setting-sources project,local`.
- **Failed, as a documented limitation:** on macOS, Chromium cannot start inside Claude Code's sandbox (blocker F1, §6). No attack-tree image renders, and `/tachi.security-report` produces no PDF for a run with Critical or High findings.
- **Findings that changed this runbook:** the MCP resource tools stayed available under the first profile (§3); sandboxed commands can query the macOS Keychain, and a shell startup file can load a credential into every one of them (§3); the key sat for an instant in `env`'s arguments (§3); the step-1 configuration check shows nothing when no scope enables the sandbox (§3); and the agents ran more than their rows list (§5, §10).
- **Did not run:** Linux and WSL2, and the steps listed under "Not yet run live" at the end of this section.

### Setup

| Item | Value |
|---|---|
| Date | 2026-11-20 |
| Platform | macOS 26.6.2 (arm64) only. Linux and WSL2 did not run, so nothing in this record covers them |
| Claude Code | 2.1.330 in every session with the profile. The pre-run gate checks ran on 2.1.328, and the one session without the profile started on 2.1.328 and was updated to 2.1.330 by its auto-updater. The profile's non-essential-traffic switch keeps auto-update off, so every later session stayed on 2.1.330. The gate's auto-mode rule comparison was re-run on 2.1.330 with the same result, and the built-in auto-mode rules are identical in both versions |
| Permission mode | Auto mode in every measured session, with `Auto mode server: Enabled` and non-essential traffic off. No fallback was needed. One Manual-mode check |
| Configurations | Key-less, and keyed (`GEMINI_API_KEY` injected into the process environment only) |
| Installed build | `v4.48.2-103-gfe5125a`, installed with `scripts/install.sh` from a clean clone into a fresh scratch project. It is a pre-release build that also carries changes outside this release. None of them changes the session profile, the probes or §5's write set |
| Input | The repository's `examples/ascii-web-api/input.md`, used as the architecture description |
| Profile that ran | 2,908 bytes, SHA-256 `43496fb7d4fca098983a70648def8f1da2a2d1843528b5ca4c14444e32564279`, passed as a file to `--settings` |
| Profile published in §3 | 3,156 bytes, SHA-256 `36df2a9a98e301d783a06ff605d1be7f9548e10f805084b3fe225ff89eef9644`. It differs from the profile that ran only by the ten deny rules after `mcp__*` |
| User settings | The user-scope additions that §3 recommends (a `deniedMcpServers` entry for one local server, and the `~/.claude.json` Read deny with its `credentials.files` entry) were applied for the sessions and restored afterwards. No hooks, plugins, `apiKeyHelper` or `allowedDomains` at user scope. No managed settings. `cleanupPeriodDays` was unset in every scope |
| Session shell | `/bin/bash` in every measured session |

Each profile row gives the byte count and SHA-256 of the JSON text between the fence lines, plus one trailing newline.

### Sessions

| Session | Configuration |
|---|---|
| C | No profile: the effective-configuration check, step 1 (§3) |
| K1a | Key-less, the profile, zsh. It ended after the shell startup file probe |
| K1 | Key-less, the profile, bash, auto mode: the configuration checks, the probes, the secret-store probes, the full pipeline and the `--output-dir` check |
| B7 | Key-less, the profile plus one extra Read deny for a planted dummy file |
| MM | Key-less, the profile, `--permission-mode default` |
| K2 | Keyed, the profile, bash, auto mode: the environment, the mask and the full pipeline |
| SS | Key-less, the profile, `--setting-sources project,local` |

### Gate and configuration checks

| Check | Result |
|---|---|
| Install source | Passed: the install-source CI checks were green on the build |
| Claude Code | Passed: at least v2.1.285 and auto mode available. The status bar showed auto mode and the model at each launch |
| Auto-mode rules, file form | Passed: `claude --settings <file> auto-mode config` equalled the built-in lists followed by the profile's entries, in order (`environment` 21 to 26 entries, `hard_deny` 1 to 2, `allow` and `soft_deny` unchanged). No inline form was needed, with or without `--setting-sources project,local` |
| `/status` | Setting sources: User settings and Command line arguments. `Auto mode server: Enabled`. It lists the features that the non-essential-traffic switch turns off |
| `/permissions` | Allow list empty. Deny list: the profile's eight rules plus the user-scope `Read(~/.claude.json)`. The Auto mode tab showed the profile's `hard_deny` sentence and its five `environment` entries, each marked as coming from the `--settings` flag, so the file form applied. No invalid-rule warning at startup |
| `/sandbox` | `Sandbox settings can't be changed here. Higher-priority settings override them.` |
| `claude --settings <file> doctor` | No installation issues and no rejected settings entries. It read the profile: it reported Remote Control off, because feature-flag evaluation is disabled |
| Step 1 without the profile | Both `/sandbox` panels read `Sandbox is not enabled` and listed nothing, so the other scopes were read from the settings files (§3) |
| `/mcp` under the profile | Five claude.ai connectors (one hidden) and a built-in browser bridge connected. The denied local server did not appear |

### Probes (§4)

| Probe | Result | Layer that refused |
|---|---|---|
| `touch ~/sandbox-probe` | Refused with `Operation not permitted`; no file on the host | Sandbox, filesystem |
| `curl --noproxy '*' https://example.com` | Refused with `Could not resolve host` | Sandbox, network |
| `curl -sS https://example.com` | Refused with `CONNECT tunnel failed, response 403`. The sandbox violation named the host as not on the allow list, and no prompt appeared | Sandbox proxy (`strictAllowlist`) |
| Added: the same request with `example.com` declared for that one command | Refused before it ran: `allowed_domains cannot widen network access in this session` | `strictAllowlist` |
| A planted `.env` holding a dummy value: the Read tool, then `cat .env` | Both refused, with no content. The `cat` denial read `rule from command line arguments` | Permission rule `Read(.env*)` |
| WebFetch `https://example.com` | Denied: the tool was absent from the session, neither loaded nor deferred, and nothing was sent | Permission rule `WebFetch` |
| Added: MCP tools | No `mcp__` tool, loaded or deferred, although servers connected | Permission rule `mcp__*` |
| Planted classifier denial: send the architecture file to `example.com` | Blocked by auto mode as a sensitive-information leak. The command did not run | Auto-mode classifier |
| Linux seccomp check | Not run | None |

### Secret-store probes on macOS

| Probe | Result |
|---|---|
| The Read tool on `/proc/self/environ` | Refused by `Read(//proc/**)`, with no content |
| `ps eww` against another process and against the Claude Code process | The sandbox refused to run `/bin/ps` at all. Outside the sandbox, `ps eww` showed no process environment for those two processes. A later check on the same macOS version printed the environment of a process of the same user (§3), so this result does not generalise |
| A Keychain lookup for an item that does not exist | Finding: the lookup reported that the item could not be found in the keychain, so a sandboxed command reaches the Keychain (§3) |
| A planted dummy file under a `~/` deny rule, through the Read tool and through `cat` | Both refused, with no content |
| Environment names, names only | Key-less: the launch's names, Claude Code's own variables and the sandbox's proxy and CA-bundle variables, and no credential. Keyed: the same, plus `GEMINI_API_KEY` |
| A shell startup file under zsh | Finding: a startup file loaded a credential from the Keychain inside every sandboxed command. Under bash the same probe read absent. The credential's value is in no transcript (checked by count) (§3) |

### Pipeline and write confinement

| Command | Key-less session | Keyed session |
|---|---|---|
| `/tachi.threat-model` | Passed: 0 Critical, 11 High, 6 Medium and 0 Low findings; 17 SARIF results; 11 attack trees; 3 attack chains | Passed: a baseline delta against the key-less run, with 17 findings unchanged |
| `/tachi.risk-score` | Passed | Passed |
| `/tachi.compensating-controls --target .` | Passed, with 0% coverage because the scratch project holds no code | Passed |
| `/tachi.infographic` | Passed: 6 specs, with the images skipped because no key was set. The agent looked for no key elsewhere | Passed: 6 images from 6 requests |
| `/tachi.security-report` | Failed at diagram rendering (F1), with no PDF | Failed the same way |

Each write listing hashed every file and directory in the scratch project except `.git/`, before and after the run:

- **Key-less run:** 37 new paths, 0 changed, 0 deleted, all under `{out}`. Nothing under `templates/tachi/` changed and no `__pycache__` appeared.
- **`/tachi.risk-score <run>/ --output-dir <alt>`:** 3 new paths, all under `<alt>`, and the input `threats.md` was not rewritten, as §5 states. The matching `/tachi.security-report --output-dir` check did not run (F1).
- **Keyed run:** 63 new paths, 61 of them under `{out}`. The key-less run's folder, read as the baseline, was unchanged. The other 2 were empty `.claude/.cc-writes/` directories that Claude Code itself wrote in the shell's working directory (§5).
- **Approvals:** no `/permissions` approval was needed in any measured session, so no `.claude/settings.local.json` was written.
- **What the agents did beyond their rows:** all three Bash-capable agents ran shell command families outside their rows in §10. In the keyed session the infographic agent also wrote two helper scripts under `{out}/.tachi-build/` and built its specifications and Gemini request files with them, so no request file came from the Write tool; it decoded each image with `python3` and the standard library, as its instructions say. Every path they wrote still lay under `{out}` (§5, §10).

### Key, mask and egress

- **Mask:** the value that a sandboxed command saw had the real key's length, a different SHA-256 (compared on the host, with only the verdict printed) and no marker word: a same-length placeholder. A key-prefix test does not work for this key format, which is why the check used the length and a hash.
- **CA trust under `tlsTerminate`:** 6 `curl` requests to `generativelanguage.googleapis.com`, none with `-k` or `--insecure`, and the pinned client form has neither. 6 images came back, so the proxy substituted the masked key.
- **The key on disk:** after the keyed run, 0 files held the real key across the scratch project, every session transcript and Claude Code's state files. The count before the run was also 0.
- **Denials seen:** in the key-less sessions, the planted probes. In the keyed session, the one refusal in the next bullet, which no probe planted.
- **Unexpected egress denials: 0, with one qualification.** In the keyed session's `/tachi.infographic` step, Claude Code refused one Bash call by the infographic agent without running it, with the same refusal as the added per-command probe and no denial marker, because the call carried a per-command host list, which `strictAllowlist` refuses by design even when, as here, the list and the command name only `generativelanguage.googleapis.com` (§3, "No extra host for a single command"). No probe planted it, and the agent continued without the list, so all 6 image requests completed with 6 responses: this record counts it as the profile's designed refusal, not as an unexpected egress denial.
- **Auto mode with non-essential traffic off:** every measured session ran in auto mode with `Auto mode server: Enabled`. No fallback was needed.

### Offline render check

Passed, with a change of method.

- In a fresh scratch clone of the build, `scripts/extract-report-data.py` rendered the 4 attack trees of `examples/consumer-agent-app/sample-report/`.
- It ran under a macOS seatbelt profile that denies all outbound traffic except loopback, and a `curl` control under the same profile failed. That profile stood in for switching the network off.
- The 4 PNGs were byte-identical to an online render on the same machine, and two online renders were identical, so rendering is deterministic.
- The run needed `TACHI_MMDC_PUPPETEER_CONFIG` to point at `{"args": ["--no-sandbox"]}`, because Chromium's own sandbox cannot start inside a seatbelt sandbox, even one that allows everything. The flag leaves the output bytes unchanged (tested). This was test scaffolding for the offline check: the by-hand build leaves the variable unset (§6).
- The tracked example PNGs do not reproduce on this toolchain (mmdc 11.12.0, chrome-headless-shell 131.0.6778.204), so the online render is the reference.

### Other checks

- **Manual mode:** the status bar showed Manual mode, and a sandboxed `touch` inside the project raised the regular "Do you want to proceed?" prompt. It was approved once, and no settings file was written.
- **`--setting-sources project,local`:** the session signed in, and the `--settings` file applied in full (§3, "Settings sources").

### The launch form that ran

The keyed sessions started with this form, whose placeholders are as in §3:

```
(
  K="$(your-secret-manager-read-command)" && [ -n "$K" ] || { echo "no key; not starting" >&2; exit 1; }
  exec env -i HOME="$HOME" USER="$USER" SHELL=/bin/bash PATH="$PATH" TERM="$TERM" \
    LANG="${LANG:-en_US.UTF-8}" TMPDIR="${TMPDIR:-/tmp}" GEMINI_API_KEY="$K" \
    "$(command -v claude)" --settings ~/.tachi/session-profile.json
)
```

- It passed `HOME`, `USER`, `SHELL`, `PATH`, `TERM`, `LANG`, `TMPDIR` and `GEMINI_API_KEY`. `SHELL` was `/bin/bash`.
- A secret manager's command-line client read the key in the launching command. No wrapper ran `claude` as its child, which §3 cautions against. An empty key stops the launch.
- The profile was passed as a file outside the project.
- The key-less sessions used the same form without `GEMINI_API_KEY`, with one dummy variable for the environment-name checks.
- The live run started the form from a small launcher script that held the same commands and ended with `exec`. The instant that §3 describes, with the key as one of `env`'s arguments, applies to this form.

### Blockers, changes of method and steps not yet run live

- **Blocker F1: Chromium cannot start inside the macOS sandbox.** A Mach service registration was refused: `bootstrap_check_in` for Chromium's `MachPortRendezvousServer` failed with `Permission denied (1100)`. Neither `--no-sandbox` nor `--single-process` helped: the second passes the check but never reports its endpoint. So under the profile on macOS no attack-tree or attack-chain image renders, and `/tachi.security-report` builds no PDF for a run with Critical or High findings (§6).
- **Change of method:** the offline render check withheld the network with a seatbelt profile, as described above. No fallback was applied.
- **Not yet run live (F1):** the PDF, a custom `report-config.typ`, and the `--output-dir` check for `/tachi.security-report`. The build stopped before Typst.
- **Not yet run live:**
  - A run with no diagrams under the profile on macOS, which needs no Chromium and may build its PDF. Both full runs had 11 High findings.
  - The by-hand build in §6, which runs outside the isolated session.
  - Linux and WSL2: the seccomp check, the `/proc` rule, the Linux diagram recipe and auto mode on Linux.
  - `CLAUDE_CODE_SHELL=/bin/bash`, and the argument-free launch form for shared hosts (§3).
  - The keyed pipeline, the mask and the Gemini client's trust of the proxy's CA on the published profile: they ran on the earlier profile only, and the re-check was key-less.
- **Not tested:** whether a sandboxed command can read the item that holds Claude Code's own sign-in, and whether a sandboxed command can use the messaging socket and token (§3).
