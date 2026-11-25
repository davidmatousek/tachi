# TW-ESC at M3: the end of build session 1 (T062)

**Date:** 2026-11-23. **Session 1:** PR 1's W0, W1 and W2. **W2's pushed tip:** `5d218af`, with CI 14 of 14 green. **The team-lead's re-projection** was invoked per TL-T6.

## Result: TW-ESC DOES NOT FIRE, so T063 doesn't run

| Clause (as the PM restated it) | Value | Fires? |
|---|---|---|
| PR 1's delivery, re-projected from the actual M3 date plus the remaining windows, above TW-0 as re-based (T0 + 11.0) | central **T0 + 6.45** (floor 4.95, ceiling 10.05) | No: 4.55 d of margin |
| Any lane more than 50% over its budget | the highest is ADR, at 1.1× | No |

## The actuals

- **Milestones.** T0 and M1 are both 2026-11-22.
  - W0 started that evening, and G0 closed (`9457a3e`).
  - W1 was pushed (`03a8f0d`, CI 12 of 12 green), and G1 closed (`e9bd0e1`, M2).
  - W2 was pushed in the early hours of 2026-11-23 (`5d218af`, CI 14 of 14 green).
- **Session 1 took about 7.1 hours** of wall clock, against windows of 0.35 + 1.6 + 2.4 = 4.35 d. **M3 is taken as T0 + 1.15**, T062's own tail included, against T0 + 5.35 planned.
- **The ratio rule.** At 8 hours per eng-day, the actual-to-planned ratio for W0–W2 is 0.20. It would exceed 1.0 only if an eng-day were shorter than 1.63 hours. So nothing is scaled.
- **Tasks.** 56 of 150 are done: all of W0–W2, with T063 not fired. Of PR 1's 91 tasks, 35 remain, in W3–W6.

## PR 1's projection

The base is the actual M3 plus the remaining windows, W3 to W6 and coordination. The plan didn't price three additions, now priced:
- **P0's fix slice, +0.2 d on W3.** P0 (T061) was APPROVED_WITH_CONCERNS: 1 HIGH, 5 MEDIUM and 6 LOW. The HIGH and four MEDIUM fixes land in W3, before PR 1 merges. One MEDIUM is a known limit, pending a W3 ruling. The LOW items are W3 work or T080 follow-ups.
- **F17 at the final batch sizes, +0.25 d on W5.** The architect re-amended D6 at W1 from T021's calibration, to `risk-score` 13, `compensating-controls` 11 and `trees` 12. W5's live matrix plans about 132–152 dispatches, against 46–54 at the plan sizes. Controls has no margin at 11.
- **Small tails:** +0.05 d on W4 and +0.1 d on W6.

The result is floor / central / ceiling **T0 + 4.95 / 6.45 / 10.05**, against TW-0 at T0 + 11.0.

## PR 2's projection, base case

- **T0 + 7.85 / 10.35 / 16.6**, against its bound of T0 + 15.0. With all three contingencies, the central is T0 + 10.95.
- **Options A and B** (T063) aren't invoked, because TW-ESC doesn't fire.
- **W1′** (PR 2's setup and rulings: T084, T086–T089, T148, and T093 once T086 commits) stays in session 2, as planned. If it doesn't close there, PR 2 idles at W3's end.

## The lane clause

- **How it's measured:** one eng-day is 8 hours, per lane, over session 1 as a whole, from first dispatch to last return. The actuals come from commit times, so they are upper bounds, and work added in-session counts against the lane.
- **The result:** no lane is judged over. **The ADR lane is a watch item.**
  - Over the whole session it ran at 1.1×.
  - On a per-wave reading, its W2 instance ran at about 2.5× its 0.15 d budget. The cause was about 25 rulings across W1 and W2 that nobody budgeted.
  - Neither reading changes the verdict.

## TW-N3

**ARMED.** N3's fix hasn't merged: `origin/main` is still `b040fa1`. The session 2 lanes it affects are **D** (W3) and **O2** (W1′).

## What session 1 added beyond the plan

None of these changed a ruled decision's intent:
- **The calibration.** T021 ran a calibration Write, and D6 was re-amended per stage.
- **Rulings.** The architect made about 25 rulings, all recorded in ADR-050 and `contracts/`.
- **The PM's erratum.** At S-8, FR-E.14 and FR-K5.6, "foreground" became the completion rule. The agent platform has no foreground dispatch.
- **A W2 plan-schema bundle** adding `refs` and `architecture_warning`, plus small follow-ups in four W1 helpers.
- **A fixture fixed-point fix.**

## Session 2's plan, from the team-lead

- **P0's fixes run as a fix lane, FX0, inside W3,** not as a serial pre-W3 wave.
  - **FX0's first slice, about 0.4 d:** P0-1's line-start `~` escape, P0-4's forbidden-character check, and P0-3's fallback reader. It is W3's first commit, alongside T034, T052 and T037.
  - **FX0's second slice, about 0.85 d:** the risk-scores fixes, in files no W3 lane owns. R3a, R2 and D take the P0 pieces that fall in their own files.
- **Slots and agents.**
  - When R2t finishes, its slot goes to a second FX0 instance, if FX0 would otherwise outlast R2's chain, or else to T093.
  - W1′'s rulings run on a second architect instance.
- **One task per agent instance,** because six lanes overflowed their context in session 1. Split T067's review in two.
