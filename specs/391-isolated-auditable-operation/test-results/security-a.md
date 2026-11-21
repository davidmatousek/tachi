# SEC-A: Read-tool exposure of the process-environment key and of Claude Code's credential stores

Task T049 (Part A, W1) | feature 391 | security-analyst | 2026-11-19

**Basis.** The public Claude Code documentation as served on 2026-11-19, plus two Linux manual pages. Analysis only: no live probe was run, and no credential file or process environment was read to write this record. Anything marked "expected" is an expectation for T020 to check, not an observation.

**Ruling: (a).** Add the Read denies in section 5.2 and keep the "injected only toward the Gemini host" claim, scoped as in section 5.6. Where the T020 probes show a route the rules cannot close, (b) applies to that platform (section 5.8).

## 1. Question

With the Gemini key in the Claude Code process environment (the key-provisioning route in `specs/391-isolated-auditable-operation/contracts/session-profile.md`), can the following read it, or read Claude Code's own login credentials, under the shipped profile?

1. The Read tool, which runs outside the shell sandbox, on `/proc/self/environ` or another process's `/proc/<pid>/environ` (Linux).
2. The Read tool on `~/.claude/.credentials.json` and other Claude Code credential stores, and the macOS equivalents.
3. A sandboxed Bash `cat /proc/self/environ`, under the sandbox's filesystem read policy.

If Claude Code does not block these, the disposition is either (a) Read denies in the runbook's credential-store extension note, with Bash-side equivalents if any, or (b) a qualified "injected only toward the Gemini host" claim.

## 2. Short answer

- **Read tool, `/proc/self/environ` and other processes' environ (Linux).** The docs describe no default block and no control that would apply: the Read tool runs outside the sandbox (D1), there is no built-in credential deny list (D5), and in auto mode reads outside the working directory run without a prompt, apart from a one-time first-read question in some interactive sessions (D6). On Linux, `/proc/self` is the process doing the reading (D15); for the in-process Read tool that is Claude Code, the holder of the real key (D2). Expected: readable. Not observed.
- **Read tool, `~/.claude/.credentials.json`.** Same reasoning (D5, D6). The sandbox page lists this file as write-protected only (D5). It holds the login credentials on Linux and in the macOS fallback case (D8). On macOS the normal store is the Keychain, which is not a file, so the Read tool cannot reach it. Other stores: D9 and section 5.2.
- **Sandboxed Bash `cat /proc/self/environ`.** It reads the sandboxed command's own environment, where the masked variable holds a placeholder (D2). That does not expose Claude Code's environment. The route that would is reading Claude Code's own `/proc/<pid>/environ`. The docs imply the default Linux sandbox hides other processes (D13) but never say so for this case; PID isolation is documented only for the subprocess scrub setting, on Linux. On macOS the docs are silent (N3). Probes A3 (Linux) and M2 (macOS) settle both.

## 3. Documented behaviour

Quotes are short and exact. Status is "stated" unless the row says "implied".

| # | What the docs say | Source |
| - | - | - |
| D1 | Built-in file tools run outside the sandbox: "tools such as Read, Edit, Write, WebFetch, and WebSearch follow permission rules instead. A `denyRead` entry doesn't stop the Read tool". Built-in file tools, MCP servers and hooks "still run directly on your host". The page's remedy is to run "the Claude Code process itself" in a container, a virtual machine or the sandbox runtime, which places these tools in that process. | [sandboxing](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox); [sandbox-environments](https://code.claude.com/docs/en/sandbox-environments#compare-sandboxing-approaches) |
| D2 | The Claude Code process holds credentials: "The Claude Code process keeps the credentials for its own API calls." Masking and the `credentials` block reach sandboxed commands only: "`sandbox.credentials` affects sandboxed Bash commands only." For a masked variable "The command and anything it logs never hold the real credential". The proxy substitutes the real value, so Claude Code must hold it (implied for this variable; stated for credentials in general). | [env-vars](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes); [sandboxing](https://code.claude.com/docs/en/sandboxing#protect-credentials); [sandboxing](https://code.claude.com/docs/en/sandboxing#mask-environment-variables) |
| D3 | Sandboxed commands inherit the Claude Code environment by default: "Inherited from Claude Code, including any secrets in its environment". Only variables listed under `credentials` are masked or removed. | [sandboxing](https://code.claude.com/docs/en/sandboxing#what-the-sandbox-restricts) |
| D4 | Hooks, local MCP servers, plugin monitors, LSP servers, the status-line command and `apiKeyHelper` "run with your full access", outside the sandbox. The subprocess scrub is described as removing credentials from "Bash commands, hooks, and stdio MCP servers", which implies they otherwise receive them (no single sentence says so). | [sandboxing](https://code.claude.com/docs/en/sandboxing#what-runs-outside-the-sandbox); [env-vars](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes) |
| D5 | No documented read block for either target. Sandboxed default read access is "the entire computer, except certain denied directories. This default still allows reading credential files". "There is no built-in credential deny list, so only the files and variables you list are restricted." For `.credentials.json` the sandbox page lists write protection only (its protected-paths list is about writes). | [sandboxing](https://code.claude.com/docs/en/sandboxing#filesystem-isolation); [sandboxing](https://code.claude.com/docs/en/sandboxing#protect-credentials); [sandboxing](https://code.claude.com/docs/en/sandboxing#protected-paths) |
| D6 | Auto mode: "file reads other than reads from network paths run without a prompt in auto mode, including reads outside the working directories". Where the prompt shows, the first read outside them asks once, with allow and block-from-now-on answers; it is absent from some surfaces: "The prompt doesn't appear in `-p` runs, Agent SDK sessions, background sessions, the VS Code chat panel, or the desktop app. There, the read runs." It is a question, not a default block. The classifier's default block list includes "Printing a live credential or token into the transcript or a file"; that is a model judgement, not a rule, and is not relied on here. | [permission-modes](https://code.claude.com/docs/en/permission-modes#the-first-read-outside-the-working-directories); [permission-modes](https://code.claude.com/docs/en/permission-modes#what-the-classifier-blocks-by-default) |
| D7 | What a tool reads is persisted: "Transcripts and history are not encrypted at rest ... If a tool reads a `.env` file or a command prints a credential, that value is written to `projects/<project>/<session>.jsonl`." The mitigation list includes "Use permission rules to deny reads of credential files". | [claude-directory](https://code.claude.com/docs/en/claude-directory#plaintext-storage) |
| D8 | Login credential storage. macOS: "the encrypted macOS Keychain", falling back to `~/.claude/.credentials.json` (mode `0600`) "When the Keychain rejects the write". Linux: `~/.claude/.credentials.json`, mode `0600`. Windows: `%USERPROFILE%\.claude\.credentials.json`. With `CLAUDE_CONFIG_DIR` set the file lives under that directory and the Keychain entry is keyed to it. Credentials can also arrive through the environment: `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `CLAUDE_CODE_OAUTH_TOKEN`. The legacy `/iam` URL serves this same page. | [authentication](https://code.claude.com/docs/en/authentication#credential-management); [authentication](https://code.claude.com/docs/en/authentication#authentication-precedence) |
| D9 | Other stores. `~/.claude.json` "Holds account details, per-project trust decisions, your personal MCP servers, and UI toggles"; local and user-scope MCP servers are stored there, local scope being for servers "with credentials you don't want in version control". MCP OAuth client secrets sit in "your system keychain (macOS) or a credentials file"; the file is not named. | [claude-directory](https://code.claude.com/docs/en/claude-directory); [mcp](https://code.claude.com/docs/en/mcp#local-scope); [mcp](https://code.claude.com/docs/en/mcp#use-pre-configured-oauth-credentials) |
| D10 | Rule anchoring. `//path` is an "Absolute path from filesystem root" (the docs' own example is a `Read(//...)` rule on a `secrets/**` directory); `~/path` is home-relative; `/path` "anchors at the settings source, not the filesystem root", and for a file passed with `--settings` resolves to `<directory of file>/path`. Sandbox path lists use the other convention: "`/tmp/build` is an absolute path", and `//path` also works. | [permissions](https://code.claude.com/docs/en/permissions#how-path-patterns-match); [permissions](https://code.claude.com/docs/en/permissions#where-a-pattern-anchors); [settings-reference](https://code.claude.com/docs/en/settings-reference#sandbox-path-prefixes) |
| D11 | Symlinks: deny rules "apply when either the requested path or the file it resolves to matches". `/proc/self/...` is covered through either spelling. | [permissions](https://code.claude.com/docs/en/permissions#symlinks) |
| D12 | Reach of a Read deny rule. The Read tool; "best-effort" for Grep and Glob; in Bash, also recognised file commands (`cat`, `head`, `tail`, `sed`, `tee`) and redirections, but not "arbitrary subprocesses". The sandbox read-deny list "adds the paths from your `Read(...)` deny permission rules", so sandboxed commands are blocked at the OS level too. On Linux and WSL2, "A trailing `/**` works" in a read-deny path. | [permissions](https://code.claude.com/docs/en/permissions#what-read-and-edit-rules-cover); [settings-reference](https://code.claude.com/docs/en/settings-reference#sandbox-filesystem-denyread); [sandboxing](https://code.claude.com/docs/en/sandboxing#permission-rules); [settings-reference](https://code.claude.com/docs/en/settings-reference#sandbox-path-prefixes) |
| D13 | `/proc` in the Linux sandbox. The sandbox mounts a fresh `/proc`; the weaker nested mode instead "bind-mounts the container's existing `/proc`, which exposes process information that a fresh mount would hide" (implies the default hides it). With the subprocess scrub on: "On Linux, the scrub also runs Bash subprocesses in an isolated PID namespace so they can't read host process environments through `/proc`." | [settings-reference](https://code.claude.com/docs/en/settings-reference#sandbox-enableweakernestedsandbox); [env-vars](https://code.claude.com/docs/en/env-vars#what-the-subprocess-environment-scrub-removes) |
| D14 | `ps` with the `e` option "prints process environment variables"; Claude Code prompts for it in Manual mode. A prompt is not a block, and the profile runs in auto mode. | [permissions](https://code.claude.com/docs/en/permissions#read-only-commands) |
| D15 | Linux semantics (OS manual). `/proc/pid/environ` "contains the initial environment that was set when the currently executing program was started via execve(2)", does not reflect later `putenv` changes, and is governed by "a ptrace access mode PTRACE_MODE_READ_FSCREDS check". `/proc/self/` "refers to the process accessing the /proc filesystem". Files under `/proc/pid` become root-owned when the process is non-dumpable. | [proc_pid_environ(5)](https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html); [proc_pid(5)](https://man7.org/linux/man-pages/man5/proc_self.5.html) |
| D16 | Stronger options the docs offer. `permissions.blockReadsOutsideWorkingDirectories` makes the file tools refuse reads outside the working directories "in every permission mode", and also denies sandboxed commands the home directory. Running the whole Claude Code process in the sandbox runtime, a container or a VM restricts file tools, MCP servers and hooks too. | [settings-reference](https://code.claude.com/docs/en/settings-reference#permissions-blockreadsoutsideworkingdirectories); [sandbox-environments](https://code.claude.com/docs/en/sandbox-environments#compare-sandboxing-approaches) |

## 4. Not documented (unconfirmed)

A search of every fetched page for `/proc` found only the statements in D13; the only other `environ` hit is an unrelated Python snippet on the MCP page. Each item below is unconfirmed and stays so until T020 runs.

- **N1.** Any default refusal by the Read tool of `/proc/**` or of the credentials file.
- **N2.** Whether a sandboxed command on Linux can read the Claude Code process's `/proc/<pid>/environ` without the scrub setting (D13 implies not).
- **N3.** Whether a sandboxed command on macOS can read another process's environment (`ps eww`, sysctl). The scrub's PID isolation is stated for Linux only.
- **N4.** Whether sandboxed commands on macOS can reach the Keychain service at all.
- **N5.** How the scrub setting combines with a `mask` entry (placeholder kept, or variable removed). Testable only with a key.
- **N6.** Whether Claude Code marks its own process non-dumpable, which would make `/proc/self/environ` root-owned and unreadable (D15).
- **N7.** Whether the Read tool returns content for procfs files, which report size 0 (an empty file yields a notice per the [tools reference](https://code.claude.com/docs/en/tools-reference#read-tool-behavior)). An empty-file result would be incidental and version-specific; it would not change the ruling.
- **N8.** Whether the broad `/proc/**` deny, once added to the sandbox read-deny list, leaves sandboxed Linux tools working (Chromium through the diagram renderer, Node, process substitution).
- **N9.** The Read tool's own refusal text for a deny-rule match. The [errors page](https://code.claude.com/docs/en/errors#file-is-covered-by-a-read-deny-rule) documents only the Edit and Write variant.
- **N10.** Grep and Glob enforcement beyond "best-effort". The [errors page](https://code.claude.com/docs/en/errors#refusing-to-read-write-or-search-a-path) documents a refusal when ripgrep cannot apply deny rules outside the working directory, which suggests fail-closed in that case only.

## 5. Ruling

### 5.1 Disposition: (a)

Add the Read denies below and keep the claim in its scoped form (5.6). Reasons:

1. The docs describe no default block, and by OS semantics the in-process Read tool sees the environment of the process that holds the real key (D2, D15).
2. The deny rules are cheap, documented and deterministic for the Read tool, and the docs' own plaintext-storage guidance prescribes them (D7).
3. (b) alone would leave that control unused while the key can land in a plaintext transcript kept 30 days or more.
4. (a) alone cannot make the claim unconditional (5.7), so the claim is scoped rather than dropped.

### 5.2 Exact rule strings

| String | Goes in | Covers | Platform |
| - | - | - | - |
| `Read(//proc/**)` | `permissions.deny` | The Read tool on `/proc/self/environ`, `/proc/thread-self/environ` and any process's `/proc/<pid>/environ`, `cmdline` and `fd`; sandboxed Bash through the documented merge (D12) | Linux; inert on macOS, where `/proc` does not exist |
| `Read(~/.claude/.credentials.json)` | `permissions.deny` | The Read tool and, by the merge, sandboxed Bash, on Claude Code's login file (Linux, Windows, and the macOS Keychain-fallback file) | All |
| `{ "path": "~/.claude/.credentials.json", "mode": "deny" }` | `sandbox.credentials.files` | Sandboxed Bash, in the same idiom as `~/.ssh` and `~/.aws`. Duplicates the merge (D12); kept as an explicit Bash-side line | All |
| `Read(~/.claude.json)` | Extension note, not baseline | Account details and personal MCP server definitions that can carry credentials (D9) | All |

In context, the baseline edit is two array entries and one object, with no new key path:

```json
"permissions": {
  "deny": ["WebFetch", "WebSearch", "Read(~/.ssh/**)", "Read(~/.aws/**)", "Read(.env*)",
           "Read(//proc/**)", "Read(~/.claude/.credentials.json)"]
},
"sandbox": {
  "credentials": {
    "files": [{ "path": "~/.ssh", "mode": "deny" }, { "path": "~/.aws", "mode": "deny" },
              { "path": "~/.claude/.credentials.json", "mode": "deny" }]
  }
}
```

If `CLAUDE_CONFIG_DIR` is set, the credentials file lives under that directory (D8). Write both credentials-file entries for `<that directory>/.credentials.json` using the `~/` or `//` form; the documented path forms include no variable expansion.

**Fallback, only if probe C fails with the broad rule** (N8): replace `Read(//proc/**)` with `Read(//proc/*/environ)` and `Read(//proc/*/task/*/environ)`. In gitignore syntax `*` matches within one path segment, so the first covers `self`, `thread-self` and numeric pids, and the second covers per-thread files. These cover the secret but not `cmdline` or `fd`; rerun B1 to B3 after the swap.

### 5.3 Anchoring check

`//` is correct for a Read deny rule that names an absolute path (D10). Two traps:

- `Read(/proc/**)` is wrong. The single slash anchors at the settings source, which for a file passed with `--settings` is that file's directory, so the rule would match nothing under `/proc`. This agrees with the contract's note to avoid the single-slash form.
- Sandbox path lists use the opposite convention: there `/proc` is absolute and `//proc` also works. Copying a path between `permissions.deny` and a `sandbox.*` list changes its meaning silently.

`~/` means the home directory in both places.

### 5.4 Bash-side equivalents

None is needed beyond the same Read rules. The docs add the paths of `Read(...)` deny rules to the sandbox read-deny list (D12), so sandboxed commands are blocked at the OS level, and recognised file commands such as `cat` are refused at the permission layer. The explicit Bash-side line for the credentials file is the `credentials.files` entry in 5.2. Do not add a `/proc` line under `sandbox.*`: the merge already carries it, and `sandbox.filesystem.denyRead` would add a key path to the closed key set.

### 5.5 Placement

Security-analyst position: put the two `permissions.deny` strings and the `credentials.files` entry in the **baseline block**, not only in the extension note.

- The baseline is what T017 pins and what T020 runs; prose in a note is neither tested nor present in a copy-pasted profile.
- The exposure comes from the profile's own key-provisioning route, not from an adopter's extra files.
- No key path is added, so the closed key set holds. T017 should be checked for whether it pins the `deny` array or the `files` length.
- Files that carry the list: the block in `specs/391-isolated-auditable-operation/contracts/session-profile.md`, the deny list at line 53 of `specs/391-isolated-auditable-operation/data-model.md`, and T016's first commit.

The architect owns the contract text. If the baseline stays closed, the minimum is the extension note with the strings marked **required** for any session that provisions a key or authenticates through environment variables, and T020 must run with them added so the configuration it exercises includes them.

### 5.6 Claim wording

The sentence is accurate as a statement about the proxy (D2). Left bare, it reads as "the key cannot be reached", which the docs do not support. Replacement text for the runbook:

> The image key is masked for sandboxed commands: they see a placeholder, and the sandbox proxy substitutes the real value only on connections to `generativelanguage.googleapis.com`. The real value is still held by the Claude Code process, which runs outside the sandbox, and it can reach hooks, the status line and local MCP servers, which Claude Code starts outside the sandbox, unless you scrub the environment. The Read denies in the profile keep Claude's file tools away from that environment on Linux and from Claude Code's own login file; whatever a tool does read is written to the plaintext transcript.

The "can reach ... unless you scrub" clause rests on D4 (implied, not a single stated sentence); T016 may reword it but should keep "can".

### 5.7 What the ruling does not close

1. **Grep and Glob** are covered "best-effort" (D12). Probe B4.
2. **Hooks, status line, stdio MCP servers, `apiKeyHelper`** run outside the sandbox and can receive the environment unless `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` is set (D4). The profile's existing MCP and hooks residual stays.
3. **Every other variable in the launch environment is inherited by sandboxed commands** (D3); the mask covers one variable. Adjacent finding for the key-provisioning text: launch from a minimal environment (6.1 shows the form) or list further `credentials.envVars` deny entries. `/proc/self/environ` for the Read tool also exposes `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` if the adopter authenticates that way (D8), which the `Read(//proc/**)` rule covers.
4. **macOS** sandboxed `ps` reading the Claude Code process environment is undocumented (N3).
5. **The Read tool is an in-process surface.** The structural fix is a boundary around the whole process (D16), which is outside the profile.

### 5.8 Triggers that turn (a) into (b) for a platform

| T020 result | Consequence |
| - | - |
| B1 to B3: the Read tool still returns environ content with the rules present | Key-ful operation on that platform is not claimed; the key-less default stands; file a follow-up on Claude Code's behaviour |
| A3 (Linux) or M2 (macOS): a sandboxed command can read the Claude Code process environment | Qualify the claim for that platform. Key-ful operation there needs a boundary around the whole process (D16) or is not claimed. On Linux, evaluate the scrub (probe E) |
| B4: Grep returns the dummy line | Keep the disclosure "Grep and Glob coverage is best-effort"; key-ful operation on Linux is not claimed unless the architect accepts the residual |
| C fails only with the broad rule | Swap to the two narrow strings (5.2 fallback) and rerun B1 to B3 |
| T020 runs on macOS only | The Linux strings ship unchecked and the runbook says so ("Last validated" names macOS) |

### 5.9 Alternatives considered

- **(b) alone.** Rejected: leaves a deterministic control unused.
- **Subprocess scrub** (`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`). Strips credentials from subprocess environments and, on Linux, isolates Bash from host `/proc` (D13). It does not touch the Read tool (D2), and its interaction with the `mask` placeholder is undocumented (N5). Not part of this ruling; probe E checks the documented behaviour key-less.
- **`permissions.blockReadsOutsideWorkingDirectories`.** Default-deny for the file tools outside the working directory, which would cover `/proc` and every home-directory credential store at once. It also cuts sandboxed commands off from the home directory (D16), which can break toolchains installed there and external target checkouts, and it adds a key path to a closed set. Not recommended as baseline; the architect may want it as opt-in hardening.
- **A `sandbox.filesystem.denyRead` line for `/proc`.** Redundant by the merge (D12); adds a key path.

## 6. T020 probe steps

Run in the W2 session set, key-less. The existing probe table (`touch ~/sandbox-probe`, `curl --noproxy '*' https://example.com`, planted `.env`, WebFetch denied) runs first and must pass, so that Bash probes below are meaningful. Record each result as PASS, FAIL or INCONCLUSIVE with one sentence in `specs/391-isolated-auditable-operation/test-results/w2-live.md`: no excerpts, ids, home paths or key material.

### 6.0 Safety rules

- No `GEMINI_API_KEY`, and no other secret, in the launch environment. Use the cleaned launch in 6.1.
- Only dummy values may appear in probe output. Never print the credentials file, and never print the environment of a process that was not started with a dummy environment. The probes use `test`, `wc -c` and `grep -c`, which print a flag or a count.
- If any probe returns content that is not a dummy value, stop. Treat that session's transcript as holding a credential: end the session, delete that session's transcript file, and run `/logout` then `/login` if it was the credentials file.
- Do not repeat these probes in the key-ful session. The deny rules do not depend on the variable's value, so the key-less result carries over; the one key-only unknown is the scrub and mask interaction (N5), which is a separate decision.
- Restart the session between stage A and stage B, because the profile differs.

### 6.1 Setup

Terminal 1, a dummy second process (Linux and macOS):

```
env -i TACHI_SEC_A_OTHER=not-a-secret sleep 3600 &
OTHER_PID=$!
```

Terminal 2, the session, launched from a cleaned environment (`<profile file>` is the pre-staged profile; for stage A, a scratch copy with the three SEC-A strings removed; if `claude` is an alias or shell function, use the full path to the binary):

```
env -i HOME="$HOME" USER="$USER" SHELL="$SHELL" PATH="$PATH" TERM="$TERM" \
  LANG="${LANG:-en_US.UTF-8}" TMPDIR="${TMPDIR:-/tmp}" TACHI_SEC_A_PROBE=not-a-secret \
  "$(command -v claude)" --settings <profile file>
```

Terminal 1, a names-only check of what the session received (prints variable names, never values):

```
CLAUDE_PID=$(pgrep -n -f -- "--settings <profile file>")
ps -o pid,ppid,command -p "$CLAUDE_PID"                      # confirm it is the launched process
# Linux
tr '\0' '\n' < /proc/$CLAUDE_PID/environ | cut -d= -f1 | sort
# macOS
ps eww -p "$CLAUDE_PID" | tr ' ' '\n' | grep '=' | cut -d= -f1 | sort
```

Expected names: `HOME`, `USER`, `SHELL`, `PATH`, `TERM`, `LANG`, `TMPDIR`, `TACHI_SEC_A_PROBE`. Any other name, especially a credential-shaped one: stop and fix the launch. If the macOS command cannot read the process, skip the check and say so.

In the session, record the output of `claude --version`, then run `/permissions` and confirm the SEC-A deny rules are listed with no invalid-rule warning at startup. Open the `/sandbox` Config tab and record whether `/proc` appears among the read denies (this shows whether the documented merge applied).

### 6.2 Probes and expected results

All results below are expectations. "Refused" means the call is refused with a permission message and no file content in the result.

| ID | Stage | Platform | Tool | Expected |
| - | - | - | - | - |
| A1 | A, baseline, optional evidence | Linux | Read | Returns content including the line `TACHI_SEC_A_PROBE=not-a-secret` (exposure exists). Also acceptable, and recorded as such: a permission error (N6) or an empty-file notice (N7). The ruling stands either way |
| A2 | A | Linux | Read | Content includes `TACHI_SEC_A_OTHER=not-a-secret` |
| A3 | A and B | Linux | Bash | `not-readable` (D13 implies). `readable` with count 1 triggers 5.8 row 2 |
| A4 | A | All | Bash | Informational: `present` or `absent`; decides whether B6 can use the real file |
| B1 | B, shipped profile | Linux | Read | Refused |
| B2 | B | Linux | Read | Refused |
| B3 | B | Linux | Read | Refused |
| B4 | B | Linux | Grep | Refused or no match. The dummy line appearing is a documented best-effort gap (D12): FAIL, 5.8 row 3 |
| B5 | B | Linux | Bash | Refused at the permission layer or blocked by the sandbox. A printed `1` is the sandboxed command's own inherited dummy, no exposure: record "Bash-side deny did not apply to `/proc`" |
| B6 | B | All | Read, then Bash | Only if A4 says `present`, and only after B1 to B3 pass (or B7 passes on macOS). Read refused; Bash `wc -c` fails or is blocked instead of printing a byte count |
| B7 | B | All | Read, then Bash | Planted control refused by both paths. Confirms the dotfile `~/` form when the real file is absent |
| C1 | C, regression | Linux | Bash | `ok` |
| C2 | C | Linux | Bash | `ok` (process substitution works) |
| C3 | C | Linux | Bash | `2` from each of Node and Python |
| C4 | C | Linux | Bash | The T020 offline diagram-renderer check, run with the strings in place: byte-identical images |
| M1 | M | macOS | Read | "Does not exist" or a refusal; either is fine, the string is inert |
| M2 | M | macOS | Bash | Count `0` or an error. Count `1` for the other process, or for the Claude Code process, triggers 5.8 row 2 for macOS. If a classifier or prompt stops the command, record "stopped before the sandbox" separately |
| M3 | M, optional | macOS | Bash | An "item could not be found" line (service reachable) or a sandbox error (not reachable). Informational for N4 |
| E1 | E, optional, key-less | Linux | Bash | See below |

### 6.3 Exact instructions

`<OTHER_PID>` and `<CLAUDE_PID>` are the numbers from terminal 1, typed into the prompts and commands. Stage A (baseline profile; Linux): prompts are given to Claude as written.

```
A1  "Use the Read tool on /proc/self/environ. Report only whether the line TACHI_SEC_A_PROBE=not-a-secret appears."
A2  "Use the Read tool on /proc/<OTHER_PID>/environ. Report only whether TACHI_SEC_A_OTHER=not-a-secret appears."
A3  test -r /proc/<CLAUDE_PID>/environ && echo readable || echo not-readable
    # only if it printed "readable":
    tr '\0' '\n' < /proc/<CLAUDE_PID>/environ | grep -c '^TACHI_SEC_A_PROBE='
A4  test -e ~/.claude/.credentials.json && echo present || echo absent
```

Stage B (shipped profile with the SEC-A strings; restart the session first). Run A3 again here and record both results.

```
B1  "Use the Read tool on /proc/self/environ."
B2  "Use the Read tool on /proc/<OTHER_PID>/environ."
B3  "Use the Read tool on /proc/thread-self/environ."
B4  "Use the Grep tool with pattern TACHI_SEC_A_PROBE and path /proc/self. Report only whether any line matched."
B5  cat /proc/self/environ | tr '\0' '\n' | grep -c '^TACHI_SEC_A_PROBE='
B6  "Use the Read tool on ~/.claude/.credentials.json."          # only per the table's precondition
    wc -c < ~/.claude/.credentials.json
B7  # on a scratch copy of the profile, add the deny entry Read(~/tachi-sec-a-probe/.credentials.json)
    mkdir -p ~/tachi-sec-a-probe && printf 'not-a-secret\n' > ~/tachi-sec-a-probe/.credentials.json
    "Use the Read tool on ~/tachi-sec-a-probe/.credentials.json."
    cat ~/tachi-sec-a-probe/.credentials.json
    # afterwards, from a plain shell outside the session: rm -r ~/tachi-sec-a-probe
```

If B6's Read returns file content, follow the stop rule in 6.0 at once.

Stage C (Linux, shipped profile):

```
C1  echo ok
C2  bash -c 'cat <(echo ok)'
C3  node -e 'console.log(1+1)'    and    python3 -c 'print(1+1)'
C4  the offline diagram-renderer render from T020, with the SEC-A strings in place
```

Stage M (macOS, shipped profile):

```
M1  "Use the Read tool on /proc/self/environ."
M2  ps eww -p <OTHER_PID> | grep -c TACHI_SEC_A_OTHER
    ps eww -p <CLAUDE_PID> | grep -c TACHI_SEC_A_PROBE
M3  security find-generic-password -s tachi-sec-a-nonexistent-service 2>&1 | head -n 1
    # never run this with a real service name, and never with -w or -g
```

Stage E (optional, only if the architect adopts the scrub; key-less). Launch as in 6.1 with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` and an extra `TACHI_SEC_A_FAKE_TOKEN=not-a-secret` in the `env -i` list, then:

```
E1  printenv TACHI_SEC_A_PROBE            # expected: not-a-secret (not credential-shaped, kept)
    printenv TACHI_SEC_A_FAKE_TOKEN       # expected: empty (credential-shaped name, removed)
    test -r /proc/<CLAUDE_PID>/environ && echo readable || echo not-readable    # Linux; expected: not-readable
```

## 7. Hand-offs

| Owner | Action |
| - | - |
| T016 second commit, or T021 | Apply 5.2 and 5.6. The extension note adds `Read(~/.claude.json)` and the `CLAUDE_CONFIG_DIR` caveat. Key provisioning gains the inherited-environment sentence (5.7 item 3). The probe table gains the B1 and B6 rows. |
| Architect | Decide 5.5 placement. If baseline: edit the block in `contracts/session-profile.md` and the deny list at `data-model.md:53`. |
| T017 | Closed key set is unchanged; check whether the test pins the `permissions.deny` array or the `credentials.files` length. |
| T020 | Run section 6; stamp the Claude Code version, operating system, permission mode and date; record in `w2-live.md`. |
| T021 | Fold the probe outcomes, apply any 5.8 row that fired, and scope the platform claim if Linux was not run. |
| T042 | Check the shipped profile and note against this ruling; append to `test-results/security-b1.md`. |
| Plan records | The risk item at `plan.md:259` is resolved by this ruling, pending the T020 probes. |

## Sources

Claude Code documentation, read as raw markdown on 2026-11-19 (11 pages):

- https://code.claude.com/docs/en/sandboxing
- https://code.claude.com/docs/en/permissions
- https://code.claude.com/docs/en/settings-reference
- https://code.claude.com/docs/en/env-vars
- https://code.claude.com/docs/en/authentication (the legacy `https://docs.anthropic.com/en/docs/claude-code/iam` URL redirects to the same content)
- https://code.claude.com/docs/en/permission-modes
- https://code.claude.com/docs/en/claude-directory
- https://code.claude.com/docs/en/mcp
- https://code.claude.com/docs/en/sandbox-environments
- https://code.claude.com/docs/en/tools-reference
- https://code.claude.com/docs/en/errors

Linux manual pages (2):

- https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html
- https://man7.org/linux/man-pages/man5/proc_self.5.html (renders proc_pid(5))
