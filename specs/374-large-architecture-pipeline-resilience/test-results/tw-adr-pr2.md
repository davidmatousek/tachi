# TW-ADR gate before W2′ (T089)

**Date:** 2026-11-23, build session S2. **PR 2's branch:** `374-pipeline-resilience-track-o`, draft PR #425. It is cut at the cut line `03a8f0d`, and W1′ is integrated on top of it.

## Result: the gate PASSES, and W2′ is unblocked

| Check (T089) | Result |
|---|---|
| T086–T088 committed as ADR-050 rev. 3 | Yes. T086 (O-α), T087 (O-β) and T088 (O-γ, RR3 and the `tachi.check-handoff/1` key set) each touched only ADR-050 and `contracts/`. The rev. 3 Revision History row carries all three. |
| The contracts are aligned | Yes: `part-files.md` (the `phase2` notes, the `threats-md` and `report` payloads, §6's hand-off key set), `threat-model-records.md` (the record statuses, Phase 2 dispatches, the section manifest) and `cli.md` (RR3's PLAN argument and return line). |
| Each contingency recorded as fired or not | See below. |
| PR 2 re-projected against its bound (T0 + 15.0) | About **T0 + 14.5** on the plan's basis, a margin of about 0.5. It isn't above the bound, so nothing goes to the PM before W2′. |
| TW-N3 for PR 2's lanes | **ARMED.** N3's fix hasn't merged (`origin/main` is still `b040fa1`). PR 2's affected lanes are **O2** (W1′, W2′ and W3′) and **T** (W3′). |
| W2′'s window re-set to its new pacing lane | Yes: OS, at about 1.80 (below). |

## The contingencies

| Item | Task and lane | Fired? | Priced (d) | Now estimated (d) | Where it lands |
|---|---|---|---|---|---|
| O-α (`phase2`) | T105, OS, W2′ | **No** (T086) | 0.30 | 0 | Released from OS. OC gains about 0.10 in W3′ (T095 and T096 each +0.05) for the lineage rules, the `unrecovered` status and the six counts in the hand-off. |
| O-β (`threats-md`) | T107, OS, W2′; T112, O2, W3′ | **Yes** (T087) | 0.40 | about 0.55 | +0.05 each in T091 (R3b), T092 (OS) and T119 (O3). |
| O-γ (`report`) | T110, T, W2′ | **Yes** (T088) | 0.25 | about 0.70 | +0.15 T109 (T), +0.07 T091 (R3b), +0.15 T092 (OS), +0.03 T103 (F), and +0.05 for the shared reference's report rows. |
| RR3 (base) | T109, T112 | base | 0.10 | +0.05 | +0.03 T092 (OS), +0.02 T097 (O3). |

The contingency effort is about 1.40 d, against 0.95 priced. Duration moves only where the effort lands on a pacing chain.

## Re-projection

- **W2′.** OS becomes the pacing lane: T085 → T091 → T092 → T106 → T107, about 1.80 against the old 1.4. W2′'s central goes from 1.8 to about **2.2** (+0.40), with the 0.05 throttle and T114's 0.1 as its tail. OC stays at 1.4, T at 1.40, and R3b at about 1.5.
- **W3′.** O2 stays the pacing lane, at about 1.12 (+0.12). O3 reaches about 0.97, OC 0.90, T 0.50 and P′ 0.60.
- **PR 2.** The central goes from T0 + 14.0 to about **T0 + 14.5**, inside the bound of T0 + 15.0. On session 1's measured pace (TW-ESC's T0 + 10.35 central), the same additions give about T0 + 10.9.
- **Options for W2′'s +0.40**, for W2′'s session to choose with the team-lead. Each keeps one writer per file:
  - (a) T092 starts on a committed first slice of T091 (the plan and record key sets and the stage enums), saving up to about 0.2 on OS;
  - (b) T106 and T107 (the joiner) move off OS, to a lane that is free after T091;
  - (c) accept the +0.40, which is within the bound. This is the default.

## For W2′ and later

- **T093** (O2's Phases 1–3 in `orchestrator.md`) is done, and held back from W1′'s integration, as T093 rules. It lands in the same commit as T094, which inverts PR 1's inertness assertions, so W1′'s push keeps T010's pins green.
- **T113** should also own the report rows of `part-file-contract-shared.md` (about 0.05 d), which no task holds yet (T088).
- **For the PM's awareness** (T088): the report changes in two ways users see, for release notes item 5. A `multiple`-pattern finding is listed only under Multi-Pattern Findings. A correlation group's roadmap row lists each member's mitigation verbatim, rather than a merged one. Also, NFR-4's reading for the report stage: the report agent runs once per part.
- **TW-K4** is (c), as recorded at W0's gate, so D13 stands and T115–T118 keep their scope.
- **T085's merge** of PR 1's W3 tip will meet textual conflicts in ADR-050's Revision History (keep every row, in date order), in `part-files.md` §3 and §4 (keep both sides' rows) and in `cli.md` (keep both "Readings ruled at" sections, W2 first, and the `plan` row's W2 sentence).
