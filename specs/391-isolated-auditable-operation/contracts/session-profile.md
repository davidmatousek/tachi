# Session profile for isolated operation (Part A2)

Shipped as one fenced JSON block in `docs/guides/ISOLATED_OPERATION_TACHI.md` between `<!-- BEGIN TACHI SESSION PROFILE -->` and `<!-- END TACHI SESSION PROFILE -->` markers; the adopter saves it anywhere and launches `claude --settings <file>` for tachi sessions. Validated by `tests/scripts/test_isolated_profile_contract.py` (extracts the block) and live in SC-A1. Every key cites the public Claude Code docs page it comes from (sandboxing, permissions, auto-mode configuration, settings reference, permission modes). Final at the T016 profile review (`test-results/w1-audit-rulings.md`, AR-15 to AR-20): T016's first commit copies the block verbatim, and the pre-staged W2 profile is replaced by the block extracted from the runbook before T020.

*Amended at W3 (architect, AR-21, 2026-11-20): eight built-in tools denied by bare name, member list only; no key path added.*

*Amended again at W3 (architect, AR-21a, W3-3a, 2026-11-20): `Workflow` and `Agent(isolation:*)` added to `permissions.deny`; member list only; no key path added.*

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

**Contract test**: a **closed key set**, the profile's exact key paths as shown and nothing else (19 paths). The scalar values as shown: `sandbox.enabled`, `sandbox.failIfUnavailable` and `sandbox.network.strictAllowlist` are `true`; `sandbox.allowUnsandboxedCommands` and `sandbox.autoAllowBashIfSandboxed` are `false`; `sandbox.network.tlsTerminate` is `{}`; `env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is `"1"`. The member lists as shown, compared as sets: `permissions.deny` (eighteen rules), `sandbox.credentials.files` (three `deny` entries) and `sandbox.credentials.envVars` (one `mask` entry). The invariants: exactly one host in `allowedDomains`; every `injectHosts` entry ∈ `allowedDomains`; `"$defaults"` present in every `autoMode` list; `tlsTerminate` present whenever a `mask` entry exists; the `hard_deny` sentence byte-exact against PRD FR-6; AR-21: the eight tool denies, bare names (each present exactly as written); AR-21a: `Workflow` by bare name and `Agent(isolation:*)` as that exact rule (a rule for one value, such as `Agent(isolation:remote)`, does not count). Named negative cases, each a key path the test must reject. They are the keys that the sandboxing page lists as weakening or loosening the sandbox (under "Keep developers from widening the policy" and "Repository settings under an admin-required sandbox"), plus the profile's own forbidden keys: `sandbox.excludedCommands`, `sandbox.ignoreViolations`, `sandbox.allowNestedUserNamespaces`, `sandbox.allowAppleEvents`, `sandbox.enableWeakerNestedSandbox`, `sandbox.enableWeakerNetworkIsolation`, `sandbox.filesystem.allowWrite`, `sandbox.filesystem.allowRead`, `sandbox.filesystem.disabled`, `sandbox.network.allowAllUnixSockets`, `sandbox.network.allowUnixSockets`, `sandbox.network.allowLocalBinding`, `sandbox.network.allowMachLookup`, `sandbox.network.httpProxyPort`, `sandbox.network.socksProxyPort`, `sandbox.credentials.allowPlaintextInject`, `permissions.allow`, `permissions.additionalDirectories`, `permissions.defaultMode`, `autoMode.allow`, `autoMode.soft_deny`. The audiences text is the PM's T005 ruling (`test-results/field-list.md` §10.3), checked against the pinned client form (AD-15).

**Disclosures the runbook prints beside the block** (content for T016's second commit; task IDs and `test-results/` pointers are authoring notes, not runbook text):

- **TLS termination.** `tlsTerminate` is experimental and lets the local proxy read sandboxed commands' HTTPS; masking requires it. The fallback is to deny the key: the key-less isolated default, with no image.
- **Secret files and the process environment.** Read deny rules are the primary secret-file control: the Read tool runs outside the sandbox, `credentials.files` covers sandboxed Bash only, and Claude Code adds the paths of Read deny rules to the sandbox's read denies. The baseline covers `~/.ssh`, `~/.aws`, Claude Code's login file `~/.claude/.credentials.json`, `.env*` files under the working directory and, on Linux, `/proc`, where the Read tool could otherwise read the environment of the Claude Code process, which holds the real image key and any provider credential set in the environment. On macOS, `Read(//proc/**)` has no effect. The extension note names `~/.claude.json` (account details and personal MCP server definitions), `~/.netrc`, `~/.git-credentials`, `~/.kube`, `~/.docker/config.json` and cloud-CLI configs. With `CLAUDE_CONFIG_DIR` set, add both credentials-file entries for `<that directory>/.credentials.json` in the `~/` or `//` form, because rule paths expand no variables. The key-provisioning claim uses the scoped wording in `test-results/security-a.md` §5.6.
- **MCP servers.** The profile denies every MCP tool (`mcp__*`) and the three built-in tools that list and read MCP resources, whose names do not start with `mcp__`: `ListMcpResourcesTool` and `ReadMcpResourceTool` (both in the tools reference) and `ReadMcpResourceDirTool` (not in the tools reference; observed on Claude Code 2.1.330). A configured local MCP server still starts and runs outside the sandbox, so list each configured server in `deniedMcpServers` to stop it loading, or confirm there are none. Command hooks, local MCP servers, plugin monitors, LSP servers, mods, and helper commands such as the status line and `apiKeyHelper` run outside the sandbox with your full access.
- **Built-in tools past the sandbox.** Eight built-in tools run in the Claude Code process, outside the sandbox, and most need no permission prompt, so the profile denies each by bare name: the three MCP resource tools above, `SendMessage` and `ListAgents` (messaging between your sessions), `Monitor` (a WebSocket watch that Claude Code opens itself), `RemoteTrigger` (cloud scheduled tasks on claude.ai) and `ShareOnboardingGuide` (an upload to claude.ai); tachi uses none of them. `Artifact`, `PushNotification` and `SendUserFile` stay because the profile's `env` key turns off what they need (claude.ai publishing and Remote Control), and `Agent` stays because tachi needs it.
- **Cloud sessions from the Agent tool.** On Claude Code 2.1.330 the Agent tool also offers a `remote` isolation value, which launches the agent in a cloud environment that does not enforce the local session's restrictions. The profile therefore denies every Agent call that sets an isolation value (`Agent(isolation:*)`), and denies `Workflow` by bare name because the docs describe no launch options for a workflow script's agents. tachi's dispatches set no isolation value and tachi uses no workflow; an organization Owner can turn cloud sessions off with `allow_remote_sessions`, which is not a profile key.
- **Classifier coverage.** `autoAllowBashIfSandboxed: false` keeps sandboxed commands in the regular permission flow, whatever the version default is (`true` before v2.1.324) and whatever a repository, local or user file sets. In auto mode they therefore reach the classifier and its `hard_deny` like any other command; read-only commands, and commands that a narrow allow rule matches, can still skip it. In Manual mode (the pre-ruled fallback) each such command prompts. `strictAllowlist` also makes Claude Code refuse auto mode's per-command host lists, so no host outside `allowedDomains` opens for a single command.
- **Effective configuration.** It is a union across scopes. Lists merge, so the profile cannot remove another file's entries; a scalar the profile sets wins over user, project and local files. Under the profile `/sandbox` does not open ("Sandbox settings can't be changed here"), because the profile sets sandbox keys above the local level. Check the other scopes from a session started in the same project without the profile: its `/sandbox` Config tab lists what your user, project and local files add, such as allowed domains, write paths, excluded commands, read re-opens and weakening switches. In the profile session, read `/status` (the setting sources include command-line arguments), `/permissions` (the merged rules, including user `WebFetch(domain:…)` allows, which widen the sandbox allowlist, and narrow Bash allow rules, which skip the classifier in auto mode) and `claude --settings <file> auto-mode config`. If that output lacks the profile's entries, pass the same JSON inline (`claude --settings "$(cat <file>)"`). Then run the probes under the profile.
- **Linux and WSL2.** Install the optional seccomp filter (`npm install -g @anthropic-ai/sandbox-runtime`) and check the Dependencies tab of `/sandbox` in a session without the profile. Without the filter the sandbox does not block Unix-socket connections, such as a container runtime's socket or, on WSL2, the interop socket that launches Windows programs.
- **Path forms.** In permission rules avoid the single-slash `/path` form, which anchors at the profile's directory; `~/`, `//` and working-directory-relative forms are fine. Sandbox path lists use the opposite convention (`/path` is absolute), so a path copied between the two changes its meaning.
- **A form not to substitute.** Keep the bare `WebFetch` deny. `WebFetch(domain:*)` in `deny` also denies every host to sandboxed commands, the Gemini host included.
- **Scope of the profile.** It is for local sessions. In an Anthropic-hosted cloud session `failIfUnavailable` lets the session start with a warning, and the `sandbox.filesystem` and `sandbox.network` rules are not enforced. The `env` key also keeps Claude Code's artifact publishing off.

**User-global (optional)**: `cleanupPeriodDays` ≥ 30 in `~/.claude/settings.json`, never lowered. If any settings file lowers it, raise it again, or copy the transcripts you need out of `~/.claude/projects/`, before starting another session, since the sweep's cross-project scope is undocumented; the archiver form of this sentence is Part B text (T048, AD-14). An opt-in always-on copy of the sandbox block, presented merge-not-replace; it carries `autoAllowBashIfSandboxed: false`, so other sessions in Manual mode prompt for sandboxed commands, and leaving that key out of the always-on copy is the adopter's choice because the profile sets it for tachi sessions. **`--setting-sources`**: not recommended by default (excluding `project` disables tachi's installed agents, commands and skills); excluding `user` is opt-in hardening with its costs listed: provider and auth configuration; user-scope environment-variable masks; the retention sweep pauses when no enabled source sets `cleanupPeriodDays`; a mode dialog that the user file suppressed can appear again (documented for the bypass-permissions warning). The effective-config check names user-scope `excludedCommands`, `allowWrite`, `allowedDomains`, `WebFetch(domain:…)` allows, narrow Bash allow rules and weakening switches set to `true` as things to look for. Model selection: the runbook states that a per-invocation `model` overrides agent frontmatter and that tachi passes none; that `CLAUDE_CODE_SUBAGENT_MODEL` alone does not change tachi's pins, while `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` set with it (v2.1.257 or later) overrides them all; and that the session transcripts record what served. It links §8.1 of `CLAUDE_PERMISSIONS.md` for the rest. The manifest clause ("the manifest or the transcripts") is Part B text (T048, AD-14).

**Probe table** (run first, inside the session; ask Claude to run each line, because a line typed at the `!` prompt runs outside the sandbox):

- `touch ~/sandbox-probe` fails with `Operation not permitted` (macOS) or `Read-only file system` (Linux, WSL2);
- `curl --noproxy '*' https://example.com` fails with `Could not resolve host`;
- `curl -sS https://example.com` fails without reaching `example.com` (the result names the host as blocked), and no prompt appears; this confirms that `strictAllowlist` is in force;
- a planted `.env` is refused through Read and through `cat`;
- a WebFetch is denied.

Record which layer refused each line. A permission-rule or classifier refusal of a `touch` or `curl` line is not a sandbox result: approve the action under `/permissions` → Recently blocked and let Claude retry it. The `/proc` and credentials-file rules are checked by configuration, not by reading a real secret store: `/permissions` lists `Read(//proc/**)` and `Read(~/.claude/.credentials.json)`, and no startup warning names them. The live `/proc` and credentials-file probes belong to the maintainer's validation run (T020, `test-results/security-a.md` §6) and are not adopter steps.
