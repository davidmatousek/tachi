# Data Model: Isolated and Auditable Operation (Feature 391)

All entities are files or document sections; there is no database. Field names below are the ones the contracts in `contracts/` fix.

## VersionMarker (`templates/tachi/VERSION`) — Part B2
| Field | Type | Rule |
|---|---|---|
| `tachi_version` | string, one line `tachi_version: <value>` | Tracked placeholder value `unknown`. At install `<value>` = `git describe --tags --always --dirty` of the source clone after any `--version` checkout; `<manifest ".">-release-manifest` when no git tree (labelled, never a describe string); else `unknown`. Never SemVer `+` build metadata. |
Writers: `install.sh` (removes any existing marker before the copy loop; writes after it, inside the containment and symlink guards), the README manual-install loop (same line after its copy). Every copy path resets the value to `unknown` because the placeholder is tracked. Readers: `stamp-tachi-version.py` (Step 2.6 of `/tachi.threat-model`) and `archive-run-transcripts.py` (P0B0-6; the archiver is not shipped in 391: B1 was honest-stopped at T051, TW-B1). Residual: a pre-391 installer used to downgrade cannot reset the marker.

## ThreatsFrontmatter (`threats.md`, schema 1.5) — Part B2
Declared keys after reconciliation: `schema_version` ("1.5"), `date`, `input_format`, `classification` ("confidential"), plus the de-facto keys documented: `run_id`, `baseline`, `coverage_gate`, `has_attack_chains`, `has_agentic_patterns`, `has_source_attribution`, and the new `tachi_version` (string; marker value or `unknown`). Additive: 1.4 readers ignore unknown keys. `generated_at` is never added.

## RunManifest (`run-manifest.json`, `manifest_version: 1`) — Part B1
*Not shipped in 391: B1 was honest-stopped at T051 (TW-B1, `test-results/tw-b1-w2.md`). This section stays as the design record for the follow-up.*

| Field | Type | Rule |
|---|---|---|
| `manifest_version` | int | 1 |
| `tachi_version` | string | marker value or `unknown` |
| `session_id` | string | main transcript stem |
| `claude_code_versions` | [string] | distinct `version` values seen in transcripts |
| `started_at`, `ended_at`, `archived_at` | ISO-8601 UTC | first/last transcript timestamps; archive time |
| `transcripts[]` | {`path`, `bytes`, `sha256`} | every archived file |
| `main` | {`served_model_histogram`: {model: int}, `turns`: int, `synthetic_turns`: int, `tool_calls_by_tool`: {tool: int}} | main session; no `pinned_model` |
| `subagents[]` | {`agent_id`, `agent_type`, `attribution_agent`, `spawn_depth`, `parent_tool_use_id`, `pinned_model`, `served_model_histogram`, `synthetic_turns`, `turns`, `tool_calls_by_tool`, `unknown_meta_keys`: [string]} | one per subagent instance, tachi or not; `pinned_model` from the agent file matched by `agent_type` or `null` |
| `dispatches[]` | {`agent`, `tool_use_id`, `dispatched_from`: "main" or `<agent_id>`, `spawn_depth`, `status`: recorded|dispatch-failed|not-recorded} | every `Agent`/`Task` `tool_use` naming a tachi agent, in any transcript at any depth, failed ones included |
| `tachi_agents_not_recorded[]` | {`agent`, `tool_use_id`, `dispatched_from`, `reason`: no-transcript|dispatch-failed} | successful dispatches with no matching meta (`no-transcript`, trips TW-B1) and errored dispatches (`dispatch-failed`, listed only); never inferred |
| `tachi_agents_not_dispatched` | [string] | installed tachi agents (roster = the `name:` values of the installed `.claude/agents/tachi/*.md`; the matrix is not installed and its absence never exits 2) with neither a recorded instance nor a dispatch, so an inline-analysing orchestrator never yields an empty listing |
| `permission_modes_seen` | [string] | distinct values of the `permission-mode` entries in every archived transcript |
| `egress_observed[]` | {`host`, `tool`, `count`} | hostnames only (no userinfo, query, fragment); unparsable → `<unparseable>` |
| `egress_unparsed_count` | int | |
| `egress_denied[]` | {`host`, `kind`: sandbox|classifier|permission-rule, `count`} | |
| `denial_detection` | {`validated_claude_code_versions`: [string], `status`: validated|not-validated} | fails closed: `validated` only when every version in `claude_code_versions` has a passing fixture; never an empty list standing for "none" |
| `artifacts[]` or `null` + `artifacts_reason` | {`path`, `bytes`, `sha256`} | requires `--output-dir` |
Validation: structured fields only, no free text; final secret scan per `schemas/run-manifest.yaml` (`redaction.final_scan`). It applies 20 key-format rules with boundaries, and it checks the values of environment variables whose names contain KEY, TOKEN, SECRET, PASSWORD, PASSWD, PASSPHRASE, PWD, CREDENTIAL, PRIVATE, AUTH, DSN or DATABASE_URL. `PWD`, `OLDPWD`, `SSH_AUTH_SOCK` and `XAUTHORITY`, and names that start with `GIT_AUTHOR_` or `GIT_COMMITTER_`, are excluded by name (T040 X-8); `AUTH` itself is not loosened. Each value is stripped, split into pieces when it holds whitespace, JSON or a URL password, and matched raw and as hex, base32, base64, base64url, percent-encoded and JSON-escaped text. Values under 8 characters, and date, timestamp, version and IP shapes, are skipped (P0B0-11 as amended at T034). Hash fields are excluded, and the run reports how many values it compared. A hit fails the run with no manifest written.

### Archive run states
`discovered` (project matched by `cwd`) → `resolved` (destination realpath; work-tree/ignore check) → `refused` (exit 1 with reason) | `copied` (0700/0600, `O_EXCL`, verbatim) → `parsed` (minimal contract) → `manifest-written` | `failed` (exit 1, no manifest). Re-archive of an identical session: `no-op` only when `run-manifest.json` is present and matches the source (P0B0-5); hash-equal transcripts without it are `refused` (incomplete archive).

## MatrixRow (`CLAUDE_PERMISSIONS.md` §8, agents table) — Part A3
| Column | Values | Enforcement |
|---|---|---|
| Agent | `tachi-*` name | n/a |
| Tier | read-only / writer / Bash | derived |
| Tools | set from `tools:` | **enforced** by Claude Code |
| Model | `model:` value | applies unless an invocation passes a model (tachi's commands never do) |
| Bash families | first tokens allowed in fenced shell blocks | declared |
| Writes | paths under `{out}` (and `$TMPDIR` for the extractor's children) | declared |
| Hosts | model provider (all); Gemini host (threat-infographic, with key) | declared |
## CommandRow (§8, commands table)
Command, frontmatter keys (today `{description}`; values recorded once `allowed-tools`/`model` are set), **Dispatches** (the tachi agent the command invokes; `/tachi.security-report` → `tachi-report-assembler` after AD-13), Bash it instructs (declared-only; `/tachi.threat-model` gains `stamp-tachi-version.py` at Step 2.6), writes (`{out}/…`; architecture: `docs/security/architecture.md` + `.archive/v{N}/`), child processes (mmdc, headless Chromium — invisible to transcripts and permission rules).

## SessionProfile (fenced JSON in the runbook) — Part A2
Keys: `env.CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`; `permissions.deny` [WebFetch, WebSearch, mcp__*, ListMcpResourcesTool, ReadMcpResourceTool, ReadMcpResourceDirTool, SendMessage, ListAgents, Monitor, RemoteTrigger, ShareOnboardingGuide, Read(~/.ssh/**), Read(~/.aws/**), Read(~/.claude/.credentials.json), Read(//proc/**), Read(.env*)]; `sandbox.{enabled, failIfUnavailable, allowUnsandboxedCommands=false, autoAllowBashIfSandboxed=false, network.{allowedDomains=[gemini host], strictAllowlist, tlsTerminate}, credentials.{envVars[mask GEMINI_API_KEY injectHosts=[gemini host]], files[deny ~/.ssh, ~/.aws, ~/.claude/.credentials.json]}}`; `autoMode.{environment, hard_deny}` each containing `"$defaults"`. The contract test asserts a **closed key set** (the 19 exact key paths in `contracts/session-profile.md`), the scalar values shown there, and the members of `permissions.deny`, `sandbox.credentials.files` and `sandbox.credentials.envVars` (compared as sets); named negatives: `sandbox.excludedCommands`, `sandbox.ignoreViolations`, `sandbox.allowNestedUserNamespaces`, `sandbox.allowAppleEvents`, `sandbox.enableWeakerNestedSandbox`, `sandbox.enableWeakerNetworkIsolation`, `sandbox.filesystem.allowWrite`, `sandbox.filesystem.allowRead`, `sandbox.filesystem.disabled`, `sandbox.network.allowAllUnixSockets`, `sandbox.network.allowUnixSockets`, `sandbox.network.allowLocalBinding`, `sandbox.network.allowMachLookup`, `sandbox.network.httpProxyPort`, `sandbox.network.socksProxyPort`, `sandbox.credentials.allowPlaintextInject`, `permissions.allow`, `permissions.additionalDirectories`, `permissions.defaultMode`, `autoMode.allow`, `autoMode.soft_deny`. Invariants: exactly one host in `allowedDomains`; `injectHosts` ⊆ `allowedDomains`; `"$defaults"` in every `autoMode` list; `tlsTerminate` present with any `mask`; the `hard_deny` sentence byte-exact against PRD FR-6. Rulings: `test-results/w1-audit-rulings.md` AR-15 to AR-20.

## LiveValidationRecord (runbook section) — Part A2
Claude Code version; OS(es); permission mode actually run; date; configurations (with/without key); probe results (table, planted `.env` via Read and `cat`, WebFetch denied, offline mmdc byte-identical, Gemini CA trust, auto mode with non-essential traffic off or fallback); unexpected egress denials = 0; blockers.

## SweepRecord (W3 / delivery.md) — all parts
SC-002 sweep (six documents, D-3 sentence present or claim removed; immutable records untouched) and Wording Rules sweep (Pattern A hits = 0; Pattern B hits with disposition).

## GuardResult (`check-agent-privileges.py --json`)
`{status: pass|drift|infra, roster: {agents: int, allowlisted: [path], red: [path]}, drift: [{agent, check: tools|model|keyset|command|bash|writes, expected, actual}], self_test: pass|fail}`; exit 0/1/2.
