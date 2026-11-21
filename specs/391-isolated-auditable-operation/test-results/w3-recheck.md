# W3 re-check of the published session profile (architect W3-3 and W3-3a)

| Item | Value |
|---|---|
| Why | The W2 live run (`w2-live.md`) used the profile at SHA-256 `43496fb7…` (2,908 bytes). W3 added deny rules (AR-21, AR-21a), and a changed profile ends the "Last validated" claim (runbook §0, refresh trigger 2). The architect required a bounded re-check before T046 (`architect-w3-findings` W3-3, R1 to R6; W3-3a, R4a) |
| Date | 2026-11-20 |
| OS | macOS 26.6.2 (arm64). Linux and WSL2 not run |
| Claude Code | 2.1.330 |
| Permission mode | auto |
| Configuration | key-less only, as the ruling specifies |
| Project | the W2 scratch adopter project; tachi build `v4.48.2-103-gfe5125a`, unchanged since W2 |
| Profile checked | the published block at Part A `b2f5e54`: 3,156 bytes, SHA-256 `36df2a9a98e301d783a06ff605d1be7f9548e10f805084b3fe225ff89eef9644`, 18 deny rules. It differs from the W2 profile only by ten deny rules after `mcp__*` |
| Launch | the runbook's validated `env -i` form, key-less, with `SHELL=/bin/bash` and the profile passed as a file to `--settings` |
| User settings | as restored after W2; the runbook §3 user-scope additions were not applied for this re-check |
| How it ran | Claude drove each session as a real interactive Claude Code TUI in tmux, at the maintainer's standing instruction, as in W2 (the AD-12 deviation that T045 records). Neither session was archived |
| Verdict | **PASS**, R1 to R6 with R4a, on the 18-rule profile |

Structure only: no transcript excerpts, session ids, home paths or account details.

## 1. First attempt: the 16-rule block, stopped at R4

The first re-check ran on the 16-rule block (`ac79ace`: 3,110 bytes, SHA-256 `0880db3b…`). R1 to R3 passed. R4's tool inventory showed no `mcp__` tool and none of the eight AR-21 names, but the Agent tool's `isolation` parameter accepted `"worktree"` and `"remote"`. R4's stop condition applied, and the session closed without R5 or R6. The architect ruled W3-3a: deny `Agent(isolation:*)` and `Workflow`. The block went to 18 rules (`b2f5e54`), and the re-check restarted at R1.

## 2. Results on the 18-rule block

| Step | Result |
|---|---|
| R1 | PASS. The block extracted from `b2f5e54` is 3,156 bytes, SHA-256 `36df2a9a…`, with 18 deny rules. The same extraction gives W2's 2,908 bytes and `43496fb7…` from `858ac85` |
| R2 | PASS. `claude --settings <file> auto-mode config` equals the built-in lists followed by the profile's entries, in order: `environment` 21→26, `hard_deny` 1→2, `allow` (16) and `soft_deny` (72) unchanged. Identical to the W2 profile's output |
| R3 | PASS. `claude --settings <file> doctor`: no installation issues, and no rejected or skipped rule listed. Auto-updates disabled by the non-essential-traffic variable; Remote Control off, because feature-flag evaluation is disabled. In the session: no startup warning names a rule; auto mode on; `/status` lists the setting sources as User settings and Command line arguments, with `Auto mode server: Enabled`; `/permissions` Allow is empty, and Deny holds exactly the 18 profile rules, `Agent(isolation:*)` and `Workflow` among them |
| R4 | PASS. Tool inventory, listed by the session without calling a tool. Loaded: AskUserQuestion, Agent, Bash, Edit, Read, ReportFindings, ScheduleWakeup, Skill, ToolSearch, Write. Deferred: CronCreate, CronDelete, CronList, EnterPlanMode, EnterWorktree, ExitPlanMode, ExitWorktree, NotebookEdit, TaskStop. No `mcp__` tool, none of the nine bare names (the eight AR-21 names and `Workflow`), and Agent present. The Agent tool still lists the `isolation` values `"worktree"` and `"remote"`: a parameter rule removes no schema value, as the ruling expected |
| R4a | PASS. Asked to start one `general-purpose` subagent with `isolation: "worktree"` and a one-word prompt, the session's Agent call was refused before it ran, with "Permission to use Agent with isolation:* has been denied". No subagent ran, and `git worktree list` in the project showed only the main worktree. Layer: the permission rule from the command-line settings. `"remote"` was never requested |
| R5 | PASS. `touch ~/sandbox-probe`: "Operation not permitted", and no file on the host. `curl --noproxy '*' https://example.com`: "Could not resolve host". `curl -sS https://example.com`: "CONNECT tunnel failed, response 403", and the sandbox named the host as not on the allow list. A planted dummy `.env`: the Read tool was refused by the permission settings, and `cat .env` was refused before it ran ("rule from command line arguments"). The dummy file was removed afterwards |
| R6 | PASS. `/tachi.threat-model --output-dir docs/security/w3-recheck` (a fresh parent, so a first run with no baseline) completed in 6m24s: 1 Critical, 11 High, 5 Medium, 0 Low, and 17 SARIF results. The dispatch tree was `tachi-orchestrator` (depth 1) → `tachi-threat-report` (depth 2) → `tachi-attack-tree-delta` (depth 3), all finished. None set an isolation value, so the new parameter rule left tachi's dispatches untouched. The orchestrator analysed inline rather than dispatching the STRIDE agents, as in W2's K1 run (not new). Write listing (hash of every path except `.git/`, before and after): 21 new, 0 changed, 0 deleted, 0 flagged, all under the run's output directory |

## 3. What the record supports

- The published 18-rule profile is validated for what the re-check covered: startup and the rule list, the tool inventory, a refused isolated Agent call, the sandbox and `.env` probes, and one key-less `/tachi.threat-model` run with the deepest dispatch tree.
- The rest of the live validation, including the keyed pipeline, the mask and the Gemini CA trust, ran in W2 on the earlier profile. The ten added rules only deny. They name tools that tachi does not use, and Agent calls that set an isolation value, which tachi's dispatches never do.
- Nothing here changes F1. On macOS, `/tachi.security-report` still cannot render diagrams under the profile (runbook §6).
