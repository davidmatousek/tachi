---
prd:
  number: 373
  topic: adopter-install-output-fidelity
  created: 2026-09-27
  status: Approved
  type: feature
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-09-27
    status: APPROVED
    notes: "v1.1: revised on the Triad review of v1.0 (architect CHANGES_REQUESTED, 0 BLOCKING / 4 HIGH / 10 MEDIUM / 9 LOW; team-lead APPROVED_WITH_CONCERNS, C-1..C-9). H1-H4 folded into D-1, D-2 and FR-K3/K11/K12/K14/K15; the five flagged technical inaccuracies corrected; M1-M4, M7, M10 and C-1..C-9 folded; L-items folded or carried to spec. PM rulings: M5 adopt (fallback on every Tier-1 run, 'Threat-model mitigation:' prefix, land before #364's re-key); M9 adopt (update the clone first; the D-1 note covers every destination component); C-8 keep fix:; M6 adopt (root-anchored path matcher); M8 option (a) (manifest-driven manual install). OQ-2..OQ-4 resolved; §10-§11 taken from feasibility-check.md. v1.0: authored via /aod.define from lead issue #373; decisions D-1 (K3), D-2 (K11), D-3 (K13), D-4 (#370)."
  architect_signoff:
    agent: architect
    date: 2026-09-27
    status: APPROVED_WITH_CONCERNS
    notes: "Iteration 2. v1.0 was CHANGES_REQUESTED (0 BLOCKING / 4 HIGH / 10 MEDIUM / 9 LOW; 5 technical inaccuracies against the constitution's <3). The v1.1 re-review resolved H1-H4 (D-2 one row set + inherent parse + tolerant status incl. Missing + clamp + row-derived reduction; FR-K12.4 4b|4c; K14 five blocks + executive-architecture 3:4 portrait + supported-ratio contract test; D-1 union checked set, pwd -P root, copies-only opt-in, dangling/looping refused, placement after the --version checkout) with 0 BLOCKING / 0 HIGH / 2 MEDIUM / 7 LOW new. Its 2 carried-over inaccuracies (the NFR-7 mmdc precedent and the §1 block date) are corrected in v1.2. Carry-forwards for /aod.plan are listed in §13: K15 prompt-scaffold contract (M-N2), CI wiring (M-N1/L-N5), D-1 source-tree refusal + looping-link test (L-N2), and row-rule precision (L-N1/L-N3/L-N4/L-N6). Full review: .aod/results/architect-373.md."
  techlead_signoff:
    agent: team-lead
    date: 2026-09-27
    status: APPROVED_WITH_CONCERNS
    notes: "FEASIBLE WITH MODIFICATIONS; neither the timeline veto nor the capacity veto was exercised. Estimate: planning 4.5 / floor 2.5 / ceiling 7.0 eng-days (branch to merge; bottom-up effort 6.0 / 3.45 / 9.8), confidence MEDIUM, calibrated against F-281/F-338/F-329/F-302/F-362. 9 concerns (2 HIGH, 4 MEDIUM, 3 LOW), all folded in v1.1: a K1/K2 cut line committed green in W1, a TW-7 escape hatch, and K3 shipping with K1 (C-1); a corrected file-ownership map (C-2); executive-architecture config/lock/image_size rulings (C-3); a Group B data-layer oracle and golden-regen by file name (C-4); a dedicated fast workflow instead of widening the 22-29 min gate (C-5); K3 pre-flight granularity (C-6); release-please markers (C-7); fix: for the D-1 behavior change (C-8, PM kept fix:); preview model availability (C-9). Trip-wires TW-0..TW-7 are in the feasibility check; the central estimate is re-tested at TW-0 because v1.1 adopts D-1's full checked set (priced in K3's ceiling band). Full review: specs/373-adopter-install-output-fidelity/feasibility-check.md."
source:
  idea_id: 373        # equals prd.number (GitHub Issue #373)
  story_id: null
bundle:
  lead: 373
  members: [K1, K2, K3, K9, K10, K11, K12, K13, K14, K15]
  companion: 374      # K4–K8, large-architecture pipeline resilience; order-independent
  split_valve_candidates: [K11, K13-posture, K15]
  coordinate: [370]
  release: "patch — PR titled fix(373); #364 blocks the next minor release"
---

# PRD-373 — Adopter Install + Output Fidelity Fixes

> **Bundle PRD.** Lead issue **#373** carries ten defects with stable IDs **K1–K3** and **K9–K15**. The companion bundle **#374** (K4–K8, large-architecture pipeline resilience) holds the design work. The two ship in either order, because this bundle's parsers accept both today's controls-table format and the one #374 K8 corrects. This bundle ships as a **patch release** (`fix(373):`), because #364 blocks the next minor release.
>
> **v1.1** folds in the Triad review of v1.0: the architect's findings (H1–H4 in full, plus five corrected technical inaccuracies), the team-lead's concerns (C-1–C-9) and estimate, and five PM rulings (§4, "v1.1 rulings"). Items marked *(v1.1)* are new or rewritten.

---

## 1. Problem Statement

Running the full stock pipeline (installer → threat model → risk score → controls → infographics → PDF) on a large real-world architecture (26 components, 200+ findings), plus a static review of the installer, surfaced ten defects with one theme: **what adopters install, and what the deterministic extraction and render layer produces, doesn't match what the pipeline actually needs or emits.**

1. **Incomplete installs since April.** The machine-parseable block in `INSTALL_MANIFEST.md` last changed on 2026-04-12 (the file itself last changed on 2026-04-14). Three skills added after that never joined it: `tachi-output-integrity` (2026-04-19), `tachi-misinformation` (2026-04-24) and `tachi-human-trust-exploitation` (2026-04-27). `scripts/populate-affected-assets.py` never joined it either. So every `install.sh` adopter since 2026-04-19 has run the output-integrity, misinformation and human-trust-exploitation agents **without their detection references** (OWASP LLM10:2026, LLM07:2026, ASI09:2026). Every installer-based adopter also lacks the deterministic Affected Assets populator that three pipeline steps invoke. The manifest has a maintenance checklist, but nothing enforces it, so the drift went unnoticed.
2. **An installer that writes where it wasn't asked to.** When `.claude/skills` is a symlink to a folder shared with other AI tools, the installer follows the link and writes tachi's skills into that shared folder with no warning. The same happens under any symlinked destination folder, and the deprecated-command cleanup *deletes* files through one. A failed `--version` ref restore is swallowed, which can leave the adopter's tachi clone detached at a tag.
3. **Reports that disagree with their own source artifacts.** As shipped, the infographic agent cannot render any image (HTTP 400). On the large run, residual bands, MAESTRO layers, the risk funnel, delta counts, recommendations and the posture label all reached the infographics and the PDF wrong or empty. A security lead could not have presented them without hand-correcting them.

Root causes are known for all ten defects, and several have more than one part. K12 has three: (a) the infographic counts delta status on findings that never carry it; (b) a placeholder row becomes a resolved finding; and (c) the parser looks for the resolved-findings heading at `## 4b.`, which the template moved to `## 4c.` (found at architect review; FR-K12.4). Every `file:line` pointer below was verified against `v4.48.0` (`63438d7`), the v1.1 additions included.

**Why now.** K1 affects every installer-based adopter today. The extraction layer is where tachi promises fidelity: the agent-authored artifacts are the source, and the deterministic scripts must reproduce them exactly. The next large real-world run also needs a release that contains these fixes.

---

## 2. Goals & Non-Goals

### Goals

- **G1 (K1, K2): installer completeness, enforced.** Every skill dir and every pipeline script ships, and CI fails when the manifest drifts.
- **G2 (K3): installer safety.** The installer never writes through a symlinked destination without the adopter's explicit consent, never deletes through one, and always restores the source repo's ref or says it couldn't.
- **G3 (K9–K13): extraction fidelity.** The infographic JSON and the PDF report data match the source artifacts.
- **G4 (K14, K15): a working render path.** The stock agent renders every template at its intended orientation, with no leaked prompt text and no wrong IDs.
- **G5: remediation reach.** The release notes tell affected adopters to update their tachi clone and re-run the installer.

### Non-Goals

- **NG1: agent-side output contracts.** The controls Section 2 column schema and the Section 4 recommendation-block contract belong to #374 K8. This bundle tolerates both formats and falls back where needed; it does not change what the agents write.
- **NG2: K4–K8.** These are in #374.
- **NG3: wiring `scripts/populate-maestro-coverage.py` into production.** It stays deliberately unwired; K10 only borrows its heading tolerance.
- **NG4: installer upgrade semantics.** Deleting stale files on upgrade is out of scope. The copy loop only adds files, and no distributable file has been deleted or renamed since v4.47.0.
- **NG5: regenerating tracked example PNGs or PDF baselines (#365), or re-keying examples and baselines (#364).** Infographic JSON goldens are regenerated only where the DoD's oracle authorizes them by file name.
- **NG6: visual redesign of any infographic template.** Only four things change: the funnel data contract (K11), the posture label (K13), the request configuration (K14) and the prompt hardening (K15).
- **NG7: committing real-world run output.** Tests use synthetic fixtures only.

---

## 3. User Stories

- **US-1 (adopter; K1, K2):** When I install tachi with `install.sh`, I want every skill and script that the commands and agents use, so that no threat agent runs without its detection references and no command step fails on a missing script.
- **US-2 (adopter with a shared folder; K3):** When my `.claude/skills` (or any folder tachi installs into) is a symlink to a folder shared with other AI tools, I want the installer to tell me exactly where tachi's files would go, write there only if I say so, and never delete anything there, so that it never silently changes a folder other tools read.
- **US-3 (security lead; K9–K13):** When I share tachi output, I want the infographics and the PDF to show the same numbers as the source artifacts (residual bands, MAESTRO layers, funnel, delta, recommendations and posture), so that I can present them without hand-correcting anything.
- **US-4 (adopter running `/tachi.infographic`; K14, K15):** When I run the infographic command, I want the stock agent to render every image at the right orientation, with no leaked prompt text and no wrong IDs, so that the images can be presented as generated.
- **US-5 (maintainer; K1/K2 guard):** When I add a skill or a pipeline script, I want CI to fail if I forget the install manifest, so that a K1-style omission can't ship silently again.

---

## 4. PRD Decisions

The lead issue delegates three behaviors to the PRD: K3, K11 and K13. A fourth decision covers the #370 fold-in. v1.1 tightens D-1 to D-3 after the Triad review and records five PM rulings on review items at the end of this section. Each decision below is binding for the spec. If any of them grows past its estimate, the split valve (§10) applies.

### D-1 (K3): symlinked destinations are refused unless the adopter opts in, and nothing is ever deleted through one

**Decision.**
- **The checked set** *(v1.1)*. Before any write or delete in the target project, the installer tests `[ -L ]` on every existing path in the union of:
  - every ancestor of each manifest entry, strictly below the project root;
  - the entry itself;
  - every path of the entry's source subtree, mapped into the target (the directory branch's `cp -r` writes all of them, `scripts/install.sh:192`);
  - the five deprecated-command cleanup paths (`:132-144`), which are deleted *before* the copy loop (`:184-212`) runs.

  The test is not gated on `[ -e ]`, which is false for a dangling link.
- **A canonical root** *(v1.1)*. The project root is resolved with `pwd -P`, and only components strictly below it are checked. A symlink above the root never trips the check: macOS's `/tmp → /private/tmp` or `/var → /private/var`, a symlinked home directory, or a project directory reached through a link. Resolved destinations are classified inside or outside the project against the physical root. The self-install guard (`:95`) compares the canonical `SOURCE_DIR` and root the same way.
- **Placement** *(v1.1)*. The pre-flight runs after the `--version` checkout (`:125`), because the destination set comes from the tagged manifest and source subtree, and before the cleanup (`:132`). A refusal exits through `die` and the existing EXIT trap (`:112-117`), which restores the ref, or warns that it couldn't (FR-K3.5).
- **Without the opt-in flag, the installer refuses:**
  - it names each symlinked component and its resolved destination;
  - it says whether that destination is inside or outside the project;
  - it states that nothing was written;
  - it names the two remedies: re-run with the flag, or replace the link with a real directory;
  - it exits non-zero, leaves the target project untouched, and puts the source repo back on its original ref.
- **With the opt-in flag** (working name `--follow-symlinks`; the final name is set at `/aod.plan`), the installer copies into the resolved destination on purpose. It names each resolved destination before copying, and again in the summary. **The flag authorizes copies only** *(v1.1)*: a cleanup path that resolves through a symlinked component is skipped and reported, never deleted.
- **Unresolvable links are always refused** *(v1.1)*. A dangling or looping link is refused with or without the flag, and the message reports its `readlink` text. Otherwise `mkdir -p` or `cp` would fail mid-copy and leave a partial install. *Optional, ruled at `/aod.plan`:* also refuse, regardless of the flag, any destination that resolves into the tachi source tree.

**Why.**
- The installer's footprint is the adopter's project. A symlinked destination belongs to something else: often a folder other AI tools read, sometimes one tracked in git, possibly one outside the repo.
- A warning printed after the copy (the issue's minimum) arrives after the write. The cleanup step *deletes* files, and no warning can undo a delete. The deprecated names (`threat-model.md`, `risk-score.md`, …) are generic, so in a shared folder they may belong to another tool. That is why even the flag never deletes.
- Checking only each entry's own path components would miss two cases. A pre-existing symlinked subdirectory inside a destination subtree aborts BSD `cp` mid-install today, which leaves a partial install under `set -euo pipefail` (`:21`). A leaf-file link is written through, because POSIX `cp` opens an existing destination for truncation.
- One flag costs a deliberate adopter seconds, while a surprise write into a shared or global folder is costly to notice and undo. Deny-by-default is also the posture a security tool should model.

**Alternatives considered.**
- **(a) Warn and proceed.** This meets the issue's minimum, but writes and deletes land before the adopter can react.
- **(b) Always install into the resolved target on purpose.** The outcome is the same as (a), under a different label.
- **(c) Proceed when the link resolves inside the repo, refuse when it resolves outside.** That is two policies to explain and test. And the in-repo shared folder is exactly the case US-2 says must not happen silently.
- **(d) Check only each manifest entry's own path components.** It is cheaper, but it misses nested and leaf-file links.

**Cost.** A refusal can trigger on any symlinked destination component: `.claude/` and its subfolders, `docs/`, `scripts/`, `templates/`, `schemas/`, `brand/` or `adapters/`, not only `.claude/skills`. Adopters with such a link who re-run the installer (as the K1 notice asks) will hit the refusal first. Its message names the flag, and the release notes say so too (R-1).

### D-2 (K11): the funnel narrows by risk volume, summed over one row set

**Decision.** The funnel sizes its tiers by **risk volume**, the sum of per-finding scores over **one row set**. Every tier carries its severity mix. The four tiers keep their names and their order:

| Tier | Meaning | Volume (4-tier mode) | Severity mix |
|---|---|---|---|
| 1 Threats Identified | The risk that was found | None. This tier counts findings and is the 100% anchor | Qualitative severity (threats.md) |
| 2 Inherent Risk Scored | The risk, measured | Σ inherent score | Inherent score bands |
| 3 Controls Applied | The risk left once fully effective controls are credited | Σ (residual if the row's control is found, else inherent) | Bands of those per-row scores |
| 4 Residual Risk | The risk left once all controls, full and partial, are credited | Σ residual | Residual bands |

- **One row set** *(v1.1)*. In 4-tier mode, Tiers 2–4 are all summed over the controls report's Section 2 rows. That is after the parser's first-occurrence dedup (`scripts/tachi_parsers.py:1169-1178`) and after phantom and placeholder rows are dropped (FR-K9.2). Summing Tier 2 over risk-scores rows and Tiers 3–4 over controls rows would book any row-set difference as control credit. The row sets diverge in exactly the large-run failure modes that #374 K6 and K7 describe.
  - `risk-scores.md` composites size Tier 2 only in 3-tier mode (no controls report). In 4-tier mode they only fill a controls row's missing inherent score, by ID join. The controls command requires risk-scores input (`.claude/commands/tachi.compensating-controls.md:53-66`), so the join source normally exists. A row with no inherent score even after the join is left out of all three volumes, with a warning.
  - The extractor warns when the controls row count differs from the risk-scores row count.
- **Per-row rules** *(v1.1)*.
  - The controls parser newly reads `Inherent Score` (alias `Inherent`). Today it emits no inherent score (`tachi_parsers.py:1147-1155`).
  - Control status is classified by the existing tolerant substring idiom (`tachi_parsers.py:1202-1208`), lifted into one shared helper: contains `partial` → partial; contains `found` and not `no` → found; otherwise → no control. An empty or unrecognized status counts as no control (inherent, no credit) and warns.
  - Residual is clamped to ≤ inherent on every row, with a warning. With one row set, the clamp makes V2 ≥ V3 ≥ V4 hold row by row, so no reduction is ever negative.
  - Tier 3 scores are banded with the standard thresholds 9.0 / 7.0 / 4.0 (`tachi_parsers.py:1108`).
- **Reductions.** Reductions are computed on volume between adjacent available tiers:
  - Tier 1 → 2 is 0% by definition, because scoring measures risk rather than reducing it.
  - Tier 2 → 3 is what fully effective controls remove.
  - Tier 3 → 4 is what partial controls remove.
  - Tier 2 → 4 is the overall reduction. *(v1.1)* The JSON's `risk_reduction`, which the sidebar shows, is this row-derived value whenever rows exist. The controls report's Section 1 figure is kept only as the comparand for a warning, so the sidebar and the annotations can't disagree.
- **Widths** are computed deterministically in the extraction layer, not by the agent, by the algorithm in FR-K11.5. Tiers 2–4 are sized against the Tier 2 volume, since Tiers 1 and 2 describe the same risk. The reduction annotations carry the exact numbers.
- **Counts** stay on every tier for its label. Widths and reductions use volume.
- **Degraded modes** keep today's template behavior (`templates/tachi/infographics/infographic-risk-funnel.md:118,145-147`). In 3-tier mode, Tier 3 shows "Unmitigated Risk" from the Tier 2 data and Tier 4 is a ghost tier. With threats.md alone, Tiers 2–4 are ghost tiers.

**Why.**
- Controls lower scores, not the number of findings. So a count-based funnel can never narrow, and that is the defect.
- The template already sizes tiers by `tier_volume` (`templates/tachi/infographics/infographic-risk-funnel.md:130`) and asks for a severity breakdown per tier (`:159`). The extractor never supplied either.
- Every number the table needs is already on each controls row: `Inherent Score`, `Control Status` and `Residual Score` (`templates/tachi/output-schemas/compensating-controls.md:81`). So the two drops split the report's own reduction rather than invent a new metric. Only the parser has to start reading `Inherent Score`.

**Alternatives considered.**
- **(a) Keep counts and add a severity mix.** The funnel still never narrows.
- **(b) Size Tier 3 by the count of findings that have a control.** This mixes units, and Tier 3 can come out narrower than Tier 4.
- **(c) Size Tier 3 at the residual.** It duplicates Tier 4.
- **(d) Keep sizing Tier 2 from risk-scores rows in 4-tier mode** (today's source, `infographic-risk-funnel.md:110`). Row-set drift would then show up as control credit.

### D-3 (K13): one posture rubric, where the highest band present sets the label

**Decision.**
- **The rubric.** The highest severity band present sets the label: `CRITICAL RISK`, `HIGH RISK`, `MODERATE RISK` or `LOW RISK`.
- **The counts it uses.** It runs on the same data-tier severity counts both extractors already select: residual counts when the controls report exists, else inherent composite, else qualitative.
- **One implementation, emitted as a level and a label** *(v1.1)*. A single function in the shared parser module computes two additive fields, emitted into both the infographic JSON and `report-data.typ`:
  - `risk_posture_level`: `critical` | `high` | `medium` | `low`;
  - `risk_posture_label`: `CRITICAL RISK` | `HIGH RISK` | `MODERATE RISK` | `LOW RISK`.

  The existing `risk_posture` sentence (`scripts/extract-infographic-data.py:625-636`, a required field in `schemas/infographic.yaml:51`) stays as supporting text.
- **Rendered verbatim, colored by level.** Every surface renders the label as-is and takes its color only from the level. The Typst cover no longer derives its own label (`templates/tachi/security-report/cover.typ:26-45`), and the image prompt no longer infers one from a sentence. The baseball card's third rubric, "Color matches highest severity with >20% of findings" (`templates/tachi/infographics/infographic-baseball-card.md:128`), is deleted.
- **Every consumer** *(v1.1)*:
  - the cover and its wiring in `templates/tachi/security-report/main.typ`;
  - the baseball card's badge (`infographic-baseball-card.md:125-129`) and prompt (`:201`);
  - the reference prompt (`.claude/skills/tachi-infographics/references/gemini-prompt-construction.md:296`);
  - the placeholders `{risk_posture}` and `{posture_color}` (`templates/tachi/infographics/INFOGRAPHIC_TEMPLATES.md:108-109`);
  - the spec reference (`.claude/skills/tachi-infographics/references/infographic-specifications.md:53,171`);
  - the agent's JSON contract (`.claude/agents/tachi/threat-infographic.md:206`) and the spec schema (`schemas/infographic.yaml:51`);
  - the Typst variable contract (`.claude/skills/tachi-report-assembly/references/typst-template-contract.md`), which documents the new variables.
- **Stale data fails loudly** *(v1.1)*. A `report-data.typ` generated before this change lacks the posture variables. The report reads them with `dictionary(report-data-module).at(...)`, following the `main.typ:111-120` precedent. When they are absent, it stops with an instruction to regenerate the data file. It does not re-derive the label, which would bring back a second rubric.

**Why.**
- It is the rubric the PDF already ships (`templates/tachi/security-report/cover.typ:35-45`), and it is deterministic.
- "The worst finding sets the level" is the conventional reading of a security report's overall rating.
- It covers all four bands. The baseball card's three-level badge (`{HIGH|MEDIUM|LOW}`, `templates/tachi/infographics/infographic-baseball-card.md:127`) cannot express Critical, which is part of how the surfaces diverged. Today the card receives a sentence (`scripts/extract-infographic-data.py:625-636`) and the image model picks the word.
- A level beside the label lets the cover pick its color without matching strings in Typst.

**Alternatives considered.**
- **(a) A proportional rubric** (the share of findings that are Critical or High). It needs thresholds with no evidence base.
- **(b) Keep both rubrics on a shared basis.** The story requires one label.
- **(c) Emit the label only.** Typst would then derive the color by string matching.

### D-4 (#370): fold in the FR-012b guard test as a separable P2 item

#370 adds a covering test for the FR-012b form-drift guard in `scripts/extract-report-data.py`, the file K10 and K13 also edit. The guard is `_warn_unmatched_attribution_refs` (`scripts/extract-report-data.py:1174`), a helper that precedes `classify_framework_items` (`:1210`), rather than code inside it as #370 says; the recipe is unaffected. That recipe is fully specified: two test cases, plus two docstring notes. It changes no behavior, which makes it trivial in the issue's sense. **Fold it in** if it stays within that recipe at `/aod.tasks`; otherwise leave #370 open. It can drop out without affecting anything else. If it is folded in, the PR also closes #370.

### v1.1 rulings on review items

The Triad review left five questions to the PM. Each ruling below is binding for the spec.

| Item | Ruling | Rationale |
|---|---|---|
| **M5:** reach of the K13.1 fallback | **Adopt.** The fallback runs on every Tier-1 run, not only drifted ones, and marks its provenance with a `Threat-model mitigation:` prefix. The PR records which example PDFs' data changes. No baseline is regenerated here, and this bundle lands before #364's re-key. | A conformant Section 4 covers only a subset of findings, so blank cells are today's conformant output too: up to 79 of 110 findings on a shipped example. The prefix keeps analyzer recommendations distinguishable from generic mitigations. Landing first lets #364 absorb the change instead of re-dirtying fresh baselines. |
| **M9:** release-note text | **Adopt.** Adopters update their tachi clone first (`git pull`, or `git fetch --tags` then `--version vX.Y.Z`), then re-run `install.sh`. The D-1 note covers every symlinked destination component, and R-1 widens to match. | `install.sh` copies from the local clone (`scripts/install.sh:57-58`), so a stale clone re-installs the old manifest. The tag check is local-only (`:119`), and tags are fetched only after copying (`:219`). |
| **C-8:** release type | **Keep `fix:`.** | D-1 corrects a safety defect (silent write-through and delete-through). #364 blocks minor releases anyway, and the release notes call out the behavior change. |
| **M6:** the K2 matcher | **Adopt** root-anchored path references (FR-K2.4), plus an `ast` import walk, a manifest reader that mirrors the installer's, and one end-to-end install. | It is a strict superset of the issue's invocation matcher and still excludes the `tests/scripts` mentions the issue names. Interpreter spellings already vary, and presence checks name scripts without invoking them. A miss silently recreates K1; a false positive fails loudly. |
| **M8:** manual install blocks | **Option (a).** Every enumerated manual block (the README's and both of the developer guide's) becomes "copy every path between the manifest markers", plus a short portable loop (FR-K2.2). | One contract leaves no drift surface. All three blocks have already drifted (no skills, no scripts, stale counts). Option (b) would keep three prose copies and make the test parse them. |

---

## 5. Functional Requirements

### Group A: Installer (`INSTALL_MANIFEST.md`, `scripts/install.sh`, `README.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`)

#### K1: the manifest omits three skills

- **FR-K1.1** — The machine-parseable block (`INSTALL_MANIFEST.md:92-126`) MUST list all 21 `.claude/skills/tachi-*` dirs, adding `tachi-output-integrity`, `tachi-misinformation` and `tachi-human-trust-exploitation`.
- **FR-K1.2** — The prose MUST match what ships:
  - "21 threat analysis agent definitions" (`:9`, which says 18 today);
  - "21 dirs" (`:16`, which says 18 today);
  - an agent table (`:36-57`) that gains the output-integrity, misinformation and human-trust-exploitation rows.
- **Acceptance:** a fresh `install.sh` into an empty project yields 21 skill dirs and 21 agent definitions.

#### K2: the manifest omits the populator, and the manual installs omit skills and scripts

- **FR-K2.1** — The block, both "3 Python files" notes (`:15`, `:61`) and the script table MUST cover the four distributable scripts: `extract-report-data.py`, `extract-infographic-data.py`, `tachi_parsers.py` and `populate-affected-assets.py`. The four are self-contained: the populator imports only `tachi_parsers`. *(v1.1)* In the same file, the dependency note (`:69`) says what is true (NFR-2), and the stale list of non-distributed scripts (`:73`) is replaced by the rule that every other file in `scripts/` is tachi-internal, so the list can't drift again.
- **FR-K2.2** *(v1.1, M8 option (a))* — Every manual install block MUST derive from the manifest instead of enumerating paths. That covers the README's "Manual install (alternative)" block (`README.md:130-156`) and both blocks in the developer guide (`docs/guides/DEVELOPER_GUIDE_TACHI.md:104-128` and `:1016-1025`, whose verify lines also carry stale counts).
  - Each block becomes "copy every path between the `BEGIN MANIFEST` and `END MANIFEST` markers in `INSTALL_MANIFEST.md`", plus a short loop that runs on bash 3.2 and on both userlands (NFR-3).
  - Each block states that the manual path skips the installer's symlink check (D-1).
  - The maintenance checklist item that asks for install-instruction edits (`INSTALL_MANIFEST.md:140`) is reworded to match.
- **FR-K2.3** — A new **manifest completeness test** (gated per NFR-7) MUST assert that the block contains:
  - (a) every `.claude/skills/tachi-*` dir;
  - (b) every `.claude/commands/tachi.*.md` file *(PRD addition)*;
  - (c) every `scripts/*.py` that a distributed command, agent, skill or template references (FR-K2.4);
  - (d) every local module those scripts import, transitively *(PRD addition)*.
- **FR-K2.4** *(v1.1, M6)* — The test MUST match root-anchored path references, `(?<![\w./-])scripts/[\w-]+\.py`, across commands, agents, skills and templates. It keeps an explicit, commented exclusion list and fails closed: a matched reference that is neither in the manifest nor on that list fails the test.
  - This is a strict superset of the issue's `python3 scripts/<name>.py` invocation matcher. Spellings already vary (`python scripts/…` at `.claude/agents/tachi/threat-infographic.md:166`), and presence checks name scripts without invoking them (`.claude/agents/tachi/report-assembler.md:125`, `threat-infographic.md:144`).
  - The `tests/scripts/test_pattern_*.py` mentions in `.claude/agents/tachi/orchestrator.md:632,758` must not count, and the anchor already excludes them. Scripts that nothing distributed references are not required: `populate-maestro-coverage.py`, the `generate-*-sarif.py` generators and the `check-*.py` CI tools.
  - For (d), the test walks the required scripts with `ast` for imports that resolve to `scripts/<name>.py`. The lazy `import yaml` (`scripts/extract-report-data.py:1119`) is not local, so it is ignored.
  - The test's manifest reader mirrors `parse_manifest` in `scripts/install.sh:156-177` exactly (exact markers, no stripping), and it asserts that no entry has leading or trailing whitespace.
  - One end-to-end case runs `install.sh` into an empty temp project and asserts that the required set exists. That proves SC-1 with the real parser.
- **FR-K2.5** — Removing any required entry from a copy of the block MUST turn the test red (negative cases).
- *Why (b) and (d).* Commands are the only other category that the block lists file by file. `tachi_parsers.py` is imported, not invoked, so without (d) the test would not require it, and a future helper module could go missing the same way. Each addition extends the same invariant by one glob or one `ast` walk. The architect review kept both.

#### K3: symlinked destinations and the `--version` ref restore

- **FR-K3.1** — The installer MUST run D-1's pre-flight over D-1's checked set, after the `--version` checkout and before any write or delete. The set covers:
  - both branches of the copy loop: the directory branch (`mkdir -p` at `scripts/install.sh:191`, and `cp -r` at `:192` with every path of the copied subtree) and the file branch (`:202-204`);
  - the deprecated-command cleanup (`:132-144`).
- **FR-K3.2** — The refusal path MUST behave as D-1 specifies:
  - it names every symlinked component and its resolved destination (inside or outside the physical project root), or its `readlink` text when the link can't be resolved;
  - it states that nothing was written and names the remedies;
  - it exits non-zero, with the target project untouched and the source ref restored;
  - *(v1.1)* dangling and looping links are refused even with the flag.
- **FR-K3.3** — The opt-in path MUST name each resolved destination before copying, and again in the summary. *(v1.1)* It copies only: a cleanup path that passes through a symlinked component is skipped and listed in the summary, never deleted.
- **FR-K3.4** — `--help` and the README install section MUST document the opt-in flag. *(v1.1)* Those edits keep the release-please version markers (`x-release-please-version` at `README.md:120,471` and `scripts/install.sh:13,19,43`), and any new example line that carries a version gets its own marker.
- **FR-K3.5** — The source repo MUST be back on its original ref (a branch name, or a SHA if it started detached) after:
  - a successful `--version` install;
  - a failing one;
  - a refusal.

  A failed restore (the EXIT trap at `:112-117`) MUST print a warning that names the original ref and the command that restores it. It must never be swallowed, as it is today (`:114` ends in `2>/dev/null || true`).
- **FR-K3.6** — Tests MUST cover the following, sandboxed and synthetic:
  - `.claude/skills → ../.agents/skills` is refused without the flag, with zero files written;
  - the same case installs with the flag, and the output names the resolved destination;
  - a file-branch case where a target's parent directory is a symlink;
  - *(v1.1)* a pre-existing symlinked subdirectory inside a destination `tachi-*` subtree, a leaf-file link, and a dangling link (refused even with the flag, with its `readlink` text reported);
  - *(v1.1)* the cleanup through a symlinked `.claude/commands`: refused without the flag; skipped and reported with it, and the shared folder's file survives;
  - a symlink above the project root doesn't trip the check; *(v1.1)* neither does running from a project directory reached through a link, where an in-project link is classified as inside;
  - an install with no symlinks is unchanged;
  - the ref is restored after success and after failure, and a forced restore failure prints the warning.

  *Harness (v1.1).* The `--version` cases build a throwaway source repo (git init, commit, tag) and never run against the live checkout. The forced restore failure uses a `git` shim on `PATH` that fails only the restore checkout, so production code gains no test seam.

### Group B: Extraction and report data (`scripts/tachi_parsers.py`, `scripts/extract-infographic-data.py`, `scripts/extract-report-data.py`)

#### K9: residual severity is mislabeled

- **FR-K9.1** — `parse_compensating_controls_md` (`scripts/tachi_parsers.py:1127,1131`) MUST read the residual score and residual severity from either form: the template's `Residual Score` / `Residual Severity`, or the short forms `Residual` / `Residual Sev.`. *(v1.1)* Headers are normalized before matching (casefold, strip a trailing `.`, collapse spaces), then mapped through one alias table: `Residual Score`/`Residual`, `Residual Severity`/`Residual Sev.`, `Inherent Score`/`Inherent` (K11) and `Control Status`/`Status`. The score-derived banding then runs on both forms.
- **FR-K9.2** *(v1.1, M1)* — `parse_markdown_table` (`scripts/tachi_parsers.py:205-207`) MUST stop scanning at the next heading of the same or higher level than the **matched line**, where the level is the count of leading `#` on that line. An empty `### Critical Residual Severity` section then returns `[]` instead of adopting the next band's table.
  - A match on a non-heading line keeps today's stop rule (the next `#` or `##` heading). Three callers match bold paragraph text by substring: `tachi_parsers.py:585` ("Risk Summary"), `:600` ("Severity Distribution") and `:1232` ("Coverage Distribution").
  - The function's 21 call sites span four files: `tachi_parsers.py`, both extractors, and a fourth consumer, `scripts/generate-risk-scores-sarif.py` (`:53`, `:139`), which passes only `##` headings. Existing `##` callers MUST be unaffected.
  - The controls parser skips rows whose `Threat ID` is empty or a placeholder, using the FR-K12.3 predicate. Today an empty last band placed directly before `### Summary Statistics` adopts the summary table and yields phantom findings with empty IDs, which can flip the posture (D-3) to `CRITICAL RISK`.
- **Acceptance:**
  - a fixture with an empty Critical band and short-form headers yields correct residual band counts;
  - *(v1.1)* an empty last band before Summary Statistics yields 0 phantom rows and correct totals;
  - *(v1.1)* regression cases pin the three substring callers;
  - the existing parser tests stay green.

#### K10: the MAESTRO layer distribution is empty

- **FR-K10.1** — Both extractors MUST match `^#{3,4}\s+Risk by MAESTRO Layer` (`scripts/extract-infographic-data.py:1502`, `scripts/extract-report-data.py:262`). The report path's `most_exposed_layer` (`:428-439`) follows from the same table.
  - The template stays at `####` (`templates/tachi/output-schemas/threats.md:598`).
  - `populate-maestro-coverage.py` is untouched.
- **Acceptance:** a `###` fixture yields the same layer distribution and most-exposed layer as the `####` form.

#### K11: the risk funnel doesn't narrow

- **FR-K11.1** — `compute_risk_funnel` (`scripts/extract-infographic-data.py:1340`, tiers built at `:1361-1402`) MUST implement D-2: every tier carries its count, volume and severity mix, and Tiers 2–4 are summed over D-2's one row set.
- **FR-K11.2** — `_compute_reduction_percentages` (`:1433-1467`) MUST compute on volume. No reduction is negative (D-2's clamp).
- **FR-K11.3** *(v1.1, H1)* — Volumes MUST follow D-2's per-row rules:
  - The controls parser emits each row's inherent score. A missing one is filled by ID join to the risk-scores composites (`parse_risk_scores_findings`, `tachi_parsers.py:925`); a row still without one is left out of the volumes, with a warning.
  - `Control Status` is classified by the shared tolerant helper, not by an exact-label table. The observed drift label for "No Control Found" is `Missing` (#374 K8), which the idiom already classifies as no control. An empty or unrecognized status counts as no control and warns.
  - Residual is clamped to ≤ inherent on every row, with a warning.
  - The controls report's Section 1 totals are only a comparand. If they disagree with the row sums beyond rounding (the #374 K7 symptom), the extractor warns and the rows win. The JSON's `risk_reduction`, which comes from Section 1 today (`extract-infographic-data.py:1412-1423`), becomes the row-derived Tier 2 → 4 value.
  - The extractor warns when the controls and risk-scores row counts differ.
- **FR-K11.4** — The funnel template's tier blocks and its Tier Width Calculation (`templates/tachi/infographics/infographic-risk-funnel.md:98-134`), plus the skill reference (`.claude/skills/tachi-infographics/references/template-specific-formats.md:62-69`), MUST define each tier's volume per D-2.
  - *(v1.1)* The template's Tier 2 data-source line (`:110`) states the one-row-set rule: controls rows in 4-tier mode, risk-scores rows in 3-tier mode.
  - The sidebar's stage-to-stage annotations MUST read the volume-based reductions, and its Risk Reduction reads the row-derived value.
  - *(v1.1)* The PDF's funnel caption (`templates/tachi/security-report/main.typ:292`) says that Tier 3 credits fully effective controls and Tier 4 adds partial ones.
- **FR-K11.5** *(PRD addition: a second root cause; algorithm v1.1, M2)* — The extraction layer MUST compute the tier widths deterministically and emit them per tier in the infographic JSON. They are carried into the funnel spec and the prompt's `{tier_N_data}` slots (the prompt block has no width slot today, `infographic-risk-funnel.md:208-215`), and the template renders them verbatim.
  - Today the agent applies the template's rule `tier_width = max(actual_width, previous_tier_width - 10)` (`:130-133`). That rule caps any drop at 10 points and allows a tier wider than the one above it. It contradicts its own comment ("Minimum 10% narrowing per tier"), and with equal counts it keeps every tier at full width. It also divides by `tier_1_volume`, which D-2 says has no volume, and it leaves ghost widths undefined (`:142`).
  - **The algorithm.** W1 = 100 and W2 = 100 − STEP. For k = 3 and 4: W_k = clamp(W2 · V_k / V2, lo = FLOOR + (4 − k) · STEP, hi = W_{k−1} − STEP). By construction every tier is at least STEP narrower than the one above and never below FLOOR, provided FLOOR + 3 · STEP ≤ 100.
  - If V2 = 0, widths fall back to the STEP cascade (W_k = W_{k−1} − STEP) with a warning. Ghost tiers use the same cascade.
  - STEP and FLOOR are pinned at `/aod.plan` (TW-1); today's template values are 10 and 10.
  - The spec states the tier-index mapping. JSON `tier` 0–3 are this PRD's Tiers 1–4 (`extract-infographic-data.py:1365-1398`), and neither is the data-source tier (1 = controls … 3 = threats).
- **Acceptance** (on a fixture with controls):
  - tier widths equal the FR-K11.5 algorithm's output;
  - reductions are non-zero where risk fell: Tier 2 → 3 when a found control exists, and Tier 3 → 4 when a partial one does;
  - every tier carries a severity breakdown;
  - the Tier 2 → 4 reduction equals the JSON's `risk_reduction`;
  - *(v1.1)* the fixture includes a `Missing` label, classified as no control. Warnings fire, and every reduction stays non-negative, for an unrecognized status, a residual above its inherent score, Section 1 totals that disagree with the rows, and a controls/risk-scores row-count mismatch.

#### K12: the infographic `delta_counts` is wrong

- **FR-K12.1** — `delta_counts` MUST equal the threats.md Section 7 delta column (NEW / UPDATED / UNCHANGED), counted through FR-K12.2's map, plus the real count of resolved rows. Today, `scripts/extract-infographic-data.py:2054` counts `delta_status` on Tier 1/2 findings, which never carry it.
- **FR-K12.2** *(v1.1, M3)* — One shared helper in the shared parser module, `delta_status_by_id`, MUST return `{id: status}` from the Section 7 Status column (`templates/tachi/output-schemas/threats.md:645-651`).
  - Both extractors count NEW, UPDATED and UNCHANGED from that map, which is exact by construction. The PDF path also uses it to badge findings.
  - The extractors warn when the map's ID set differs from the tier's finding IDs (the #374 K6/K7 case).
  - The PDF path's `_merge_delta_status` (`scripts/extract-report-data.py:1045`) stays importable from `extract-report-data.py`, because `tests/scripts/test_extractor_contract_fixes.py:242` calls it; otherwise that test changes in the same commit.
- **FR-K12.3** — Placeholder rows, whose ID is a dash or empty, MUST be skipped inside `parse_resolved_findings` (`scripts/tachi_parsers.py:662-681`), which both extractors already call. The predicate is shared only because the controls rows are a second consumer (FR-K9.2); no abstraction goes beyond it.
- **FR-K12.4** *(v1.1, H2)* — `parse_resolved_findings` MUST accept both the template's `## 4c. Resolved Findings` heading (`templates/tachi/output-schemas/threats.md:480`) and the legacy `## 4b.` form, e.g. `^##\s+4[bc]\.\s+Resolved Findings\s*$` (the K10 pattern class).
  - Today it searches only for `## 4b. Resolved Findings` (`tachi_parsers.py:668`). Schema 1.4 gave `4b` to Findings by Agentic Pattern (`threats.md:392`), so a template-conformant threats.md yields zero resolved findings on both surfaces.
  - The stale "Section 4b (Resolved Findings)" references at `.claude/skills/tachi-orchestration/references/output-schemas.md:275` and `.claude/agents/tachi/report-assembler.md:242` change to 4c.
- **Acceptance:**
  - a baseline fixture under the template's `## 4c.` heading, with known NEW, UPDATED, UNCHANGED and resolved counts plus one placeholder row, yields exact `delta_counts` in the infographic JSON and the same counts in the PDF data;
  - *(v1.1)* one legacy `## 4b.` case yields the same resolved count, and an ID-set mismatch warns. No test exercises `parse_resolved_findings` today.

#### K13: gaps in the PDF report data

- **FR-K13.1 (recommendations)** *(fallback reach: v1.1, PM ruling M5)* — `build_remediation_actions` (`scripts/extract-report-data.py:189-202`) MUST never render a blank recommendation.
  - Today the parser (`scripts/tachi_parsers.py:1085-1104`) recognizes only the template's per-finding blocks: `#### N. <ID> — …` followed by `**What to Implement**:` (`templates/tachi/output-schemas/compensating-controls.md:158-172`).
  - On every Tier-1 run, any finding without a joined recommendation falls back to its threats.md Section 7 mitigation, prefixed `Threat-model mitigation:`. A conformant Section 4 covers only a subset of findings, so this changes conformant output too.
  - If neither source has text, the cell shows an explicit placeholder, pinned in the spec, rather than an empty string. The `default: "--"` at `templates/tachi/security-report/remediation-roadmap.typ:309` covers only a missing key.
  - When controls Section 4 has content but zero recommendations join, the extractor warns; that is the drift signal.
  - A template-conformant Section 4 still populates the recommendations it covers.
- **FR-K13.2 (MAESTRO)** — The distribution and the most-exposed layer MUST be populated. This comes via FR-K10.1.
- **FR-K13.3 (placeholder)** — Resolved findings MUST contain no placeholder rows. This comes via FR-K12.3.
- **FR-K13.4 (posture)** *(v1.1)* — The extraction layer MUST implement D-3. One function in the shared parser module emits `risk_posture_level` and `risk_posture_label` into both `report-data.typ` and the infographic JSON. Every consumer D-3 lists renders the label verbatim and takes its color from the level, and a stale `report-data.typ` fails with a regenerate instruction.
- **Acceptance:**
  - a drifted Section 4 produces a warning plus prefixed fallback text; a conformant Section 4 populates its recommendations, and the findings it doesn't cover carry the prefixed fallback;
  - the MAESTRO fields are populated;
  - no placeholder rows appear;
  - given the same run directory and data tier, the cover and the baseball card show the identical label and severity color;
  - *(v1.1)* a `report-data.typ` without the posture variables fails with the regenerate message.
- **Coordination:** #370 per D-4.

### Group C: Render path (`.claude/skills/tachi-infographics/`, `templates/tachi/infographics/`)

#### K14: the Gemini request body is rejected (HTTP 400)

- **FR-K14.1** — The reference request body (`.claude/skills/tachi-infographics/references/gemini-prompt-construction.md:252-256`) MUST use the known-good form, which was verified live:
  - `generationConfig.responseModalities: ["TEXT","IMAGE"]`;
  - `generationConfig.imageConfig.aspectRatio`;
  - no top-level `aspectRatio`, and no `imageSize`.

  *(v1.1)* Dropping `imageSize` is a deliberate trade-off. The Gemini 3 image models accept `imageConfig.imageSize`, so the primary model now renders at its default size instead of the intended 2K; in exchange, one body stays valid across the whole fallback chain. The dead keys go: `image_size: "2K"` in all five template blocks, and `resolution: "2K"` in the reference (`:204`, described at `:209`). The reference also gains an explicit table mapping template keys to request-body fields, reconciles its default model (`:199`) with its fallback order (`:232`), and records the model ID and date of the verified render (R-4).
- **FR-K14.2** *(v1.1, H3)* — **Five** templates carry a `## Gemini API Configuration` block, all at `aspect_ratio: "16:9"`:
  - `templates/tachi/infographics/infographic-baseball-card.md:218`;
  - `infographic-maestro-heatmap.md:229`;
  - `infographic-maestro-stack.md:228`;
  - `infographic-risk-funnel.md:231`;
  - `infographic-system-architecture.md:419`.

  The agent maps their flat values into the request body, and the mapping MUST produce the known-good form for every template.
  - The sixth template, executive-architecture, has no such block. It is portrait at 8.5:11 (`.claude/skills/tachi-infographics/references/executive-architecture.md:3,101`; `schemas/infographic.yaml:195-196`; `.claude/agents/tachi/threat-infographic.md:264`), and that reaches the API only as prompt text. 8.5:11 is not a supported `aspectRatio`.
  - Executive-architecture MUST get an explicit request configuration, outside its locked prompt block, with `aspect_ratio: "3:4"`: the closest supported portrait ratio to 8.5:11 (about 0.773). Where the configuration lives is set at `/aod.plan` (P-1).
  - A static contract test MUST pin the reference body, the five blocks and the executive-architecture configuration against the known-good form. It asserts that every mapped `aspectRatio` is in the API's supported set (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9), and that executive-architecture is portrait.
- **FR-K14.3** — One live render on a tachi example MUST succeed. It runs in a scratch copy of the example, because the example's images are tracked. The API key is handled per NFR-5.

#### K15: rendered images leak prompt text

- **FR-K15.1** — The prompts MUST state that uppercase section labels are layout instructions, not text to render. That covers the reference (`gemini-prompt-construction.md:296-306`), the five template prompt blocks (e.g. `templates/tachi/infographics/infographic-baseball-card.md:201-209`) and the executive-architecture prompt.
  - *(v1.1, PM sanction)* The executive-architecture prompt is verbatim-locked by FR-212-6 (`executive-architecture.md:140-193`; lock rule at `gemini-prompt-construction.md:43`). This PRD sanctions one minimal, additive amendment inside the lock markers, limited to the two K15 instructions (this one and FR-K15.2). If the architect rules otherwise at `/aod.plan` (P-2), that one template is carved from K15 under TW-3 and the other five proceed.
- **FR-K15.2** *(v1.1: the source of the list, answering OQ-4)* — The prompts MUST list the exact strings allowed on the image, matching the legend, and MUST forbid any other ID. The extractor emits that allow-list per template; it already computes the finding-ID set (`scripts/extract-infographic-data.py:1893`). Templates that show component names list names instead of IDs. The prompt quotes the emitted list, rather than the agent transcribing IDs.
- **Acceptance:** one live render per template (all six, including the two MAESTRO templates; executive-architecture in portrait) shows no layout-label text, and every ID on it is in its allow-list and legend. The output is non-deterministic, so it's verified live, not by a unit test, within at most two prompt iterations (TW-5).

---

## 6. Interface Contract

- **Controls-table tolerance.**
  - K9 normalizes headers and maps one alias table (FR-K9.1). K11 classifies control status with one tolerant helper rather than an exact-label list (FR-K11.3).
  - #374 K8 makes the output-schema template the single Section 2 contract.
  - Neither bundle needs the other to land first.
- **Shared helpers**, all in `scripts/tachi_parsers.py` and pure stdlib:
  - `delta_status_by_id` (K12);
  - the placeholder-row predicate (K12, reused by K9's controls rows);
  - the control-status classifier (K11);
  - the posture level and label (K13).
- **Infographic JSON.** The additions are additive: per-tier volume, severity mix and width (K11); `risk_posture_level` and `risk_posture_label` beside the kept `risk_posture` sentence (K13); and the per-template allow-list (K15). `risk_reduction` becomes the row-derived value, which is one of the values the defects correct.
- **`report-data.typ`.** It gains the posture level and label, documented in the Typst variable contract. A stale file fails with a regenerate instruction instead of re-deriving the label.
- **Manifest.** The machine-parseable block remains the single install contract. The completeness test enforces it, and every manual install path copies from it (FR-K2.2).

---

## 7. Non-Functional Requirements

- **NFR-1: determinism and fixtures.** Every deterministic fix is proven on **synthetic fixtures only**. No real-world run output is ever committed.
- **NFR-2: stdlib-only at import** *(v1.1 wording)*. The four distributable scripts import only the standard library and `tachi_parsers` at module load (KB-037, enforced by `tests/scripts/test_pyyaml_deferred_import.py`). PyYAML is imported lazily for the PDF coverage-attestation page (`scripts/extract-report-data.py:1119`). The new shared helpers are pure stdlib, no dependency is added, and the four scripts stay self-contained.
- **NFR-3: shell portability.** Installer changes run on bash 3.2 (macOS `/bin/bash`) and on both GNU and BSD userlands. That rules out `mapfile`, associative arrays and `readlink -f`. `[ -L ]`, `cd -P` / `pwd -P` and plain `readlink` are the verified portable primitives.
- **NFR-4: compatibility.**
  - An install with no symlinks copies the same files as before.
  - The parsers accept both the current and the corrected formats.
  - Existing `##` callers of `parse_markdown_table` are unchanged.
  - Changes to the infographic JSON are additive, except for the values the defects themselves correct. The `risk_posture` sentence stays.
- **NFR-5: secrets** *(v1.1: handling rules)*. The Gemini API key goes from the secret store into the process environment only. Separate shell calls don't share environment, so it is loaded per command, or the render session runs under the secret store's runner. It is sent only as the `x-goog-api-key` header, never as a `?key=` query parameter, and never through verbose or trace output (`curl -v`, `--trace*`). It is never echoed, logged or committed.
- **NFR-6: public hygiene.** Issues, PRDs, specs, PRs and the CHANGELOG describe the defects generically. They carry no real-world findings, threat text, IDs or report content.
- **NFR-7: CI, with each module in its gating workflow** *(v1.1, resolves OQ-2)*.
  - **Completeness and extraction-fidelity modules** run in a new dedicated, fast workflow on pull requests and `push: [main]`. It follows the single-concern precedent of `tachi-maestro-coverage.yml` and `tachi-catalog-drift.yml`. Its `paths:` are broad, since the run takes seconds: `INSTALL_MANIFEST.md`, `.claude/skills/**`, `.claude/commands/tachi.*.md`, `.claude/agents/tachi/**`, `templates/tachi/**`, `scripts/*.py`, `scripts/install.sh` (for the end-to-end case), the tests, their fixtures and the workflow file.
  - **Installer (K3) tests** run on the existing 2-OS bash matrix in `.github/workflows/tachi-pytest.yml`: bash 3.2 with BSD tools on macOS, bash 5 with GNU tools on ubuntu. That matrix is NFR-3's gate. Its `paths:` gain only `scripts/install.sh`, the installer tests and their fixtures. Its trigger is not widened to agents, skills, commands or templates, because a run takes 22–29 minutes.
  - **The existing green parser and extractor modules are gated too**, because R-3's safety net relies on them. `test_tachi_parsers.py`, `test_extract_infographic_data.py` and `test_extractor_contract_fixes.py` are gated as they are. `test_extract_report_data.py` is gated on the bare runner, with only its five mmdc-dependent cases skipped when `shutil.which("mmdc")` finds nothing (the repo's skip-when-absent idiom, as `test_coverage_attestation.py` does for typst). No workflow installs mmdc, and adding one is out of scope; production still requires mmdc (ADR-022). *(v1.2: corrects v1.1, which cited `tachi-mmdc-preflight.yml` as an mmdc-installed precedent; that workflow asserts mmdc is absent.)* New report-path tests stay off the mmdc path (in-process, or fixtures without attack trees). The #365 byte-identity module (`test_backward_compatibility.py`) is not gated.
  - **Lock-step, per workflow.** Each module is added to its gating workflow's `paths:` list and invocation in the same commit, and `paths:` also names the source surfaces the tests guard (the F-302 and F-362 precedent). Branch protection on `main` requires no status checks, so a dedicated workflow gates exactly as much as `tachi-pytest.yml` does.
- **NFR-8: images stay out of the repo.** Re-rendered example PNGs are never committed (#365), and live-render images stay out of the repo. One local run of the extraction modules rewrites tracked PNGs, so commits stage explicit paths only (never `git add -A`), and `examples/**/*.png` is restored before each commit.

---

## 8. Definition of Done

- **Tests.**
  - Every deterministic fix (K1–K3, K9–K14) has a regression test built on synthetic fixtures.
  - Each test module is wired into its gating workflow's `paths:` and invocation in lock-step (NFR-7). *This departs from the issue's DoD, which names `tachi-pytest.yml` for every module. Both reviewers advised against widening that 22–29 minute job's trigger, and a dedicated workflow gates exactly as much.*
  - The gated suites clone the committed HEAD, so commit before running them. About 19 failures outside the gate pre-exist and are known; don't chase them.
- **Group B oracle** *(v1.1, C-4)*.
  - Before the build, snapshot the data layer at a pinned SHA, in a scratch clone: `report-data.typ` and the infographic JSON for every template and every example that has source artifacts.
  - After the build, diff the snapshot and attribute every diff to a K-item. The PR lists the examples whose data changed (M5).
  - Infographic goldens are regenerated only where they are authorized by file name, with a reviewed diff: the funnel golden for K11, the goldens that gain posture fields for K13, and all five scaffolded-template goldens for K15, whose prompt-scaffold text and allow-list field they embed *(v1.2, architect re-review M-N2)*.
  - PDF baselines are untouched (#365, #364).
- **Staging hygiene** *(v1.1)*. Stage explicit paths, never `git add -A`, and restore `examples/**/*.png` before each commit (NFR-8).
- **K14/K15.** One live render per template, in a scratch copy of a tachi example, is recorded in the PR. The record gives the status, a visual check (including executive-architecture's portrait orientation), and the model ID and date. The images are not committed.
- **PR title.** The PR is titled `fix(373): …` from the draft onward. If the plan stage opens the draft as `373: …`, retitle it. This makes the release a **patch release**; there is no `feat:`, because #364 blocks the next minor release (ruling C-8).
- **Release notes** *(v1.1: M9 wording)*. They say plainly:
  - **anyone who ran `install.sh` since 2026-04-19 received the output-integrity, misinformation and human-trust-exploitation agents without their skills. Update your tachi clone first (`git pull`, or `git fetch --tags` and then `install.sh --version vX.Y.Z`), then re-run `install.sh`;**
  - an install whose destination passes through a symlink, at any destination folder (for example `.claude/`, `docs/`, `scripts/`, `templates/`, `schemas/`, `brand/` or `adapters/`), now stops unless the opt-in flag is passed, and even with the flag the installer never deletes through a link (D-1);
  - the risk funnel now narrows by risk volume, and findings the controls report gives no recommendation for show the threat model's mitigation, marked `Threat-model mitigation:`.
- **Release markers** *(v1.1)*. `README.md` and `scripts/install.sh` keep their `x-release-please-version` markers (FR-K3.4).
- **Public text.** Issues, PRDs, PRs and the CHANGELOG describe the defects generically.
- **Live confirmation** on the next large real-world run, after the release. This is DoD step 3 (user validation), and it is tracked outside this issue.

---

## 9. Success Criteria

| # | Criterion | Baseline (v4.48.0) | Target |
|---|---|---|---|
| SC-1 | A fresh `install.sh` into an empty project | 21 agents, 18 skill dirs, 3 scripts | 21 agents, **21** skill dirs, **4** scripts |
| SC-2 | Manifest drift is caught | Nothing checks it | The gated completeness test is green on the fixed manifest and red on every negative case |
| SC-3 | Symlinked destination | Silent write-through and delete-through | Without the flag: 0 files written or deleted, and each link and its resolved destination named. With the flag: installed and named, with 0 files deleted through a link. A dangling link is refused either way. The ref is restored or a warning is printed |
| SC-4 | Extraction matches the sources (synthetic fixtures) | Residual Critical mislabeled; MAESTRO empty on `###`; flat funnel; wrong `delta_counts`; resolved findings missed under `4c`; placeholder row; blank recommendations; two posture rubrics | Correct residual band counts and 0 phantom rows; identical MAESTRO output at `###` and `####`; the funnel narrows by volume over one row set, with Tier 2 → 4 equal to `risk_reduction`; exact `delta_counts` under both `4b` and `4c`; 0 placeholder rows; 0 blank recommendations; one posture level and label on both surfaces |
| SC-5 | Live render | Every request fails with HTTP 400 | 6/6 templates render, executive-architecture in portrait; 0 leaked layout labels; every ID in its allow-list |
| SC-6 | Release | — | A `fix(373)` patch release whose notes carry the update-and-re-run notice and the D-1 behavior note |
| SC-7 | Live confirmation *(lagging; tracked outside this feature)* | — | The next large real-world run shows none of K1–K3 or K9–K15 |

---

## 10. Bundle & Split-Valve Strategy

*(v1.1)* v1.0 said the three groups touch disjoint files. They don't, and the lane plan follows from the real overlaps.

**Shared files** (measured at HEAD; `specs/373-adopter-install-output-fidelity/feasibility-check.md` §5):
- `scripts/tachi_parsers.py` is edited by K9, K11 (the controls parser must newly read `Inherent Score`), K12 and K13 (posture).
- The infographic text surfaces are edited by three items at once:
  - the baseball card and `gemini-prompt-construction.md`: K13 posture, K14 and K15;
  - the funnel template: K11, K14 and K15;
  - `template-specific-formats.md`, `infographic-specifications.md`, `INFOGRAPHIC_TEMPLATES.md` and `executive-architecture.md`: K11, K13 and K15.
- `README.md` is edited by K2 (the manual block) and K3 (the flag docs).
- Every group adds test modules to the CI workflows.

**Ownership.** Lanes follow files, not K-items, so each file has one writer per wave:

| Lane | Items | Owns | Risk |
|---|---|---|---|
| A: Installer | K1 and K2, then K3 | `INSTALL_MANIFEST.md`, `scripts/install.sh`, the README and developer-guide install sections, the completeness and installer tests | Low (K1/K2); Medium (K3: a new harness, shell portability) |
| B: Code and data | The code of K9–K13, plus #370 | `scripts/tachi_parsers.py` (a single owner, in sequence K9 → K12 → K11 → K13); each extractor (one owner per wave); `cover.typ` and `main.typ`; the K12 stale-reference fixes | Medium (the shared-helper refactor; R-3 measured neutral) |
| C: Infographic text | The text of K11 and K13, plus K14 and K15 | Every infographic text surface: `templates/tachi/infographics/`, `.claude/skills/tachi-infographics/`, the infographic agent and its schema | Low (K14); Medium (K15 is non-deterministic) |

- Lane B writes code and emits data. Lane C owns every infographic text surface, including K11's and K13's text.
- Live renders run last, because they consume both the extractor JSON and the template text.
- CI wiring is one final task per workflow.

**Split valve.** K1/K2 is the load-bearing, customer-urgent item, so it gets two layers of protection. The details live in `feasibility-check.md` §7.
- **The cut line.** K1/K2, its completeness test and its gating workflow are committed green in the first build wave, before any other lane's work lands. From that commit on, the bundle can be cut at any wave boundary without holding K1/K2 back.
- **K3 ships with K1.** K3 is not a split candidate. K1's notice tells every installer adopter to re-run, and an adopter with a symlinked destination who re-runs before K3 ships gets exactly the write-through K3 fixes. If K3 ever misses a cut, that release's notes tell such adopters to replace the link before re-running.
- **Trip-wires.** The team-lead evaluates five at `/aod.tasks`:
  - **TW-0, aggregate:** if the projected duration exceeds 5.5 days, carve K15, then K11, then K13-posture, until it fits;
  - **TW-1, K11:** carve it if the plan hasn't pinned STEP, FLOOR and the Tier-3 formula, or if K11's tasks exceed 1.2 days;
  - **TW-2, K13-posture:** carve it if OQ-3 reopens or its tasks exceed 0.6 days;
  - **TW-3, K15:** carve it if OQ-4 reopens or P-2 is unruled; a partial carve (executive-architecture only) is allowed;
  - **TW-4, #370:** drop it if it outgrows its recipe.

  Three more apply during the build:
  - **TW-5:** at most two K15 prompt iterations; any residual leakage becomes a follow-up issue (R-5);
  - **TW-6:** if renders are blocked for more than half a day, carve K15, and K14 keeps its one render;
  - **TW-7, the escape hatch:** at the end of build Session 1, if remaining work exceeds 2.0 days or any lane is more than 50% over budget, ship Lane A (K1/K2, plus K3 if it is green) as its own `fix(373)` PR first.
- v1.1 answers OQ-3 and OQ-4, so TW-2 and TW-3 now trip only on budget or on the P-2 ruling. #370 (D-4) can drop out at no cost.

---

## 11. Timeline & Milestones

Sized 1:1 from the team-lead's feasibility check (`specs/373-adopter-install-output-fidelity/feasibility-check.md`, verdict APPROVED_WITH_CONCERNS). An eng-day is an attention-day at the agent-orchestrated pace, measured from branch to merge.

| Band | Eng-days | Conditions |
|---|---|---|
| Floor | 2.5 | The split valve fires for K11, K13-posture and K15, and #370 is dropped. K3 converges on its first 2-OS CI cycle |
| **Planning (central)** | **4.5** | All ten items plus #370. K3 needs one CI fix-forward, and K15 needs one prompt iteration |
| Ceiling | 7.0 | Everything is in and grows: K3's full pre-flight plus extra macOS CI cycles; two K15 iterations and a debate over the FR-212-6 lock; one K11 width redesign; posture drift across all five goldens; a third build session |

**Confidence: MEDIUM.** It is higher for Groups A and B (known roots, a green pre-state, R-3 measured) and lower for the three items with new logic (the K3 pre-flight, the K11 widths, K13 posture) and for K15, which can't be verified deterministically. Bottom-up effort is 6.0 eng-days (floor 3.45, ceiling 9.8). Three lanes that share no files compress that to 4.5 days of duration. The binding constraint is serial verification: 2-OS CI cycles of about 25 minutes, attention-bound reviews, and live renders that need a human look.

| Milestone | Gate | Central | Floor | Ceiling |
|---|---|---|---|---|
| M1: Plan complete | spec + plan + tasks triple sign-off; the open plan rulings (§13) made; TW-0 to TW-4 evaluated | 2026-09-28 | 2026-09-28 | 2026-09-29 |
| M2: Build Session 1 (W0–W2) | the K1/K2 cut line green in W1; architect checkpoint; NEXT-SESSION handoff; TW-7 check | 2026-09-30 | 2026-09-29 | 2026-10-01 |
| M3: Build Session 2 (W3–W4) | both CI legs green; live renders recorded; code review | 2026-10-01 | 2026-09-30 | 2026-10-05 |
| **M4: Deliver** | `fix(373)` squash-merge; patch release PR verified | **2026-10-02** | **2026-09-30** | **2026-10-06** |
| SC-7: Live confirmation | the next large real-world run | lagging; tracked outside this feature | | |

*Scope note (v1.1).* v1.1 makes rulings the estimate expected the plan to make (OQ-2 to OQ-4, and the team-lead's P-3 and P-4). D-1's full checked set (subtree paths, dangling links) is the scope the estimate priced in K3's ceiling band (1.75 eng-days against 1.00 central), so the team-lead re-tests the central estimate at TW-0.

---

## 12. Dependencies

- **#374 (companion bundle, K4–K8).** It doesn't block this bundle, because the parsers here are tolerant (§6). *Coupling (v1.1):* if #374 moves SARIF generation into deterministic scripts, the K2 completeness test will require those scripts, and any helper they import, in the manifest. #374's plan should note this.
- **#370 (FR-012b guard test).** Same file as K10/K13; folded in per D-4.
- **#364.** It blocks the next minor release, which is why this bundle ships as `fix:`. *(v1.1)* This bundle lands before #364's re-key of the example baselines, so #364 absorbs the K13.1 fallback's data change (ruling M5).
- **#365.** Test runs re-render tracked example PNGs, and its byte-identity suite is already red. Don't commit the PNGs or regenerate the PDF baselines.
- **Delivered foundations:**
  - F-066: the installer, the manifest and `--version`;
  - F-302: `populate-affected-assets.py` and its callers;
  - F-311 and F-315: the MAESTRO outputs that K10 reads;
  - F-212: the executive-architecture template and its FR-212-6 prompt lock.
- **Secret store.** The "Gemini API Key" item, for the K14/K15 live renders.

---

## 13. Risks & Open Questions

### Risks

- **R-1: refusal friction (D-1)** *(v1.1: widened)*. A refusal can trigger on any symlinked destination component, not only `.claude/skills`. An adopter with a linked `.claude/`, `docs/`, `scripts/`, `templates/`, `schemas/`, `brand/` or `adapters/` folder who re-runs the installer per the K1 notice will be refused on the first try. *Mitigation:* the message names each link and gives the exact re-run command, and the release notes list the folders.
- **R-2: the funnel's meaning changes (D-2).** Readers of earlier reports saw count-based tiers. *Mitigation:* tier labels keep their counts, the annotations say "risk volume", the template text defines each tier, and the PDF caption changes with it (FR-K11.4).
- **R-3: `parse_markdown_table` scope (K9)** *(v1.1: now LOW)*. The audit of all 21 call sites is done. A simulation of the level-aware rule found 0 diffs across the shipped examples (551 probes) and the test fixtures (1,653 probes), while the positive control (an empty `###` band) went from 1 row to 0. *Mitigation:* the three substring callers keep today's rule, and the existing parser and extractor suites become gated (NFR-7).
- **R-4: the Gemini API drifts again (K14).** *Mitigation:* the known-good body is verified live at build, and the reference records the model ID and date it was verified on. The static contract test catches edits to the reference, but not upstream API changes. Model availability is covered by TW-6.
- **R-5: K15 is non-deterministic.** Prompt hardening lowers leakage but can't guarantee zero. *Mitigation:* one live render per template, at most two prompt iterations (TW-5), and any residual leakage becomes a follow-up issue via the split valve.
- **R-6: CI cost** *(v1.1: resolved by OQ-2)*. The broad triggers sit on a workflow that runs in seconds. The 22–29 minute matrix gains only the installer surface.
- **R-7: harness and hygiene hazards.** The gated harness clones the committed HEAD, and one local run of the extraction modules rewrote 36 tracked PNGs. *Mitigation:* commit before running, stage explicit paths (never `git add -A`), and restore `examples/**/*.png` before each commit.
- **R-8: the K13.1 fallback changes conformant report data** *(v1.1, ruling M5)*. Shipped examples go from up to 79 of 110 blank recommendations to none, so their report data changes. *Mitigation:* the prefix marks provenance, the PR lists the affected examples from the oracle diff, no baseline is regenerated here, and this bundle lands before #364's re-key.

### Open Questions

- **OQ-1 (`/aod.plan`):** the final name of the opt-in flag. The working name is `--follow-symlinks`, which the architect finds acceptable.
- **OQ-2: resolved (v1.1).** The completeness and extraction-fidelity modules run in a dedicated fast workflow, and the installer tests run on the `tachi-pytest.yml` bash matrix (NFR-7).
- **OQ-3: resolved (v1.1).** The fields are additive, `risk_posture_level` and `risk_posture_label`, and the `risk_posture` sentence stays as supporting text (D-3).
- **OQ-4: resolved (v1.1).** The extractor emits each template's allow-list, and templates that show component names list names (FR-K15.2).
- **OQ-5 (`/aod.tasks`):** confirm that the #370 fold-in stays within its recipe (D-4). The architect recommends folding it in.
- **Plan-stage rulings still open (v1.1):**
  - P-1: where executive-architecture's request configuration lives (its ratio is set at 3:4);
  - P-2: the architect's ruling on the sanctioned FR-212-6 amendment (otherwise, a TW-3 partial carve);
  - the funnel constants STEP and FLOOR (TW-1);
  - the explicit placeholder for a finding with no recommendation from either source (FR-K13.1);
  - whether D-1 also refuses destinations that resolve into the tachi source tree. The architect's re-review recommends making it required, regardless of the flag. BSD and GNU `cp` both abort on a destination that resolves into the source ("identical" / "same file"), which leaves a partial install under `set -e`.

**Architect re-review carry-forwards (v1.2, for `/aod.plan`).** These come from the v1.1 re-review, APPROVED_WITH_CONCERNS. None changes a decision; each becomes an explicit FR or acceptance case in `spec.md`:

1. **K15 prompt-scaffold contract (M-N2).**
   - K15's hardening text lands in the verbatim preamble or postamble.
   - The split markers that `extract_prompt_scaffold` depends on (`scripts/extract-infographic-data.py:102-198`: a line starting `DATA CONTENT`, and `FOOTER`) are preserved, or the splitter changes in the same wave. This is a Lane C → Lane B coupling.
   - The FR-K15.2 allow-list is quoted in the DATA CONTENT region.
   - The K14 static contract test asserts that the scaffold is found for all five scaffolded templates.
2. **CI wiring (M-N1, L-N5).**
   - The mmdc cases are skipped when mmdc is absent (NFR-7).
   - The new workflow's `paths:` adds `examples/**` and `tests/scripts/conftest.py`.
   - FR-K2.4's scan globs are pinned to the distributed set: `.claude/commands/tachi.*.md`, `.claude/agents/tachi/**`, `.claude/skills/tachi-*/**` and `templates/tachi/**`. That keeps AOD-internal skill references out of scope.
   - Optionally, the K3 tests invoke `/bin/bash` explicitly, so a runner-image change can't silently move the strict leg off bash 3.2.
3. **D-1 rulings (L-N2).**
   - Rule on the source-tree refusal above.
   - Add a looping-link test case.
   - Settle OQ-1.
4. **Row-rule precision (L-N1, L-N3, L-N4, L-N6).**
   - **Clamp once.** Clamp residual ≤ inherent once, inside `parse_compensating_controls_md`, so the posture counts equal the funnel's Tier-4 mix.
   - **Status classifier.** The classifier recognizes an explicit no-control set (`No Control Found`, `Missing`, `None`, `Not Found`), uses whole-token negation, and warns on anything else. Both call sites (`tachi_parsers.py:1202-1208` and `:1244`) use the one helper.
   - **Header match.** One regex-capable header match serves both K10 and FR-K12.4.
   - **The 4b → 4c fix.** FR-K12.4's edit becomes a grep-driven sweep of every "Section 4b" reference that means Resolved Findings. That includes `templates/tachi/output-schemas/threat-report.md`, the parser docstring, an extractor comment and the architecture README.
   - **Typst contract.** Lane B owns `typst-template-contract.md`. It marks the posture variables REQUIRED, with no default, and the report-assembler's inline-extraction fallback must emit both.

---

## 14. References

- **Lead issue:** [#373](https://github.com/davidmatousek/tachi/issues/373)
- **Companion:** [#374](https://github.com/davidmatousek/tachi/issues/374)
- **Related:** [#370](https://github.com/davidmatousek/tachi/issues/370), [#364](https://github.com/davidmatousek/tachi/issues/364), [#365](https://github.com/davidmatousek/tachi/issues/365)
- **Triad:** `specs/373-adopter-install-output-fidelity/feasibility-check.md` (estimate, trip-wires, ownership map)
- **Installer:**
  - `INSTALL_MANIFEST.md`
  - `scripts/install.sh`
  - `README.md` (Install, Manual install)
  - `docs/guides/DEVELOPER_GUIDE_TACHI.md` (the two manual install blocks)
  - PRD-066 (`066-install-script-and-version-tagging-2026-04-06.md`)
- **Extraction:**
  - `scripts/tachi_parsers.py`
  - `scripts/extract-infographic-data.py`
  - `scripts/extract-report-data.py`
  - `scripts/generate-risk-scores-sarif.py` (the fourth `parse_markdown_table` consumer)
  - `scripts/populate-maestro-coverage.py` (heading-tolerance precedent)
- **Templates:**
  - `templates/tachi/output-schemas/{threats,compensating-controls}.md`
  - `templates/tachi/infographics/infographic-{risk-funnel,baseball-card}.md` and `INFOGRAPHIC_TEMPLATES.md`
  - `templates/tachi/security-report/{cover,main,remediation-roadmap}.typ`
- **Render:**
  - `.claude/skills/tachi-infographics/references/{gemini-prompt-construction,template-specific-formats,infographic-specifications,executive-architecture}.md`
  - `.claude/agents/tachi/threat-infographic.md`, `schemas/infographic.yaml`
  - `.claude/skills/tachi-report-assembly/references/typst-template-contract.md`
- **CI:**
  - `.github/workflows/tachi-pytest.yml` (the installer tests on the bash matrix)
  - a new dedicated workflow (completeness and extraction fidelity)
  - precedents for dedicated single-runner jobs: `tachi-maestro-coverage.yml`, `tachi-catalog-drift.yml`

---

## Approval & Sign-Off

| Role | Agent | Status | Date | Notes |
|------|-------|--------|------|-------|
| Product Manager | product-manager | ✅ APPROVED | 2026-09-27 | v1.1: Triad review folded; M5, M9, C-8, M6 and M8 ruled |
| Architect | architect | 🟡 APPROVED_WITH_CONCERNS | 2026-09-27 | Iteration 2: H1–H4 resolved; 0 BLOCKING / 0 HIGH new; carry-forwards in §13 |
| Team-Lead | team-lead | 🟡 APPROVED_WITH_CONCERNS | 2026-09-27 | Feasible with modifications; 4.5 / 2.5 / 7.0 eng-days, MEDIUM confidence; C-1–C-9 folded |

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-09-27 | product-manager | Initial draft from lead issue #373 (K1–K3, K9–K15); decisions D-1–D-4 |
| 1.1 | 2026-09-27 | product-manager | Folded the Triad review: architect H1–H4 into D-1, D-2 and FR-K3/K11/K12/K14/K15, the five flagged inaccuracies corrected, M1–M4, M7, M10 and L1–L9 folded; team-lead C-1–C-9 (the §10 ownership map and split valve, §11 sized to the feasibility check, the NFR-7 CI split, the Group B oracle); PM rulings M5, M9, C-8, M6 and M8 (a); OQ-2 to OQ-4 resolved |
| 1.2 | 2026-09-27 | /aod.define orchestrator | After the architect's re-review (APPROVED_WITH_CONCERNS): corrected its two carried-over inaccuracies (the §1 manifest-block date, the NFR-7 mmdc precedent); added K15 to the DoD's golden-regen authorization; recorded the re-review carry-forwards in §13; recorded the architect and team-lead sign-offs; status Approved |
