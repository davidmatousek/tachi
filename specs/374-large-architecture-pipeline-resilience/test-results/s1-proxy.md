# S-1 proxy: measured batch sizes (T003, W0)

**What this is.** The W0 proxy that ADR-050 D6 asks for: per-unit output measured on the shipped examples, turned into batch sizes by D6's formula. T004 hands it to T021 and T023, and W1's pre-fix fixture run (T021(a)) confirms it.

**Inputs.** Every committed file under `examples/` at branch tip `1c55360`, whose code is identical to v4.48.4. Read only, in a scratch clone (H1). The examples come from several earlier releases, so formats and verbosity vary (§6).

**The headline.** The proxy sizes are 9 per scorer batch, 9 per controls batch and 12 trees. The scorer and controls sizes are 4.4x and 3.3x below plan.md's 40 and 30, and no shipped example is at or below them, so SC-8's precondition has no candidate (§5).

## 1. Method

- **Bytes and tokens.** Bytes are UTF-8 bytes of the unit's text as committed. Tokens are bytes ÷ 4 (S-4's estimator).
- **p90.** Linear interpolation over the pooled units of all examples. Nearest-rank differs by under 1% in every row.
- **u** = p90 tokens × 1.25 (the envelope). **size** = min(⌊8,000 ÷ u⌋, ⌊32,000 ÷ (u × F)⌋), with F the files per unit (D6).
- **How u and F are read.** S-1 bounds the largest single write (8,000) and the batch total (32,000). So u is a unit's cost in one file, F is the number of files a unit lands in, and the heaviest file sets u. For F up to 4 the second term is never smaller than the first, so it doesn't bind here. The "both files summed" reading is §4, row B.
- **Which units count.** For the scorer and controls, a unit counts only if it appears in every file of the set. Findings an example left out of a file are skipped, because they would understate the cost of a unit written in full.
- **What is attributed to a unit** (everything else, such as summaries, rules and methodology, is stage overhead and not counted):
  - **Scorer.** `risk-scores.md`: the Scored Threat Table row, the Dimensional Breakdown block and the Governance row. `risk-scores.sarif`: the `results[]` element, from its first byte to the next element's.
  - **Controls.** `compensating-controls.md`: the Coverage Matrix row, any Control Details row keyed by the ID, and the Recommendations block. `.sarif`: the `results[]` element. Control Details prose is per control, not per finding, so it isn't attributed.
  - **Trees.** One `*-attack-tree.md` file. The manifest item adds about 30 tokens, inside the envelope.
  - **`threats.md` rows.** A pipe-table row whose first cell is a finding ID: Sections 3 and 4 (the finding tables) and Section 7 (Recommended Actions), counted apart.
  - **Report finding.** The paragraph that opens with the bold ID (split equally when it opens with several), the roadmap row and the appendix rows. The inline tree is excluded, since code assembles it in PR 2. The one-line `tree_summary` isn't in the old reports. Adding 150 to 200 bytes for each Critical or High finding would move the size from 24 to 20 or 21.

## 2. Result

| Stage | Unit | Files per unit | n | p90 B | p90 tok | u | ⌊8,000÷u⌋ | ⌊32,000÷(u×F)⌋ | **Size** | Plan |
|---|---|---|---|---|---|---|---|---|---|---|
| scorer | one scored finding | 2 (`risk-scores.md`, `.sarif`) | 183 | 2,566 | 641.5 | 802 | 9 | 19 | **9** | 40 |
| controls | one scored finding | 2 (`compensating-controls.md`, `.sarif`) | 255 | 2,701 | 675.4 | 844 | 9 | 18 | **9** | 30 |
| trees | one attack tree | 1 | 245 | 2,098 | 524.5 | 656 | 12 | 48 | **12** | 12 |
| threats.md | one Section 3 or 4 table row | 1 | 474 | 952 | 238.0 | 298 | 26 | 107 | **26** | none |
| threats.md | one Section 7 table row | 1 | 431 | 270 | 67.5 | 84 | 94 | 379 | **94** | none |
| report | one finding | 1 | 160 | 1,044 | 261.0 | 326 | 24 | 98 | **24** | none |

- **Scorer.** The SARIF is the heavier file: p90 2,566 B against 1,731 B for the markdown. The size sits just under a boundary: at u = 800 it would be 10 (u = 801.9).
- **Controls.** The SARIF is again the heavier file: p90 2,701 B against 1,471 B for the markdown.
- **Trees.** The proxy gives plan.md's 12. Each tree is its own Write (D6), so the 8,000 limit bounds each tree (the largest is 3,020 B, about 755 tokens) and the batch total alone would allow 48. D6's formula, read literally, gives 12.
- **threats.md.** The planner uses 26 for the finding tables and 94 for Section 7. The pooled Section 3 and 4 figure is 27 without the one example whose rows are very wide (p90 2,620 B), and 28 with only the current sample directories.
- **Report.** The sample is three examples (110, 31 and 19 findings). The other three reports describe findings by category, not one by one, so they have no per-finding unit.

## 3. Spread by example

Sizes use the heavier file's p90 (the primary reading). Counts are units present in both files.

| Example | Scorer n | md p90 B | SARIF p90 B | Scorer size | Controls n | md p90 B | SARIF p90 B | Controls size | Trees n / p90 B / size |
|---|---|---|---|---|---|---|---|---|---|
| agentic-app | 86 | 1,762 | 3,246 | 7 | 85 | 1,316 | 3,462 | 7 | 78 / 1,255 / 20 |
| consumer-agent-app | 19 | 1,878 | 2,323 | 11 | 19 | 1,953 | 2,388 | 10 | 9 / 2,916 / 8 |
| maestro-reference | 35 | 1,480 | 2,082 | 12 | 110 | 1,108 | 1,240 | 20 | 71 / 2,194 / 11 |
| mobile-banking-app | 31 | 1,607 | 2,121 | 12 | 31 | 1,614 | 2,705 | 9 | 24 / 1,995 / 12 |
| predictive-ml-app | 12 | 226 | 502 | 50 | 10 | 843 | 555 | 30 | 24 / 2,613 / 9 |
| mermaid-agentic-app | - | - | - | - | - | - | - | - | 12 / 1,885 / 13 |
| agentic-app (older run) | - | - | - | - | - | - | - | - | 27 / 1,334 / 19 |

- One example's scorer SARIF holds 35 of its 110 findings, and its markdown has the dimensional block for only 13. The compact-format example writes table rows only. Both pull the pooled p90 down a little, and neither changes a size.
- Restricting the scorer and controls to fully written units (every part present) moves the heavier file's p90 by under 5% and changes no size. Leaving out the oldest tree run (27 trees) moves the tree size from 12 to 11.

## 4. Sensitivity: how conservative the proxy is

D6's measure is the old output per finding. The new agent writes a JSON part, with no tables and no SARIF envelope, so the proxy is an upper bound on a part item. Only rows A to D come from the old files as written. Row E is a model.

| | Reading | Scorer u / size | Controls u / size |
|---|---|---|---|
| **A** | The heavier file as committed (the primary reading above) | 802 / **9** | 844 / **9** |
| B | Both files summed, F still 2 | 1,338 / 5 | 1,220 / 6 |
| C | SARIF re-serialized compact, heavier file | 580 / 13 | 585 / 13 |
| D | The markdown file only | 541 / 14 | 460 / 17 |
| E | A contract-shaped JSON item built from the same text (the part contract's keys, prose cut at its limits) | 372 / 21 | 566 / 14 |

- Row E takes the scorer item from the vector and four rationale bullets, and the controls item from the matrix row, the recommendation text and the SARIF evidence. Its n is 149 and 113.
- T021(a) measures v4.48.4 again, so it can confirm rows A to D. Only a live run of the new agents (W5) can confirm row E.

**What the sizes cost.** Dispatches per stage at the base set's size (390 to 450 open findings):

| | Plan sizes (40, 30) | Proxy (9, 9) | Row E (21, 14) |
|---|---|---|---|
| Scorer batches | 10 to 12 | 44 to 50 | 19 to 22 |
| Controls batches | 13 to 15 | 44 to 50 | 28 to 33 |

D6 said the live matrix "may double the planned dispatches" (C-3). At the proxy sizes it is closer to four times, so F17 (T073, T074) and the W5 window need re-pricing.

## 5. SC-8's example

**No shipped example is at or below both proxy sizes (9 and 9).** The smallest has 11 open findings. Open findings are the rows in `threats.md`.

| Example | Open findings | Committed scorer and controls output | Batches per stage at 9 | Size needed for one batch |
|---|---|---|---|---|
| ascii-web-api | 11 | no (`threats.md` only) | 2 | 11 |
| free-text-microservice | 15 | no | 2 | 15 |
| web-app | 16 | no | 2 | 16 |
| consumer-agent-app | 19 | yes | 3 | 19 |
| mermaid-agentic-app | 19 | no (trees and report) | 3 | 19 |
| microservices | 23 | no | 3 | 23 |
| mobile-banking-app | 31 | yes | 4 | 31 |
| predictive-ml-app | 49 | partial | 6 | 49 |
| agentic-app | 86 | yes | 10 | 86 |
| maestro-reference | 110 | yes | 13 | 110 |

- **Recommendation: `ascii-web-api`.** It is the smallest of all, and no other example could be one batch under any reading in §4 (rows C, D and E give sizes of at least 13, 14 and 14, which clears 11 but not 15). It has the canonical shape (schema 1.4, Section 7 with a Status column, one table row per finding). It lacks committed scorer and controls output, but SC-8 compares two live runs and doesn't read those files. The small-run oracle (NFR-1, T066) runs separately over the examples that have them.
- **The closest with committed scorer and controls output is `consumer-agent-app`** (19 findings). It needs both constants at 19 or more, which no reading supports (row E's controls size is 14).
- **A decision is needed at G0.** At the proxy sizes P-7's "below both stages' thresholds" can't be met by any shipped example, so SC-8's small run would be 2 batches per stage at best. Either T023 sets both constants to 11 or more on evidence (rows C to E), or the PM rules on P-7. The baseline run (T021(b)) needs no batching and is valid on any example, so the example can be named now and the constants decided later (a later change of example would re-run it).

## 6. Limits

- The examples were written at several releases, by agents with varying verbosity. Committed SARIF is pretty-printed, and a compact writer costs about 30% fewer bytes (row C).
- Bytes ÷ 4 is a rough estimator: it charges indentation like text and can undercount dense identifiers. T021(a) records real counts.
- Control Details prose is per control and isn't attributed, so the markdown figure for controls is a floor.
- Section 7 rows are one per finding, so a finding costs one Section 3 or 4 row and one Section 7 row in `threats.md`.

## 7. Generator skeleton (T003's second deliverable)

`tests/scripts/generate_large_arch_fixture.py`, 310 lines: the CLI (`--out DIR`, `--variant NAME|all`), the seeded helpers, a hand-rolled JSON serializer, a path and newline guard, and 12 stubbed parts for T019, T040, T148 and T103.

- **Contract.** Fixed seed. One stream per part, so adding a part never moves another's bytes. Every decision comes from `random()` or a label hash. Nothing reads `hash()`, set order, the clock, the locale or directory order. LF only, one trailing newline.
- **What it emits now.** A canary part of 2 files and 687 bytes that exercises every helper (`probe.json` sha256 `18ef9bc16b1c`, `probe.txt` `6deecd466308`). The stubs return `{}`.
- **Byte-identical output on Python 3.9.6, 3.10.18, 3.11.13, 3.12.11, 3.13.7 and 3.14.4**: one tree digest on all six. It also held across hash seeds, locales, time zones, I/O encodings and dev mode with warnings as errors (3.9.6 and 3.14.4).
- **Other checks, run in a scratch clone.**
  - The source parses under `feature_version=(3, 9)`, has `from __future__ import annotations`, and is ASCII.
  - Its only stream calls are `random()` and `seed()`, and no other stdlib random method name appears anywhere in its text.
  - The serializer matches `json.dumps` byte for byte on 4,000 random values in both layouts on all six interpreters. The one intended difference is that it escapes U+007F.
  - Exit codes are 0, 1 (a part broke the contract) and 2 (usage), and `main()` never raises `SystemExit`.
- **For T019 and T020.** Parts are pure functions of their own `Rng` and SEED. Tests can call `build()` for bytes or `main(["--out", tmp])` in-process (H15).
