---
prd_reference: docs/product/02_PRD/373-adopter-install-output-fidelity-2026-09-27.md
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-09-27
    status: APPROVED_WITH_CONCERNS
    notes: "Traces 1:1 to PRD v1.2. D-1..D-4 and M5/M9/C-8/M6/M8 are not re-argued, and NFR-6 hygiene passes. S-1..S-13, the FR-K14.2 mapping creation, SC-6 (published notes) and SC-8 (the baseball-card golden) are all ACCEPTED as inside G1-G5. S-6 narrows D-1's flag by D-1's own no-partial-install rationale. S-8's shutdown dates were verified, and US-4a P1 is accepted. 8 required changes (MEDIUM RC-1 DoD pointer + the M5 release-note bullet, RC-2 K14 doesn't bend the cut line, RC-3 a non-blocking 400 row; LOW RC-4..RC-8) were FOLDED 2026-09-27, along with R-a and R-c..R-g. R-b (W0 smoke render) goes to /aod.tasks. PM rulings P-9.1..P-9.5 are recorded in the spec. TW-0 note: the growth lands mostly on non-carvable items, and K14 is above its 0.50 ceiling, so re-cost bottom-up at /aod.tasks. The PM verifies the fold at /aod.project-plan. Details: .aod/results/product-manager-373-spec.md"
  architect_signoff: null  # Added by /aod.project-plan
  techlead_signoff: null   # Added by /aod.tasks
---

# Feature Specification: Adopter Install + Output Fidelity Fixes

**Feature Branch**: `373-adopter-install-output-fidelity`
**Created**: 2026-09-27
**Status**: Draft
**Input**: Bundle PRD `docs/product/02_PRD/373-adopter-install-output-fidelity-2026-09-27.md` (v1.2, Approved; PM ✓, Architect ⚠, Team-Lead ⚠). Lead issue **#373** carries ten defects: **K1–K3** (installer) and **K9–K15** (extraction, report data and render path). **#370** is folded in per D-4. The companion bundle **#374** (K4–K8) ships in either order. Research: [research.md](research.md). Estimate and trip-wires: [feasibility-check.md](feasibility-check.md).

> **Bundle spec.** This spec refines PRD-373 into testable requirements. It keeps the PRD's namespaced IDs (`FR-K1.1` and so on) for 1:1 traceability. Decisions D-1 to D-4 and the v1.1 PM rulings (M5, M9, C-8, M6, M8) are binding.
>
> The spec adds three things:
> - **Spec-stage rulings** (§ Rulings, S-1 to S-13): the ones the PRD left open (the flag's name, the source-tree refusal, the recommendation placeholder), plus those that research made necessary.
> - **The architect's v1.2 carry-forwards** (PRD §13), each as an explicit FR or acceptance case, marked *(carry-forward …)*.
> - **The plan-stage inputs** that belong to `plan.md`, registered as inputs rather than ambiguities.
>
> **Research changed three premises** (details in research.md, "PRD Corrections"):
> - **Every configured image model** is already shut down (the two preview models, 2026-06-25) or shuts down on **2026-10-02** (`gemini-2.5-flash-image`).
> - **No code reads the templates' Gemini configuration blocks**, so K14 must create that mapping.
> - **BSD `cp` cannot write through links nested in a copied directory**, so the opt-in flag cannot follow them.
>
> Each correction is resolved inside the PRD's goals (G2, G4) by a spec ruling. None reverses a PRD decision.
>
> The bundle ships as a **patch release** (`fix(373)`, draft PR #375), because #364 blocks the next minor release. Public text stays generic: no real-world findings, IDs or report content (NFR-6).

### Terminology

Two different "tier" numberings appear below. They are not interchangeable.

| Term | Meaning |
|---|---|
| **Data tier** | The richest source artifact present for a run: **1** = compensating-controls report, **2** = risk scores without controls, **3** = threats.md alone. "A data-tier-1 run" means a run with a controls report. |
| **Funnel mode** | **4-tier mode** = data tier 1; **3-tier mode** = data tier 2; **threats-only** = data tier 3. |
| **Funnel tier** | The four funnel stages: **1** Threats Identified, **2** Inherent Risk Scored, **3** Controls Applied, **4** Residual Risk. In the infographic JSON, `tier` **0–3** are funnel Tiers **1–4**. Neither numbering is the data tier. |
| **Risk volume** | The sum of per-finding scores over one row set (D-2). V2, V3 and V4 are the Tier 2–4 volumes. |
| **Checked set** | Every destination path the installer tests for a symlink before writing or deleting (D-1, FR-K3.1). |
| **At or above an entry's destination** | A manifest entry's destination path itself, or any of its ancestors strictly below the project root. **Nested** means strictly inside a directory entry's destination subtree. |
| **Allow-list** | The finding IDs an infographic image may show (exactly those its prompt renders) and the component names it may refer to (FR-K15.2). |
| **Chain** | The image models the agent tries in order: a primary model, then its fallbacks (FR-K14.4). |

---

## User Scenarios & Testing *(mandatory)*

User stories keep the PRD's numbering (US-1 to US-5). US-3 and US-4 are split along the split valve (§ Scope Boundaries), so that each story is one independently shippable slice. US-6 covers the #370 fold-in.

| Story | Items | Priority | Split valve |
|---|---|---|---|
| US-1 Every skill and script ships | K1, K2 | **P1** | Cut line (committed green in the first build wave) |
| US-2 No write or delete through a link without consent | K3 | **P1** | Not a candidate; ships with K1 |
| US-3a The report matches its sources | K9, K10, K12, K13 (recommendations, MAESTRO, placeholder) | **P2** | Not a candidate |
| US-3b The funnel narrows by risk volume | K11 | P3 | Candidate (TW-0 second, TW-1) |
| US-3c One posture label on every surface | K13-posture | P3 | Candidate (TW-0 third, TW-2) |
| US-4a The stock agent renders | K14 | **P1** | Not a candidate (must-ship since the PRD's floor band). The fix must target live models (S-8) |
| US-4b No leaked prompt text or wrong IDs | K15 | P3 | Candidate (TW-0 first, TW-3, TW-5, TW-6) |
| US-5 CI catches manifest drift | K1/K2 guard | **P1** | Cut line |
| US-6 The FR-012b guard is test-covered | #370 | P3 | Drop-able (TW-4) |

### User Story 1 — Every skill and pipeline script ships (Priority: P1) · K1, K2

*As an adopter installing tachi with `install.sh`,* I want every skill and script that tachi's commands and agents use, *so that* no threat agent runs without its detection references and no command step fails on a missing script.

**Why this priority**: Every installer-based adopter since 2026-04-19 has run the output-integrity, misinformation and human-trust-exploitation agents without their detection references (OWASP LLM10:2026, LLM07:2026, ASI09:2026). Every installer-based adopter also lacks the deterministic Affected Assets populator that three pipeline steps invoke. This is the customer-urgent item and the cheapest one, so it forms the cut line: committed green in the first build wave, and shippable on its own from that commit.

**Independent Test**: Install into an empty temporary project and count what lands: 21 skill dirs, 21 threat-agent definitions, 4 scripts.

**Acceptance Scenarios**:

1. **Given** an empty project, **When** `install.sh` runs, **Then** the project contains 21 `.claude/skills/tachi-*` dirs (including `tachi-output-integrity`, `tachi-misinformation` and `tachi-human-trust-exploitation`), 21 threat-agent definitions, and the four distributable scripts: `extract-report-data.py`, `extract-infographic-data.py`, `tachi_parsers.py` and `populate-affected-assets.py`.
2. **Given** `INSTALL_MANIFEST.md`, **When** its prose is compared with its machine-parseable block, **Then** the two agree:
   - 21 agent definitions and 21 skill dirs;
   - an agent table that includes the output-integrity, misinformation and human-trust-exploitation rows;
   - four scripts in both script notes and in the script table;
   - a true dependency note (stdlib-only at import; PyYAML is imported lazily for the PDF coverage-attestation page);
   - in place of the stale non-distributed list, the rule that every other file in `scripts/` is tachi-internal;
   - no claim that missing scripts make agents fall through to inline extraction (the agents hard-fail instead).
3. **Given** a fresh, empty project and any of the three manual install blocks (the README's "Manual install (alternative)" and the developer guide's two), **When** an adopter follows it, **Then** the install succeeds, and the block:
   - tells them to copy every path between the `BEGIN MANIFEST` and `END MANIFEST` markers in `INSTALL_MANIFEST.md`;
   - gives a short copy loop that runs on bash 3.2 and on both GNU and BSD userlands, pastes cleanly into an interactive zsh, and is safe to re-run;
   - states that the manual path does not check for symlinked destinations (D-1);
   - carries no enumerated path list and no count that can drift.
4. **Given** the manifest's maintenance checklist, **When** a maintainer adds a skill, command or script, **Then** the checklist no longer asks them to edit install instructions by hand, because every manual block derives from the manifest.

---

### User Story 2 — The installer never writes or deletes through a symlink without consent (Priority: P1) · K3

*As an adopter whose `.claude/skills` (or any folder tachi installs into) is a symlink to a folder shared with other AI tools,* I want the installer to tell me exactly where tachi's files would go, write there only if I say so, and never delete anything there, *so that* it never silently changes a folder other tools read.

**Why this priority**: K1's release notes tell every installer adopter to re-run the installer. An adopter with a symlinked destination who re-runs before K3 ships gets exactly the write-through that K3 fixes, so K3 is not a split candidate and ships with K1 (C-1). Deny-by-default is also the posture a security tool should model.

**Independent Test**: In sandboxed synthetic projects, a `.claude/skills → ../.agents/skills` link is refused without the flag, with zero files written. With the flag, the install succeeds and names the resolved destination.

**Acceptance Scenarios**:

1. **Given** a project whose `.claude/skills` is a symlink to `../.agents/skills`, **When** `install.sh` runs without `--follow-symlinks`, **Then** it:
   - exits non-zero;
   - names the symlinked component, its resolved destination, and whether that destination is inside or outside the project;
   - states that nothing was written;
   - names both remedies (re-run with `--follow-symlinks`, or replace the link with a real directory);
   - writes and deletes zero files, in the project and in the link's target.
2. **Given** the same project, **When** `install.sh --follow-symlinks` runs, **Then** it installs, and it names each resolved destination before copying and again in the summary.
3. **Given** a project where the parent directory of a single-file destination is a symlink, **When** `install.sh` runs, **Then**:
   - without the flag, it is refused as in scenario 1;
   - with the flag, the file is copied through the link and the resolved destination is named.
4. **Given** a manifest entry's destination that is itself a symlink (a `tachi-*` skill dir, or a single file), **When** `install.sh` runs, **Then**:
   - without the flag, it is refused as in scenario 1;
   - with the flag, the entry is copied through the link and the resolved destination is named.
5. **Given** a symlinked subdirectory or symlinked file *nested inside* a directory entry's destination subtree, **When** `install.sh` runs with or without the flag, **Then** it is refused. The message names the nested link and says the copy cannot pass through it (remedy: replace it with a real directory or file), and nothing is written *(spec ruling S-6)*.
6. **Given** a destination path that passes through a dangling link, a looping link, or a link to the wrong type of target (a file where a folder is needed, or the reverse), **When** `install.sh` runs with or without the flag, **Then** it is refused, the message reports the link's `readlink` text, and nothing is written.
7. **Given** a destination that resolves into the tachi source tree the installer copies from, or a project root that is the source clone or sits inside it (including when reached through an alias), **When** `install.sh` runs with or without the flag, **Then** it is refused, the message names the tachi source tree and offers no flag remedy, and nothing is written *(spec ruling S-2; carry-forward L-N2)*.
8. **Given** a project whose `.claude/commands` is a symlink to a shared folder that holds a file with a deprecated tachi command name, **When** `install.sh` runs, **Then**:
   - without the flag, it is refused and the file survives;
   - with the flag, the cleanup skips that path, the summary lists it as skipped, and the file survives.
9. **Given** a project reached through a symlink above its root (such as macOS's `/tmp → /private/tmp`, or a symlinked home directory), or a project directory itself reached through a link, **When** `install.sh` runs, **Then** it is not refused on that account, and an in-project link is classified as inside the project.
10. **Given** a project with no symlinked destination component, **When** `install.sh` runs, **Then** it copies exactly the same files as before this change.
11. **Given** `install.sh --version <tag>` run from a source clone that is on a branch (or detached at a SHA), **When** the install succeeds, fails or is refused, **Then** the source clone is back on its original ref afterwards. **When** the restore itself fails, **Then** a warning names the original ref and the command that restores it, and the failed restore doesn't change the run's exit status.
12. **Given** `install.sh --help` and the README install section, **When** an adopter reads them, **Then** both document `--follow-symlinks` and its scope: destination components at or above each entry only; copies only; never deletes; always refuses dangling, looping, wrong-type and nested links, and destinations inside the tachi clone. Both files keep their release-please version markers.

---

### User Story 3a — The report shows the same numbers as its source artifacts (Priority: P2) · K9, K10, K12, K13 (recommendations, MAESTRO, placeholder)

*As a security lead sharing tachi output,* I want the infographics and the PDF to show the same residual bands, MAESTRO layers, delta counts, resolved findings and recommendations as the source artifacts, *so that* I can present them without hand-correcting anything.

**Why this priority**: This is the deterministic core of G3. Its root causes are known and it starts from a green pre-state, so it is not a split candidate. It ranks below the installer stories because it affects the fidelity of what adopters present, not what they install.

**Independent Test**: Synthetic fixtures produce the exact expected values in both the infographic JSON and the PDF report data. The fixtures follow the templates' real section order and cover:
- short-form controls headers with an empty Critical band;
- an empty last band directly before `### Summary Statistics`;
- a `###` MAESTRO heading;
- a `## 4c.` baseline with known delta counts and one placeholder row;
- a controls Section 4 that covers only some findings;
- a drifted Section 4.

**Acceptance Scenarios**:

1. **Given** a controls report that uses the short-form headers (`Residual`, `Residual Sev.`) and has an empty Critical band, **When** extraction runs, **Then** the residual band counts are correct, and the empty band yields no rows instead of adopting the next band's table.
2. **Given** a controls report whose last band is empty and sits directly before `### Summary Statistics`, **When** extraction runs, **Then** it yields zero phantom rows and correct totals.
3. **Given** the three callers that match bold paragraph text ("Risk Summary", "Severity Distribution", "Coverage Distribution"), one `##` caller, and the risk-scores SARIF generator, **When** the level-aware stop rule is in place, **Then** their results are unchanged, and regression cases pin each of them.
4. **Given** a threats.md whose MAESTRO table sits under `### Risk by MAESTRO Layer`, **When** both extractors run, **Then** the layer distribution and the most-exposed layer equal those of the `####` form.
5. **Given** a threats.md baseline under the template's `## 4c. Resolved Findings` heading, with known NEW, UPDATED, UNCHANGED and resolved counts plus one placeholder row, **When** both extractors run, **Then**:
   - the infographic `delta_counts` are exact;
   - the PDF data carries the same counts;
   - no placeholder row appears among the resolved findings.
6. **Given** the same baseline under the legacy `## 4b. Resolved Findings` heading, **When** extraction runs, **Then** the resolved count is the same.
7. **Given** a baseline run whose Section 7 status map has an ID set that differs from the tier's finding IDs, **When** extraction runs, **Then** it warns. A run without a baseline, or whose Section 7 has no Status column, does not emit the ID-set warning (a baseline run without a Status column gets the single "delta counts unavailable" warning instead). Bracketed statuses (`[NEW]`) count as their bare values.
8. **Given** a data-tier-1 run whose controls Section 4 covers only some findings, **When** the PDF data is built, **Then**:
   - covered findings carry their analyzer recommendation;
   - every other finding carries its threats.md Section 7 mitigation, prefixed `Threat-model mitigation:`;
   - a finding with no text from either source shows `No recommendation available`;
   - the remediation roadmap, the finding cards and the attack-path remediation all show the same text for each finding, and none of them is blank.
9. **Given** a drifted controls Section 4 (content present, but zero recommendations join), **When** the PDF data is built, **Then** the extractor warns, and every finding carries the prefixed fallback or the placeholder.
10. **Given** a controls file with short-form headers passed explicitly to `/tachi.infographic`, **When** the command detects the file's type, **Then** it recognizes it as a controls report, instead of rejecting it as `UNABLE TO DETECT DATA SOURCE TYPE` *(spec ruling S-12)*. Auto-detection is by file name and is unaffected.
11. **Given** the maintained, distributed surface (agents, skills, templates, scripts and architecture docs), **When** it is searched for "Section 4b" references that mean Resolved Findings, **Then** none remain, the references that mean Findings by Agentic Pattern are untouched, and the PR's disposition ledger lists every site with its outcome.

---

### User Story 3b — The risk funnel narrows by risk volume (Priority: P3 · split-valve candidate) · K11

*As a security lead,* I want the risk funnel to narrow as controls reduce risk, *so that* it shows how much risk the controls remove, instead of a finding count that can never shrink.

**Why this priority**: It is the largest deterministic item: new per-row logic, deterministic widths, template text, and two goldens. The split valve carves it second under TW-0, and TW-1 carves it if `plan.md` hasn't pinned STEP, FLOOR, the numeric semantics and the Tier-3 formula, or if its tasks exceed 1.2 days.

**Independent Test**: Controls fixtures with found, partial and missing controls produce tier volumes, severity mixes, widths and reductions equal to hand-computed values. One is STEP-bound, and one has a strong reduction that exercises FLOOR.

**Acceptance Scenarios**:

1. **Given** a 4-tier fixture, **When** the funnel is computed, **Then** Tiers 2–4 are summed over the controls rows alone, after first-occurrence dedup and with phantom and placeholder rows dropped:
   - Tier 2 = Σ inherent;
   - Tier 3 = Σ (residual if the row's control is found, else inherent);
   - Tier 4 = Σ residual.

   Every tier carries its count, volume and severity mix. Tier 1 carries its count and its qualitative severity mix, and no volume.
2. **Given** that fixture, **When** reductions are computed, **Then**:
   - Tier 1→2 is 0%;
   - Tier 2→3 is non-zero when a found control exists;
   - Tier 3→4 is non-zero when a partial control exists;
   - no reduction is negative;
   - the Tier 2→4 reduction equals the JSON's `risk_reduction` under the pinned numeric semantics.
3. **Given** a STEP-bound fixture and a strong-reduction fixture, **When** widths are computed, **Then** they equal the FR-K11.5 algorithm's output with the STEP and FLOOR pinned in `plan.md`, and the funnel template renders them verbatim.
4. **Given** a controls row whose status reads `Missing`, **When** it is classified, **Then** it counts as no control, with no warning. **Given** an empty or unrecognized status, **Then** it counts as no control and the extractor warns.
5. **Given** a row whose residual exceeds its inherent score, a controls Section 1 total that disagrees with the row sums, or controls and risk-scores row counts that differ, **When** the funnel is computed, **Then**:
   - the extractor warns in each case;
   - the residual is clamped to the inherent score;
   - every reduction stays non-negative.
6. **Given** a controls row with no inherent score, **When** the funnel is computed, **Then** its inherent score is filled from the risk-scores composite with the same ID. A row still without one (for example, when the run has only risk-scores SARIF) is left out of all three volumes, with a warning, but still counts in the severity mixes and the posture.
7. **Given** a 3-tier run or a threats-only run, **When** the funnel is computed, **Then** today's degraded modes are kept:
   - in 3-tier mode, Tier 3 shows "Unmitigated Risk" from the Tier 2 data and Tier 4 is a ghost tier;
   - with threats.md alone, Tiers 2–4 are ghost tiers;
   - ghost-tier widths follow the STEP cascade.
8. **Given** a Tier 2 volume of zero, **When** widths are computed, **Then** they fall back to the STEP cascade, with a warning.
9. **Given** a data-tier-1 run, **When** the baseball card and the funnel are both extracted, **Then** they show the same `risk_reduction`, inherent total and residual total, all row-derived *(spec ruling S-9)*.
10. **Given** the funnel template, its skill reference and the PDF funnel caption, **When** a reader reads them, **Then**:
    - each tier's volume is defined per D-2, and the template's Tier 2 data-source line states the one-row-set rule;
    - the sidebar's stage-to-stage annotations read the volume-based reductions, and its Risk Reduction reads the row-derived value;
    - a run with 0% reduction still carries the "0% risk reduction — no effective controls detected" note, so the forced STEP narrowing isn't read as reduction;
    - no text contradicts the algorithm (the "Tier 4 width equals Tier 2 width" zero-reduction rule and the fixed ~75/50/30% headings are gone);
    - the caption says that Tier 3 credits fully effective controls and Tier 4 adds partial ones, and that widths narrow by at least one step per stage for readability while the percentages are exact.

---

### User Story 3c — One posture label on every surface (Priority: P3 · split-valve candidate) · K13-posture

*As a security lead,* I want the PDF cover and the baseball card to state the same overall risk posture, *so that* the report never contradicts itself.

**Why this priority**: The split valve carves it third under TW-0, and TW-2 carves it if its tasks exceed 0.6 days. It touches the Typst cover and four infographic text surfaces, and it drifts every golden that gains the posture fields.

**Independent Test**: For the same run directory and data tier, the PDF data and the infographic JSON carry an identical posture level and label, and the two surfaces render them identically.

**Acceptance Scenarios**:

1. **Given** the same run directory and data tier, **When** both extractors run, **Then**:
   - both outputs carry the same `risk_posture_level` (`critical`, `high`, `medium` or `low`);
   - both carry the same `risk_posture_label` (`CRITICAL RISK`, `HIGH RISK`, `MODERATE RISK` or `LOW RISK`);
   - the existing `risk_posture` sentence is still present.
2. **Given** the run's data-tier severity counts (residual counts when the controls report exists, else inherent composite, else qualitative), **When** the posture is computed, **Then** the highest band present sets the level and the label.
3. **Given** the PDF cover and the baseball card, **When** they render, **Then** each shows the label verbatim and takes its color only from the level. The cover no longer derives its own label, and the baseball card's ">20% of findings" rubric is gone.
4. **Given** a `report-data.typ` generated before this change (no posture variables), **When** the report compiles, **Then** it stops with an instruction to regenerate the data file, and it does not re-derive the label. This is verified in CI, not skipped for a missing tool.
5. **Given** the Typst variable contract and the report-assembler agent, **When** a maintainer reads them, **Then**:
   - both posture variables are marked required with no default;
   - the no-default rule is scoped to these two variables;
   - the report-assembler's deprecation note says a hand-built `report-data.typ` without them no longer compiles *(carry-forward L-N6, restated)*.

---

### User Story 4a — The stock infographic agent renders every template (Priority: P1) · K14

*As an adopter running `/tachi.infographic`,* I want the stock agent's image request to be accepted, *so that* images render at all, at the orientation each template intends.

**Why this priority**: Every request fails with HTTP 400 today, so no adopter gets an image, and G4 can't be met without this story. The PRD already made K14 must-ship (its floor band includes K14 with a render), and P1 formalizes that. Research adds a constraint rather than a deadline:
- every image model tachi names is already shut down, or shuts down on 2026-10-02 (research.md), so the fix must target live models (S-8);
- because the stock path fails on every request anyway, that date is not a break an early ship could beat.

The fix is deterministic configuration plus live verification. K14 is not a split candidate. It keeps its renders even if K15 is carved under TW-6, and PM ruling P-9.2 governs a render blockage.

**Independent Test**: A static contract test pins every request configuration to the known-good form and the current chain. K14's render set succeeds through the agent on a scratch copy of a tachi example: each template once, each chain model at least once, and executive-architecture on one portrait PDF page (FR-K14.3).

**Acceptance Scenarios**:

1. **Given** the reference request body, the five templates' `## Gemini API Configuration` blocks, executive-architecture's new configuration and the shipped adapter reference, **When** the static contract test runs, **Then**:
   - each maps to the known-good form: `generationConfig.responseModalities: ["TEXT","IMAGE"]` and `generationConfig.imageConfig.aspectRatio`, with no top-level `aspectRatio`;
   - every mapped `aspectRatio` is in the supported set;
   - the five scaffolded templates are 16:9, and executive-architecture is portrait at 3:4;
   - every model named is in the reference's chain.
2. **Given** a render of any template, **When** the agent builds the request, **Then** it reads the active template's configuration and maps it through the reference's key-to-field table, rather than sending one hard-coded body. For executive-architecture, it reads that template's own configuration and its verbatim prompt, never the 16:9 fallback prompt.
3. **Given** the reference, the five template blocks, executive-architecture's configuration and the shipped adapter reference, **When** a reader looks for model IDs, **Then** they name only the current GA chain (`gemini-3-pro-image` as the primary, then `gemini-3.1-flash-image`), and no model with a published shutdown date on or before the release. The reference's default model agrees with its fallback order *(spec ruling S-8)*.
4. **Given** a request that the API rejects with HTTP 400, **When** the agent handles it, **Then** the agent's error table treats it as an error row:
   - the spec is saved;
   - no image is generated;
   - the pipeline is not blocked;
   - it is logged at Error level;
   - the model chain is not walked (the chain is for an unavailable model);
   - the command's final summary reports the image step as failed, with the API's message and the request-body keys sent.

   The spec is still saved, but the failure is never silent *(spec ruling S-11)*.
5. **Given** a scratch copy of a tachi example and the API key held only in the process environment and sent only as a header, **When** K14's render set runs (each template once, each chain model at least once), **Then** each render succeeds. The record gives the endpoint, model ID and date, the saved file's extension matches its image bytes, and a 3:4 executive-architecture image lands on one portrait PDF page. `[MANUAL-ONLY] needs a live API key, network access and a human look at the rendered images`

---

### User Story 4b — Rendered images carry no leaked prompt text or wrong IDs (Priority: P3 · split-valve candidate) · K15

*As an adopter running `/tachi.infographic`,* I want the images to show only the text they should, *so that* they can be presented as generated.

**Why this priority**: The output is non-deterministic and can only be verified live, which makes K15 the highest-variance item. The split valve carves it first under TW-0. TW-3 carves it if the architect hasn't ruled on P-2 (a partial carve of executive-architecture alone is allowed). TW-5 caps it at two prompt iterations, and TW-6 carves it if renders are blocked for more than half a day.

**Independent Test**: A static check confirms each prompt's hardening text, allow-list reference and scaffold boundaries. One live render per template then shows no layout-label text and no ID outside its allow-list.

**Acceptance Scenarios**:

1. **Given** the reference prompt, the five template prompt blocks and the executive-architecture prompt, **When** a reader reads each prompt, **Then** it states that uppercase section labels are layout instructions, not text to render, and it restricts IDs to the template's allow-list and forbids any other.
2. **Given** each template, **When** the extractor runs, **Then** the infographic JSON carries that template's allow-list: the finding IDs its prompt renders (the full set where the prompt can show any finding, a subset or none otherwise) and the run's component names.
3. **Given** each of the five scaffolded templates, **When** the static contract test runs, **Then**:
   - the prompt scaffold is found;
   - the preamble's last line starts `DATA CONTENT` and the preamble contains the K15 instruction;
   - the postamble's first line starts `FOOTER`;
   - the allow-list is quoted in the DATA CONTENT region, as a line marked not to render *(carry-forward M-N2)*.
4. **Given** one live render per template (all six, with executive-architecture in portrait), **When** a reviewer inspects each image, **Then** no layout-label text appears and every ID shown is in its allow-list and legend, within at most two prompt iterations. `[MANUAL-ONLY] image output is non-deterministic and needs a live key plus a human visual check`

---

### User Story 5 — CI catches manifest drift (Priority: P1) · K1/K2 guard

*As a maintainer,* when I add a skill, a command or a pipeline script, I want CI to fail if I forget the install manifest, *so that* a K1-style omission can't ship silently again.

**Why this priority**: K1 is the third occurrence of this omission. The first two (2026-04-12: the whole `scripts/` dir, then all 18 skill dirs) were each fixed by hand with a prose warning "so it cannot recur", and no guard was added. The manifest's maintenance checklist is enforced by nothing. The guard is part of the cut line and is committed green in the first build wave with K1/K2.

**Independent Test**: The completeness test is green on the fixed manifest and red on a copy of the block with any one required entry removed.

**Acceptance Scenarios**:

1. **Given** the fixed manifest, **When** the completeness test runs, **Then** it passes, because the block contains:
   - (a) every `.claude/skills/tachi-*` dir;
   - (b) every `.claude/commands/tachi.*.md` file;
   - (c) every `scripts/*.py` that a distributed command, agent, skill or template references;
   - (d) every local module those scripts import, transitively.
2. **Given** a copy of the block with any one required entry removed, **When** the test runs, **Then** it fails, naming `INSTALL_MANIFEST.md` and the exact missing path. There is one negative case per category, (a) to (d).
3. **Given** a distributed file that references a `scripts/<name>.py` that is neither in the block nor on the commented exclusion list, **When** the test runs, **Then** it fails (fail-closed).
4. **Given** the references to `tests/scripts/test_pattern_*.py` in the orchestrator agent, and the references to AOD-internal scripts under non-tachi skills, **When** the scan runs, **Then** neither counts. The root anchor excludes the first, and the pinned scan scope excludes the second *(carry-forward L-N5)*.
5. **Given** a block with an entry that has leading or trailing whitespace, a `..`, a leading `/` or a `~`, or a marker that is missing or repeated, **When** the test runs, **Then** it fails. The test's reader mirrors the installer's parser exactly.
6. **Given** a scan that finds nothing (a renamed marker or glob), **When** the test runs, **Then** it fails rather than passing vacuously.
7. **Given** an empty temporary project and a `.git`-less copy of the source, **When** the test's end-to-end case runs the real `install.sh`, **Then** the required set exists in the project, and no network call or ref change touches the developer's clone.
8. **Given** the four distributable scripts, **When** the test walks their module-level imports, **Then** every import is from the standard library or is `tachi_parsers` *(spec ruling S-13; NFR-2)*.
9. **Given** a pull request or a push to `main` that touches any guarded surface, **When** CI runs, **Then** the dedicated fast workflow runs the completeness test and the extraction-fidelity modules, and it visibly runs on PR #375.

---

### User Story 6 — The FR-012b form-drift guard is test-covered (Priority: P3 · drop-able) · #370

*As a maintainer,* I want the FR-012b form-drift guard in `extract-report-data.py` covered by a test, *so that* a regression that silently loses its warning can't go unnoticed.

**Why this priority**: The guard is diagnostic-only and changes no output, so it is the lowest-value item. It is folded in because it touches the same file as K10 and K13 and its recipe is fully specified. TW-4 drops it at no cost if it outgrows the recipe.

**Independent Test**: The two recipe cases pass against the current guard and fail if the guard's warning or its "never misreported as unmatched" promise regresses.

**Acceptance Scenarios**:

1. **Given** a finding whose source attribution cites a stale-form ID (`{taxonomy: owasp, id: "LLM05:2025"}`), **When** the guard runs (`_warn_unmatched_attribution_refs`, called from `build_per_framework_aggregates` since `3d67ca7` moved it out of `classify_framework_items`), **Then** its warning is emitted on stderr, and the returned items are identical to the no-guard case.
2. **Given** a legitimate out-of-scope catalog ID (for example, MITRE ATT&CK `T1070.001`), **When** `build_per_framework_aggregates` runs against the real MITRE catalog, **Then** it is not reported as unmatched.
3. **Given** the guard's docstring, **When** a maintainer reads it, **Then** it documents that the guard is skipped for a framework whose in-scope count is 0. Its "never raises" claim stays: since `3d67ca7`, the guard does no catalog I/O, so the claim holds by construction.

---

### Edge Cases

**Installer (K1–K3)**
- **A symlink above the project root, or a project reached through a link.** Only components strictly below the physical root are checked, so neither trips the refusal. An in-project link is classified as inside (US-2 #9).
- **Links at or above an entry's destination.** With the flag, they are followed: the copy writes through an ancestor link, a linked entry directory, or a linked single file (US-2 #2–#4).
- **Links nested inside a copied directory subtree.** Always refused, even with the flag. BSD `cp -r` cannot write through a nested symlinked subdirectory ("Not a directory") or a nested symlinked file ("Permission denied"). It aborts mid-copy and leaves a partial install (US-2 #5).
- **Dangling or looping links.** Always refused, with the `readlink` text reported. Otherwise `mkdir -p` or `cp` fails mid-copy and leaves a partial install under `set -euo pipefail` (US-2 #6).
- **A destination inside the tachi source tree, or a project root inside the source clone.** Always refused:
  - `cp` aborts on a destination that is the source ("identical" / "same file"), which leaves a partial install;
  - writing into the clone would dirty it and break every later `--version` install;
  - the containment test runs on physical paths, so an alias to the clone can't bypass it the way it bypasses today's self-install guard (US-2 #7).
- **Cleanup through a link.** The deprecated-command cleanup is the only destructive path. It is refused without the flag and skipped with it, never deleted (US-2 #8).
- **A failed `--version` restore.** It is warned with the original ref and the restore command, never swallowed, and it doesn't change the run's exit status (US-2 #11).
- **A corrupted manifest marker.** The installer matches the markers exactly. A stray trailing space or carriage return on BEGIN makes it copy nothing, print "Copied: 0 item(s)" and exit 0. The completeness test guards the tracked manifest's markers (US-5 #5). The installer's own handling of a corrupted marker is unchanged.
- **The manual install path.** It bypasses the symlink check by definition. Each manual block says so (US-1 #3).
- **A stale tachi clone.** Re-running `install.sh` from a stale clone re-installs the old manifest, so the release notes tell adopters to update their clone first (M9).
- **The race between check and write (TOCTOU).** Out of scope. The installer runs as the adopter, in the adopter's own project. The refusal defends against a pre-existing link, not a concurrent attacker.

**Extraction (K9–K13)**
- **Header drift.** The short forms (`Residual`, `Residual Sev.`, `Inherent`, `Status`) resolve through one alias table (FR-K9.1), in the extractors and in the infographic command's tier detection (FR-K9.3).
- **An empty band.** It yields no rows, including an empty last band before `### Summary Statistics` (FR-K9.2).
- **Placeholder rows.** A Threat ID that is a dash or empty is dropped from the controls rows and from the resolved findings (FR-K9.2, FR-K12.3).
- **Control status.** A recognized no-control label (`No Control Found`, `Missing`, `None`, `Not Found`) is silent. An empty or unrecognized status counts as no control and warns. Whole-token matching means "known", "node" or "annotated" never read as "no" (FR-K11.3).
- **Residual above inherent.** It is clamped once, with a warning, so every consumer sees the same value (FR-K11.3).
- **No inherent score after the join.** The row is left out of the volumes, with a warning, but still counts in the severity mixes and the posture. This also covers a data-tier-1 run whose risk scores exist only as SARIF (FR-K11.3).
- **A Tier 2 volume of zero, or no inherent scores at all** (for example a run with only risk-scores SARIF and a controls table without an Inherent column). Volumes are unavailable: widths fall back to the STEP cascade, and the volumes, reductions and Risk Reduction are null rather than 0, with a warning (FR-K11.5).
- **Section 1 totals that disagree with the rows** (the #374 K7 symptom, and already true of the golden fixture). The rows win, with a warning, on the funnel and the baseball card alike (FR-K11.3).
- **Row-count and ID-set mismatches between artifacts** (the #374 K6/K7 symptoms). Each one warns (FR-K11.3, FR-K12.2).
- **The legacy `## 4b.` resolved-findings heading.** Accepted alongside `## 4c.` (FR-K12.4). The producer checklist that still tells the orchestrator to write 4b is corrected (FR-K12.5).
- **Neither source has a recommendation.** `No recommendation available` is shown, the same on every surface (FR-K13.1).
- **A stale `report-data.typ`.** Compilation stops with a regenerate instruction (FR-K13.4).

**Render path (K14–K15)**
- **A model shutdown.** Every model tachi names today is shut down or shuts down on 2026-10-02. The chain moves to the GA replacements, and each chain model is live-verified (FR-K14.4).
- **An HTTP 400.** It is surfaced as an error with the API's message and the keys sent. The spec is still saved and the pipeline is not blocked, but the failure is never silent, and it doesn't walk the model chain (FR-K14.5).
- **K14's live renders are blocked** (key access, quota or model availability) beyond TW-6's half day plus one retry session. K1–K3 and Group B are not held. K14 ships its deterministic parts under the static contract test: the schema-conformant body, the mapping, the chain update and the 400 path. FR-K14.3 is recorded as open, a follow-up issue is filed, and the release notes say the render path is statically verified only (PM ruling P-9.2).
- **A lost scaffold marker.** Today this silently degrades to agent-composed prompts. The static contract test now fails instead (FR-K15.3).
- **Model availability for a given key.** TW-6 carves K15 if renders are blocked for more than half a day. K14 keeps its renders.
- **Residual leakage after two prompt iterations.** Ship what has been hardened, record the residual per template, and file a follow-up (TW-5, R-5).

**Bundle**
- **#374 lands first or second.** The parsers accept both today's controls-table format and the one #374 K8 corrects, so neither order breaks this bundle.

---

## Requirements *(mandatory)*

> **AC rule.** The acceptance scenarios above follow Given/When/Then. `[MANUAL-ONLY] <reason>` marks the scenarios that need a live API key and a human look (US-4a #5, US-4b #4). Every other scenario is automatable, by one of three methods:
> - synthetic fixtures (NFR-1);
> - static assertions on agent and command text. US-4a #1–#4 cover the key-to-field mapping instruction, the executive-architecture routing, the model chain and the HTTP 400 row, and US-3a #10 covers the command's detection text. US-4a #2 is also confirmed by the live record (executive-architecture at 3:4);
> - running the documented manual-install loop (US-1 #3). A test in the fast workflow runs the README's loop into an empty temporary project and asserts that all three manual blocks carry the same loop. A one-time recorded run under macOS `/bin/bash` 3.2 covers the strict shell, because NFR-7 keeps README and docs off `tachi-pytest.yml`'s trigger.
>
> **Traceability.** IDs match the PRD (`FR-K1.1` …). Requirements this spec adds are marked *(spec …)* or *(carry-forward <ID>)*. File pointers are those the PRD verified at `v4.48.0` (`63438d7`), which is this branch's base content. Research re-verified them, with the corrections listed in research.md.

### Functional Requirements

#### Group A — Installer (`INSTALL_MANIFEST.md`, `scripts/install.sh`, `README.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md`)

##### K1 — the manifest omits three skills

- **FR-K1.1** — The machine-parseable block MUST list all 21 `.claude/skills/tachi-*` dirs, adding `tachi-output-integrity`, `tachi-misinformation` and `tachi-human-trust-exploitation`. → US-1 #1
- **FR-K1.2** — The manifest prose MUST match what ships: "21 threat analysis agent definitions", "21 dirs", and an agent table that gains the output-integrity, misinformation and human-trust-exploitation rows. → US-1 #2

##### K2 — the manifest omits the populator, and the manual installs drift

- **FR-K2.1** — The block, both "3 Python files" notes and the script table MUST cover the four distributable scripts: `extract-report-data.py`, `extract-infographic-data.py`, `tachi_parsers.py` and `populate-affected-assets.py`. In the same file:
  - the dependency note says what is true (NFR-2);
  - the stale list of non-distributed scripts is replaced by the rule that every other file in `scripts/` is tachi-internal;
  - the stale claim that missing scripts make agents "silently fall through to LLM inline extraction" is corrected: the report and infographic agents stop with `EXTRACTION SCRIPT MISSING`, and a pipeline step that runs `populate-affected-assets.py` fails at that step.

  → US-1 #1, #2
- **FR-K2.2** — Every manual install block MUST derive from the manifest instead of enumerating paths: the README's "Manual install (alternative)" and both developer-guide blocks.
  - Each block becomes "copy every path between the `BEGIN MANIFEST` and `END MANIFEST` markers in `INSTALL_MANIFEST.md`", plus a short loop that:
    - reads the block the way the installer does;
    - creates each parent directory first;
    - copies a directory's contents into it, so a re-run neither fails nor nests;
    - runs on bash 3.2 and on both userlands (NFR-3).

    All three blocks fail on a fresh project today.
  - Each block states that the manual path does not check for symlinked destinations, so it should run only into real directories (D-1). The block carries no comment, because stock interactive zsh does not treat `#` as a comment.
  - The developer guide's stale verify counts are corrected, and its install section gains no version-bearing example (release-please bumps only `README.md` and `scripts/install.sh`). Its stale `--version v4.0.0` example becomes a generic `vX.Y.Z`.
  - The maintenance checklist item that asks for install-instruction edits is reworded to match.

  → US-1 #3, #4
- **FR-K2.3** — A manifest completeness test, gated per NFR-7, MUST assert that the block contains:
  - (a) every `.claude/skills/tachi-*` dir;
  - (b) every `.claude/commands/tachi.*.md` file;
  - (c) every `scripts/*.py` that a distributed command, agent, skill or template references (FR-K2.4);
  - (d) every local module those scripts import, transitively.

  → US-5 #1
- **FR-K2.4** — **The reference scan** MUST match root-anchored path references, `(?<![\w./-])(?:\./)?scripts/[\w-]+\.py` (the PRD's pattern, widened to also catch a `./scripts/` spelling).
  - **Scope** *(carry-forward L-N5)*: the scan globs are pinned to the distributed set: `.claude/commands/tachi.*.md`, `.claude/agents/tachi/**`, `.claude/skills/tachi-*/**` and `templates/tachi/**`.
  - **Fail-closed**: the test keeps an explicit exclusion list with a reason per entry. A matched reference that is neither in the manifest nor on that list fails the test. Scripts that nothing distributed references are not required: `populate-maestro-coverage.py`, the `generate-*-sarif.py` generators and the `check-*.py` CI tools.
  - **Imports**: for (d), the test walks the required scripts' syntax trees for imports that resolve to `scripts/<name>.py`. It also asserts that every module-level import of the four scripts is from the standard library or is `tachi_parsers`. This enforces NFR-2 *(spec ruling S-13)*.
  - **Reader parity and hygiene**: the test's manifest reader mirrors the installer's `parse_manifest` exactly (exact markers, no stripping). It asserts:
    - each marker occurs exactly once;
    - no entry has leading or trailing whitespace;
    - no entry contains `..` or starts with `/` or `~`.
  - **Non-vacuous**: the scan, the reader and the import walk each assert a non-zero cardinality floor.
  - **Failure messages** name `INSTALL_MANIFEST.md` and the exact missing path.
  - **End to end**: one case runs `install.sh` from a `.git`-less copy of the source into an empty temporary project, and asserts that the required set exists (SC-1 with the real parser). It never uses the live checkout as the source.

  → US-5 #2–#8
- **FR-K2.5** — Removing any required entry from a copy of the block MUST turn the test red. There is at least one negative case per category, (a) to (d). → US-5 #2

##### K3 — symlinked destinations and the `--version` ref restore

- **FR-K3.1** — **The pre-flight.** After the `--version` checkout and before the cleanup or any write, the installer MUST test for a symlink on every existing path in D-1's checked set. The set is the union of:
  - every ancestor of each manifest entry, strictly below the project root;
  - the entry itself;
  - every path of the entry's source subtree, mapped into the target;
  - the five deprecated-command cleanup paths.

  The link test MUST NOT be gated on the path existing, because a dangling link does not "exist". The project root is resolved physically, and only components strictly below it are checked. Resolved destinations are classified against the physical root:
  - not a link;
  - a link resolving inside the project;
  - a link resolving outside it;
  - a destination whose physical location is in the tachi source tree (checked for every manifest entry and cleanup path, whether or not a link is involved);
  - a nested link;
  - an unresolvable link (dangling, looping, or pointing at the wrong type of target).

  The check covers both branches of the copy loop (directories and single files) and the cleanup. → US-2 #1, #3–#5, #9
- **FR-K3.2** — **The refusal.** Without the opt-in flag, any symlinked component MUST stop the install. The installer:
  - names every symlinked component and its resolved destination (inside or outside the physical project root), or its `readlink` text when the link can't be resolved;
  - states that nothing was written, and names the remedies;
  - exits non-zero, with the target project untouched and the source ref restored (FR-K3.5).

  Three classes are refused **even with the flag**: unresolvable links (dangling, looping or wrong-type), links nested inside a directory entry's destination subtree *(spec ruling S-6)*, and destinations physically inside the tachi source tree (FR-K3.7). For these, the message offers no flag remedy. → US-2 #1, #5–#7
- **FR-K3.3** — **The opt-in.** The flag is **`--follow-symlinks`** *(spec ruling S-1, OQ-1)*: long form only, no short alias, and it takes no value.
  - With it, the installer follows links at or above each entry's destination, copying into each resolved destination on purpose. It names each resolved destination before copying and again in the summary.
  - **The flag authorizes copies only.** A cleanup path that passes through a symlinked component is skipped and listed in the summary, never deleted.

  → US-2 #2–#4, #8
- **FR-K3.4** — Both help surfaces in `install.sh` (the header comment and `usage()`) and the README install section MUST document `--follow-symlinks` and its scope, as US-2 #12 lists it. Those edits MUST keep the release-please `x-release-please-version` markers in `README.md` and `scripts/install.sh`. Any new example line that carries a version gets its own marker. → US-2 #12
- **FR-K3.5** — **The ref restore.** After a `--version` install that succeeds, fails or is refused, the source repo MUST be back on its original ref: a branch name, or a SHA if it started detached. A failed restore MUST print a warning that names the original ref and the command that restores it. It MUST never be swallowed, and it MUST NOT change the run's exit status: 0 for a completed install, non-zero for a refusal or failure. → US-2 #11
- **FR-K3.6** — **Tests**, sandboxed and synthetic, MUST cover every US-2 scenario:
  - linked `.claude/skills` (refused; installed with the flag);
  - a linked parent of a single-file destination, and a linked entry (each refused, then installed with the flag);
  - a nested linked subdirectory and a nested linked file, each refused even with the flag;
  - a dangling link and *(carry-forward L-N2)* a looping link, refused even with the flag, with `readlink` text reported;
  - a destination in the source tree, and a project root inside the source clone and reached through an alias, all refused even with the flag;
  - the cleanup through a linked `.claude/commands`: refused, then skipped and reported with the flag, with the shared file surviving;
  - a link above the root, and a project reached through a link;
  - an unchanged install with no links;
  - the ref restored after success, failure and refusal, and a forced restore failure that warns without changing the exit status.

  **Test validity:**
  - The tests invoke the system `/bin/bash` explicitly with `LC_ALL=C`, so the strict leg stays on bash 3.2 whatever `PATH` holds *(spec ruling S-7; resolves the optional carry-forward)*.
  - They assert installer-authored text only, never `cp` or `readlink` error wording, which differs between userlands.
  - They build every symlink at test time (the repo tracks none).
  - They assert "zero files written" with before-and-after snapshots of the target and of each link's resolved directory.
  - They make the "reached through a link" and "above the root" cases real rather than vacuous: a logical `PWD`, and an explicitly built ancestor link.

  **Harness:**
  - The `--version` cases build a throwaway source repo (init, commit, tag, isolated git config), never the live checkout, so they make no network call.
  - The forced restore failure uses a `git` shim on `PATH` that fails only the restore checkout, so production code gains no test seam.
  - The cleanup safety negatives are written before the implementation.

  → US-2 all
- **FR-K3.7** *(spec ruling S-2; carry-forward L-N2)* — A destination that resolves into the tachi source tree the installer copies from MUST be refused, with or without the flag. So must a project root that is the source clone or sits inside it. The containment test uses physical paths, generalizing today's self-install equality guard, which compares logical paths and can be bypassed through an alias. The message names the tachi source tree and gives the remedy: remove or repoint the link, or run from a project outside the clone. → US-2 #7

#### Group B — Extraction and report data (`scripts/tachi_parsers.py`, `scripts/extract-infographic-data.py`, `scripts/extract-report-data.py`)

**Sibling parity** (applies to K9–K13): every value that both the infographic JSON and the PDF report data carry is tested from one fixture on both extractors, so the two surfaces cannot drift apart. Every fix lives in the shared parser module, not in one extractor.

##### K9 — residual severity is mislabeled

- **FR-K9.1** — The controls parser MUST read the residual score and residual severity from either form: the template's `Residual Score` / `Residual Severity`, or the short forms `Residual` / `Residual Sev.`. Headers are normalized before matching (casefold, strip a trailing `.`, collapse spaces), then mapped through one alias table:
  - `Residual Score` / `Residual`;
  - `Residual Severity` / `Residual Sev.`;
  - `Inherent Score` / `Inherent` (K11);
  - `Control Status` / `Status`.

  The score-derived banding runs on both forms. → US-3a #1
- **FR-K9.2** — The markdown-table reader MUST stop scanning at the next heading of the same or higher level than the **matched line**, where the level is the count of leading `#` on that line. An empty `### Critical Residual Severity` section then returns no rows instead of adopting the next band's table.
  - A match on a non-heading line keeps today's stop rule (the next `#` or `##` heading). This preserves the three callers that match bold paragraph text.
  - Existing `##` callers MUST be unaffected across all 21 call sites, including the fourth consumer, `scripts/generate-risk-scores-sarif.py`.
  - The controls parser skips rows whose Threat ID is empty or a placeholder, using the FR-K12.3 predicate.

  → US-3a #1–#3
- **FR-K9.3** *(spec ruling S-12)* — On its explicit-path branch, the `/tachi.infographic` command's data-source detection MUST recognize a controls report by the same aliases (`Residual Score` or `Residual`). A short-form controls file passed explicitly is then no longer rejected as `UNABLE TO DETECT DATA SOURCE TYPE`. Auto-detection is by file name and is unaffected. → US-3a #10

##### K10 — the MAESTRO layer distribution is empty

- **FR-K10.1** — Both extractors MUST match the MAESTRO table heading at level 3 or level 4 (`^#{3,4}\s+Risk by MAESTRO Layer`). The report path's most-exposed layer follows from the same table.
  - The template stays at `####`, and `populate-maestro-coverage.py` is untouched.
  - *(Carry-forward, row-rule precision)*: one regex-capable header match serves both this requirement and FR-K12.4.

  → US-3a #4

##### K11 — the risk funnel doesn't narrow

- **FR-K11.1** — The funnel computation MUST implement D-2. Every tier carries its count, volume and severity mix. Tiers 2–4 are summed over D-2's one row set: in 4-tier mode, the controls report's Section 2 rows after first-occurrence dedup, with phantom and placeholder rows dropped. → US-3b #1
- **FR-K11.2** — Reductions MUST be computed on volume, between adjacent available tiers. Tier 1→2 is 0% by definition, and no reduction is negative. → US-3b #2
- **FR-K11.3** — Volumes MUST follow D-2's per-row rules.
  - **Inherent score.** The controls parser emits each row's inherent score. A missing one is filled by ID join to the risk-scores composites. A row still without one is left out of all three volumes, with a warning, but still counts in the severity mixes and the posture, because its residual exists *(spec ruling S-4; carry-forward L-N4)*.
  - **Status classifier** *(spec ruling S-5; carry-forward L-N3)*. One shared helper classifies each row's control status, and it replaces both copies of today's tolerant idiom: the row read and the coverage fallback derivation. It matches whole tokens, case-insensitively:
    - a status with a token starting `partial` (for example `partial`, `partially`) → partial;
    - a status in the recognized no-control set (`No Control Found`, `Missing`, `None`, `Not Found`) → no control, silently;
    - a status with the token `found` and no negation token (`no`, `not`, `none`, `nothing`) → found;
    - anything else, including an empty status → no control (inherent, no credit), with a warning.

    The Section 1 coverage-summary reader keeps its own matching, because it must skip rows that aren't statuses. Its totals are only a comparand.
  - **Clamp once** *(carry-forward L-N4)*. Residual is clamped to ≤ inherent once, where the controls rows are parsed, with a warning. So the residual band counts, the posture counts and the funnel all see the same clamped values, and V2 ≥ V3 ≥ V4 holds row by row.
  - **Tier 3 bands.** Tier 3 per-row scores are banded with the standard thresholds 9.0 / 7.0 / 4.0.
  - **Section 1 is a comparand.** If the controls report's Section 1 totals disagree with the row sums beyond rounding, the extractor warns and the rows win. `risk_reduction` becomes the row-derived Tier 2→4 value. The inherent and residual totals become V2 and V4. When no controls row carries an inherent score, volumes are unavailable: `risk_reduction` and both totals are null, never 0. This applies on **every infographic template that carries them**, the baseball card included, so two images from one run can't disagree *(spec ruling S-9)*.
  - **Row counts.** The extractor warns when the controls and risk-scores row counts differ.

  → US-3b #4–#6, #9
- **FR-K11.4** — The funnel template's tier blocks and width rule, and the skill reference's funnel format, MUST define each tier's volume per D-2.
  - The template's Tier 2 data-source line states the one-row-set rule: controls rows in 4-tier mode, risk-scores rows in 3-tier mode.
  - The sidebar's stage-to-stage annotations read the volume-based reductions, and its Risk Reduction reads the row-derived value.
  - The "0% risk reduction — no effective controls detected" note stays, because the algorithm narrows by at least STEP even at 0%.
  - Text that contradicts the algorithm is removed: the "Tier 4 width equals Tier 2 width" zero-reduction rule and the fixed ~75/50/30% headings.
  - The PDF's funnel caption says that Tier 3 credits fully effective controls and Tier 4 adds partial ones, and that widths narrow by at least one step per stage for readability while the percentages are exact.

  → US-3b #10
- **FR-K11.5** — The extraction layer MUST compute the tier widths deterministically and emit them per tier in the infographic JSON. They are carried into the funnel spec and the prompt's tier-data slots, and the template renders them verbatim.
  - **The algorithm.** W1 = 100 and W2 = 100 − STEP. For k = 3 and 4: W_k = clamp(W2 · V_k / V2, lo = FLOOR + (4 − k) · STEP, hi = W_{k−1} − STEP). Every tier is then at least STEP narrower than the one above and never below FLOOR, provided FLOOR + 3 · STEP ≤ 100.
  - **Fallbacks.** If V2 = 0, or no row carries an inherent score, volumes are unavailable: widths fall back to the STEP cascade (W_k = W_{k−1} − STEP), and the volumes, reductions and `risk_reduction` are null, with a warning. Ghost tiers use the same cascade. Every funnel tier is emitted as an object, with `ghost` marking an absent data source *(plan PD-18)*.
  - **Constants and numeric semantics** are pinned in `plan.md` (TW-1):
    - STEP and FLOOR, subject to FLOOR + 3 · STEP ≤ 100 and to every tier label staying legible at FLOOR width;
    - the precision of volume sums;
    - the rounding of widths and reductions;
    - the type of `risk_reduction`, so that "Tier 2→4 equals `risk_reduction`" is well-defined;
    - the largest remainder method for any severity-mix percentages.
  - **Tier indices.** JSON `tier` 0–3 are funnel Tiers 1–4 (see Terminology).

  → US-3b #2, #3, #7, #8

##### K12 — the infographic `delta_counts` is wrong

- **FR-K12.1** — `delta_counts` MUST equal the threats.md Section 7 Status column (NEW / UPDATED / UNCHANGED, after normalization, so the orchestrator's bracketed `[NEW]` counts as NEW), counted through FR-K12.2's map, plus the real count of resolved rows. → US-3a #5
- **FR-K12.2** — One shared helper in the shared parser module, `delta_status_by_id`, MUST return `{id: status}` from the Section 7 Status column.
  - Both extractors count NEW, UPDATED and UNCHANGED from that map, and the PDF path also uses it to badge findings.
  - Statuses are normalized before counting: whitespace, one surrounding `[…]` pair and emphasis markers are stripped, then the value is upper-cased.
  - On a baseline run whose Section 7 has a Status column, the extractors warn (never raise) when the map is empty or its ID set differs from the tier's finding IDs. Runs without a baseline, or whose Section 7 has no Status column, skip both checks; a baseline run without the column gets one "delta counts unavailable" warning *(plan PD-16)*.
  - The PDF path's `_merge_delta_status` stays importable from `extract-report-data.py`, because an existing test calls it; otherwise that test changes in the same commit.

  → US-3a #5, #7
- **FR-K12.3** — Placeholder rows, whose ID is a dash or empty, MUST be skipped inside the resolved-findings parser, which both extractors already call. The predicate is shared only because the controls rows are a second consumer (FR-K9.2). No abstraction goes beyond it. → US-3a #5
- **FR-K12.4** — The resolved-findings parser MUST accept both the template's `## 4c. Resolved Findings` heading and the legacy `## 4b.` form (the FR-K10.1 pattern class, for example `^##\s+4[bc]\.\s+Resolved Findings\s*$`). → US-3a #6
- **FR-K12.5** *(carry-forward L-N1)* — A sweep MUST change every "Section 4b" reference that means Resolved Findings to 4c. It leaves the references that mean Findings by Agentic Pattern, and records a per-occurrence disposition in the PR. Research found 16 change sites in 7 files:
  - `.claude/skills/tachi-orchestration/references/output-schemas.md`: the producer checklist that tells the orchestrator to write 4b (the likely source of legacy `## 4b.` outputs), and the stale collision note that hedges on it;
  - `.claude/agents/tachi/report-assembler.md`;
  - `templates/tachi/output-schemas/threat-report.md`: five lines that feed the attack-tree delta dispatch;
  - `scripts/tachi_parsers.py`: the resolved-findings docstring and code (FR-K12.4);
  - `scripts/extract-report-data.py`: one comment;
  - `docs/architecture/01_system_design/README.md`: one row;
  - `docs/architecture/00_Tech_Stack/README.md`: three lines, two of them mixed.

  Out of the sweep: the non-distributed legacy `agents/` tree, the frozen init-baseline-tree fixture, historical PRDs and CHANGELOG entries, and AOD step numbers. → US-3a #11

##### K13 — gaps in the PDF report data

- **FR-K13.1 (recommendations)** — A recommendation shown in the PDF MUST NOT be blank.
  - On every data-tier-1 run, a finding with no joined analyzer recommendation falls back to its threats.md Section 7 mitigation, prefixed `Threat-model mitigation:` (PM ruling M5). A conformant Section 4 covers only a subset of findings, so this changes conformant output too.
  - If neither source has text, the finding shows **`No recommendation available`** *(spec ruling S-3)*. On data tiers 2 and 3, a recommendation or mitigation that resolves empty also shows `No recommendation available`; the `Threat-model mitigation:` fallback stays tier-1 only *(PM plan review RC-P7)*.
  - The fallback and the placeholder apply to the finding's recommendation itself, so all three consumers show the same text: the remediation roadmap, the finding cards and the attack-path remediation.
  - When controls Section 4 has content but zero recommendations join, the extractor warns. That is the drift signal.
  - A template-conformant Section 4 still populates the recommendations it covers.

  → US-3a #8, #9
- **FR-K13.2 (MAESTRO)** — The MAESTRO distribution and the most-exposed layer MUST be populated, via FR-K10.1. → US-3a #4
- **FR-K13.3 (placeholder rows)** — The resolved findings MUST contain no placeholder rows, via FR-K12.3. → US-3a #5
- **FR-K13.4 (posture)** — The extraction layer MUST implement D-3. One function in the shared parser module emits `risk_posture_level` and `risk_posture_label` into both `report-data.typ` and the infographic JSON.
  - Every consumer D-3 lists renders the label verbatim and takes its color only from the level: the cover and its wiring, the baseball card's badge and prompt, the reference prompt, the posture placeholders, the spec reference, the agent's JSON contract, and the spec schema.
  - The baseball card's ">20% of findings" rubric is deleted, and the cover no longer derives its own label.
  - A `report-data.typ` that lacks the posture variables fails with an instruction to regenerate it. It does not re-derive the label.
  - The test that proves this runs in CI with the tool it needs, rather than skipping when the tool is absent.

  → US-3c #1–#4
- **FR-K13.5** *(carry-forward L-N6, restated)* — The Typst variable contract MUST document `risk_posture_level` and `risk_posture_label` as **required, with no default**, scoped to these two variables. The other variable groups keep their compile-cleanly defaults. The report-assembler's inline-extraction path is already deprecated and forbidden, so the carry-forward's intent is met instead by two things: the contract, and a line in the report-assembler's deprecation note saying that a hand-built `report-data.typ` without the posture variables no longer compiles. Lane B owns the contract. → US-3c #5

#### Group C — Render path (`.claude/skills/tachi-infographics/`, `templates/tachi/infographics/`, `.claude/agents/tachi/threat-infographic.md`)

##### K14 — the Gemini request is rejected (HTTP 400), and its models are retiring

- **FR-K14.1** — The reference request body MUST use the known-good form, which was verified live and is confirmed by the API's published schema: `generationConfig.responseModalities: ["TEXT","IMAGE"]` and `generationConfig.imageConfig.aspectRatio`, with no top-level `aspectRatio`.
  - **`imageSize`** stays dropped per the PRD. It is restored only under PM ruling P-10.3: live-verified at every shipped model × ratio combination (both chain models × 16:9 and 3:4), with the size actually honored and real-template latency headroom confirmed at W3.
  - **The dead keys go**: `resolution: "2K"` in the reference goes. `image_size: "2K"` goes from all five template blocks unless PM ruling P-10.3 restores it, in which case it maps to `imageConfig.imageSize` (static assertion A2).
  - **Mapping table.** The reference gains a table that maps template keys to request-body fields.
  - **Provenance.** The reference records the endpoint the form applies to (`models/{model}:generateContent`) and the model IDs and date of the verified renders. The public image-generation guide now documents a different endpoint and body shape, so the endpoint is pinned explicitly.

  → US-4a #1
- **FR-K14.2** — **The mapping.** Today, nothing reads any template's configuration. K14 MUST create the mapping.
  - **Five templates** carry a `## Gemini API Configuration` block at `aspect_ratio: "16:9"`: baseball card, MAESTRO heatmap, MAESTRO stack, risk funnel and system architecture. The agent reads the active template's block and maps it through the reference's key-to-field table.
  - **Executive-architecture** gets an explicit configuration outside its locked prompt block, with `aspect_ratio: "3:4"`, the closest supported portrait ratio to its 8.5:11 page. Where it lives is `plan.md`'s ruling P-1.
  - **Agent routing.** The agent is pointed at that configuration and at executive-architecture's verbatim prompt. The reference's no-scaffold routing, which today sends executive-architecture to a template file that doesn't exist and then to a 16:9 fallback prompt, is corrected.
  - **The static contract test** pins these to the known-good form: the reference body, the five blocks, executive-architecture's configuration and the shipped adapter copy (FR-K14.6).
    - Every mapped `aspectRatio` is in the supported set (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9), and executive-architecture is portrait.
    - Every model named is in the reference's chain.
    - *(carry-forward M-N2)*: the prompt scaffold is found for all five scaffolded templates.
    - This test is the check the templates' contract promises ("the agent validates that these sections exist"), and the contract text says so.

  → US-4a #1, #2
- **FR-K14.3** *(PM ruling P-10.2)* — Live renders MUST succeed through the agent, on a scratch copy of a tachi example (the example's images are tracked), with the API key handled per NFR-5: each of the six templates at least once (K15's first-iteration renders count when K15 ships), at least one render on each chain model, and executive-architecture assembled on one portrait PDF page. A model blocked under P-9.2 or P-10.1 is recorded as statically verified only. The record gives:
  - the status and a visual check;
  - the endpoint, model ID and date;
  - that the saved extension matches the image bytes;
  - for executive-architecture, portrait orientation and that the image lands on one portrait PDF page.

  Images are not committed. → US-4a #5
- **FR-K14.4** *(spec ruling S-8)* — **The model chain MUST name only models that are available at release.**
  - The reference's default model, its fallback chain, every template block, executive-architecture's configuration and the shipped adapter copy move to the GA replacements: `gemini-3-pro-image` as the primary, then `gemini-3.1-flash-image`.
  - Retired models go: `gemini-3-pro-image-preview` and `gemini-3.1-flash-image-preview` shut down on 2026-06-25, and `gemini-2.5-flash-image` shuts down on 2026-10-02.
  - The default model agrees with the fallback order.
  - The chain and each model's verified-render date are recorded in the reference, so the next shutdown is visible.
  - The chain is walked when a model is unavailable to the key (HTTP 404 `NOT_FOUND` or 403 `PERMISSION_DENIED`). When every chain model is exhausted, the agent logs at Error, and its summary names each model tried with its status *(plan PD-14; PM R-P2, R-P3)*.

  → US-4a #3
- **FR-K14.5** *(spec ruling S-11)* — **HTTP 400 is loud, but not blocking.** The infographic agent's error table MUST gain an HTTP 400 row:
  - the spec is saved;
  - no image is generated;
  - the pipeline is not blocked;
  - the log level is Error;
  - the model chain is not walked (the chain is for an unavailable model);
  - the command's final summary reports the image step as failed, with the API's message and the request-body keys sent.

  The agent's existing contract that "the pipeline is never blocked by image generation failures" stays. The spec is still saved, but the failure is never silent. Silence is what let a request shape that always failed ship unnoticed. → US-4a #4
- **FR-K14.6** *(spec ruling S-10)* — **The shipped copy.** The request-body reference that ships to adopters under `adapters/claude-code/agents/references/` MUST use the known-good form and the current chain, and the static contract test covers it. Legacy copies outside the manifest (the root `agents/` tree and the copilot, cursor and generic adapters) are out of scope. → US-4a #1, #3

##### K15 — rendered images leak prompt text

- **FR-K15.1** — The prompts MUST state that uppercase section labels are layout instructions, not text to render. That covers the reference, the five template prompt blocks and the executive-architecture prompt.
  - **The lock.** The executive-architecture prompt is verbatim-locked by FR-212-6. The PRD sanctions one minimal, additive amendment inside the lock markers, limited to the two K15 instructions (this one and FR-K15.2), subject to the architect's ruling at plan (P-2). Research found the amendment mechanically safe on these conditions:
    - both marker lines are unchanged;
    - no fence and no new slot are added;
    - the allow-list is expressed as "every finding ID must be one listed under CALLOUTS, and every component name one listed under LAYER STACK, FLOW EDGES or CLUSTERS";
    - the text goes right after the block's IMPORTANT paragraph;
    - a dated amendment note in the lock rule also reconciles the rule's stale header and slot lists;
    - the amendment is one paragraph, and its layout-label sentence cites only labels present in this prompt;
    - a static test proves the amendment additive (the block without it hashes to the pinned pre-change value).
  - **The agent's section.** The agent's executive-architecture section defers to the verbatim block, which it contradicts today, so the amendment takes effect.
  - **If P-2 is not sanctioned**, executive-architecture is carved from K15 under TW-3, and the other five proceed.

  → US-4b #1
- **FR-K15.2** — The prompts MUST restrict the finding IDs and component names in the image to its allow-list (plan PD-17), matching the legend, and MUST forbid any other ID.
  - The extractor emits the allow-list per template, as a new JSON field. Its finding IDs are exactly the IDs the template's prompt renders (top findings, callouts, per-layer summaries, the legend): the full finding-ID set where the prompt can show any finding (system-architecture's legend and pills, the baseball card's boundary annotations), the rendered subset elsewhere, and none where no ID is rendered. Its component names are the run's known component names *(plan PD-17)*.
  - The prompt text references the field by name, and the agent quotes its values in the DATA CONTENT region. The locked or verbatim text never transcribes values.

  → US-4b #1, #2
- **FR-K15.3** *(carry-forward M-N2, corrected)* — K15's edits MUST keep the prompt-scaffold contract. The splitter's real markers are:
  - the first occurrence anywhere of the substring `DATA CONTENT (render this`, with a line-start `DATA CONTENT` fallback;
  - the first line-start `FOOTER` anywhere, the preamble included.

  So:
  - K15's hardening text goes in the verbatim preamble (between the `IMPORTANT:` paragraph and `STYLING DIRECTIVES`) or after the `FOOTER` line;
  - no preamble line starts with `FOOTER`;
  - the marker text never appears before the DATA CONTENT header;
  - no extra fence is added under the prompt heading.

  These constraints bind every edit to these five files (K11, K13, K14 and K15 alike). The static contract test asserts the scaffold boundaries for all five (US-4b #3). The golden-regen authorization names K15 for all five scaffolded-template goldens, because they embed the scaffold text and gain the allow-list field. Whether to also harden the splitter is a plan input. → US-4b #3

#### D-4 — #370 fold-in (`scripts/extract-report-data.py`)

- **FR-370.1** — Two covering tests for the FR-012b form-drift guard (`_warn_unmatched_attribution_refs`, called from `build_per_framework_aggregates`) MUST follow #370's recipe:
  - a stale-form attribution ID warns on stderr and leaves the returned items unchanged;
  - a legitimate out-of-scope catalog ID is not reported as unmatched, exercised through `build_per_framework_aggregates` against the **real** MITRE catalog (OQ-5, closed at the tasks review), which adds `schemas/taxonomy/*.yaml` to the fast workflow's `paths:`.

  → US-6 #1, #2
- **FR-370.2** — The guard's docstring MUST document that the guard is skipped for a framework whose in-scope count is 0. The "never raises" softening #370 asked for is no longer needed: since `3d67ca7` the guard does no catalog I/O, so the claim holds by construction (the tasks review's R-6). No behavior changes. If this item is folded in, the PR closes #370. TW-4 still drops it if it outgrows the recipe (now 2 tests and 1 docstring note). → US-6 #3

### Non-Functional Requirements

- **NFR-1: determinism and fixtures.** Every deterministic fix is proven on **synthetic fixtures only**, following the templates' real section order. No real-world run output is ever committed.
- **NFR-2: stdlib-only at import.** The four distributable scripts import only the standard library and `tachi_parsers` at module load (ADR-037 D-8; KB-037 at `f74ba0f`). PyYAML is imported lazily for the PDF coverage-attestation page. The new shared helpers are pure stdlib, no dependency is added, and the four scripts stay self-contained. Enforcement is FR-K2.4's manifest-scoped import assertion, gated in the fast workflow. The older yaml-only guard runs outside the gate and is red on a non-distributed CI tool.
- **NFR-3: shell portability.** Installer changes run on bash 3.2 (macOS `/bin/bash`) and on both GNU and BSD userlands. That rules out `mapfile`, associative arrays and `readlink -f`. `[ -L ]`, `cd -P` / `pwd -P` and plain `readlink` are the verified portable primitives.
- **NFR-4: compatibility.**
  - An install with no symlinks copies the same files as before.
  - The parsers accept both the current and the corrected controls-table formats.
  - Existing `##` callers of the markdown-table reader are unchanged.
  - Changes to the infographic JSON are additive, except for the values the defects themselves correct (`risk_reduction` and the controls totals, `delta_counts`, the funnel tiers). The `risk_posture` sentence stays.
- **NFR-5: secrets.** The Gemini API key goes from the secret store into the process environment only. It is loaded per command or under the secret store's runner, because separate shell calls don't share environment. It is sent only as the `x-goog-api-key` header, never as a `?key=` query parameter, and never through verbose or trace output. It is never echoed, logged or committed.
- **NFR-6: public hygiene.** Issues, PRDs, specs, PRs, commits and the CHANGELOG describe the defects generically. They carry no real-world findings, threat text, IDs or report content.
- **NFR-7: CI, with each module in its gating workflow.**
  - **Completeness and extraction-fidelity modules** run in a new dedicated, fast workflow. It is modeled on `tachi-catalog-drift.yml`: one YAML-anchored `paths:` list shared by `pull_request` and `push: [main]`, `contents: read`, and pytest plus PyYAML (test collection needs it). Its `paths:` are broad, because the run takes seconds:
    - the manifest, `.claude/skills/**`, `.claude/commands/tachi.*.md`, `.claude/agents/tachi/**`, `templates/tachi/**`, `scripts/*.py`, and `scripts/install.sh` (for the end-to-end case);
    - the tests and their fixtures, and the workflow file;
    - `examples/**` *(carry-forward L-N5)*;
    - both `tests/conftest.py` and `tests/scripts/conftest.py`, and `pyproject.toml` *(research correction)*;
    - `README.md` and `docs/guides/DEVELOPER_GUIDE_TACHI.md` (the manual-loop test byte-compares their blocks), `adapters/claude-code/**` (the static contract test pins the shipped adapter copy), and `schemas/taxonomy/*.yaml` if #370's tests load the real catalogs *(plan review RC-P5)*.

    Each path lands in the lock-step commit that adds the test reading it. The first-wave cut-line commit invokes only the completeness module; the pre-existing extraction modules join afterward, together with the mmdc skip *(PM ruling RC-P1)*. It must visibly run on PR #375, and it provides Typst, in a separate job, for the stale-data test (FR-K13.4).
  - **Installer (K3) tests** run on the existing 2-OS bash matrix in `tachi-pytest.yml`: bash 3.2 with BSD tools on macOS, bash 5 with GNU tools on Ubuntu. That matrix is NFR-3's gate. Its `paths:` anchor gains only `scripts/install.sh`, the installer tests and their helpers and fixtures, each marked `# F-373`, with a line in the header log. Its trigger is not widened to agents, skills, commands or templates, because a run takes 22–29 minutes.
  - **The existing green parser and extractor modules are gated too**, because the R-3 safety net relies on them. The report-data module is gated on the bare runner. Only its five mmdc-dependent cases skip when mmdc is absent (the repo's skip-when-absent idiom, placed in their shared fixture) *(carry-forward M-N1)*. No workflow installs mmdc, and production still requires it (ADR-022). New report-path tests stay off the mmdc path. The #365 byte-identity module is not gated.
  - **Lock-step, per workflow.** Each module is added to its gating workflow's `paths:` list and invocation in the same commit, and `paths:` also names the source surfaces the tests guard.
  - **Co-fired gates stay green.** `tachi-mmdc-preflight`, `tachi-catalog-drift` and `tachi-maestro-coverage` also fire on this diff.
- **NFR-8: images and examples stay out of the diff.**
  - Re-rendered example PNGs are never committed (#365), and live-render images stay out of the repo.
  - New tests never write into `examples/`; they use temporary copies or run in-process.
  - One local run of the existing extraction modules rewrites tracked PNGs. So commits stage explicit paths only (never `git add -A`), and only PNG changes this session produced are restored before each commit.

### Key Entities

- **Install manifest block**: the single install contract, the list of paths between the `BEGIN MANIFEST` and `END MANIFEST` markers. The installer and the completeness test parse it identically, and every manual install path copies from it.
- **Checked set** (D-1): every destination path tested for a symlink before any write or delete. Each member is classified as not a link, a link inside the project, a link outside it, a nested link, or an unresolvable link (dangling, looping or wrong type). Separately, every destination whose physical location is inside the tachi source tree is refused.
- **Controls row**: Threat ID, Inherent Score, Control Status (found / partial / no control), Residual Score (clamped to ≤ inherent) and Residual Severity, read through one alias table. The row set is deduplicated by first occurrence, with placeholder rows dropped.
- **Funnel tier**: a tier index (JSON 0–3), name, count, volume (funnel Tiers 2–4 only), severity mix, width, and the reduction to the next tier.
- **Posture**: a level (`critical` | `high` | `medium` | `low`) and a label (`CRITICAL RISK` | `HIGH RISK` | `MODERATE RISK` | `LOW RISK`), with the supporting `risk_posture` sentence.
- **Delta status map**: `{finding ID: NEW | UPDATED | UNCHANGED}`, from the threats.md Section 7 Status column.
- **Allow-list**: per template, the finding IDs an image may show and the component names it may refer to.
- **Request configuration**: per template, a flat key set (model, fallback model, modalities, aspect ratio) that maps to one request-body form through the reference's key-to-field table.

### Key Artifacts

| Group | Item | New / modified | Path | Nature |
|---|---|---|---|---|
| A | K1, K2 | modified | `INSTALL_MANIFEST.md` | block, prose, tables, checklist |
| A | K2 | modified | `README.md`, `docs/guides/DEVELOPER_GUIDE_TACHI.md` | manual blocks derive from the manifest |
| A | K2 | **new** | completeness test module + dedicated workflow | CI guard (NFR-7) |
| A | K3 | modified | `scripts/install.sh`, `README.md` | pre-flight, refusal, opt-in flag, restore warning, docs |
| A | K3 | **new** | installer test module(s) and helper | 2-OS bash matrix (NFR-7) |
| A | K3 | modified | `.github/workflows/tachi-pytest.yml` | `paths:` anchor + invocation, in lock-step |
| B | K9–K13 | modified | `scripts/tachi_parsers.py` | alias table, stop rule, predicate, classifier, clamp, delta map, posture |
| B | K10–K13 | modified | `scripts/extract-infographic-data.py`, `scripts/extract-report-data.py` | MAESTRO heading, funnel, row-derived totals, delta counts, recommendations, posture, allow-list |
| B | K9 | modified | `.claude/commands/tachi.infographic.md` | tier detection accepts the aliases |
| B | K11, K13 | modified | `templates/tachi/security-report/{cover,main}.typ` | posture from data, fail-loud guard, funnel caption |
| B | K13 | modified | `.claude/skills/tachi-report-assembly/references/typst-template-contract.md`, `.claude/agents/tachi/report-assembler.md` | required posture variables, deprecation note |
| B | K12 | modified | the FR-K12.5 sweep set (7 files) | stale "Section 4b" references |
| C | K11, K13–K15 | modified | `templates/tachi/infographics/*.md`, `.claude/skills/tachi-infographics/references/*.md` | tier text, posture text, configuration blocks, mapping table, model chain, prompt hardening |
| C | K13–K15 | modified | `.claude/agents/tachi/threat-infographic.md`, `schemas/infographic.yaml` | JSON contract, posture, allow-list, config mapping, HTTP 400 path, executive-architecture routing |
| C | K14 | modified | `adapters/claude-code/agents/references/infographic-gemini-api.md` | the shipped copy of the request body |
| B/C | K11, K13, K15 | regenerated | `tests/scripts/fixtures/golden/*.json` | authorized by file name only (SC-8) |
| — | #370 | modified | `scripts/extract-report-data.py` + its test module | 2 tests, 2 docstring notes |

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

| # | Criterion | Baseline (v4.48.0) | Target |
|---|---|---|---|
| **SC-1** | A fresh `install.sh` into an empty project | 21 agents, 18 skill dirs, 3 scripts | 21 agents, **21** skill dirs, **4** scripts |
| **SC-2** | Manifest drift is caught | Nothing checks it | The gated completeness test is green on the fixed manifest and red on every negative case |
| **SC-3** | A symlinked destination | Silent write-through and delete-through | Without the flag: 0 files written or deleted, and each link and its resolved destination named. With the flag: installed through links at or above each entry and named, with 0 files deleted through a link. Dangling, looping, wrong-type and nested links, and destinations inside the tachi clone, are refused either way. The ref is restored, or a warning is printed |
| **SC-4** | Extraction matches the sources (synthetic fixtures) | Residual Critical mislabeled; MAESTRO empty on `###`; flat funnel; wrong `delta_counts`; resolved findings missed under `4c`; placeholder row; blank recommendations; two posture rubrics | Correct residual band counts and 0 phantom rows; identical MAESTRO output at `###` and `####`; the funnel narrows by volume over one row set, with Tier 2→4 equal to `risk_reduction` on every template; exact `delta_counts` under both `4b` and `4c`; 0 placeholder rows; 0 blank recommendations on any surface; one posture level and label on both surfaces |
| **SC-5** | Live render | Every request fails with HTTP 400, and every configured model is retired or retiring | Every chain model renders. 6/6 templates render, with executive-architecture in portrait on one PDF page. 0 leaked layout labels, and every ID in its allow-list |
| **SC-6** | Release | Earlier manifest fixes shipped without a re-install notice | A `fix(373)` patch release whose **published release notes**, not only the CHANGELOG, carry: (1) the update-and-re-run notice (update the clone first, then re-run `install.sh`; it names the three skills and the Affected Assets populator); (2) the D-1 behavior note: an install through a symlinked destination stops unless `--follow-symlinks` is passed, the flag never deletes through a link, and dangling, looping, wrong-type and nested links, and destinations inside the tachi clone, are refused **even with the flag**; (3) that findings the controls report gives no recommendation for show the threat model's mitigation, marked `Threat-model mitigation:` (always, per M5); (4) that the risk funnel now narrows by risk volume, and that the Risk Reduction figure on the funnel and the baseball card is computed from the controls rows and can differ from the controls report's summary (only if K11 ships); (5) that a `report-data.typ` compiled outside `/tachi.security-report` now stops with a regenerate instruction (only if K13-posture ships); (6) that the render path is statically verified only, per blocked model (only if P-9.2 or P-10.1 fires); (7) to replace a symlinked destination before re-running (only if TW-7 ships Lane A without K3). The notices appear verbatim in the published notes, verified with `gh release view` |
| **SC-7** | Live confirmation *(lagging; tracked outside this feature)* | — | The next large real-world run, installed with the stock `install.sh`, shows none of K1–K3 or K9–K15 |
| **SC-8** *(spec)* | No collateral change | — | The existing gated suites and the co-fired workflows stay green. 0 tracked example PNGs and 0 PDF baselines change in the PR. Infographic goldens change only where authorized by file name: the funnel and baseball-card goldens for K11 (the baseball card only while K11 ships; PM ruling P-9.5), the goldens that gain posture fields for K13, and all five scaffolded-template goldens for K15. Every data-layer diff against the pre-build snapshot (with run-specific fields such as timestamps and absolute paths normalized) is attributed to a K-item, and the PR lists the examples whose data changed |

**Verification.**
- SC-1 to SC-4 and SC-8 are verified automatically.
- SC-5 is verified live and recorded in the PR (FR-K14.3).
- SC-6 is verified when the release publishes, which may be after `/aod.deliver`. Deliver carries a follow-through item if the release PR merges later.
- SC-7 is DoD step 3 (user validation), after the release.

**Carved items.** An SC clause tied to an item the split valve carves moves with that item to its follow-up issue: SC-4's funnel and posture clauses, and SC-5's leakage and allow-list clauses.

**Definition of Done.** PRD-373 §8 applies in full. This spec refines its elements in SC-6, SC-7, SC-8, NFR-7, NFR-8, FR-K3.4 and FR-K14.3. Two DoD rules not restated elsewhere also bind:
- the gated suites clone the committed HEAD, so commit before running them;
- the PR is titled `fix(373): …` from the draft onward (PR #375 already is).

---

## Scope Boundaries & Split Valve

### In scope

K1–K3 (Group A), K9–K13 (Group B), K14–K15 (Group C), and #370 per D-4. One bundle, one PR (#375), one patch release.

### Split valve (decided mechanically at `/aod.tasks` and during the build, not here)

- **Cut line.** K1/K2, its completeness test and its gating workflow are committed green in the first build wave, before any other lane's work lands. From that commit on, the bundle can be cut at any wave boundary without holding K1/K2 back.
- **K3 ships with K1.** K3 is not a split candidate. If K3 ever misses a cut, that release's notes tell adopters with a symlinked destination to replace the link before re-running.
- **K14 is must-ship and never bends the cut line** (PM ruling P-9.1). K14 may ride a TW-7 early PR only if three conditions hold:
  - its static contract test is green;
  - FR-K14.3's full render set is recorded, made from the early PR's own code (each template once, each chain model at least once, executive-architecture on one portrait PDF page); the only exception is a model blocked for the project key, recorded as statically verified only with notice 6 (P-10.1), and if both models are blocked, K14 does not ride early (P-10.4);
  - its commits separate cleanly from the K13 and K15 edits in the files they share.

  Otherwise K14 ships in the main PR. PM ruling P-9.2 governs a render blockage.
- **At `/aod.tasks`**, the team-lead evaluates:
  - **TW-0** (aggregate): if the projected duration exceeds 5.5 days, carve K15, then K11, then K13-posture, until it fits;
  - **TW-1** (K11): carve it if `plan.md` hasn't pinned STEP, FLOOR, the numeric semantics and the Tier-3 formula, or if its tasks exceed 1.2 days;
  - **TW-2** (K13-posture): carve it if OQ-3 reopens or its tasks exceed 0.6 days;
  - **TW-3** (K15): carve it if OQ-4 reopens or P-2 is unruled; a partial carve (executive-architecture only) is allowed;
  - **TW-4** (#370): drop it if it outgrows its recipe.
- **During the build**:
  - **TW-0..TW-2 re-check** (W1 exit, T039; PM ruling P-11.3): once, before any K11 or K15 W2 task starts, re-run TW-0, TW-1 and TW-2 on the W0/W1 actuals with their PRD §10 thresholds. If one fires, carve in the order K15 → K11 → K13-posture until it fits. A carved K11 or K13-posture reverts its landed W1 commits (T020, T024), K14 keeps its render set (P-10.2), and the result is recorded. After T039, K15 is carved only through TW-6;
  - **TW-5**: at most two K15 prompt iterations; any residual leakage becomes a follow-up issue;
  - **TW-6**: if renders are blocked for more than half a day, carve K15, and K14 keeps its renders;
  - **TW-7** (the escape hatch): at the end of build Session 1, if remaining work exceeds 2.0 days or any lane is more than 50% over budget, ship Lane A (K1/K2, plus K3 if it is green) as its own `fix(373)` PR first.

### Out of scope

- **NG1: agent-side output contracts.** The controls Section 2 column schema and the Section 4 recommendation-block contract belong to #374 K8. This bundle tolerates both formats and falls back where needed; it does not change what the agents write.
- **NG2: K4–K8.** These are in #374.
- **NG3: wiring `populate-maestro-coverage.py` into production.** It stays deliberately unwired; K10 only borrows its heading tolerance.
- **NG4: installer upgrade semantics.** Deleting stale files on upgrade is out of scope; the copy loop only adds files. So is changing how the installer handles a corrupted marker (the completeness test guards the tracked manifest instead).
- **NG5: regenerating tracked example PNGs or PDF baselines (#365), or re-keying examples and baselines (#364).** Infographic JSON goldens are regenerated only where SC-8 authorizes them by file name.
- **NG6: visual redesign of any infographic template.** Only four things change: the funnel data contract (K11), the posture label (K13), the request configuration and models (K14), and the prompt hardening (K15).
- **NG7: committing real-world run output.** Tests use synthetic fixtures only.
- **NG8** *(spec)*: **migrating the render path to a different Gemini endpoint.** The public image-generation guide now documents a newer endpoint with a different request shape. This bundle pins the `generateContent` form that was verified live and records the endpoint (FR-K14.1). A migration would be a separate feature.
- **NG9** *(spec)*: **defending against a concurrent attacker (TOCTOU).** The refusal protects against pre-existing links in the adopter's own project, not against a race between check and write.
- **Follow-up candidates, deliberately not adopted** *(spec)*:
  - a warning comparand for the orchestrator-authored frontmatter `delta_counts`;
  - a provenance check before the deprecated-command `rm` in a real (unlinked) folder;
  - a presence preflight for `populate-affected-assets.py` at its call sites;
  - fixing the legacy, non-distributed copies of the request body;
  - the shipped `adapters/claude-code/agents/references/infographic-error-handling.md`, which has no 400 row and which the stock agent doesn't reference;
  - a per-file copy path that could follow links nested in a copied directory (deferred until an adopter asks; PM ruling P-9.3).

---

## Rulings

### Made in this spec

| # | Question | Ruling | Basis |
|---|---|---|---|
| **S-1** | OQ-1: the opt-in flag's final name | **`--follow-symlinks`**: long form only, no short alias, no value | It names the consequence (write where the link points) and matches Python's `follow_symlinks` (operate on the target) and the repo's kebab-case long flags. It is the working name the architect accepted. tachi's source tracks no symlinks, so the source-side `cp -L` reading can't change behavior. Runner-up: `--allow-symlinked-dest` |
| **S-2** | L-N2: refuse destinations that resolve into the tachi source tree? | **Yes, with or without the flag, on physical paths, for every destination and for the project root** (FR-K3.7) | `cp` aborts on a destination that is the source, leaving a partial install. Writing into the clone dirties it and breaks later `--version` installs. The logical-path self-install guard can be bypassed through an alias. The architect recommended it |
| **S-3** | FR-K13.1: the placeholder for a finding with no recommendation from either source | **`No recommendation available`** | Explicit and short (it fits one line of the 2.6in roadmap cell). It matches the report's existing register ("No remediation actions identified") and stays distinct from the missing-key `--` and the dash placeholder-ID predicate. `N/A` would wrongly imply "not applicable" |
| **S-4** | L-N4: does a row left out of the volumes still count in the severity mixes and the posture? | **Yes** (FR-K11.3) | Its residual exists, so dropping it would understate risk. The architect recommended it |
| **S-5** | L-N3: the status classifier's rules | Whole tokens, with `partial` matched as a token prefix and the negation tokens `no`, `not`, `none`, `nothing`; the recognized no-control set `No Control Found`, `Missing`, `None`, `Not Found`; anything else warns. The helper classifies each row once, at parse time, and replaces both copies of the row idiom. The Section 1 summary reader keeps its own matching (FR-K11.3) | This makes D-2's "otherwise → no control" and "unrecognized → warn" hold together, and fixes raw-substring negation ("known", "node", "annotated"). Research corrected the PRD's pointer to the idiom's second copy. Plan review: without the prefix rule `Partially Found` would read as found, and without `none` `None found` would too |
| **S-6** | Research: may the flag follow links nested inside a copied directory subtree? | **No. They are refused even with the flag** (FR-K3.2) | BSD `cp -r` can't write through a nested link: it aborts mid-copy and leaves a partial install. That is the same failure D-1 refuses dangling links to avoid, so the ruling applies D-1's own rationale. The flag still follows links at or above each entry, which the copy can pass through. The alternative, a per-file copy path, would add K3 cost for an unusual layout |
| **S-7** | Optional carry-forward: invoke `/bin/bash` explicitly in the K3 tests? | **Yes, with `LC_ALL=C`** (FR-K3.6) | Dev Macs put Homebrew bash 5.3 first on `PATH`. Without an explicit shell, the strict leg can silently stop testing bash 3.2 |
| **S-8** | Research: the configured image models are retired or retiring | **Move the chain to `gemini-3-pro-image`, then `gemini-3.1-flash-image`, and live-verify each** (FR-K14.4) | Google's deprecation table gives shutdowns of 2026-06-25 (both preview models) and 2026-10-02 (`gemini-2.5-flash-image`), and names these two GA models as the replacements. Without the update, G4 fails for every adopter after 2026-10-02 |
| **S-9** | Research: the baseball card reads Section 1's `risk_reduction` and totals | **Every template that carries them uses the row-derived values** (FR-K11.3). S-9 belongs to K11: if K11 is carved, the baseball card keeps today's Section 1 values, which match the uncarved funnel (P-9.5) | Otherwise two images from one run show two "Risk Reduction" figures whenever Section 1 disagrees with the rows, as it already does on the golden fixture (26.9% vs 20.1%) |
| **S-10** | Research: a shipped copy of the defective request body | **Fix it and cover it in the contract test** (FR-K14.6) | It lives in a manifest directory, so adopters receive it. Legacy copies outside the manifest are out of scope |
| **S-11** | Research: HTTP 400 has no error path today | **Surface it as an error, with the API's message and the keys sent; don't walk the chain** (FR-K14.5) | Silent degradation is how a request shape that always failed shipped unnoticed. This is the constitution's fail-loud principle |
| **S-12** | Research: a short-form controls file passed explicitly to the infographic command halts as `UNABLE TO DETECT DATA SOURCE TYPE` | **The command's explicit-path detection recognizes the aliases** (FR-K9.3) | It is the same K9 defect at a second consumer, and a one-line tolerance fix consistent with the bundle's "accept both formats" approach. Auto-detection is by file name and is unaffected |
| **S-13** | Research: NFR-2's cited guard is yaml-only and red outside the gate | **Enforce NFR-2 through the completeness test's import walk** (FR-K2.4) | The walk already exists for (d), so the assertion is one line. It is scoped to the four distributable scripts and gated in the fast workflow |

### Registered as `plan.md` inputs (the architect's domain; not ambiguities)

- **P-1**: where executive-architecture's request configuration lives (ratio 3:4). *Research recommends* a `## Gemini API Configuration` section in `.claude/skills/tachi-infographics/references/executive-architecture.md`, outside the lock markers, in the other five blocks' shape. FR-K14.2.
- **P-2**: the architect's ruling on the sanctioned FR-212-6 amendment. *Research found* it mechanically safe on the conditions FR-K15.1 lists. If it is not sanctioned, executive-architecture is carved from K15 under TW-3.
- **P-4 (reopened by research)**: with a chain of only Gemini 3 GA models, whether to restore `imageSize: "2K"`. Without it, renders default to 1K. The PRD's reason to drop it assumed a chain that included `gemini-2.5-flash-image`. Guardrail (PM ruling P-9.4): the PM has no objection to restoring it, which would restore the PDF booklet's intended print quality. It needs a live verification on **both** chain models inside the existing TW-5 render budget. If either is unverified, the default stays dropped. FR-K14.1. Refined by PM ruling P-10.3 at plan review: every shipped model × ratio, the size honored, latency headroom; settled by the eight-call W0 smoke.
- **The funnel constants and numeric semantics** (TW-1): STEP, FLOOR, volume precision, rounding, the type of `risk_reduction`, and the method for severity-mix percentages. *Research recommends* STEP = 10 and FLOOR = 30: a 10% floor cannot hold a tier label, and the template's own Tier 4 is about 30%. FR-K11.5.
- **Scaffold splitter hardening**: whether to anchor the DATA CONTENT marker and look for `FOOTER` only after it. *Research recommends* doing it in the same wave. The static test guards the boundaries either way. FR-K15.3.
- **The release-notes mechanism**: how the notices reach the *published* release notes, since release-please doesn't move CHANGELOG prose (SC-6). Two options: edit the release-please PR body before it merges, or edit the release after it publishes. Include deliver's follow-through if the release PR merges after `/aod.deliver`.
- **Where the mmdc skip and the Typst provisioning live** (NFR-7, FR-K13.4). Typst provisioning in the fast workflow lands with the K13-posture stale-data test, **never** in the first-wave cut-line commit, so a Typst setup failure can never redden the workflow that gates K1/K2. If K13-posture is carved, no Typst is added.

**For `/aod.tasks`** (the team-lead's domain):
- **OQ-5**: **closed at the tasks review** (team-lead). The #370 recipe fits, now 2 tests and 1 docstring note, and its second case uses the real MITRE catalog (FR-370.1). TW-4 did not fire.
- **A W0 smoke render**: eight calls (both chain models × 16:9 and 3:4 × default size and 2K; P-10.3, PD-3) with the known-good body, run in the scratchpad with the key loaded per NFR-5. It retires model-access risk before K14 is committed as must-ship, and costs minutes.
- **Re-cost at TW-0.** The PM's directional read (`.aod/results/product-manager-373-spec.md` §10) is that most of the spec-stage growth lands on items the valve can't carve: K2, K3, K12, the K13 recommendations and **K14, which is now above its 0.50-day ceiling and needs a bottom-up re-cost**. The floor rises by about half a day, and K11 and K13-posture sit near TW-1 and TW-2. The carve order K15 → K11 → K13-posture stays sound.

### PM rulings from the spec review (2026-09-27; binding for `/aod.plan` and `/aod.tasks`)

- **P-9.1: K14 timing.** The cut line is not bent for K14. K14 may ride a TW-7 early PR only under the three conditions in § Split valve, and it never delays Lane A.
- **P-9.2: K14 render blockage.** If K14's live renders on the GA chain stay blocked past TW-6's half day plus one retry session, K1–K3 and Group B are **not held**. K14 ships its deterministic parts under the static contract test (the body, the mapping, the chain update and the 400 path). FR-K14.3 is recorded as open, a follow-up issue is filed, and the release notes say the render path is statically verified only.
- **P-9.3: S-6 disclosure.** The nested-link narrowing is accepted on one condition: it is disclosed in the help text and README (US-2 #12), in the refusal message (US-2 #5) and in the release note (SC-6). The per-file copy path is deferred until an adopter asks.
- **P-9.4: the P-4 guardrail.** See the P-4 input above.
- **P-9.5: S-9's carve unit.** S-9 belongs to K11. If K11 is carved, the baseball card keeps today's Section 1 values, and its golden is untouched for K11.

### PM rulings from the plan review (2026-09-27; binding for `/aod.tasks` and the build)

- **P-10.1: render blockage, per model.**
  - A model unreachable at W0 triggers diagnosis and retries within TW-6's budget. W1 is never held for it.
  - P-9.2's full path applies only after the half day plus one retry session, and only if **both** chain models stay blocked.
  - If only one model is blocked for the project key, both GA models stay in the chain, because they are Google's named replacements. The blocked one is recorded as statically verified only, in the reference provenance, the PR record and the release notes, and FR-K14.3 stays open for that model with a follow-up issue. The reachable model's renders carry SC-5.
  - Under PD-3, a blocked model means 2K stays dropped, as P-9.4 already provides.
- **P-10.2: SC-5 under a K15 carve.** Only SC-5's leakage and allow-list clauses move with K15. The "6/6 templates render", "every chain model renders" and "executive-architecture in portrait on one PDF page" clauses stay with K14, and K14's render set must satisfy them on its own (FR-K14.3). Rationale: K14 creates per-template mapping behavior that did not exist before. The static test proves the blocks, but only a live render proves that the agent reads each one, and G4 promises every template.
- **P-10.3: PD-3's restore rule.** Restore `image_size: "2K"` only if it is live-verified at every model × ratio combination that ships, with the size actually honored and real-template latency headroom confirmed at W3. Otherwise the default size ships. This refines P-9.4; it does not replace it.
- **P-10.4: an early K14 ship carries the full render set** (reconciles P-9.1's early-ship condition 2 with P-10.2; architect re-review T30).
  - A TW-7 early PR that carries K14 needs FR-K14.3's full render set, made from the early PR's own code, because the files K14 shares with K13 and K15 differ there.
  - The only exception is P-10.1's per-model path. A model blocked for the project key is recorded as statically verified only, and notice 6 goes in the release notes.
  - If both models are blocked, K14 does not ride early. It ships in the main PR under P-9.2.

### PM rulings from the tasks review (2026-09-27; binding for the build)

- **P-11.1: installer scope wording.**
  - The help text (both surfaces), the README K3 section and the D-1 release note name the always-refused set as "broken, looping or wrong-type links, links nested inside an installed folder, and destinations inside the tachi source clone".
  - Wrong-type links are named, not folded into "broken" (this resolves the architect's re-review item T27).
  - "Destinations inside" replaces "links into", because containment works on physical destinations (M1, AR-1).
  - The refusal messages are unchanged.
- **P-11.2: notices when TW-7 splits the release.**
  - **The early release** carries:
    - notice 1: update the clone first, then re-run `install.sh`; it names the three skills and the populator;
    - notice 2 if K3 rides, otherwise notice 7;
    - notice 6 if K14 rides with a model recorded as statically verified only.

    The PM writes these when TW-7 fires, and PD-7's mechanism applies to that release.
  - **The main release** carries notices 3 to 6 as applicable, plus notice 2 if K3 did not ride early. It opens with one line: "Update your tachi clone and re-run `install.sh` to pick up these fixes."
  - SC-6 is verified per release with `gh release view`.
- **P-11.3: the W1-exit trip-wire re-check (T039) is accepted.** It re-evaluates TW-0..TW-2 once at W1 exit, on actuals. It is the cheapest carve point, because no K15 work has landed yet. It is mechanical, using PRD §10's thresholds and the fixed carve order K15 → K11 → K13-posture. It preserves P-9.5 (S-9 stays with K11) and P-10.2 (K14 keeps its render set). The spec's split-valve list records the rule.

---

## Dependencies

- **#374** (companion bundle, K4–K8). It doesn't block this bundle, because the parsers here are tolerant. If #374 moves SARIF generation into deterministic scripts, the K2 completeness test will require those scripts, and any helper they import, in the manifest. #374's plan should note this.
- **#370** (the FR-012b guard test). Same file as K10/K13; folded in per D-4.
- **#364**. It blocks the next minor release, which is why this bundle ships as `fix:`. This bundle lands before #364's re-key of the example baselines, so #364 absorbs the K13.1 fallback's and K10's data changes (PM ruling M5). At delivery, a handoff comment on #364 lists the example data surfaces that changed.
- **#365**. Test runs re-render tracked example PNGs, and its byte-identity suite is already red. Don't commit the PNGs or regenerate the PDF baselines.
- **Delivered foundations**: F-066 (the installer, the manifest and `--version`; this bundle adds the automated test its SC-005 promised), F-302 (`populate-affected-assets.py` and its callers), F-311 and F-315 (the MAESTRO outputs K10 reads), F-212 (the executive-architecture template and its FR-212-6 prompt lock).
- **Gemini model availability**: the GA models `gemini-3-pro-image` and `gemini-3.1-flash-image`, reachable with the "Gemini API Key" secret-store item, for the live renders.

## Assumptions

- **Base content.** Every PRD pointer was verified at `v4.48.0` (`63438d7`), which is this branch's base content. Research re-confirmed 135 of 138 pointers checked and corrected the rest (research.md).
- **The API schema.** The `generateContent` schema (published 2026-09-27) supports `generationConfig.imageConfig.aspectRatio` with the ten ratios FR-K14.2 pins (among 14), and `imageSize` with 512, 1K, 2K and 4K. The live renders re-verify the form at build (R-4).
- **GNU userland.** GNU `cp` behavior was not verified locally, so the ubuntu CI leg is its first real check. Tests assert the installer's own refusals, which are userland-independent, not `cp` messages.
- **Installer tests.** No test invokes `install.sh` today, so K3 needs a new harness (feasibility E-3).
- **Group B pre-state.** The parser and extractor modules are green at HEAD, apart from the six known #365 byte-identity reds (feasibility E-1). The out-of-gate failure set predates F-362, so it is re-recorded in a clean clone before the build.
- **Examples.** Only one shipped example carries threats, risk scores, controls and a MAESTRO table at its top level, so the live renders use a scratch copy of it. No shipped example has a Resolved Findings section, so K12 is verified on synthetic fixtures only (feasibility E-8). No tracked example uses the `###` MAESTRO heading. The six runs that do are untracked local `test-output` directories, so K10 is verified on synthetic fixtures and moves no tracked example's data.
- **The manual install path** is documented, not enforced. It skips the symlink check by definition.
