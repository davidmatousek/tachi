# FR-E.17 disposition ledger (started at T009)

**Date:** 2026-11-22. **Census pinned at:** `b040fa1` (v4.48.4; full SHA `b040fa198260ee33a2b1c7ff3edd16080d1daad2`). **Started by:** T008 and T009 (lane O1, W1). **Continued by:** lane C (T029), lane D (T037 and the controls guide), O3 (T101), and the delivery tasks (T082, T138).

FR-E.17 and spec S-14 require each PR to carry a ledger for the occurrences in its track. Every occurrence gets exactly one disposition: changed, retired, or carved out with a filed issue (KB 23). This file is the working ledger. T082 copies PR 1's rows into the PR body, and T138 does the same for PR 2.

## Reading rules

- **The census is fixed.** It has 17 rows: the four SARIF contract copies (FR-E.1, rows A1–A4), D-6(a)'s seven count rewordings (FR-N15.1(a), rows B1–B7) and the six platform-neutral clauses (FR-N4.1, rows C1–C6). Line numbers are `b040fa1`'s. Later edits move them, so each row also carries a text anchor.
- **Track and PR.** S is shared text and references, R is the renderers (scorer and controls) and O is the orchestrator and threat model. PR 1 carries Tracks S and R. PR 2 carries Track O.
- **Disposition.** One of `changed`, `retired` or `carved out (<issue>)`. A row that its lane hasn't reached reads `pending`. A Track O row in PR 1's ledger reads `deferred to PR 2`, because the change isn't inert (S-5, ADR-050 D7).
- **Who edits what.** Lane O1 wrote this file and recorded rows C1–C6 and A1. Lane C fills A2 and B1–B4. Lane D fills A3, A4, B5–B7 and note N1. O3 fills A1's PR 2 disposition. No lane edits another lane's rows.
- **Overlaps are real.** B2, B3 and B4 lie inside A2's range, and B6 and note N1 lie inside A4's range. Each census row still gets its own disposition.
- **S1** is the no-hand-back sentence that replaced the clauses: "You return no code: you never hand back a program for your caller to run, and you never write a program for someone else to run."

## Census (17 rows)

| ID | Group | Occurrence at `b040fa1` | Track | PR | Owner | Disposition |
|----|-------|-------------------------|-------|----|-------|-------------|
| A1 | SARIF contract copy | `.claude/skills/tachi-orchestration/references/sarif-specification.md`: the identity and membership sections (`:197-280`, `:329-413`, `:570`, `:585`, `:593-624`) | O | 2 | O3, T101 (W3′) | deferred to PR 2. PR 1 leaves the file untouched (T005) |
| A2 | SARIF contract copy | `.claude/agents/tachi/risk-scorer.md` §10, SARIF output generation (`:454-550`) | R | 1 | lane C, T029 (W2) | changed (§10's SARIF authoring is retired. The section points at `sarif-identity-shared.md`, and §10a, §10e and §10h are superseded by it) |
| A3 | SARIF contract copy | `adapters/claude-code/agents/references/sarif-generation.md`, the installed SARIF guide (the whole file) | R | 1 | lane D (W3), FR-K8.3 | pending |
| A4 | SARIF contract copy | `.claude/agents/tachi/control-analyzer.md` Phase 6c, SARIF output generation (`:371-397`) | R | 1 | lane D, T037 (W3) | pending |
| B1 | D-6(a) rewording | `risk-scorer.md:450`, §9h: the two outputs are consistent on "finding count" | R | 1 | lane C, T029 (W2) | changed (reworded in §9's "Consistency" paragraph: each file holds one entry for each open finding) |
| B2 | D-6(a) rewording | `risk-scorer.md:456`, §10: "All scored findings MUST appear in the SARIF output" | R | 1 | lane C, T029 (W2) | changed (reworded in §10's first paragraph: one result for each open finding) |
| B3 | D-6(a) rewording | `risk-scorer.md:474`, §10c: "one result object per scored finding" | R | 1 | lane C, T029 (W2) | changed (reworded in §10's "Results" bullet: each result is one open finding, correlated peers included) |
| B4 | D-6(a) rewording | `risk-scorer.md:548`, §10j: the SARIF is consistent with the markdown on "finding count" | R | 1 | lane C, T029 (W2) | changed (reworded in §10's "Consistency with the markdown" bullet: both files count the same open findings) |
| B5 | D-6(a) rewording | `control-analyzer.md:345`, Phase 6: the two files are consistent on "finding count" | R | 1 | lane D, T037 (W3) | pending |
| B6 | D-6(a) rewording | `control-analyzer.md:394`, §6c check 5: "Result count matches Phase 1 finding count" | R | 1 | lane D, T037 (W3) | pending |
| B7 | D-6(a) rewording | `control-analyzer.md:402`, §6d check 1: "Coverage Matrix entries MUST equal SARIF result count" | R | 1 | lane D, T037 (W3) | pending |
| C1 | Platform-neutral clause | `.claude/agents/tachi/orchestrator.md:68` | S | 1 | O1, T008 (W1) | changed (rewritten) |
| C2 | Platform-neutral clause | `.claude/agents/tachi/risk-scorer.md:18` | S | 1 | O1, T009 (W1) | changed (rewritten) |
| C3 | Platform-neutral clause | `.claude/agents/tachi/control-analyzer.md:20` | S | 1 | O1, T009 (W1) | changed (rewritten) |
| C4 | Platform-neutral clause | `.claude/agents/tachi/threat-report.md:44` | S | 1 | O1, T009 (W1) | changed (rewritten) |
| C5 | Platform-neutral clause | `.claude/agents/tachi/report-assembler.md:52` | S | 1 | O1, T009 (W1) | changed (rewritten) |
| C6 | Platform-neutral clause | `.claude/agents/tachi/threat-infographic.md:99` | S | 1 | O1, T009 (W1) | changed (rewritten) |

**Tally.** PR 1 owes 16 dispositions: 6 Track S (C1–C6) and 10 Track R (A2–A4, B1–B7). PR 2 owes 1 (A1). At the end of W1, 6 were recorded (C1–C6), 1 was deferred (A1) and 10 were pending. At the end of W2, lane C has recorded A2 and B1–B4, so 11 are recorded, 1 is deferred and 5 are pending (A3, A4 and B5–B7, with note row N1).

## Note row (outside the 17)

| ID | Occurrence at `b040fa1` | Track | PR | Owner | Disposition |
|----|-------------------------|-------|----|-------|-------------|
| N1 | `control-analyzer.md:383`, §6c `relatedLocations`: "For correlation group peers, append peer references." This is D8's peer-reference line. It is **not** one of D-6(a)'s seven (PM-T8, AR-T12) | R | 1 | lane D, T037 (W3) | pending |

## The six clauses: what each one became (recorded at W1)

All six clauses read: "You are platform-neutral. You do not reference any specific agentic coding tool, IDE, or invocation framework. Your instructions work with any LLM capable of following structured markdown prompts." (C3's ends "...and reading files from a local filesystem.") None survives in `.claude/agents/tachi/`. Each was rewritten in place as a `**Contract.**` paragraph.

| ID | Replacement |
|----|-------------|
| C1 | The orchestrator's contract paragraph: it dispatches typed agents by `subagent_type` and never replaces or imitates one; it runs only the shipped scripts its file names and writes no script of its own; then S1. The same file's Agent Invocation Protocol carries the typed dispatch rules, the stop and the stop message (T008) |
| C2 | S1 |
| C3 | S1 |
| C4 | Typed helpers only, with `tachi-attack-tree-delta` as the one helper, named by its `subagent_type` (FR-K5.4); then S1. Section 5 names the `subagent_type` and carries the stop and its message |
| C5 | S1 |
| C6 | S1 |

## Outside the census

- **Adapter copies (R-17, FR-C.1).** The Claude Code adapter copies of the specs edited in W1 (`orchestrator.md`, `threat-report.md` and `threat-infographic.md`) carry a superseded-by header and no ported text. The adapter copies of `orchestrator.md`, `risk-scorer.md` and `threat-infographic.md` hold the same clause, and R-17 leaves it in place by design. The `risk-scorer` copy's header comes with T030. The follow-up issue in the #369 family is filed at T080.
- **Other adapters.** The Copilot, Cursor and generic adapters also carry the clause. NG10 leaves them out of scope, and they aren't census rows.

## The five lane C rows: what each one became (recorded at W2, T029 and T030)

`risk-scorer.md` is judgment-only. It writes one part per batch under the part contract, and the renderer writes both output files. Its SARIF section now holds no authoring instruction.

| ID | What the new text says |
|----|------------------------|
| A2 | §10 reads "SARIF Output (risk-scores.sarif)". It states that the agent writes no SARIF, and points at `sarif-identity-shared.md` (T005) for the tools and categories, the rule IDs, the hash, the URI, membership and correlation. §10a (tool driver), §10e (fingerprints) and §10h (correlation) are superseded by that reference and carry no text of their own. R-33's case at `:462` is fixed: the tool names are `tachi-risk-scorer` and, for `threats.sarif`, `Tachi` with a capital T |
| B1 | §9's "Consistency" paragraph: the two files agree on every value, and each holds one entry for each open finding, which the renderer checks before it replaces a canonical file |
| B2 | §10's first paragraph: the renderer writes `risk-scores.sarif` with one result for each open finding |
| B3 | §10's "Results" bullet: each result is one open finding, correlated peers included, and a RESOLVED finding has none |
| B4 | §10's "Consistency with the markdown" bullet: the SARIF agrees with `risk-scores.md` on every value, and both files count the same open findings |

Two lines of the old §10g.1 are not census rows, and are recorded here so that none is lost:

- **F-302's `:528`** ("Provenance only — does NOT affect scoring") is reworded per ADR-050 D2 and now stands in §3.5: `affected_assets` lists the tags the asset-modifier step used for this finding. Emitting it changes no score; only the modifier step does, and it reads the same tags from the same source.
- **`:519`'s copy-verbatim line** is retired. The agent no longer writes `affected_assets`, so there is nothing to copy. The same instruction retired from `/tachi.risk-score` (`:83-90` and `:135-140`), where the command's new Step 1.5 states the one tag source instead.
