# Session profile for isolated operation (Part A2)

Shipped as one fenced JSON block in `docs/guides/ISOLATED_OPERATION_TACHI.md` between `<!-- BEGIN TACHI SESSION PROFILE -->` and `<!-- END TACHI SESSION PROFILE -->` markers; the adopter saves it anywhere and launches `claude --settings <file>` for tachi sessions. Validated by `tests/scripts/test_isolated_profile_contract.py` (extracts the block) and live in SC-A1. Every key cites the public Claude Code docs page it comes from (sandboxing, permissions, auto-mode configuration, settings reference, permission modes).

```json
{
  "env": { "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1" },
  "permissions": {
    "deny": ["WebFetch", "WebSearch", "Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(.env*)"]
  },
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false,
    "network": {
      "allowedDomains": ["generativelanguage.googleapis.com"],
      "strictAllowlist": true,
      "tlsTerminate": {}
    },
    "credentials": {
      "envVars": [{ "name": "GEMINI_API_KEY", "mode": "mask", "injectHosts": ["generativelanguage.googleapis.com"] }],
      "files": [{ "path": "~/.ssh", "mode": "deny" }, { "path": "~/.aws", "mode": "deny" }]
    }
  },
  "autoMode": {
    "environment": [
      "$defaults",
      "Primary use: threat modeling with tachi. tachi reads an architecture description and a local checkout, writes only under the run's output directory, and never connects to, scans or modifies a running system.",
      "Host containment: Bash runs in Claude Code's sandbox with network limited to generativelanguage.googleapis.com; the cloud metadata endpoint is not reachable.",
      "Trusted internal domains: generativelanguage.googleapis.com, only for the optional /tachi.infographic image request.",
      "Sensitive data locations & audiences: the run's output directory and the architecture file hold confidential threat models. Audiences: the security team; Google's Gemini API for the derived infographic prompt only (finding IDs with one-line threat descriptions; component, trust-zone and data-flow labels; severity counts and the overall risk posture).",
      "Data retention: Claude Code transcripts are kept 30 days or more via cleanupPeriodDays."
    ],
    "hard_deny": [
      "$defaults",
      "Never use a tool (Bash, WebFetch, WebSearch, an MCP server or any other) to send tachi threat-model outputs, the architecture description, or files read from the analyzed repository to any network host other than generativelanguage.googleapis.com. Requests to that host are acceptable only from the /tachi.infographic image step and only with the derived infographic prompt."
    ]
  }
}
```

**Contract test**: a **closed key set** — the profile's exact key paths as shown, nothing else — plus the invariants: exactly one host in `allowedDomains`; every `injectHosts` entry ∈ `allowedDomains`; `"$defaults"` present in every `autoMode` list; `tlsTerminate` present whenever a `mask` entry exists; the `hard_deny` sentence byte-exact against PRD FR-6. Named negative cases: `sandbox.excludedCommands`, `sandbox.filesystem.allowWrite`, `allowNestedUserNamespaces`, `enableWeakerNestedSandbox`, `enableWeakerNetworkIsolation`, `filesystem.disabled`, `ignoreViolations`, `network.allowAllUnixSockets`, `network.allowLocalBinding`, `permissions.allow`, `defaultMode`, `autoMode.allow`, `autoMode.soft_deny`. The audiences text is confirmed by Lane R against the pinned client form (AD-15) before the runbook is written.

**Disclosures the runbook prints beside the block**: `tlsTerminate` is experimental and lets the local proxy read sandboxed commands' HTTPS; the fallback is to deny the key (key-less isolated default, no image). Read deny rules are the primary secret-file control (the Read tool runs outside the sandbox; `credentials.files` covers sandboxed Bash only); the baseline invites extension to `~/.netrc`, `~/.git-credentials`, `~/.kube`, `~/.docker/config.json` and cloud-CLI configs. MCP servers: list any configured server in `deniedMcpServers` or confirm none; hooks, the status line and local MCP servers run outside the sandbox. The effective configuration is a union across scopes: check it (`/sandbox` Config tab; `claude --settings <file> auto-mode config`) and run the probes under the profile. Path forms: avoid the single-slash `/path` form (anchors at the profile's directory); `~/`, `//` and working-directory-relative forms are fine.

**User-global (optional)**: `cleanupPeriodDays` ≥ 30 (never lowered; archive with B1 before starting another session if any settings file lowers it, since the sweep's cross-project scope is undocumented) in `~/.claude/settings.json`; an opt-in always-on copy of the sandbox block, presented merge-not-replace. **`--setting-sources`**: not recommended by default (excluding `project` disables tachi's installed agents, commands and skills); excluding `user` is opt-in hardening with its costs listed (provider and auth config, user-scope masks, retention default, auto-mode re-prompt); the effective-config check names user-scope `excludedCommands`, `allowWrite`, `allowedDomains` and `WebFetch(domain:…)` allows as things to look for. Model selection: the runbook states only that a per-invocation `model` overrides agent frontmatter, that tachi passes none, and that the manifest or transcripts record what served.

**Probe table** (run first, inside the session): `touch ~/sandbox-probe` fails; `curl --noproxy '*' https://example.com` fails; a planted `.env` is refused through Read and through `cat`; a WebFetch is denied.
