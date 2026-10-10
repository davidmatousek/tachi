---
artifact: feasibility-check
feature_id: 373
owner: team-lead
date: 2026-09-27
prd_number: 373
status: draft
estimate:
  planning_days: 4.5
  floor_days: 2.5
  ceiling_days: 7.0
---

# Team-Lead Feasibility Check — Feature 373: Adopter Install + Output Fidelity Fixes

**Verdict**: APPROVED_WITH_CONCERNS · **FEASIBLE WITH MODIFICATIONS**. This is one bundle and one PR, with a K1/K2 cut line and a mechanical split valve.
**Estimate**: planning **4.5** · floor **2.5** · ceiling **7.0** eng-days · confidence **MEDIUM**
**Scope reviewed**: PRD-373 v1.0 (K1–K3, K9–K15, optional #370). Every `file:line` pointer was re-verified at `63438d7` (v4.48.0).
**Lenses**: Constraint Analysis (§12) and Systems Thinking (the file-ownership map, §5)
**Vetoes**: Timeline veto and capacity veto are both **not exercised**.
**Concerns**: 9 in total (2 HIGH, 4 MEDIUM, 3 LOW). Each one resolves as either a PRD text fold-in or a plan-stage ruling. None blocks Define exit.

---

## 1. Verdict

One bundle is realistic. Four facts support this:
- Root causes are known.
- Every pointer re-verifies at HEAD.
- The deterministic Group B surface starts from a green pre-state.
- The riskiest audit in the PRD (R-3, the `parse_markdown_table` stop rule) measured behavior-neutral across the whole example and fixture corpus (§4).

Total effort is about **6.0 eng-days**, spread across three lanes that don't share files once the ownership corrections in §5 are applied. That compresses to about **4.5 attention-days from branch to merge**.

"With modifications" means four things have to change before `/aod.tasks`:
1. K1/K2 needs a structural guarantee (a cut line plus an escape hatch), not only a split valve (C-1).
2. The overlap map in PRD §10 is incomplete (C-2).
3. The "six templates" premise behind K14 and K15 does not hold for the executive-architecture template (C-3).
4. Group B's regression oracle and golden-regen policy must be chosen up front (C-4).

---

## 2. Estimate (engineering-days)

**Unit.** An eng-day here is an attention-day at the AOD agent-orchestrated pace, measured from branch to merge. That is the same unit the precedent checks were scored against in their `delivery.md` records.

| Band | Days | Conditions |
|---|---|---|
| **floor** | **2.5** | The split valve fires for K11, K13-posture and K15 at `/aod.tasks`, and #370 is dropped. K3 converges on its first 2-OS CI cycle. What ships: K1–K3, K9, K10, K12, K13 (recommendations, MAESTRO, placeholder) and K14 with its one live render. |
| **planning (central)** | **4.5** | All ten items plus #370 are in. The plan closes OQ-1..OQ-5 and P-1..P-4 (§9) in one pass. K3 needs one CI fix-forward, K15 needs one prompt iteration, and golden regen touches at most 2 files. |
| **ceiling** | **7.0** | Everything is in and grows:<br>• K3's pre-flight widens to every destination file, adds dangling-link handling, and needs 2 extra macOS CI cycles.<br>• K15 needs 2 re-render iterations plus a debate over the FR-212-6 lock.<br>• K11's width rule gets redesigned once.<br>• OQ-3 drifts all five goldens.<br>• A third build session is needed. |

`floor ≤ planning ≤ ceiling` holds: 2.5 ≤ 4.5 ≤ 7.0.

**Why confidence is MEDIUM.**
- Higher for: Groups A and B (known roots, a green pre-state, R-3 measured, the K2 set measured).
- Lower for: three items with new logic (the K3 pre-flight, the K11 width rule, K13 posture unification). K15 cannot be verified deterministically. And there is no existing installer test harness to build on.

**Effort vs duration.** Bottom-up effort is **6.0 / 3.45 / 9.8** eng-days (central / floor / ceiling, §3). Three parallel lanes compress this by roughly 0.71–0.75×. The compression is capped because about 1.3 days of the central estimate is attention-bound and serial: plan rulings, oracle and golden review, visual checks of the live renders, checkpoints, and deliver.

**Calibration basis** (branch → merge, from the delivery records):

| Feature | Estimate (floor / central / ceiling) | Actual | Reading |
|---|---|---|---|
| F-281 | 1.0 / 2.0 / 3.0 | same day | small, reuse-heavy items land at or below the floor |
| F-338 | 1 / 2 / 3 | ~1 day | same |
| F-329 | 1.0 / 1.5 / 3.0 | same day | a new CI guard, still at the floor |
| F-217 | 0.5 / 1.0 / — | 1 day | on target |
| F-302 | 1–2 | ~2 days | scripts + gated tests + wiring: on target |
| F-362 | 4.0 / 4.9 / 6.0 (re-issued) | 6 days | the only multi-lane bundle: +22% over central, at the band ceiling |

#373 falls between F-302 and F-362 in shape. It is roughly 70–75% of F-362's effort: about a third of the file surface, but more new logic and a non-deterministic live verification. The small-item precedents argue against padding. The F-362 overrun argues against going below 4.5.

**ICE.** Effort 6 is consistent with a 4.5-day central, so no re-score is needed.

---

## 3. Per-item budget (bottom-up effort, eng-days)

| Item | Central | Floor | Ceiling | Dominant driver |
|---|---|---|---|---|
| K1 | 0.10 | 0.10 | 0.10 | 3 block lines, the 18→21 prose counts, 3 agent-table rows (all three rows confirmed missing) |
| K2 | 0.40 | 0.40 | 0.50 | completeness test (4 globs, invocation regex, transitive-import scan, negative cases), README manual block, CI wiring |
| K3 | 1.00 | 0.80 | 1.75 | **no test invokes `install.sh` today, so a new harness is needed**; bash 3.2 and BSD/GNU portability; pre-flight granularity (P-3); ~25-min CI loop |
| K9 | 0.25 | 0.25 | 0.40 | column aliases + level-aware stop; R-3 measured neutral (§4 E-2) |
| K10 | 0.10 | 0.10 | 0.10 | two regexes + a `###` fixture |
| K11 | 0.80 | — (carved) | 1.30 | the controls parser must newly emit per-row `Inherent Score`; volume/severity mix; deterministic widths; template + skill text; funnel golden |
| K12 | 0.30 | 0.30 | 0.40 | move the merge helper into the shared module; placeholder filter; baseline fixture |
| K13 recommendations / MAESTRO / placeholder | 0.20 | 0.20 | 0.30 | join to the threats.md mitigation, plus a warning (MAESTRO comes via K10, placeholder via K12) |
| K13 posture | 0.40 | — (carved) | 0.60 | OQ-3 sets the golden blast radius (1 vs 5 files); `cover.typ` + `main.typ`; 4 infographic text surfaces |
| #370 | 0.15 | — (dropped) | 0.25 | recipe confirmed: 2 test cases + 2 docstring notes, no behavior change |
| K14 | 0.35 | 0.35 | 0.50 | 5 config blocks + the missing 6th (P-1) + static contract test + 1 live render |
| K15 | 0.60 | — (carved) | 1.35 | 6 prompt surfaces including a locked block (P-2); allow-lists (OQ-4); 6 renders; at most 2 iterations |
| **Items subtotal** | **4.65** | **2.50** | **7.55** | |
| Plan stage (spec/plan/tasks + triple sign-off; OQ-1..5, P-1..P-4) | 0.40 | 0.30 | 0.60 | |
| W0 pre-state snapshot + synthetic fixture scaffolding | 0.15 | 0.10 | 0.20 | |
| Data-layer oracle + golden-regen review | 0.20 | 0.10 | 0.40 | |
| Integration CI (2-OS) + session handoffs | 0.20 | 0.15 | 0.50 | |
| Architect checkpoints + code review | 0.15 | 0.10 | 0.25 | |
| Deliver (release notes, CHANGELOG, docs, release check) | 0.25 | 0.20 | 0.30 | |
| **Effort total** | **6.00** | **3.45** | **9.80** | |
| **Duration, branch → merge** | **4.5** | **2.5** | **7.0** | |

---

## 4. Evidence gathered (read-only, at `63438d7`)

| # | Check | Result | Effect on estimate |
|---|---|---|---|
| E-1 | Ran the 10 Group B test modules in a scratch clone of HEAD | **204 pass / 2 skip / 6 fail** in 44 s. All 6 failures are the `test_backward_compatibility` byte-identity reds (#365, font-subset tag). | Group B starts green. The oracle is simple except on the PDF path (C-4). |
| E-2 | R-3 audit: simulated the level-aware stop rule against the current rule, for every caller header | Examples: 29 artifacts × 19 headers = **551 probes, 0 diffs**. Test fixtures: 87 files, **1,653 probes, 0 diffs**. Positive control (empty `###` band): old rule 1 row, new rule 0 rows. | R-3 drops to LOW, and K9 moves toward its floor. The rule must take its level from the *matched line*, because several callers pass header-less substrings. |
| E-3 | Installer test coverage | **No test invokes `scripts/install.sh`.** | K3 and SC-1 need a new harness, which makes K3 Group A's largest item. |
| E-4 | K2 required set (invocation scan of commands, agents, skills and templates, plus imports) | Invoked: 3 scripts. Imported by all three: `tachi_parsers.py`. That is exactly the four in FR-K2.1. Commands on disk: 6, all already in the block. | The completeness test goes green on the fixed manifest with no surprise additions. |
| E-5 | Gated CI duration (last 8 `tachi pytest` runs) | **22–29 min** from creation to completion. The job installs Python, pytest and pyyaml only: **no typst, no mmdc**. | About 25 minutes of feedback per push. Gated fixtures must avoid the mmdc render path (C-5). |
| E-6 | Frozen goldens `tests/scripts/fixtures/golden/*.json` | 5 files. `metadata.risk_posture` appears in **all five**. The funnel golden has all-zero reductions. | K11 drifts 1 file. K13-posture drifts 1 to 5 files, depending on OQ-3. |
| E-7 | PNG side effect | A single local run of those modules rewrote **36 tracked PNGs** (15 / 9 / 12 across three examples). During this review, a concurrent test run in the main working tree dirtied 15 of them there too, so the hazard is live, not hypothetical. | Never `git add -A`; stage explicit paths only; restore `examples/**/*.png` before every commit. |
| E-8 | Examples | Only `maestro-reference` has threats, risk scores, controls **and** a MAESTRO table at the top level. No example has a Resolved Findings section. One test-output directory has a drifted Section 4. | Do the live renders against a scratch copy of that example. K12 is verifiable on synthetic fixtures only, which is what NFR-1 intends. |
| E-9 | release-please `extra-files` | `README.md` and `scripts/install.sh` are listed (5 version markers). `fix:` is a visible changelog type. | K3's help and README edits must keep the markers (C-7). `fix(373)` does cut a patch release. |
| E-10 | Overlap with `tests/fixtures/init-baseline-tree/` | None: since F-250 it holds placeholder-bearing files only. | New gated tests trigger no fixture regen. |
| E-11 | Branch protection on `main` | No required status checks, no rulesets. | A dedicated workflow needs no protection change. |
| E-12 | Secret store | The "Gemini API Key" item is present (only the name was checked). | K14/K15 live renders are unblocked. |
| E-13 | #370 | 2 test cases + 2 docstring notes, no behavior change. | 0.15 d. It can drop out at no cost. |
| E-14 | Infographic template inventory | 5 files under `templates/tachi/infographics/` have a `## Gemini API Configuration` block. **executive-architecture has none.** It declares `page_aspect_ratio: "8.5:11"`, and its prompt is FR-212-6 verbatim-locked. | See C-3. |

---

## 5. Corrected file-ownership map (Systems Thinking)

PRD §10 lists two overlaps. Measured at HEAD, there are four overlap clusters:

| Shared file(s) | Items that edit it | Owner rule |
|---|---|---|
| `scripts/tachi_parsers.py` | K9, **K11** (per-row `Inherent Score` isn't parsed today), K12, K13 (posture function) | single owner, W1, sequential commits |
| `scripts/extract-infographic-data.py` | K10, K11, K12, K13 posture | one owner per wave (B1 in W1 for K10, then B2a in W2) |
| `scripts/extract-report-data.py` | K10, K12 (helper moves out), K13 recommendations + posture, #370 | one owner per wave (B1 in W1 for K10, then B2b in W2) |
| `templates/tachi/infographics/infographic-baseball-card.md` | **K13** (badge; prompt line), K14 (config block), K15 (prompt block) | Lane C, single owner |
| `templates/tachi/infographics/infographic-risk-funnel.md` | K11 (tier blocks, width rule), K14, K15 | Lane C |
| `.claude/skills/tachi-infographics/references/gemini-prompt-construction.md` | **K13** (`:296`), K14 (`:252-256`), K15 (`:296-306`) | Lane C |
| `template-specific-formats.md`, `infographic-specifications.md`, `INFOGRAPHIC_TEMPLATES.md`, `executive-architecture.md` | K11; **K13**; **K13**; K15 | Lane C |
| `README.md` | K2 (manual block), K3 (flag docs) | Lane A: K2 in W1, then K3 in W2 |

**The rule.**
- **Lane B writes code and emits data.**
- **Lane C owns every infographic text surface**, including the K11 and K13 text, so each text file has exactly one writer.
- **Live renders come last**, because they consume both the extractor JSON and the template text.

---

## 6. Proposed wave structure and agent assignments

**Sessions.** The build runs at most 3 waves per session.
- Plan stage: its own session.
- Build Session 1: W0–W2.
- Build Session 2: W3–W4.
- Then `/aod.deliver`.

This follows the clean-session phasing practice, with a NEXT-SESSION handoff at the end of Session 1.

**W0 — Pre-state (single lane, ~0.15–0.25 d)**
- `senior-backend-engineer`: snapshot the data layer at a pinned SHA, in a scratch clone (never in place, because of E-7). The snapshot covers `report-data.typ` and the infographic JSON for every template and every example that has source artifacts.
- `tester`: scaffold the synthetic fixtures:
  - short-form controls headers with an empty Critical band;
  - `###` MAESTRO headings;
  - a baseline with known NEW / UPDATED / UNCHANGED / resolved counts plus one placeholder row;
  - a drifted Section 4;
  - symlink sandboxes: a linked directory, a linked parent of a file, a link above the project root, and a dangling link.

**W1 — Foundations (4 lanes, window ≈ 0.8 d)**
- **Lane A (the cut line):**
  - `senior-backend-engineer`: K1 + K2 (manifest block, prose, agent table, maintenance checklist, README manual block), plus the completeness test with its negative cases.
  - `devops`: the gating workflow, per OQ-2 (C-5).
  - **Commit green before W1 closes. From that commit on, K1/K2 can ship on its own.**
- **Lane A′ (K3 core):**
  - `devops`: the pre-flight, refusal, opt-in flag, trap warning, and `--help` (keeping the release-please markers).
  - `tester`: the installer harness:
    - `--source` sandboxes;
    - `--version` cases in a **local clone only** (never the working repo);
    - a forced restore failure via a test-only `git` PATH shim.
  - Iterate locally on `/bin/bash` 3.2.57, which matches CI's strict leg.
- **Lane B1:** `senior-backend-engineer` edits `tachi_parsers.py` in sequence:
  1. K9;
  2. K12 (merge helper + placeholder filter);
  3. K11 parser extension (`Inherent Score`, status-label normalization);
  4. K13 posture function.

  This lane also does the K10 regexes in both extractors.
- **Lane C1:**
  - `senior-backend-engineer`: K14 reference request body, the five config blocks, and the executive-architecture config (P-1).
  - `tester`: the static contract test.

**W2 — Consumers and text (4 lanes, window ≈ 0.8 d)**
- **Lane A:**
  - `devops`: K3 README documentation and CI convergence on both OS legs.
  - `security-analyst`: advisory review of the pre-flight and refusal path (deny-by-default; no delete before the check).
- **Lane B2a:** `senior-backend-engineer` edits `extract-infographic-data.py`:
  - the K11 funnel (volume, severity mix, deterministic widths, volume-based reductions, the totals-vs-rows warning);
  - K12 wiring;
  - K13 posture emission.
- **Lane B2b:** `senior-backend-engineer` edits `extract-report-data.py`, `cover.typ` and `main.typ`:
  - the K13 recommendations fallback and its warning;
  - posture emission;
  - #370.
- **Lane C2:** `senior-backend-engineer` edits every infographic text surface:
  - K11 tier text and width rule;
  - K13 badge, prompt, spec and placeholder text;
  - K15 hardening, including the locked-block amendment per P-2;
  - the per-template allow-lists (OQ-4).
- `tester`: K9–K13 regression tests on the W0 fixtures. These can start in W1, test-first per Principle VI.
- **Architect checkpoint (P0, end of W2):** parser semantics, golden-regen authorization by file name, and attribution of every data-layer diff. Then the NEXT-SESSION handoff and the TW-7 check.

**W3 — Integration and live verification (window ≈ 0.5 d)**
- `devops`: commit, push, and get both CI legs green (fix forward as needed).
- `senior-backend-engineer`:
  - golden regen, for the authorized files only;
  - the data-layer diff against the W0 snapshot, with every diff attributed to a K-item.
- `tester`: live renders in a scratch copy of `examples/maestro-reference/`:
  - 1 render for K14, then 6 for K15 (all six template images there are tracked, so never render in place);
  - the API key goes from the secret store into the process environment only;
  - record status and a visual check in the PR;
  - at most 2 prompt iterations (TW-5).
- `ux-ui-designer`: optional advisory read of the six images.
- `code-reviewer`: full-diff review.
- Architect checkpoint.

**W4 — Close-out (~0.25 d)**
- `senior-backend-engineer`: README and install docs sweep.
- `product-manager`: release-notes text (the K1 re-run notice, the D-1 flag note, generic wording per NFR-6).
- Confirm the PR title is `fix(373): …`.

**Load check.** This uses the F-362 model, where window = pacing lane × 1.25.
- The pacing lanes sit at 80% by construction: B1/A′ in W1, B2a in W2, and the tester's renders in W3.
- Every other lane sits at roughly 20–70%.
- No agent instance exceeds 80%.
- `senior-backend-engineer` runs up to three instances at once in W2. That is safe only because §5 keeps their files disjoint.

The product agents (such as the infographic agent) are the subject under test in W3, not assignees.

---

## 7. Split valve and trip-wires

K1/K2 gets two layers of protection.

**Layer 1: the cut line (structural).** K1/K2, its completeness test and the gating workflow are committed green in W1, before any other lane's work lands. From that commit on, the bundle can be cut at any wave boundary without holding K1/K2.

**Layer 2: the trip-wires (mechanical).**

*At `/aod.tasks` (the team-lead evaluates these during triple sign-off):*
- **TW-0, aggregate.** Compute the projected duration from tasks.md: the sum of each wave's pacing-lane estimate × 1.25, plus 1.0 d for plan and deliver. If it exceeds **5.5 d** (planning + 1.0), carve in this order until it is ≤ 5.5: **K15 → K11 → K13-posture.** K15 goes first because it has the highest variance, K11 second because it is the largest deterministic item, and K13-posture last because carving it saves the least.
- **TW-1, K11.** Carve it if plan.md hasn't pinned the width constants (minimum step, floor) and the Tier-3 formula, or if K11's tasks sum to more than **1.2 d** (1.5 × its budget).
- **TW-2, K13-posture.** Carve it if OQ-3 is still open, or if its tasks sum to more than **0.6 d**.
- **TW-3, K15.** Carve it if OQ-4 is still open, or if the architect hasn't ruled on P-2. A partial carve (executive-architecture only) is allowed.
- **TW-4, #370.** Drop it if its tasks exceed the recipe of 2 tests and 2 docstring notes.

*During the build (empirical):*
- **TW-5, K15 iterations.** Allow at most **2 prompt iterations** (no more than 13 renders beyond K14's one). If any template still shows a layout label or an ID that isn't in its legend, ship what has been hardened, record the residual per template, and file a follow-up (R-5).
- **TW-6, render availability.** If renders are blocked for more than **0.5 d** (key, quota or model availability), carve K15. K14 keeps its one render and retries next session.
- **TW-7, escape hatch.** At the end of Session 1, check two things: whether remaining projected work exceeds **2.0 d**, and whether any lane is more than **50%** over its budget. If either holds, ship **Group A** (K1/K2, plus K3 if it is green) as its own `fix(373)` PR first. If K3 is not in that PR, its release notes must tell adopters with a symlinked skills folder to replace the link before re-running (see C-1).

---

## 8. Dependencies and blockers

| Dependency | Status | Note |
|---|---|---|
| Secret store "Gemini API Key" | present (only the name was checked) | Load it into the process environment; never echo it; renders go to a scratch copy. |
| #374 (K4–K8) | `stage:discover`; #374 itself says #373 ships first | **No shared files** (agent definitions and output schemas vs. extractors and templates). One coupling: if #374 moves SARIF generation to deterministic scripts, the K2 completeness test will require those scripts, and the helper they import, in the manifest. Note this in #374's plan. |
| #370 | open; recipe confirmed | Folded in per D-4. |
| #364 | open; blocks the next minor release | So `fix(373)` produces a patch release. |
| #365 | open | The 6 byte-identity reds pre-exist. Don't regenerate PDF baselines. See the PNG side effect (E-7). |
| CI gate | present; 22–29 min per run; no required checks | See the OQ-2 recommendation in C-5. |
| Delivered foundations (F-066, F-302, F-311/F-315, F-212) | on `main` | Confirmed by the pointer checks. |
| Process hazards from past deliveries | known | Skip `create-new-feature.sh` in an orchestrated plan (it derives a divergent branch). Export `AOD_REPO` before filing any split-valve follow-up issues. Verify local `main` == `origin/main` before any deliver push. |

**Blockers: none.**

---

## 9. Concerns (ranked)

**C-1 (HIGH): protecting K1/K2 needs a cut line and an escape hatch, and K3 must ship with K1.**
- The split valve lists only K11, K13-posture and K15.
- K3 is the most likely cause of Group A delay, yet it is not a split candidate: there is no existing harness, it must work on bash 3.2 with both BSD and GNU tools, and each macOS CI loop takes about 25 minutes.
- K3 cannot simply be carved out either. K1's release note tells every installer adopter to re-run the installer. An adopter with a symlinked skills folder who re-runs before K3 ships gets exactly the write-through that K3 fixes.
- **Fold into PRD §10:** the W1 cut line, TW-7, and this coupling note.

**C-2 (HIGH): the overlap map in PRD §10 is incomplete.**
- K13-posture edits `infographic-baseball-card.md` and `gemini-prompt-construction.md`. K14 and K15 edit both of those files as well. K13-posture also edits `infographic-specifications.md` and `INFOGRAPHIC_TEMPLATES.md`.
- K11 also edits `tachi_parsers.py`, because the controls parser doesn't emit a per-row `Inherent Score` today. So all four Group B items share `tachi_parsers.py`, and three item groups share the infographic text files.
- **Fold into PRD §10:** the ownership map in §5 (Lane B writes code; Lane C owns all infographic text; live renders go last).

**C-3 (MEDIUM): K14 and K15 assume six config blocks and six editable prompt blocks, but only five exist.**
- executive-architecture has **no `## Gemini API Configuration` block**.
- It declares `page_aspect_ratio: "8.5:11"`, which doesn't match any of the standard ratio values the image API documents (for example 3:4 or 4:5). Verify this live.
- Its prompt is an **FR-212-6 verbatim-locked** block.
- Without plan rulings, K14 either ships a landscape executive image or gets the request rejected, and K15 edits a locked block without sanction.
- **Add these plan-stage items:**
  - **P-1**: give that template a config block with a supported portrait ratio.
  - **P-2**: sanction the lock amendment, or exclude that template from K15.
  - **P-4**: decide the fate of the templates' `image_size: "2K"`. Either remove it from the five blocks, or map it into the image config if the configured model accepts it. Otherwise output resolution may change silently.

**C-4 (MEDIUM): choose Group B's oracle up front.**
- `test_backward_compatibility` is already 6/6 red (#365), and #365 forbids regenerating its baselines. So it gives no signal on the K10, K12 and K13 PDF-path changes.
- The byte-frozen infographic goldens will drift on purpose: the funnel golden for K11, and 1 to 5 files for K13 depending on OQ-3.
- **The plan should:**
  - (a) take a data-layer snapshot at a pinned SHA (`report-data.typ` and the infographic JSON for every example), diff it after the build, and attribute every diff to a K-item;
  - (b) authorize golden regen by file name, with a reviewed diff;
  - (c) leave the PDF baselines alone.
- The plan should also state the PNG hazard (E-7): stage explicit paths and never use `git add -A`.

**C-5 (MEDIUM): CI cost, and NFR-7 contradicts OQ-2.**
- NFR-7's first bullet hard-codes `tachi-pytest.yml`, while OQ-2 leaves the location open.
- That job runs for 22–29 minutes. Widening its `paths:` to agents, skills, commands and templates would put a ~25-minute run on every future PR that touches them. #374, #364 and the #360/#361 candidates all do.
- **Team-lead recommendation for OQ-2:** a dedicated, lightweight, 2-OS workflow for the completeness, installer and extraction-fidelity modules.
  - It matches the repo's existing single-purpose workflows and the KB Entry 20 clone pattern.
  - It needs no branch-protection change (E-11).
- **Reword NFR-7** to "the gating workflow chosen at OQ-2".
- **Fixture constraint:** gated fixtures must carry no attack trees or chains, because mmdc isn't installed on the runners.

**C-6 (MEDIUM): K3's pre-flight granularity is not pinned (plan item P-3).**
- `cp -r` writes through symlinks nested anywhere under a copied directory, not only through the top-level manifest entry.
- The two options trade cost for coverage. Checking every destination file is thorough but costs more. Checking only the path components of each entry is cheap but misses nested links.
- A dangling link also needs a defined outcome. Today `mkdir -p` fails partway through the copy and leaves a partial install.
- This is K3's main ceiling driver, so rule on it at plan.
- The estimate assumes a test-only `git` PATH shim for the forced restore failure, with no test seam in production code.

**C-7 (LOW): keep the release-please markers.** `README.md` and `scripts/install.sh` are release-please extra-files, carrying 5 `x-release-please-version` markers between them. K3's `--help` and README edits must keep them, and any new example line that includes a version needs its own marker.

**C-8 (LOW): D-1 changes installer behavior in a patch release.** A symlinked destination now gets a refusal. Defer to the PM on whether `fix:` is the right classification; the release notes already call the change out.

**C-9 (LOW): live renders depend on preview model IDs** (a primary and a fallback). R-4 covers request-body drift but not model availability. TW-6 covers this. The reference should also record the model ID and date of the verified render, which R-4 already asks for.

---

## 10. Timeline and milestones (proposed for PRD §11)

This assumes the Plan stage starts on 2026-09-28, runs on consecutive working days, and follows clean-session phasing (plan / build Session 1 / build Session 2 / deliver).

| Milestone | Gate | Central | Floor | Ceiling |
|---|---|---|---|---|
| M1: Plan complete | spec + plan + tasks triple sign-off; OQ-1..5 and P-1..P-4 ruled; TW-0..TW-4 evaluated | 2026-09-28 | 2026-09-28 | 2026-09-29 |
| M2: Build Session 1 (W0–W2) | K1/K2 cut line green in W1; architect P0 checkpoint; NEXT-SESSION handoff; TW-7 check | 2026-09-30 | 2026-09-29 | 2026-10-01 |
| M3: Build Session 2 (W3–W4) | both CI legs green; live renders recorded; code review | 2026-10-01 | 2026-09-30 | 2026-10-05 |
| M4: Deliver | `fix(373)` squash-merge; patch release PR verified | **2026-10-02** | **2026-09-30** | **2026-10-06** |
| SC-7: live confirmation | the next large real-world run | lagging; tracked outside this feature | | |

---

## 11. Sign-off conditions for tasks.md

- Every task is mapped to an agent from the registry, and the lanes don't share files (§5).
- K1/K2, the completeness test and the gating workflow sit in W1 as the cut line. TW-0..TW-7 are written into tasks.md.
- P-1..P-4 and OQ-1..OQ-5 are closed in plan.md. Otherwise the matching item is carved under TW-1..TW-3.
- A W0 pre-state snapshot task exists, the golden files to regenerate are named, and no PDF baselines are regenerated.
- Live renders sit in the final build wave, run in a scratch copy, and keep the key in the process environment only.
- No agent instance exceeds 80% of its wave window. There are about 24–28 tasks, scoped by work bucket rather than by file.

---

## 12. Constraint Analysis (lens record)

- **Identify.** The binding constraint is **serial verification**, not agent capacity. It has three parts: ~25-minute 2-OS CI cycles, attention-bound reviews (plan rulings, golden and data-layer diffs), and non-deterministic live renders that need a human look. Three lanes that don't share files stay under 80% load.
- **Exploit.** Batch the verification: one CI cycle per session, all renders in one wave, one oracle diff.
- **Subordinate.** Every lane feeds the verification wave. Nothing renders before Group B lands.
- **Elevate.**
  - Iterate K3 locally on bash 3.2.57; the development host matches CI's strict leg.
  - Use a dedicated, fast workflow for the new modules (C-5).
  - Use synthetic fixtures that stay off the mmdc path.
- **Repeat.** After Session 1, TW-7 checks whether the constraint has moved.
