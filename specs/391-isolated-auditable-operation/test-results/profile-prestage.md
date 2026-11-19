# Profile pre-stage and docs confirmation (T006)

Lane R (DEVOPS-R) | feature 391 | 2026-11-19 | task T006 (PRD §13 items 1 and 2) | closes CF-7

**Basis.** The public Claude Code documentation as served on 2026-11-19, read as raw Markdown from `https://code.claude.com/docs/en/<page>.md`. The pages carry no version stamp, so each version-gated statement below names the Claude Code version the page itself gives. No `claude` command was run, no live probe was made, and no credential file or environment value was read. "Expected" means an expectation for T020 and gate GL to check, not an observation. Quotes are short and exact. Where a heading anchor could not be matched, the page is cited and the section is named in words.

**Status.** T006 is complete and CF-7 closes with this record. The W2 profile is pre-staged (section 6).

## 1. Result

| Item | Disposition | In one line |
| - | - | - |
| (a) model-selection precedence | confirmed | `CLAUDE_CODE_SUBAGENT_MODEL` ranks below both the per-invocation `model` and the agent's own `model:`. Only `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` (Claude Code v2.1.257 or later) overrides them. `ANTHROPIC_DEFAULT_SONNET_MODEL` is not a ranked source: it sets what the `sonnet` alias resolves to |
| (b) excluding `project` | confirmed by the docs' definition of the `project` source; not observed on the CLI | Project skills, commands and subagents belong to that source, so tachi's installed agents, commands and skills would not load |
| (b) excluding `user`, four costs | three confirmed; one documented only for a different dialog | Provider and auth keys, user-scope environment-variable masks and the retention sweep: confirmed. The "auto-mode re-prompt": the docs state it for the bypass-permissions dialog, not for auto mode |
| (c) sweep scope | not documented explicitly | The path table and a telemetry counter point to all projects, but no sentence states the cross-project effect. Rule recorded in 4.3 |

## 2. (a) Model selection

### 2.1 What the docs state

| Claim | Exact words | Source |
| - | - | - |
| Order of sources for a subagent's model | "When more than one source sets a model, Claude Code uses the first in this order:" then (1) "The per-invocation `model` parameter, which Claude can pass when it starts the subagent.", (2) "The `model` field in the subagent's definition, including `inherit`", (3) the `CLAUDE_CODE_SUBAGENT_MODEL` environment variable, (4) the main conversation's model | [sub-agents, Choose a model](https://code.claude.com/docs/en/sub-agents#choose-a-model) |
| `CLAUDE_CODE_SUBAGENT_MODEL` does not outrank the other two | "A per-invocation model or a definition's `model` field, including `inherit`, takes precedence." | [model-config, Environment variables](https://code.claude.com/docs/en/model-config#environment-variables) |
| The documented override | "set `CLAUDE_CODE_SUBAGENT_MODEL` to that model and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` to `1`. Requires Claude Code v2.1.257 or later." With it on, "Claude Code ignores the `model` field in subagent definitions, and Claude can't pass a model when it starts a subagent." Forks, and skills that run in a subagent with `model: inherit`, still use the parent's model | [sub-agents, Run every subagent on one model](https://code.claude.com/docs/en/sub-agents#run-every-subagent-on-one-model) |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` is an alias mapping | "Model ID that the `sonnet` alias resolves to, and that `opusplan` uses when Plan Mode is not active." | [env-vars, variables table](https://code.claude.com/docs/en/env-vars) and [model-config, Environment variables](https://code.claude.com/docs/en/model-config#environment-variables) |
| The mapping reaches subagents | "By default, a subagent with a model alias runs on the version the alias points to." The per-invocation parameter "takes a model alias" too, so it resolves through the same mapping. No single sentence names both the variable and subagents; the two statements together confirm it | [sub-agents, Which version a model alias selects](https://code.claude.com/docs/en/sub-agents#which-version-a-model-alias-selects) and the Choose a model section above |
| Same-family exception | "With a family alias such as `opus` in the `model` field or per-invocation parameter, the subagent runs on its parent conversation's model in two cases:" the first being "Same family: for example, if your main conversation runs on `claude-opus-4-7`, a subagent with `model: opus` runs on that version too." | [sub-agents, Which version a model alias selects](https://code.claude.com/docs/en/sub-agents#which-version-a-model-alias-selects) |
| An organization allowlist reaches all of these | The `availableModels` allowlist applies to the subagent `model` field, the Agent tool's `model` parameter and `CLAUDE_CODE_SUBAGENT_MODEL`, and the alias variables "cannot redirect an allowed alias to a model outside the list" | [model-config, Restrict model selection](https://code.claude.com/docs/en/model-config#restrict-model-selection); [sub-agents, When an allowlist blocks a subagent model](https://code.claude.com/docs/en/sub-agents#when-an-allowlist-blocks-a-subagent-model) |
| Inspecting what a subagent runs on | `/tasks` names the model on the subagent's row (Claude Code v2.1.242 or later) | [sub-agents, Check a subagent's model](https://code.claude.com/docs/en/sub-agents#check-a-subagents-model) |

Answers to PRD §13 item 1: `ANTHROPIC_DEFAULT_SONNET_MODEL` does remap the alias for subagents. `CLAUDE_CODE_SUBAGENT_MODEL` does not outrank agent frontmatter, and neither variable outranks a per-invocation `model`, unless `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` is also set.

Repo facts checked for context (read-only search of the Part A tip, no script run): all 21 agent files under `.claude/agents/tachi/` set `model: sonnet`; a search of `.claude/commands/tachi.*.md` for `model:`, `model=`, `--model` and model-parameter or override phrasing found nothing. T004's audit owns the final statement that tachi passes no `model`.

### 2.2 What the runbook may state (AD-1)

Stated only because confirmed above, for T016 to use or leave out:

- A per-invocation `model` overrides an agent's `model:` field, and tachi passes none. This is the order list; the "tachi passes none" half is the repo fact above, owned by T004's audit.
- `CLAUDE_CODE_SUBAGENT_MODEL` alone does not change tachi's pins. Setting `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` as well (v2.1.257 or later) makes every subagent run on that one model and ignores the pins. An adopter whose user settings or shell set both variables loses the pins without a visible change in tachi.
- `ANTHROPIC_DEFAULT_SONNET_MODEL` changes which model the `sonnet` alias resolves to.
- The manifest or the transcripts record what served, and `/tasks` shows it live.

### 2.3 Two cautions for the PM and T016

1. **D-1 sentence versus the same-family exception.** PRD D-1 says "Claude Code resolves that alias through your provider, whatever model your interactive session uses." The docs add that when the session itself runs on a model of the same family, a subagent pinned to the family alias runs on the session's version instead. For tachi, a session on a Sonnet model means the `sonnet` pins follow the session's Sonnet version, not the alias mapping. The sentence is accurate for a session on another family. Wording is PM-owned; nothing was changed here. A minimal qualification would be "or follows your session's version when your session runs on a Sonnet model".
2. **The served model can differ from the pin.** The docs describe two mechanisms that re-run a subagent's request on another model. Availability fallback: "Claude Code also applies the chain to subagents. When a subagent's request fails over, Claude Code tries your configured fallback models in order, and the subagent continues on the model that accepts the request." ([Fallback model chains](https://code.claude.com/docs/en/model-config#fallback-model-chains), v2.1.247 or later). Content fallback: "**Sonnet 5.5**: cybersecurity-flagged requests re-run on Sonnet 5." ([Automatic model fallback](https://code.claude.com/docs/en/model-config#automatic-model-fallback)), and in a subagent "the request re-runs on it or the subagent fails, according to your **Switch models when a message is flagged** choice in `/config`" ([Subagents switch or fail without asking](https://code.claude.com/docs/en/model-config#subagents-switch-or-fail-without-asking)). This supports the contract's line that the manifest or transcripts record what served. It is also why "pinned" must not be read as "served".

## 3. (b) `--setting-sources`

The flag is defined in one line: "Comma-separated list of setting sources to load (`user`, `project`, `local`)." ([cli-reference](https://code.claude.com/docs/en/cli-reference#cli-flags)).

**Disposition for the runbook.** Not recommended by default. Excluding `user` is opt-in hardening, with the costs in 3.2. Excluding `project` would stop tachi from running, see 3.1.

### 3.1 Excluding `project` (confirmed by definition, not observed)

- The Agent SDK page defines the `project` source: "Project `settings.json` and hooks; project CLAUDE.md and `.claude/rules/*.md`; project skills, commands, and subagents" ([Control filesystem settings with settingSources](https://code.claude.com/docs/en/agent-sdk/claude-code-features#control-filesystem-settings-with-settingsources)).
- The CLI-side pages use the same concept for the flag. The sandboxing page says "If you exclude a source with `--setting-sources` on the CLI or `settingSources` in the Agent SDK" ([Configure sandboxing](https://code.claude.com/docs/en/sandboxing#configure-sandboxing)); the debug page says to pass `--setting-sources user` "to turn off project configuration such as `.claude/settings.json`, `CLAUDE.md`, and `.mcp.json`" ([Test against a clean configuration](https://code.claude.com/docs/en/debug-your-config#test-against-a-clean-configuration)); the memory page says "Project rules are skipped if you exclude `project` from" the flag ([Set up rules](https://code.claude.com/docs/en/memory#set-up-rules)).
- **Qualification.** No CLI-side page lists agents, commands and skills by name for the flag; the link from flag to those items runs through the shared definition of a "setting source". The contract's statement may stand with that citation. Nothing in T020 runs the flag with `project` excluded, so it stays unobserved.

### 3.2 Excluding `user`: the four costs

| Cost named in the contract | What the docs state | Status |
| - | - | - |
| Provider and auth configuration | The `user` source loads user `settings.json` (same SDK page). Provider and credential keys are settings keys that can live there: `env`, `apiKeyHelper`, `awsAuthRefresh`, `awsCredentialExport` are all scoped "Any file" ([settings index](https://code.claude.com/docs/en/settings-reference)), and the Bedrock setup "saves the result to the `env` block of your user settings file" ([Sign in with Bedrock](https://code.claude.com/docs/en/amazon-bedrock#sign-in-with-bedrock)). A session that excludes `user` does not read them | confirmed |
| User-scope masks | "User settings: Claude Code still applies the `deny` entries in `~/.claude/settings.json` and keeps its file `mask` entries as restrictions that no longer authorize the proxy to substitute the real value, but drops its environment variable `mask` entries." ([Protect credentials](https://code.claude.com/docs/en/sandboxing#protect-credentials)). Also, user-scope `sandbox.filesystem` entries, `Edit` rules and `Read` deny rules are ignored when the sandbox configuration is built (v2.1.246 or later; [Configure sandboxing](https://code.claude.com/docs/en/sandboxing#configure-sandboxing)) | confirmed |
| Retention default | The sweep does not fall back to 30 days. When user settings are excluded and no enabled source provides the key, it is paused: `skip_reason` `"user_source_disabled"` means "User settings are excluded, for example by the `--setting-sources` flag or the SDK's `settingSources` option, and no enabled source provides `cleanupPeriodDays`" ([retention sweep event](https://code.claude.com/docs/en/monitoring-usage#retention-sweep-event)). The contract's label "retention default" is better worded "the retention sweep pauses" | confirmed, with a wording correction |
| Auto-mode re-prompt | Documented for the bypass-permissions warning only: "If you pass `--setting-sources` without `user`, the dialog can appear again although you accepted it earlier. To skip it, add `user`, as in `--setting-sources user,project`." ([bypassPermissions mode](https://code.claude.com/docs/en/permission-modes#skip-all-checks-with-bypasspermissions-mode)). Auto mode has its own one-time notice, whose skip key `skipAutoPermissionPrompt` is scoped "User or managed" ([reference](https://code.claude.com/docs/en/settings-reference#skipautopermissionprompt)), but no page says that excluding `user` brings it back. The profile does not use bypass permissions | not documented for auto mode |

Other documented effects of excluding `user`, for completeness: personal skills, commands, subagents, CLAUDE.md and rules under `~/.claude/` do not load (SDK page, `user` row), and the claude.ai skill sync does not run ("one you start with a `--setting-sources` list that leaves out `user`", [Where synced skills load](https://code.claude.com/docs/en/skills#where-synced-skills-load)).

### 3.3 Not documented, for T020 to observe

- Whether a `--settings` file still applies when `--setting-sources` omits sources. The docs treat the command line as its own level above the files ([settings precedence](https://code.claude.com/docs/en/settings#settings-precedence)) and list sources as only `user`, `project` and `local`, so the expectation is yes, but no sentence says so. T020's run without `user` should read the effective configuration (the `/sandbox` Config tab and `auto-mode config`) to confirm the profile's keys are still in force.
- Whether a restricted session still authenticates. It depends on where the adopter's provider and credentials are set (first row of 3.2).
- Whether any dialog appears (last row of 3.2). T020 should record what it sees.

## 4. (c) The `cleanupPeriodDays` sweep

### 4.1 What the docs state

- Default 30, minimum 1, and "Setting `0` fails validation". Scope is "Any file", so a user, project, local, `--settings` or managed file can set it. "Claude Code runs the deletion as a background sweep after a session starts, as long as it can safely determine the retention period." ([reference](https://code.claude.com/docs/en/settings-reference#cleanupperioddays)).
- The highest-ranked source that sets a key wins: "Settings precedence, highest first: managed settings, command line, project local, shared project, user." ([settings precedence](https://code.claude.com/docs/en/settings#settings-precedence)).
- What is deleted: the paths in the table under "Path under `~/.claude/`", including `projects/<project>/<session>.jsonl` and `projects/<project>/<session>/subagents/` ([Cleaned up automatically](https://code.claude.com/docs/en/claude-directory#cleaned-up-automatically)).
- Which value the sweep uses: `period_days` is "`cleanupPeriodDays` from merged settings", the merged settings of the session that runs it; managed settings pin it ([retention sweep event](https://code.claude.com/docs/en/monitoring-usage#retention-sweep-event)).
- When: "Claude Code runs the sweep in the background at most once per session", and "If Claude Code ran the sweep in any session on the same machine in the last 24 hours, it delays this session's sweep by at least 10 minutes" (same page). With no sweep in the last 24 hours, the page states no delay.

### 4.2 Not documented

No sentence states whether a session whose merged settings lower the value sweeps other projects' transcripts. Two indirect signals point to yes: the path table is generic over `<project>`, and the telemetry attribute `transcripts_deleted` is defined as "Number of session transcripts, the top-level `~/.claude/projects/*/*.jsonl` files, that the sweep deleted". An indirect signal is not a statement, so the scope is recorded as not documented, and the contract's wording ("cross-project scope is undocumented") stands.

### 4.3 Rule

Archive before starting another session if any settings file lowers `cleanupPeriodDays`. "Any settings file" includes a repository's own `.claude/settings.json` and `.claude/settings.local.json` (scope "Any file"), the `--settings` file and managed settings, not only the user file. The sweep starts after the session starts, so the archive has to finish first. The profile does not set the key, so it neither protects nor lowers retention.

## 5. Contract amendment

`specs/391-isolated-auditable-operation/contracts/session-profile.md`, line 31 only (one line replaced, nothing else touched). The new text is the PM's entry from `test-results/field-list.md` section 10.3, extracted by script rather than retyped.

- Checked: the old and new entries share the first sentence, as the PM ruled; the new line is ASCII only; the entry in the pre-staged file equals the PM's text character for character.
- The `hard_deny` sentence is unchanged and appears verbatim in the PRD (`docs/product/02_PRD/391-isolated-auditable-operation-2026-11-16.md:220`).
- Left as written: the sentence at line 42, "The audiences text is confirmed by Lane R against the pinned client form (AD-15) before the runbook is written." T005's field list and the PM ruling are that confirmation, and the instruction was to change nothing else.

## 6. Pre-staged W2 profile

| Item | Value |
| - | - |
| Path | `~/.tachi/391-w2/session-profile.json` |
| Modes | directory `0700`, file `0600` |
| SHA-256 | `e3fdf5bfc758e4c0f3c58c7d54937bcf0e49174f7f0720f999db47a9decbab1a` |
| Size | 2658 bytes, trailing newline |
| Source | the single `json` fence of the amended contract (lines 6 to 39), extracted by script |
| Secrets | none; `GEMINI_API_KEY` appears as a variable name only, and the key is injected at run time |

Checks made on the file (mine, not T017's; the contract test remains the gate):

- `jq empty` passes.
- Top-level keys are exactly `autoMode`, `env`, `permissions`, `sandbox`; `autoMode` has exactly `environment` and `hard_deny`.
- One host in `allowedDomains`; every `injectHosts` entry is in it; `"$defaults"` is first in both `autoMode` lists; `tlsTerminate` is present beside the `mask` entry.
- Not in the file: the T049 Read denies (section 9).

## 7. Expected `claude --settings <file> auto-mode config` output

What the docs say about the subcommand: "Print the four lists, with your settings applied where set and defaults otherwise" and "Both `defaults` and `config` print the four rule lists as a single JSON object, with each rule as a prose string." ([Inspect the defaults and your effective config](https://code.claude.com/docs/en/auto-mode-config#inspect-the-defaults-and-your-effective-config)).

Expected with `~/.tachi/391-w2/session-profile.json`:

- One JSON object with four arrays of strings: `allow`, `soft_deny`, `hard_deny`, `environment`.
- `environment`: the built-in entries, then the profile's five entries in file order (primary use; host containment; trusted internal domains; sensitive data locations and audiences, the PM text; data retention). "The default entries are spliced in at that position, so your custom entries can go before or after them." ([Define trusted infrastructure](https://code.claude.com/docs/en/auto-mode-config#define-trusted-infrastructure)). The literal `"$defaults"` does not appear.
- `hard_deny`: the built-in entries, then the profile's one sentence.
- `allow` and `soft_deny`: built-in entries only. "Each section is evaluated independently, so setting `environment` alone leaves the default `allow`, `soft_deny`, and `hard_deny` lists intact." ([Override the block and allow rules](https://code.claude.com/docs/en/auto-mode-config#override-the-block-and-allow-rules)).
- Extra entries are possible: "When more than one of those files sets the same array, Claude Code concatenates the entries." ([autoMode reference](https://code.claude.com/docs/en/settings-reference#automode)). Run it from a user configuration with no `autoMode` block, or accept extras; the check below tolerates them.
- The command shows `autoMode` only. The profile's `sandbox`, `permissions` and `env` keys are read from the `/sandbox` Config tab, `/permissions` and the probe table.

Documented limits to carry into the GL record:

- "While `/status` in auto mode shows `Auto mode server` as `Enabled`, the server's built-in rules can differ from this output, and no `claude auto-mode` subcommand prints them." (same page).
- The flag accepts "Path to a settings JSON file or an inline JSON string." ([cli-reference](https://code.claude.com/docs/en/cli-reference#cli-flags)), but the auto-mode page lists the `--settings` flag as "Inline JSON" for `autoMode` ([Where the classifier reads configuration](https://code.claude.com/docs/en/auto-mode-config#where-the-classifier-reads-configuration)), and no page shows `--settings <file>` combined with `auto-mode config`. If the output shows built-in rules only, the file form is not applied; fall back to inline JSON, as the contract's SC-A1 note already says, and record it.
- For the other keys the docs are closer: `mask` entries and `network.tlsTerminate` are honored "only from user settings, managed settings, and the `--settings` flag" ([Mask credentials](https://code.claude.com/docs/en/sandboxing#mask-credentials)), and `strictAllowlist` is honored "in user, managed, or CLI `--settings` settings" ([Network isolation](https://code.claude.com/docs/en/sandboxing#network-isolation)). Neither sentence separates the file form from the inline form, so the GL check of the file form still stands.

Mechanical comparison for GL. It was tested offline on synthetic input (one passing case; three failing cases: built-ins replaced, profile not applied, literal `"$defaults"` echoed). `claude` was not run.

```bash
claude auto-mode defaults > "${TMPDIR:-/tmp}/amd.json"
claude --settings ~/.tachi/391-w2/session-profile.json auto-mode config > "${TMPDIR:-/tmp}/amc.json"
jq -e --slurpfile d "${TMPDIR:-/tmp}/amd.json" --slurpfile p ~/.tachi/391-w2/session-profile.json '
  . as $c
  | (["allow","soft_deny","hard_deny","environment"] | all(. as $k | ($d[0][$k] - $c[$k]) == []))
    and (($p[0].autoMode.environment[1:] - $c.environment) == [])
    and (($p[0].autoMode.hard_deny[1:]   - $c.hard_deny)   == [])
    and ((($c.environment + $c.hard_deny) | index("$defaults")) == null)
' "${TMPDIR:-/tmp}/amc.json" && echo "auto-mode config: defaults kept, profile entries present"
```

Docs-derived expectations for the other GL items, not observed:

- Auto mode with non-essential traffic off. The profile's `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` "Also disables feature-flag fetching" ([env-vars](https://code.claude.com/docs/en/env-vars)), and the page's list of features that need feature-flag fetching does not include auto mode ([Features that need feature-flag fetching](https://code.claude.com/docs/en/env-vars#features-that-need-feature-flag-fetching)). "With Claude Code v2.1.283 or later, auto mode is the built-in starting permission mode for interactive terminal and VS Code sessions on every plan and provider." ([permission-modes, Eliminate permission prompts with auto mode](https://code.claude.com/docs/en/permission-modes)). The runbook minimum, v2.1.285, is above that.
- The same page says a session that does not fetch feature flags asks the server for classifier review by default from v2.1.282, so the server's rules, which no subcommand prints, may apply in that session.

## 8. Gate GL: re-extract and diff

The runbook's marked block is the single source. Once T016 lands, the maintainer extracts the block from `docs/guides/ISOLATED_OPERATION_TACHI.md` and diffs it against the pre-staged file. This was tested offline against a mock runbook built from the amended contract (byte-identical; a one-word change is caught by both comparisons).

~~~bash
awk '/<!-- BEGIN TACHI SESSION PROFILE -->/{f=1;next} /<!-- END TACHI SESSION PROFILE -->/{f=0} f' \
    docs/guides/ISOLATED_OPERATION_TACHI.md | grep -v '^```' > "${TMPDIR:-/tmp}/runbook-profile.json"
diff "${TMPDIR:-/tmp}/runbook-profile.json" ~/.tachi/391-w2/session-profile.json && echo "byte-identical"
diff <(jq -S . "${TMPDIR:-/tmp}/runbook-profile.json") <(jq -S . ~/.tachi/391-w2/session-profile.json) && echo "same content"
~~~

If they differ, the runbook block wins. Replace the pre-staged file with the extracted one (mode `0600`), record its SHA-256 in `w2-live.md`, and run T020 from the extracted file.

## 9. Pending: placement of the T049 Read denies

`test-results/security-a.md` (T049, ruling (a)) adds `Read(//proc/**)` and `Read(~/.claude/.credentials.json)` to `permissions.deny`, with a matching `{ "path": "~/.claude/.credentials.json", "mode": "deny" }` entry in `sandbox.credentials.files`. The security analyst's position is that they belong in the baseline block. The architect decides at T016's profile review. They are not in the contract or in the pre-staged file.

Consequence if the architect adopts them: the runbook block gains them, the GL diff in section 8 will show them, and the pre-staged file must be replaced by the extracted block before T020. `security-a.md` section 6 already expects the shipped profile to carry them in stage B and a scratch copy without them in stage A. T017's pins on the `deny` array and the `files` length would also need checking.

## 10. Observations for T016 (no change made)

1. D-1 wording and the same-family exception: section 2.3, item 1. PM-owned.
2. "Auto-mode re-prompt" and "retention default" in the contract's `--setting-sources` paragraph: reword per 3.2 ("a permission-mode acceptance dialog can appear again, documented for the bypass-permissions warning" and "the retention sweep pauses").
3. The profile's `environment` entries abbreviate the docs' slot names ("Primary use of Claude Code" and "Data retention / declassification" in the docs; "Primary use" and "Data retention" in the profile). The docs say "Entries are prose, not regex or tool patterns", so this is cosmetic. Low.
4. A matrix-link line carries the version marker: the Generic updater replaces only the first semver-looking match on a marked line (`line.replace(VERSION_REGEX, ...)` with a non-global expression), so AD-2's requirement that the marked line carry "exactly one version string" is load-bearing. Details in `w3-sweeps.md`.

## 11. Sources

All fetched 2026-11-19 from `https://code.claude.com/docs/en/`: `sub-agents`, `model-config`, `env-vars`, `cli-reference`, `settings`, `settings-reference`, `claude-directory`, `monitoring-usage`, `permission-modes`, `sandboxing`, `auto-mode-config`, `agent-sdk/claude-code-features`, `debug-your-config`, `memory`, `skills`, `amazon-bedrock`. Repo sources: `contracts/session-profile.md`, `test-results/field-list.md` section 10, `test-results/security-a.md`, `plan.md` AD-1, AD-2 and AD-5, PRD §13.
