# K4 five Whys: the Phase 3.5 skip in Run A

Task T002 (W0, K4) · FR-K4.3 · input to T004's TW-K4 ruling · inside the 0.25 d time box.
Structure only (H8): counts and structure appear. The target, its components and its findings don't. Private sources are cited as "the private run notes" and "a retained transcript".

## Result

- **R-21: does not fire.** Nothing here changes which findings join chains (see "R-21").
- **Proposed TW-K4 outcome: (c).** Run A's orchestrator transcript wasn't retained, so the trigger of the skip can't be settled (candidates 1 to 3). Candidate 4 is ruled out from retained inputs. Nothing supports (b). PR 2 proceeds as planned.
- **Premise to correct (T004, C-13).** Run A is a July 2026 run on v4.47.0, not a late-September run on v4.48.0 (see "What Run A is").

| # | Candidate | Verdict | Evidence class |
|---|---|---|---|
| 1 | Context pressure | UNDETERMINED (hard exhaustion not supported) | OUTPUT, COMPARE |
| 2 | Instruction ordering | UNDETERMINED (latent ambiguity, causal role unproven) | STATIC, COMPARE |
| 3 | A skipped conditional | CONFIRMED as why the failure was silent. UNDETERMINED as the trigger | STATIC, OUTPUT |
| 4 | Link criteria that legitimately yield zero | RULED OUT | REPRO |

**Evidence classes.** STATIC: contract text read at a tag. OUTPUT: Run A's saved outputs, read offline. REPRO: an offline run of the v4.48.0 Phase 3.5 text on Run A's retained inputs, in a scratch directory outside any tracked tree (H1). COMPARE: Run B, a later run of the same text. NONE: not kept.

## What Run A is

- A baseline-aware threat-model run on a 26-component architecture: 202 findings (41 Critical, 105 High, 45 Medium, 11 Low). They are 146 STRIDE, 24 AG and 32 LLM findings. Of the STRIDE findings, 114 carry a MAESTRO layer (L1 to L4, L6, L7) and 32 are Unclassified.
- The private run notes date it to July 2026, on v4.47.0. The skip was spotted in late September, from the saved outputs alone, when #374's line pointers were checked against v4.48.0. The notes record no late-September run.
- Phase 3.5's text is byte-identical at v4.47.0 and v4.48.0. The branch tip differs from v4.48.0 only by an unrelated two-line Phase 1a addition (N5), and `attack-chain-patterns-shared.md` is identical. So `orchestrator.md:393-550` is what Run A ran, and it is today's text.
- Run B is a November 2026 interim run on v4.48.1, with the same Phase 3.5 text: about 40 components and 387 raw findings.

## The 5 Whys

**Problem.** Run A's output directory has no `attack-chains.md`, no Phase 3.5 outcome anywhere, and a report with no chain section. Its inputs hold Critical and High STRIDE findings on six MAESTRO layers.

1. **Why no artifact and no record?** The only branch that writes nothing is the zero-chain branch: Step 5 says "skip this artifact entirely and set `has-attack-chains = false`" (`orchestrator.md:484`). A phase that never ran leaves the same state. STATIC, OUTPUT.
2. **Why can't anyone tell "never ran" from "found none"?** The boolean lives only in the orchestrator's memory, the `threats.md` template has no field for the outcome, and readers key on file presence (`orchestrator.md:546-550`, `output-schemas.md:346-358`). Nothing downstream needs Phase 3.5: Phase 3.6 says it doesn't read the chains (`:578`), and the report and PDF sections are conditional on the file. A skip can't fail loudly. STATIC.
3. **Why was the skip wrong?** Run A's own findings and data flows give chains: 541 candidate links, 78 chain starts, 75 chains (REPRO below). So the phase either never ran or ran and wrote nothing. The outputs can't separate the two. REPRO, OUTPUT.
4. **Why would the orchestrator skip it or compute a false zero?** Phase 3.5 is an algorithm for the model to run in context: a scan of 8,702 ordered cross-layer pairs, a transitive closure over a 26-node, 53-edge flow graph, a table lookup per pair, greedy assembly, dedup and ranking. It has no script, no checkpoint and no output that proves it ran. Run B had about 1.9 times Run A's raw findings. Its orchestrator computed the phase in a script it wrote, with graph-building, chain-forming and chain-breaker functions, and added two consolidation steps the text doesn't contain (S-3(d) and (f) cover them). That points to in-context execution not scaling. It doesn't show what Run A's orchestrator did. COMPARE, STATIC.
5. **Why does the contract allow that?** It gives a computation-heavy, order-dependent algorithm to the model, gives its "nothing found" path a silent no-op, and checks nothing afterwards.
   - **Root cause (contract level, established):** an unverifiable, unobservable no-op path on a computation the model can't be relied on to perform at scale.
   - **Trigger in Run A: undetermined.**

D13 fits the contract-level cause. Shipped code computes the chains, the outcome is a persisted record, and the main-session check rewrites a missing record as `skipped (no outcome recorded)`. D13 doesn't force the orchestrator to run the step, because nothing downstream requires it. It makes a repeat visible and tested, which is FR-K4.1b's purpose.

## The four candidates

1. **Context pressure: UNDETERMINED.**
   - NONE: Run A's orchestrator transcript, so its prompt size at Phase 3.5 is unknown. The model and window that served it are unverified, because the private notes' model records cover the main session only.
   - Against hard exhaustion (OUTPUT): the orchestrator went on to run Phase 3.6 (the pattern column and Section 4c are present) and Phase 3.7 (the Affected Assets block is present). It then wrote the Phase 4 sections and a SARIF of about 300 KB, and dispatched Phase 5. Those steps need more room than 3.5.
   - Against (COMPARE): Run B's orchestrator wrote its chain-computing script at about 410k prompt tokens, was still refining chain narratives at about 490k, and peaked at 700k. It had no compaction and no context error, on about 1.9 times Run A's raw findings.
   - Still open: a model choosing to leave a phase out under load, or missing it.
2. **Instruction ordering: UNDETERMINED.**
   - STATIC: Phase 3 names Phase 4 as the next boundary twice (`:321`, `:380`) and Phase 3.5 once (`:389`). The phase list labels it "3.5" with its artifact "conditional on chain detection" (`:60`, `:66`). It starts at 49% of an 802-line file, and no later phase requires it. That is a real ambiguity in the text.
   - COMPARE: Run B followed the same order. It also read the chain reference in a bulk reference load at the start, not at Phase 3.5. One success doesn't clear an ordering effect, and Run A's reading order is unknown.
3. **A skipped conditional: CONFIRMED as why the failure was silent. UNDETERMINED as the trigger.**
   - The conditional is Step 5's zero-chain branch. Its output signature (no file, no record, no report section) is exactly Run A's. That is the observability gap FR-K4.1 closes (STATIC, OUTPUT).
   - Whether the branch was taken (a false zero) or Phase 3.5 never ran can't be told from the outputs.
4. **Link criteria legitimately yield zero: RULED OUT.** Both sub-cases #374 names, STRIDE-only participation and the structural-connection requirement, still give chains under every reading tried (next section). A post-run review in the private notes, done independently, reached the same 75.

## Reproduction (REPRO)

A scratch script, outside every tracked tree, parsed Run A's saved findings tables and data-flow table. It applied Steps 1 to 3 of `orchestrator.md` and the transition table in `attack-chain-patterns-shared.md`, both at v4.48.0. It read the private outputs and wrote nothing into them. Tie-breaks follow the text: severity, then ID.

| Reading | Pool | Cross-layer pairs | Structurally connected | Links | Chains after dedup and filter |
|---|---|---|---|---|---|
| As written: STRIDE only, closure test | 114 | 8,702 | 8,290 | 541 | 75 (76 under an alphabetical tie-break) |
| Direct flows only, no closure | 114 | 8,702 | 1,290 | 134 | 43 |
| Critical and High only, closure | 81 | 4,442 | 4,292 | 369 | 55 |
| Critical only, closure | 21 | 220 | 220 | 32 | 11 |
| Critical only, direct flows only | 21 | 220 | 72 | 13 | 7 |

Even the narrowest reading gives chains. Neither STRIDE-only participation nor the structural-connection requirement can explain a zero here.

## Evidence retained (C-13)

| Evidence | Kept |
|---|---|
| Run A's orchestrator transcript (the Phase 3.5 turns) | **No.** The default 30-day cleanup applies, and no setting overrides it. The oldest transcript in the whole store dates from October. A search of the store, the private archive and file names found nothing. Under the default it aged out by mid-August, before the skip was spotted. |
| Run A's saved outputs: findings tables, data-flow table, input snapshot, SARIF, report, trees | **Yes**, in the target's own run directory. |
| Run A's orchestrator-written intermediates and its orchestrator's served-model records | **No.** |
| Phase 3.5's text as Run A ran it | **Yes.** It is tagged at v4.47.0 and v4.48.0, byte-identical. |
| Run B's transcripts, its orchestrator's included | **Yes**, in a private archive. Comparative only. |

C-13 holds for the transcript. It doesn't hold for the outputs, and that is why candidate 4 could be settled.

## R-21

Does not fire. Every finding here leaves the rules that decide which findings join chains as they are. Unclassified layers stay excluded (32 of 146 STRIDE findings, 7 of the 28 STRIDE Critical findings, can never join), AG and LLM findings stay excluded, and the transition table is as shipped. For the PM's awareness, with no change proposed: on Run A's graph the closure test passes 95% of cross-layer pairs (8,290 of 8,702), against 15% for direct flows only (1,290). Narrowing it stays an R-21 change under S-3(b).

## TW-K4

The dispositions in tasks.md's table:
- (a) "proceed."
- (b) "SV-1: the PM rules first what the record and its check assert (T144); K4.2–K4.4 go to their own issue (T080); in W1′ the architect re-scopes D13 so that `attack-chains.py` keeps the outcome record and its check; T115–T118 shrink to that; K4.1 and K4.1b stay."
- (c) "Record it and proceed; PR 2's fixture runs serve as the reproduction (C-13)."

**Proposed: (c).**
- Not (a). The contract-level cause is inside the plan's design, and D13 covers it. But (a) would also claim the cause is known, and Run A's trigger isn't.
- Not (b). It needs context pressure that neither the chain script nor the rendered outputs remove, and nothing shows that. D13 moves the scan, closure, assembly and ranking out of the orchestrator, which keeps at most five narratives. Run B did the same work at 410k to 490k prompt tokens with no compaction.
- (c) is what's true: the transcript wasn't kept.

## For PR 2's fixture runs (no plan change)

The post-fix runs reproduce the fix, not the pre-fix trigger. To serve as C-13's reproduction, T130 and T131 should carry what the plan already collects: the Phase 3.5 outcome line, the orchestrator's peak prompt (TW-CTX), and whether `plan` and `render` ran (the check's event). A pre-fix run of the unmodified orchestrator on the fixture would be the only direct test of candidates 1 to 3. It isn't planned, and this record doesn't ask for one.
