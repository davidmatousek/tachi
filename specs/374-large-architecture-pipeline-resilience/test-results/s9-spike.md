# The S-9 spike: what a dispatcher sees when a Phase 2 return fails (T104, W2′)

**Date:** 2026-11-24. **Install commit:** `6a16de2` (`git describe`: `v4.48.5-200-g6a16de2`). **Lane:** L (tester). **Inputs:** T104; spec S-8, S-9, the dispatch erratum and FR-N4.7; ADR-050 D6 (rev. 3) and its S-9 paragraph; KB 22 and KB 25; [w5-setup-pr1.md](w5-setup-pr1.md) sections 4 and 8 (D-L2); the runbook's section 3; the provisional end marker in `dispatch-record-brief-shared.md`. **Runs:** 16 live sessions under the published session profile, 7 at layer A (the main session dispatches) and 9 at layer B (a dispatching subagent dispatches). No usage-limit interruption, so no attempt was lost. This record is structure only (H8): the agents are synthetic, and no real content appears.

## Result

**DONE. All four classes were planted at both layers, and S-9's question has an answer: a dispatching subagent can wait, within three bounds (section 6). No scope change to the command layer is needed for waiting.** What the table in section 4 shows changes what T090 builds the predicate on:

- **A subagent waits by ending its turn.** The harness resumes it on each child's hand-back message and notification, and it holds the notification to the subagent's own caller until the subagent has stopped with no live child. Four of four plain waits (two quick children and a 75-second one) worked, and so did a wait through two failing children. Three things bound it: the harness never stops a dispatcher from handing back early (1 of 9 layer-B runs did); it forces a hand-back once every child has stopped, even a child that has not reported; and a child whose tool call never returns holds its dispatcher, with no timeout.
- **A truncated return never reaches the dispatcher as text.** On Claude Code 2.1.331 a report travels in the input of one `SubagentHandback` call. A call cut by the output cap is dropped whole, the harness retries three times, and after the fourth stop the agent ends `failed` with the text `error type max_output_tokens` and no report. A stop in reasoning looks the same. 12 of 13 mid-output trials and 2 of 2 mid-reasoning trials ended this way. So on this version a truncation shows as a `failed` notification, and a missing end marker is not how it shows.
- **A delivered report carries its marker inside a frame.** Every report line is indented by two spaces, a closing tag and a fixed paragraph follow the last line, and the last non-blank line of the whole turn is that paragraph. In the dispatcher's context, the provisional rule ("the last non-blank line ... exactly `TACHI-END`") matches none of the 19 delivered marker lines as written.
- **The harness hides parts of the planted failures.** A cap stop is retried three times before the dispatcher hears of it. An empty report is rejected by the tool, and a plain-text ending is nudged up to three times. What reaches the dispatcher is a placeholder report, a normal report after a recovered stop, or a notification that says no report was delivered.
- **A stall has two forms.** A shell command is auto-backgrounded after 180 seconds and the agent goes idle: the dispatcher gets a `completed` notification that says the agent "is waiting on its own background work". A blocked tool call (a read that never returns) produces nothing at all: no notification, no timeout, no change in what the dispatcher sees, for the whole window (section 5.3).

## 1. Method

1. **Install.** A fresh shared clone of the repository, detached at `6a16de2`. The scratch adopter template is a fresh `git init -b main` with a one-line README, one commit and the repo-local identity `tachi scratch adopter <adopter@example.invalid>`. From its root, in the clean environment below, `scripts/install.sh --source <install clone>` ran: exit 0, `Copied: 45 item(s)`, stderr empty, 177 files placed, each byte-identical to the clone's (177 compared, 0 differ). One commit followed. The 14 synthetic agent files (section 2) were then added in later commits as the plants were tuned. No tachi agent was dispatched, used or edited.
2. **Each live run** (D-L2): a fresh `git clone` of the template under a new name, started as a detached tmux session with `env -i` and `HOME`, `USER`, `LOGNAME`, `SHELL=/bin/bash`, `TERM=xterm-256color`, `LANG=en_US.UTF-8`, `TMPDIR` as the runbook's section 3 form passes it (the launching shell's value), and a `PATH` of the user's bin directory, `/opt/homebrew/bin` and the system directories. Then `claude --settings <published profile> --effort medium`, in auto permission mode, with the folder-trust dialog answered "Yes, I trust this folder". No `CLAUDE_CODE_*` variable was passed, except the output cap in seven sessions (deviation 1). One session's `/status` listed `User settings, Command line arguments` as its setting sources and said some features are unavailable while `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set, a variable only the profile sets, so the profile applied. No user settings file was touched.
3. **The prompts** typed into the main session named the agent types to dispatch, the fixed dispatch prompt `Run your probe.`, and asked the main to end its turn and say in one line what arrived. At layer B the main dispatched the synthetic dispatcher once, with the list of types in its prompt.
4. **The evidence** is the session transcripts: the main's, and one per agent. The model's own account of what it saw was never used as evidence. Platform: Claude Code 2.1.331 (W1's baseline recorded 2.1.330), macOS. The main session ran Opus 5.5 and every agent Sonnet 5.5 (`model: sonnet`, as every tachi agent pins), with adaptive thinking at medium effort. With no cap set, `max_tokens` was 128,000 for both.
5. **No foreground option.** Every dispatch, at both layers, was a background dispatch (`requestShape: background` in each agent's metadata, and the Agent tool's call carries only a description, a prompt and a type). The erratum's statement holds on 2.1.331.

## 2. The synthetic agents

All carry `model: sonnet`. Each leaf that reports also carries the provisional closing text from `dispatch-record-brief-shared.md` verbatim: end with `TACHI-END` alone, or with a `TACHI-OVERFLOW ` line if the findings cannot fit.

| Agent | Tools | What it is told to do |
|---|---|---|
| `s9-leaf-ok` | Read, Glob, Grep | report three fixed lines (the control) |
| `s9-leaf-overflow` | Read, Glob, Grep | report two lines, then end with a `TACHI-OVERFLOW` line |
| `s9-leaf-cut-out`, `-200` | Read, Glob, Grep | report 60, 100 or 200 numbered lines (4000 in its first version), complete, none skipped (a stop mid-output when the cap is low) |
| `s9-leaf-cut-think` | Read, Glob, Grep | work out a long product and check it twice before reporting one line (a stop mid-reasoning when the cap is low) |
| `s9-leaf-empty` | Read, Glob, Grep | deliver an empty report |
| `s9-leaf-silent` | Read, Glob, Grep | end the turn with no text and no tool call |
| `s9-leaf-plain` | Read, Glob, Grep | write the report as plain text and never call `SubagentHandback` |
| `s9-leaf-turn1` | Read, Glob, Grep | `maxTurns: 1`, so the turn limit ends it after its first tool call |
| `s9-leaf-stall` | Read, Bash | run a 590-second command and repeat it |
| `s9-leaf-slow` | Read, Bash | run a 75-second command, then report one line (the wait test) |
| `s9-leaf-fifo` | Read, Glob, Grep | read a named pipe that has no writer, so the call never returns |
| `s9-dispatcher` | Read, Glob, Grep, Agent, Bash, Write | the orchestrator's tools; dispatch the types its prompt lists in one message, with the completion rule's words ("While an agent you dispatched is still running, don't report a result and don't end your run. If you end your turn to wait, resume this loop on each completion notice."), then report one line per type |
| `s9-dispatcher-retry` | the same | dispatch the first of two types; if it fails or ends without a report, dispatch the second in its place; the same completion rule |

Three plants needed a second version. The first `s9-leaf-stall` ran a shell `sleep`, which the Bash tool refuses at once (`Blocked: standalone sleep 590 ...`), so the second runs a 590-second `python3` call. The first `s9-leaf-cut-think` told the agent to reason "in your own thinking", and the platform's safeguards stopped it (`stop_reason: refusal`, a reasoning-extraction flag), so the second asks for the long working without naming it. `s9-leaf-cut-out`'s 4000-line first version was recovered by the agent (section 5.2).

## 3. The runs

`<adopter s9-xx>` is the run's directory under the run root. Cap means `CLAUDE_CODE_MAX_OUTPUT_TOKENS` (deviation 1).

| Run | Layer | Cap | Dispatched | Outcome |
|---|---|---|---|---|
| `<adopter s9-a1>` | A | none | ok, overflow, empty, silent, stall (shell `sleep`) | five hand-backs; the `sleep` was refused, the empty message was rejected, the silent turn was nudged |
| `<adopter s9-a2>` | A | 2000 | ok, cut-out (4000 lines), cut-think (first version) | ok normal; cut-out stopped once, then delivered 50 lines and an overflow line; cut-think `failed` by refusal |
| `<adopter s9-a3>` | A | none | plain, turn1, stall (python) | plain nudged once, then delivered; turn1 no report; stall auto-backgrounded, three interim notifications |
| `<adopter s9-a4>` | A | 600 | cut-out (60 lines), cut-think | both `failed` after four stops: cut-think all in reasoning, cut-out in the hand-back call |
| `<adopter s9-a5>` | A | 1200 | cut-out (100 lines) ×3 | three `failed`, mid-output |
| `<adopter s9-a6>` | A | none | fifo | nothing arrived for 15 min 23 s; the child completed when the pipe was released |
| `<adopter s9-a7>` | A | 2000 | cut-out-200 ×3 | three `failed`, mid-output |
| `<adopter s9-b1>` | B | none | dispatcher → ok, overflow, slow | waited; hand-back after the 75-second child |
| `<adopter s9-b2>` | B | 600 | dispatcher → cut-out, cut-think | waited; both `failed`; the dispatcher reported both as not reported |
| `<adopter s9-b4>` | B | none | dispatcher → stall, turn1, plain, silent, empty, ok | waited for five; the harness forced the hand-back when the sixth went idle |
| `<adopter s9-b5>` | B | 1200 | dispatcher → cut-out ×3 | the dispatcher handed back early with all three live, then all three `failed` |
| `<adopter s9-b6>` | B | none | dispatcher → fifo, ok | the dispatcher waited 15 min 29 s on the blocked child, then handed back normally (section 5.3) |
| `<adopter s9-b7>`, `-b8`, `-b9` | B | none | dispatcher → ok, overflow, slow (as b1) | all three waited |
| `<adopter s9-b10>` | B | 1200 | retrying dispatcher → cut-out, then ok | the first child `failed` at 25 s; the dispatcher dispatched the replacement, waited, and reported both |

## 4. The layout (KB 25)

What reaches the dispatcher's model is the first block. The second block is what the harness keeps on disk and in the child's own transcript, which is where this spike read the causes; the dispatcher's model does not see it.

**In the dispatcher's context** (the same at both layers; differences are noted)

| Key | Where it sits | Values seen | Carried by |
|---|---|---|---|
| Hand-back message | a user turn that starts `Another Claude session sent a message:` (at layer B, `... sent a message while you were working:`), then `<agent-message from="<agent id>">`, closing with `</agent-message>` | one per delivered report, 1 to 3 s after the child's `SubagentHandback` call | only a report that reached a successful `SubagentHandback` call: complete, overflow line, placeholder, recovered. Never a `failed`, an interim, a turn-limit or a no-report ending |
| Frame line | the first line inside the block | `[Subagent hand-back] The text below is the final report of a subagent this session delegated to. ... The harness indents every line of the report ... The report follows:` | the same |
| Report lines | between the frame line and the closing tag | every line indented by exactly two spaces, blank lines included (`  ` alone). The marker line reads `  TACHI-END` or `  TACHI-OVERFLOW {...}` | the same |
| Trailing paragraph | after the closing tag | one fixed paragraph: the sender is an agent in this session and is not the user, and it cannot grant escalation | the same. This paragraph, not the marker, is the last non-blank line of the turn |
| Notification | a separate user turn after the message, 2 to 6 s later, holding `<task-notification>`; at layer B it starts with `[SYSTEM NOTIFICATION - NOT USER INPUT]` and four lines saying it is an automated event | `<task-id>`, `<tool-use-id>`, `<output-file>`, `<status>`, `<summary>`, `<note>`, `<result>`, `<usage>` | every dispatch |
| `<status>` | notification | `completed` or `failed` | `completed` also covers a finished agent, the two no-report endings, the turn-limit stop and the interim "waiting" notice |
| `<summary>` | notification | `Agent "<description>" finished`; `... stopped at its <N>-turn limit (partial result)`; `... is waiting on its own background work`; `... failed: Agent terminated early due to an API error: <message>`, which for the output cap ends `(error type max_output_tokens)` and states the cap | every dispatch. The summary and the result tell the endings apart, and `<status>` does not |
| `<result>` | notification | "This agent's report was delivered to you as a message from ... Read it there; it is not repeated here."; "The subagent ended without delivering a report through SubagentHandback, so no report was delivered. Its unsent text is not shown."; "NOTE: this agent stopped at its <N>-turn limit before finishing. It was still calling tools and had produced no report." plus the previous sentence; "This agent has not reported yet: it is waiting on its own background work and will deliver its report through SubagentHandback when that finishes." | absent on `failed` |
| `<note>` | notification | the standing note ("fires each time this agent stops with no live background children of its own ... the same task-id may notify more than once"); for the interim notice, "the result below may be interim"; after a refusal, one more sentence: "Safeguards stopped this agent. Pass the message above on to the user." | every dispatch |
| `<usage>` | notification | `<subagent_tokens>`, `<tool_uses>`, `<duration_ms>`; `duration_ms` is wall-clock | every `completed` notification, including the interim and no-report ones. Absent on `failed` |

**Not in the dispatcher's context** (disk and the child's transcript)

| Key | Where it sits | Values seen |
|---|---|---|
| Harness messages inside the child | user turns in the child's transcript | `Output token limit hit. Resume directly — no apology, no recap of what you were doing. Pick up mid-thought if that is where the cut happened. Break remaining work into smaller pieces.` (three times); `[handback-send-enforce] Your report has not been delivered. Call SubagentHandback({message: <your full report>}) now; the call ends your run.` (up to three times); `[Your previous response had no visible output. Please continue and produce a user-visible response.]`; the tool error `message must not be empty` |
| Stop reason | each assistant record | `max_tokens`, `tool_use`, `end_turn`, `refusal`, `stop_sequence` |
| Token split | `usage.output_tokens_details.thinking_tokens` | tells a stop in reasoning (thinking = the whole cap) from a stop in output (thinking 48 to 356 tokens, the rest in the hand-back call) |
| Error record | the child's last assistant record | `isApiErrorMessage: true`, `apiError: max_output_tokens`, stop reason `stop_sequence`, zero output tokens |
| Dropped output | the child's transcript | the partial tool call is not stored (the first stopped response keeps only its reasoning block), and the stopped responses of the three retries are not stored at all |
| Agent metadata | one small file per agent | `spawnDepth`, `parentAgentId`, `requestShape: background`, `finished` (set when the agent stops, so it is also `true` for a dispatcher that is only waiting) |
| Queue records | the main's transcript | the hand-back and the notification are queued and consumed as separate items |

## 5. The four classes, at both layers

At a glance (the dispatcher's view; trial counts in brackets). The sub-sections give the detail.

| Class | Layer A: the main session dispatches | Layer B: a subagent dispatches |
|---|---|---|
| Control: a complete report | hand-back with `  TACHI-END` last; `completed`, "finished" (2) | the same (7) |
| An overflow line the agent wrote | hand-back with `  TACHI-OVERFLOW {...}` last; `completed`, "finished" (1) | the same (4) |
| 1. Stop mid-reasoning | `failed`, `error type max_output_tokens`; no hand-back, no `<usage>` (1) | the same (1) |
| 2. Stop mid-output | `failed`, the same text (7). One trial recovered: a normal hand-back, no sign of the stop (1) | `failed`, the same text (5) |
| 3. Stall, a shell command | interim `completed`, "is waiting on its own background work", again on each cycle; never final (1) | the same notice, then a forced hand-back by the dispatcher, and an orphan (1) |
| 3. Stall, a call that never returns | nothing for 15 min 23 s (1) | nothing for 15 min 29 s, and the dispatcher held (1) |
| 4. Empty return | the empty message is refused, so a placeholder report arrives (2); plain text is nudged, then delivered (1); a turn limit gives `completed` and "no report was delivered" (1) | a placeholder report (2); plain text refused three times gives `completed` and "ended without delivering a report" (1); a turn limit, the same as at layer A (1) |

### 5.1 A stop mid-reasoning

- **Planted by** `s9-leaf-cut-think` at a cap of 600. The child's four consecutive responses all stopped on `max_tokens` with `thinking_tokens` equal to the cap: nothing but reasoning was written. The harness sent its three "Resume directly" messages, then gave up.
- **Layer A** (`<adopter s9-a4>`): `<status>failed</status>`, summary "Agent ... failed: Agent terminated early due to an API error: API Error: Claude's response exceeded the 600 output token maximum. ... (error type max_output_tokens)", no `<result>`, no `<usage>`, 20 s after the dispatch. No hand-back message.
- **Layer B** (`<adopter s9-b2>`): the same notification, inside the dispatcher's context with the system-notification preface, 21 s after the dispatch. The dispatcher kept waiting for its other child, then reported "not reported".
- **Hidden case.** With a cap high enough that a retry fits, a stop in reasoning would be invisible: the dispatcher would get a normal report, and the only trace would be a longer `duration_ms` and a larger `subagent_tokens`. This was not planted for reasoning. The mid-output case below shows the effect once.

### 5.2 A stop mid-output

- **Planted by** `s9-leaf-cut-out` and `s9-leaf-cut-out-200` at caps of 600, 1200 and 2000. In every case the first stop had 48 to 356 thinking tokens, and the rest of the cap went into the `SubagentHandback` call's `message`. The harness drops that partial call and sends the "Resume directly" message. Each of the three retries stopped at the cap again, and then the error record followed.
- **Layer A:** 7 trials (`<adopter s9-a4>`, `-a5`, `-a7`), 7 `failed` with the notification above (the cap number in its text), 15 to 45 s after the dispatch, longer for a larger cap. No partial text was delivered in any of them.
- **Layer B:** 5 trials (`<adopter s9-b2>`, `-b5`, `-b10`), 5 `failed`, the same notification in the dispatcher's context, 16 to 28 s after the dispatch.
- **One recovered trial** (`<adopter s9-a2>`, 4000 lines, cap 2000): after the first stop and one nudge the agent delivered 50 lines and then a `TACHI-OVERFLOW` line of its own (it improvised the object's keys). The dispatcher saw a normal hand-back and a `finished` notification, with no sign of the stop. That makes 13 trials, 12 `failed` and 1 recovered. In none of the 13 did the dispatcher get a cut report, or a short report closed with `TACHI-END`.

### 5.3 A stall

Two forms, because the harness changes what a stalled shell command looks like.

- **A shell command** (`s9-leaf-stall`, a 590-second python call). After 180 s the Bash tool moves the command to the background and the agent's turn ends ("Command was moved to the background ... after running for 180s"). The agent then goes idle with a live shell.
  - **Layer A** (`<adopter s9-a3>`): the main got `<status>completed</status>`, summary "Agent ... is waiting on its own background work", the note "the result below may be interim", `<usage>` present, at 187 s. The agent resumed each time its shell finished and ran the command again, and the main got a further interim notification with the same task id each cycle (three by the end of the session). None was final.
  - **Layer B** (`<adopter s9-b4>`): the dispatcher got the same interim notification. Every other child had reported, so the harness treated the dispatcher as having no live child and sent it `[handback-send-enforce]` 7 ms after its turn ended. The dispatcher handed back `not reported` for that child. The child outlived its dispatcher: the main's agent panel still showed it running when the session was checked, 28 minutes of wall-clock later (16 of them asleep, deviation 2). That is the orphan KB 22 describes, and its later interim notice reached the main, which had dispatched only the dispatcher, 12 minutes after the dispatcher returned.
- **A call that never returns** (`s9-leaf-fifo`, a read of a named pipe with no writer). The Read tool has no timeout and the harness added none.
  - **Layer A** (`<adopter s9-a6>`): the read was issued 2 s after the dispatch and returned only when the pipe was released from outside the session, 15 min 23 s later. In that time nothing was written to the child's transcript or the main's: no notification, no interim notice, no error. The status panel showed the agent as running, with its elapsed time counting up. After the release the child reported normally (`TACHI-END`: one hand-back, one `finished` notification).
  - **Layer B** (`<adopter s9-b6>`): the other child reported 4 s after the dispatch. The dispatcher ended its turn to wait and was neither resumed nor forced for 15 min 29 s, and it did not hand back early. After the release the blocked child reported and the dispatcher handed back 1.3 s later.

A real Phase 2 agent carries only Read, Glob and Grep, so it has no shell and cannot take the first form. The second form needs only a blocked tool call.

### 5.4 An empty return

Every route to an empty report was stopped or hidden by the harness, so no empty return reached a dispatcher. What did reach it:

| Plant | What the child did | What the dispatcher saw (layers A and B alike) |
|---|---|---|
| empty message | `SubagentHandback` with `""` is rejected (`message must not be empty`), and so is `" "`; the agent then sent a placeholder line | a normal hand-back whose report is the placeholder (4 of 4 trials: two agents, two layers) |
| no visible output | an `end_turn` with only reasoning; the harness injected "[Your previous response had no visible output ...]"; the agent then sent a placeholder | a normal hand-back (placeholder) (1 trial, layer A) |
| plain-text ending | the report was written as plain text. The harness sent `[handback-send-enforce]` after each ending, at most three times. At layer A the agent complied after one | layer A: a normal hand-back with the marker. Layer B: the agent refused all three times, and the dispatcher got `completed` and "The subagent ended without delivering a report ... Its unsent text is not shown." The text, marker included, was never shown (1 trial at each layer) |
| turn limit (`maxTurns: 1`) | stopped after its first tool call, with no report | `completed`, summary "stopped at its 1-turn limit (partial result)", the NOTE and "no report was delivered" (2 of 2 trials, one per layer) |
| safeguards refusal (not planted on purpose) | `stop_reason: refusal`, then an error record | `failed`, the API error text with the refusal's class, and the extra note sentence (1 trial, layer A) |

## 6. Can a dispatching subagent wait?

**Yes.** A subagent that has dispatched agents ends its turn. The harness resumes it with each child's hand-back message and notification, and sends the subagent's own notification to its caller only when it has stopped with no live child.

- **Evidence.** Four plain runs (`<adopter s9-b1>`, `-b7`, `-b8`, `-b9`; children: two that report within 3 s and one that takes 75 s): the dispatcher ended its turn at once, was resumed for each child, ended its turn again, and called `SubagentHandback` 1 to 2 s after the last child reported, about 85 s after dispatching. The caller's hand-back message followed 1 s later and its notification 5 to 6 s after the call. In `<adopter s9-b2>` the dispatcher waited through two failing children and reported them. In `<adopter s9-b4>` it waited for five of six. In `<adopter s9-b10>` it dispatched a replacement after a `failed` notice (the T111 pattern, two layers deep) and waited for that too. The waiting uses no tool the profile denies (`SendMessage`, `Monitor` and `ListAgents` are denied, and the Bash tool refuses a standalone 590-second shell `sleep` and tells the agent not to chain shorter ones), so ending the turn is the only way to wait, and it is the one that works. The R-27 smoke run's timings ([r27-smoke-pr1.md](r27-smoke-pr1.md)) are consistent: the orchestrator ran 12 minutes while its agents ran inside that span.
- **Bound 1: nothing stops a dispatcher from handing back early.** In `<adopter s9-b5>` the dispatcher called `SubagentHandback` ("I can't give you the final report yet") 4 s after dispatching, with all three children live. The caller received that as the dispatcher's report. The dispatcher stayed alive and was resumed when the children failed, and the caller's `completed` notification came 25 s later, but the report had already been delivered. 1 of 9 layer-B runs did this. The harness holds the notification, and does not hold the hand-back message.
- **Bound 2: the wait ends when every child has stopped, finished or not.** In `<adopter s9-b4>` the harness forced the hand-back as above. A child that is idle with its own background work is not "live". Phase 2's agents have no shell, so they cannot reach this state.
- **Bound 3: a child whose call never returns holds its dispatcher, with no timeout.** None fired at either layer in 15 minutes, and neither layer got any sign of trouble. Both chains completed normally once the call returned (section 5.3).

**Scope.** Waiting in the orchestrator works, so moving Phase 2 to the command layer (S-16's follow-up) is not needed for the wait itself, and nothing here goes to the PM as a scope change on that count. Whether to bound a blocked child (Bound 3) is a separate question, and it is open. A dispatcher can read the clock with `date`, but nothing wakes it while it waits except a child's message, and the profile denies the tools (`Monitor`, `SendMessage`) that could.

## 7. What bears on T090 and T111

Observations, not rulings.

1. **The marker is read inside a frame.** The provisional rule takes "the last non-blank line of the return". In the dispatcher's context the return is the indented block, and the last non-blank line of the turn is the trailing paragraph. A rule that works on the context has to say: the last non-blank line between the frame line and `</agent-message>`, with the two-space indent removed. Of 19 delivered reports from agents told to close with the marker, 13 ended with `TACHI-END` and 6 with a `TACHI-OVERFLOW ` line, always as the last report line and alone on it. A blank line came before the marker in 7 of the 19 (a line holding only the two-space indent), which "last non-blank line" absorbs.
2. **There are two channels, and a truncation uses only the second.** A report is judged from the hand-back message. Everything else is judged from the notification: `failed` and `error type max_output_tokens` for a cap stop, "no report was delivered" for a plain-text or turn-limit ending, "waiting on its own background work" for an idle child. The provisional table's third row ("anything else, or no return at all") covers all of these, but the notification names a cause, and the provisional `reason` values (`no_end_marker`, `overflow_error`) have no place for it yet.
3. **`<status>completed</status>` does not mean finished.** The turn-limit, no-report and interim notices carry it. Only the summary and result text tell them apart.
4. **The harness retries first.** A cap stop is retried three times before the dispatcher hears of it, so one truncation can be invisible (section 5.2), and a `failed` notification already stands for four stops. The orchestrator's own cap of three attempts per lineage counts on top of that.
5. **For T111's text.** The completion rule's words did not prevent the early hand-back in `<adopter s9-b5>`. The rule says not to "report a result or end the stage", and the dispatcher read `SubagentHandback` as a way to say it was not ready. A sentence that names the call ("never call `SubagentHandback` while an agent you dispatched is still running") is not tested here.
6. **The cap's default does not reach a plant.** At 128,000 tokens a natural overflow needs about four responses of that size (the first plus three retries). Every truncation here used a low cap, so the cap-independent parts (the drop, the three retries, the error text) are observed, and the 128,000 case is not.

## 8. Deviations and limits

1. **Output cap (deviation from "no `CLAUDE_CODE_*` variable").** `CLAUDE_CODE_MAX_OUTPUT_TOKENS` was set in the launch environment of seven sessions (600, 1200 and 2000; sections 3 and 5). It applies to the main session and the agents alike. Without it, a plant needs one response of more than 128,000 output tokens, and the harness repeats that three times, so four such responses per plant, at several minutes each. No other `CLAUDE_CODE_*` variable was passed.
2. **The host slept for 16 minutes** (about 03:35 to 03:52 UTC; the power log names a lid-close sleep) during `<adopter s9-a3>` and `<adopter s9-b4>`. Every wall-clock figure that spans that window is inflated, `duration_ms` included. The first interim notice at layer A (187 s) comes from before it. The 180-second auto-background threshold counts wall-clock, so in `<adopter s9-b4>` it was met on waking. From then on a `caffeinate` process held the host awake; it is a process, not a setting.
3. **User MCP servers were connected** (`/status`: six connected, one needs auth). Section 3's user-scope additions, including `deniedMcpServers`, are the maintainer's call and were not applied (w5-setup-pr1.md, D-L8). The profile's `mcp__*` rule kept their tools out.
4. **Typed into sessions:** the prompt, `/status` once, `/exit` (with Enter on "Exit and stop tasks" in the two stall sessions), and the trust answer. Nothing else. Outside the sessions, the two named pipes were written to once, after the 15-minute window, to let the blocked reads return.
5. **One platform version and one model pair.** Claude Code 2.1.331, Opus 5.5 as the main session, Sonnet 5.5 as the agents. The frame wording, the harness messages and the retry counts belong to the platform and may change with it.
6. **No true stream stall was planted.** An API stream that goes quiet cannot be made to happen on demand. The blocked read is the stand-in, and it covers the dispatcher's view only.
7. **A premature hand-back is model-dependent.** 1 of 9 layer-B runs. The sample is small.
