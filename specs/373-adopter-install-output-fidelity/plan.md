---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-09-27
    status: APPROVED_WITH_CONCERNS
    notes: "The plan matches PRD v1.2 and the spec: all 44 FRs, SC-1..SC-8 and the DoD map to a work stream, contract or gate, with no added product scope. Spec RC-1..RC-8 fold verified PASS. The user-facing texts and PD-4/PD-7/PD-8 are accepted; PD-3 is accepted on conditions (P-10.3). 8 required changes (MEDIUM RC-P1 cut-line workflow = completeness module only; RC-P2 K14 standalone render set; RC-P3 8-call W0 smoke + honored-size and latency rule; LOW RC-P4..RC-P8) FOLDED in plan rev. 1 by the architect (author role). PM rulings P-10.1..P-10.3, plus P-10.4 (an early K14 ship carries the full render set) given at re-review, are recorded in spec.md. TW-0 is likely to fire at central, so tasks must keep K14's render proof intact under a K15 carve. The PM verifies the RC-P fold at /aod.tasks. Details: .aod/results/product-manager-373-plan.md"
  architect_signoff:
    agent: architect
    date: 2026-09-27
    status: APPROVED_WITH_CONCERNS
    notes: "Iteration 2. Rev. 0 was CHANGES_REQUESTED (0 BLOCKING / 2 HIGH / 8 MEDIUM / 9 LOW: H1 bracketed [NEW] statuses; H2 allow-list field map; M1 physical-destination containment; M2 CI/test ownership; M3 PD-6 sequencing plus stronger A8; M4 null volumes; M5 ghost-tier shape; M6 zsh-safe loop; M7 camelCase inlineData; M8 bash 3.2 rules). A fresh re-review of rev. 1 verified 25/25 prior items resolved, several empirically in the scratchpad (loop under zsh -f -i, A8, bash 3.2 rules, normalization, the A10 hash). New: 0 BLOCKING / 0 HIGH / 1 MEDIUM / 12 LOW. MEDIUM N1 (string-prefix containment bypassed by APFS case variants and firmlinks) is FOLDED as ruling AR-1: an identity walk with [ -ef ], 17/17 cases on bash 3.2/5.3. Spec touches T23-T31 are FOLDED (T30 via PM P-10.4). Ratified: PD-1; PD-2 with conditions 3/8/9; PD-15 (no ADR; ADR-014 gets a dated F-373 note). Rulings AR-2 (the W0 other-status escalation is non-blocking) and AR-3 (K12 normalizes at the parser boundary in B1; tachi_parsers.py has no W2 writer) are binding for /aod.tasks. N2-N13 go to tasks.md. Details: .aod/results/architect-373-plan.md, .aod/results/architect-373-plan-rereview.md"
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: Adopter Install + Output Fidelity Fixes

**Branch**: `373-adopter-install-output-fidelity` | **Date**: 2026-09-27 (rev. 1 the same day) | **Spec**: [spec.md](spec.md) (PM: APPROVED_WITH_CONCERNS, RC-1..RC-8 folded)
**PRD**: [373-adopter-install-output-fidelity-2026-09-27.md](../../docs/product/02_PRD/373-adopter-install-output-fidelity-2026-09-27.md) (v1.2) · **Draft PR**: #375 (`fix(373): …`) · **Estimate**: [feasibility-check.md](feasibility-check.md) (to be re-costed at `/aod.tasks`)

**Revision 1.** This revision folds in both plan reviews:
- the architect's: `.aod/results/architect-373-plan.md`, CHANGES_REQUESTED, with H1, H2, M1 to M8 and L1 to L9;
- the PM's: `.aod/results/product-manager-373-plan.md`, APPROVED_WITH_CONCERNS, with RC-P1 to RC-P8, R-P1 to R-P8 and the binding rulings P-10.1 to P-10.3.

The plan's changes are marked **(rev. 1)**. The decision records are PD-1 to PD-20 in [research.md](research.md), and the item-by-item map is in `.aod/results/architect-373-plan-revision.md`.

**Revision 2 (after the fresh architect re-review, APPROVED_WITH_CONCERNS).** Four things were folded:
- MEDIUM N1 as ruling AR-1: source-tree containment by file identity (`[ -ef ]`), in `contracts/installer-cli.md` and `data-model.md` §2.2;
- stale-text touches T23 to T31 (spec, plan and quickstart; T30 through PM ruling P-10.4);
- the correction that every `###` MAESTRO run is an untracked local run, so K10 moves no tracked example;
- the re-review's rulings (AR-2, AR-3) and items, which are listed under "Carried to /aod.tasks", item 10.

## Summary

This is a patch bundle of ten defects across three surfaces, plus #370.

- **Group A: installer** (`INSTALL_MANIFEST.md`, `scripts/install.sh`).
  - The manifest gains the three missing skills and the populator (K1/K2).
  - A fail-closed completeness test gates it in a new fast workflow, and every manual install block derives from the manifest. The block carries no comments, because stock interactive zsh treats `#` literally (rev. 1).
  - A bash 3.2 pre-flight (K3) refuses symlinked destinations unless `--follow-symlinks` is passed. With or without the flag, it refuses dangling, looping, wrong-type and nested links, and every destination whose **physical location** is inside the tachi clone (rev. 1). It never deletes through a link.
  - The `--version` ref restore warns instead of failing silently.
- **Group B: deterministic extraction** (`tachi_parsers.py` and both extractors).
  - It gains a header alias table, a level-aware table stop rule, one placeholder predicate, one score parser and one status classifier.
  - A clamp-once residual, a **normalized** `delta_status_by_id` map (rev. 1: `[NEW]` counts as `NEW`) and one posture function are shared by both surfaces.
  - A volume-based funnel with deterministic widths and a pinned shape for degraded modes (rev. 1).
  - A recommendation fallback that reaches all three consumers, and a placeholder on every data tier (rev. 1).
- **Group C: render path** (`.claude/skills/tachi-infographics/`, templates, the agent).
  - A schema-conformant `generateContent` body, a key-to-field mapping that did not exist before, and camelCase response parsing (rev. 1).
  - A current GA model chain, walked on 404 or 403, and a loud but non-blocking HTTP 400 row (rev. 1).
  - Prompt hardening with an extractor-emitted allow-list, derived per template from what each prompt renders (rev. 1), inside the scaffold contract.

The approach is **reuse-first**:
- extend the existing parser module, workflows, golden mechanism and error table;
- clone `tachi-catalog-drift.yml` for the new gate;
- add no dependency.

The only substantial net-new code is the installer pre-flight and its test harness, which the spec requires.

## Technical Context

**Language/Version**:
- Bash 3.2+ for the installer, which must run on macOS `/bin/bash` 3.2.57 with BSD userland and on GNU bash 5.x.
- Python 3.11 in CI. The completeness test's stdlib assertion needs 3.10 or later, and it skips below that.
- Typst, only for the D-3 stale-data test.
- Markdown and YAML for agent, skill and template text.

**Primary Dependencies**: none new.
- The four distributable scripts stay stdlib-only at import (NFR-2). The new helpers use `re`, `ast`, `decimal` and `sys`.
- Tests use the existing `pytest>=8`, `pytest-timeout>=2` and `pyyaml>=6`.
- CI uses the existing actions: `checkout@v4`, `setup-python@v5`, and `typst-community/setup-typst@v5` (the precedent in `tachi-mmdc-preflight.yml`).

**Storage**: files. The repo is the product surface: manifest, scripts, templates, agent and skill text, golden JSON.

**Testing**:
- pytest in two gating workflows:
  - the new fast workflow, with **three jobs** (rev. 1): `manifest-completeness`, `extraction-fidelity` and `report-posture`;
  - the existing `tachi-pytest.yml` 2-OS matrix, for the K3 installer tests.
- Static contract tests cover agent and template text.
- Live renders are `[MANUAL-ONLY]`, with recorded evidence.

**Target Platform**:
- Adopter projects on macOS and Linux.
- The Claude Code runtime for agents.
- The Gemini API `models/{model}:generateContent` endpoint for images.

**Project Type**: single. An installer script, Python extraction scripts, and agent and template text. No service, API or UI.

**Performance Goals**:
- Each fast-workflow job finishes in under 2 minutes.
- The installer pre-flight adds under 1 second. Its checked set is about 220 paths at HEAD (33 entries, 173 subtree paths, about 11 ancestors, 5 cleanup files); rev. 1 corrects the earlier "~10³".

**Constraints**:
- NFR-2: stdlib at import.
- NFR-3: no `mapfile`, associative arrays or `readlink -f`, **plus the rev. 1 bash 3.2 implementation constraints** in `contracts/installer-cli.md`:
  - helpers are called only in a conditional, never as `local x=$(…)`;
  - no possibly-empty array is expanded under `set -u`;
  - enumeration uses `done < <(…)`, never `| while`;
  - `unset CDPATH`.
- NFR-4: no-symlink installs and `##` callers are unchanged; JSON changes are additive except corrected values and the pinned funnel shape.
- NFR-5: secrets.
- NFR-8: no PNG or PDF-baseline churn, and new tests never write into `examples/`.
- Release-please markers are preserved.
- The F-250 lock-step rule applies to each workflow.
- Commit before running the gated suites, because they clone the committed HEAD.

**Scale/Scope**:
- 44 FRs, touching about 45 files.
- About 7 new or extended test modules, 1 new workflow with 3 jobs, and 5 goldens (authorized by file name).
- The feasibility band is 4.5 / 2.5 / 7.0 days. The PM's plan review reads TW-0 as likely to fire at central: either K15 is carved, or delivery lands at the ceiling band. `/aod.tasks` re-costs it and evaluates TW-0.

## Constitution Check

*GATE: evaluated before Phase 0 and re-checked after the Phase 1 design and again after rev. 1. **PASS**: no violations, and Complexity Tracking is empty.*

- **I. General-Purpose**: the installer and extractors stay generic. No domain logic is added to shared code. PASS.
- **II. API-First**: N/A. This bundle has no API. Its interfaces are CLI and file contracts, documented in `contracts/`.
- **III. Backward Compatibility (NON-NEGOTIABLE)**: NFR-4 holds.
  - A no-symlink install copies the same files.
  - The parsers accept both the current and the corrected controls-table formats, and both bare and bracketed lifecycle statuses (rev. 1).
  - JSON changes are additive, except for the values the defects correct and the funnel shape the correction needs (always four tier objects, three reductions), which is pinned in the contract.
  - The `risk_posture` sentence stays.

  Two deliberate behavior changes are justified and disclosed.
  - D-1's refusal is a safety fix, released as `fix:` per PM ruling C-8, and SC-6's notes carry it.
  - D-3's stale-data failure is loud, with a regenerate instruction. `report-data.typ` is a per-run generated artifact.

  PASS.
- **IV. Concurrency / V. Privacy (SaaS)**: N/A as written, since tachi is a local harness. The equivalents are NFR-5 (the Gemini key only in the process environment and a header) and NFR-6 (public hygiene). PASS.
- **VI. Testing Excellence**:
  - Every deterministic fix has synthetic-fixture tests, gated in CI (NFR-7).
  - K3's cleanup safety negatives are written test-first.
  - Sibling-parity tests guard cross-surface drift.
  - Live renders are recorded.

  PASS.
- **VII. DoD**: PRD §8 applies in full, per the spec's DoD pointer. Step 3 (user validation) is SC-7, which lags the release. PASS.
- **VIII. Observability / RCA**:
  - Fail loudly: refusal messages, the restore warning, the HTTP 400 row, the exhausted-chain Error row (rev. 1), the catch-all error row (rev. 1), the stale-data panic, and aggregated drift warnings (rev. 1).
  - The RCA is recorded: K1 is the third recurrence, so a guard now exists.

  PASS.
- **IX. Git**: feature branch, draft PR #375 titled `fix(373):`, conventional commits, hooks never skipped. PASS.
- **X. Dual sign-off**: spec PM ✓; this plan carries PM and Architect; tasks carries all three. PASS.
- **Code economy (laziness ladder)**:
  - Reused: `parse_markdown_table`, `_get_finding_mitigation`, `_build_remediation`, the tolerant status idiom (lifted into one helper), the existing error table, the `catalog-drift` workflow shape, the golden mechanism, the T010 stale-data harness, and `populate-maestro-coverage.py`'s heading regex as precedent.
  - Nothing speculative: no scanner for markers, no generator for manual blocks (the blocks *reference* the manifest).
  - `phys_dest` reuses `resolve`.
  - The pre-flight is rung 7, required by the spec.

  PASS.

## Project Structure

### Documentation (this feature)

```
specs/373-adopter-install-output-fidelity/
├── spec.md                 # PM ✓ (RC-1..RC-8 folded)
├── research.md             # spec research + Plan-Stage Decisions PD-1..PD-20 (rev. 1)
├── feasibility-check.md    # team-lead estimate, TW-0..TW-7 (define stage)
├── plan.md                 # this file
├── data-model.md           # entities, classification tables, algorithms (rev. 1)
├── quickstart.md           # verification runbook: safety, tests, W0 smoke, live renders, oracle, release (rev. 1)
├── contracts/
│   ├── installer-cli.md                   # flags, pre-flight, containment, messages, exit codes, restore (rev. 1)
│   ├── manifest-completeness.md           # required set, reader parity, negatives, e2e, manual loop (rev. 1)
│   ├── extraction-data-contract.md        # JSON + report-data.typ, funnel shapes, allow-list, warnings (rev. 1)
│   └── gemini-request-and-scaffold.md     # body, key→field map, response keys, chain, error table, scaffold, K15 text, static asserts (rev. 1)
├── checklists/requirements.md
└── tasks.md                # /aod.tasks output
```

### Source Code (repository root: the surfaces this bundle changes)

```
INSTALL_MANIFEST.md                               # K1/K2 block + prose + checklist
scripts/install.sh                                # K3 pre-flight, containment, flag, restore (Lane A′)
README.md                                         # K2 manual block (W1), K3 flag docs (W2)
docs/guides/DEVELOPER_GUIDE_TACHI.md              # K2 manual blocks, stale counts, version example
scripts/tachi_parsers.py                          # K9, K12, K11, K13 shared helpers (Lane B, single owner)
scripts/extract-infographic-data.py               # K10 + PD-6 splitter (W1); K11, K12, K13, allow-list (W2)
scripts/extract-report-data.py                    # K10 (W1); K12, K13, #370 (W2)
templates/tachi/security-report/{cover,main}.typ  # D-3 posture from data + guard; funnel caption
templates/tachi/infographics/*.md                 # K14 config blocks (W1); K11/K13/K15 text (W2)
.claude/skills/tachi-infographics/references/     # gemini-prompt-construction, template-specific-formats,
                                                  #   infographic-specifications, executive-architecture (PD-1, PD-2)
.claude/agents/tachi/threat-infographic.md        # mapping, routing, error rows, allow-list, posture contract
.claude/commands/tachi.infographic.md             # FR-K9.3 alias detection
schemas/infographic.yaml                          # posture fields, allow-list
.claude/skills/tachi-report-assembly/references/typst-template-contract.md, .claude/agents/tachi/report-assembler.md
adapters/claude-code/agents/references/infographic-gemini-api.md   # FR-K14.6 shipped copy
docs/architecture/02_ADRs/ADR-014-gemini-api-optional-image-generation.md  # dated F-373 note (W4, PD-15) (rev. 1)
FR-K12.5 sweep set (7 files: output-schemas.md, report-assembler.md, threat-report.md template,
                    tachi_parsers.py, extract-report-data.py, 2 architecture READMEs)
.github/workflows/tachi-install-fidelity.yml      # NEW fast workflow, 3 jobs (PD-9)
.github/workflows/tachi-pytest.yml                # K3 modules, lock-step
tests/scripts/…                                   # PD-12 modules; fixtures under tests/scripts/fixtures/fidelity_373/
tests/scripts/fixtures/golden/*.json              # regenerated by file name only (SC-8)
```

**Structure decision.** This is a single project. Lanes follow **files, not K-items**, so each file has one writer per wave (the PRD §10 ownership rule, plus the feasibility check's corrected map):
- **Lane A** owns the installer docs, the manifest, the README and developer-guide install sections, the completeness test and **every edit to the fast workflow** (rev. 1).
- **Lane A′** owns `scripts/install.sh`, the installer tests and their helper, and `tachi-pytest.yml` in W1.
- **Lane B** owns every Python script, the Typst templates, the Typst contract, the report-assembler text and the FR-K12.5 sweep.
- **Lane C** owns every infographic text surface (templates, the tachi-infographics references, the infographic agent and command, `schemas/infographic.yaml`) and the adapter copy.
- **The tester** owns the extraction regression modules and the goldens in W2 (rev. 1).

### Lane and file ownership per wave: test modules and CI files (rev. 1, M2, PD-20)

Source files follow the lane rule above. This table assigns the files it did not cover. Each row has **one writer per wave**. A module's author writes it, and Lane A's **wiring commit** bundles it with its workflow entries (paths and invocation), so lock-step holds and no module is ever ungated.

| File | W0 | W1 | W2 | W3 |
|---|---|---|---|---|
| `.github/workflows/tachi-install-fidelity.yml` | — | **Lane A**: A-1 creates it (the cut line: `manifest-completeness` job only), A-2 adds the `extraction-fidelity` job with the 4 pre-existing modules and `examples/**`, A-3 adds the contract module and `adapters/claude-code/**` | **Lane A**: wiring commits for the sibling-parity module; the `report-posture` job (Typst) with its module, only if K13-posture ships; `schemas/taxonomy/*.yaml` if #370's catalog-backed test lands | Lane A (convergence fixes only) |
| `.github/workflows/tachi-pytest.yml` | — | **Lane A′** (K3 modules, `# F-373` markers, header-log line) | **Lane A** (convergence) | Lane A |
| `tests/scripts/test_install_manifest_completeness.py` | — | **Lane A** | Lane A | — |
| `tests/scripts/test_install_sh_symlink_preflight.py`, `test_install_sh_ref_restore.py` | — | **Lane A′** | Lane A | Lane A |
| `tests/scripts/install_sh_helpers.py` | **tester** (sandbox builders) | **Lane A′** | Lane A | — |
| `tests/scripts/test_tachi_parsers.py` | — | **Lane B1** (test-first unit tests for the new helpers) | **tester** | tester |
| `tests/scripts/test_extract_report_data.py` | — | **Lane A**, in A-2 only (PD-8's mmdc skip and temporary copy) | **tester** (K12/K13.1 regression tests and #370's two tests) | tester |
| `tests/scripts/test_extract_infographic_data.py`, `test_extractor_contract_fixes.py` | — | — | **tester** | tester |
| `tests/scripts/test_extraction_sibling_parity.py` | — | — | **tester** (creates) | tester |
| `tests/scripts/test_gemini_request_contract.py` | — | **Lane C1** (creates; A1–A8) | **tester** (A9–A11) | tester |
| `tests/scripts/test_report_posture_contract.py` | — | — | **Lane B2b** (creates; tied to the `main.typ` guard) | tester |
| `tests/scripts/fixtures/fidelity_373/**` | **tester** | tester | tester | tester |
| `tests/scripts/fixtures/golden/*.json` | — | — | **tester**: a wave-final W2 commit, authorized names only (SC-8), reviewed at the W2 checkpoint | tester (only if K15 iterations change prompt text) |
| `pyproject.toml` | — | — (no new markers needed) | — | — |

**W1 commit order:** A-1 (cut line) → A-2, immediately after and **before any Lane B1 commit**, so the R-3 safety net is active before the parser changes → the other lanes' commits → A-3.

## Phase 0: Plan-Stage Decisions (all registered inputs resolved) **(rev. 1)**

The full Decision, Rationale and Alternatives records are in [research.md § Plan-Stage Decisions](research.md). Summary:

| # | Input | Ruling |
|---|---|---|
| PD-1 | **P-1**: where executive-architecture's config lives | A `## Gemini API Configuration` section in `executive-architecture.md`, outside the lock markers, in the five blocks' YAML shape, with `aspect_ratio: "3:4"`. **Ratified** |
| PD-2 | **P-2**: the FR-212-6 amendment | **Ratified with amendments**: nine conditions. Condition 3 is reworded (IDs from CALLOUTS; names from LAYER STACK, FLOW EDGES or CLUSTERS); the amendment is one paragraph; condition 8 (generic label examples) and condition 9 (A10 hash proves the amendment additive) are added |
| PD-3 | **P-4**: `imageSize` (rev. 1) | P-10.3's rule. W0 makes eight calls (2 models × 16:9/3:4 × default/2K). Restore 2K only if all four 2K calls return a larger image. 3:4 at the default size must succeed on both models. W3 drops 2K if a real 2K render exceeds about 45 s |
| PD-4 | Funnel constants | **STEP = 10, FLOOR = 30**; integer widths; clamp with `Decimal` bounds, then round half-up |
| PD-5 | Numeric semantics (rev. 1) | `parse_score` into Decimal; volumes at 1 dp, half-up; reductions derived from the emitted volumes; `risk_reduction` is the Tier 2→4 value; mixes are integer counts; null when volumes are unavailable |
| PD-6 | Splitter hardening (rev. 1) | **W1, Lane B1**. Anchored marker; `FOOTER` only after it; the no-newline fallback is dropped; byte-identical today; A8 strengthened |
| PD-7 | Release notes (rev. 1) | Seven notices with conditions. Edit the release-please PR body just before merge (confirmed: the release body comes from it), then a post-publish `gh release edit` backstop. Run any polish script first. Verify with `gh release view` |
| PD-8 | mmdc skip and Typst (rev. 1) | The skip and temporary copy land in wiring commit A-2 (Lane A). Typst goes in the separate `report-posture` job, W2 only, and only if K13-posture ships. The positive control checks that the panic text is absent. The PR calls it #365-adjacent |
| PD-9 | The fast workflow (rev. 1) | Three jobs. The cut-line commit invokes only the completeness module. `paths:` land with the tests that read them (README, dev guide, `adapters/claude-code/**`, …) |
| PD-10 | The K3 pre-flight (rev. 1) | Origin sets; link classes (cleanup-only, unresolvable incl. wrong type, nested, inside/outside); **physical-destination containment** replaces the link-only source-tree class; the bash 3.2 constraints; RC-P4 messages |
| PD-11 | The ref restore | The trap records the status, warns on a failed checkout, and exits with the recorded status. **Verified** on bash 3.2 and 5 |
| PD-12 | Test layout (rev. 1) | Modules assigned to workflow jobs; fixtures under `fidelity_373/`; manifest-driven e2e copy; harness details |
| PD-13 | Contract names (rev. 1) | Posture fields in every infographic JSON (executive-architecture through its early-exit builder); four funnel tier objects with `ghost`; three reductions; `allow_list`; Typst `risk-posture-{level,label}` |
| PD-14 | Model chain (rev. 1) | `gemini-3-pro-image` → `gemini-3.1-flash-image`. **Walked on 404 or 403**. A 400 is not walked; 429 and timeouts stay single-attempt; there is a catch-all Error row. An exhausted chain logs at Error, naming each model tried. The response is read from `inlineData` (camelCase) |
| PD-15 | ADR | **None**; **ratified on condition** of a dated F-373 note in ADR-014 (W4). ADR-017 is cited |
| PD-16 | K12 statuses (new) | Normalize `[NEW]` to `NEW`. The empty-map and ID-set checks are warnings, only on baseline runs with a Status column |
| PD-17 | K15 allow-list (new) | Per-template `finding_ids`: the full set for baseball-card and system-architecture, per-layer IDs for maestro-stack, none for the funnel and heatmap, callouts for executive-architecture. One common `component_names` set. Final merged wording |
| PD-18 | Funnel shape (new) | Four tier objects with `ghost`; three reductions; volumes unavailable → nulls on both templates |
| PD-19 | Placeholder (new) | `No recommendation available` on every data tier; the prefix fallback stays tier-1 only |
| PD-20 | Test/CI ownership (new) | One writer per wave; Lane A's wiring commits bundle each module with its workflow entries; A-1 → A-2 → … → A-3 |

**Agent context update.** `.aod/scripts/bash/update-agent-context.sh` does not exist in this template version, so the step is skipped. CLAUDE.md is untouched (its "Recent Changes" stays a one-line pointer).

## Technical Approach: work streams → wave sketch (the team-lead finalizes at `/aod.tasks`) **(rev. 1)**

Dependency spine: **W0 → W1 (the cut line lands first) → W2 → W3 → W4**. Lanes share no file within a wave; test modules and CI files follow the ownership table above.

- **W0 (serial, about 0.25 d): pre-state and de-risking.**
  - Record the literal pytest totals for every module about to be gated, plus `tachi-pytest.yml`'s subset, in a **clean scratch clone** at the W0 commit. The out-of-gate set predates F-362 and is re-recorded, not assumed.
  - Take the Group B oracle **pre-snapshot** in a scratch clone: both extractors × the 12 tracked example directories that have source artifacts × every template. A working tree may also hold untracked `test-output` runs; they are out of scope, and a scratch clone doesn't see them.
  - Run the **W0 smoke render** (P-10.3, RC-P3).
    - It makes **eight calls**: both GA models × {16:9, 3:4} × {default, 2K}, with the key loaded per NFR-5.
    - Record the status, whether an image came back, the pixel dimensions, the response time and the response key casing.
    - It settles PD-3 and retires model-access risk.
    - A blocked model follows P-10.1 (RC-P8): diagnose and retry within TW-6's budget. **W1 is never held.** The smoke precedes Lane C1's K14 commit and gates nothing else.
  - The tester scaffolds the synthetic fixtures: the spec's US-3a and US-3b list, the strong-reduction funnel fixture, and the rev. 1 fixtures:
    - bracketed-status and Status-less Section 7;
    - 3-tier, threats-only and volumes-unavailable funnels;
    - `Partially Found` and `None found` statuses;
    - unparseable scores.

    The symlink sandbox builders go in `install_sh_helpers.py`.
- **W1: foundations (four lanes).**
  - **Lane A, the cut line (A-1).** Committed green **before any other lane's commit lands**, and shippable alone from that commit (PM ruling P-9.1: never bent). It contains:
    - K1/K2: the manifest block, prose (including the R-P7 `:71` wording), tables, dependency note, stale-claim fix and checklist wording;
    - the comment-free manual blocks in README and the developer guide (FR-K2.2), with the developer guide's combined fence split;
    - `test_install_manifest_completeness.py`, with its negatives, the manifest-driven e2e, S-13 and the zsh variant;
    - `tachi-install-fidelity.yml` with **only** the `manifest-completeness` job and its paths (RC-P1), **without Typst**.
  - **Lane A, wiring A-2** (immediately after A-1, before any Lane B1 commit): PD-8's mmdc skip and temporary copy in `test_extract_report_data.py`, plus the `extraction-fidelity` job with the four pre-existing modules and `examples/**`. This is the bare-ubuntu first run the plan's risk list wanted; it is now outside the cut line.
  - **Lane A′: K3 core.**
    - The pre-flight: origin sets, the link classes, physical-destination containment, the refusal, `--follow-symlinks`, the opt-in report, the cleanup skip, the trap fix, and both help surfaces with the RC-P4 texts.
    - The test-first safety negatives, then `test_install_sh_*`, including the rev. 1 cases. It iterates locally on `/bin/bash` 3.2.57 with `LC_ALL=C`.
    - `tachi-pytest.yml` lock-step, with `# F-373` markers.
  - **Lane B1: `tachi_parsers.py` as the single owner, in sequence.** It also writes the test-first unit tests in `test_tachi_parsers.py`.
    1. K9: the alias table, the level-aware stop rule, the placeholder predicate and `parse_score` (K9's `_score_to_band` uses it).
    2. K12: `delta_status_by_id` with normalization and scoped checks (PD-16), and the 4b|4c resolved parser, including its docstring (sweep).
    3. K11 parser (the **K11 carve unit**; see below): the inherent read, the status classifier (stored per row; it replaces both row-idiom copies) and the clamp-once.
    4. K13: the posture function.

    Then the K10 shared header match (`match_heading` with `start_line`) in both extractors, and the **PD-6 splitter hardening** in `extract-infographic-data.py`. Lane B1 is the only writer of the extractors in W1.
  - **Lane C1: K14.**
    - The reference: the body, the key→field table, the chain and walk set (PD-14), the camelCase response keys, the error rows, executive-architecture routing, and provenance (endpoint, models, ratios, dates, the `Retired models:` line).
    - The five template `## Gemini API Configuration` blocks.
    - Executive-architecture's config (PD-1).
    - The agent: the skill-reference pointer, the mapping instruction and the error rows.
    - The adapter copy (FR-K14.6).
    - `test_gemini_request_contract.py` (A1–A8, with `IMAGE_SIZE_RESTORED` pinned from W0).
    - Wiring **A-3** (Lane A) adds it with `adapters/claude-code/**`.
- **W2: consumers and text (four lanes plus the tester).**
  - **Lane A**: the README K3 docs, which reuse the help text's scope sentence (P-9.3). Convergence on both CI legs. The W2 wiring commits. Advisory review by `security-analyst` of the pre-flight (deny-by-default, no delete before the check, destination containment).
  - **Lane B2a, `extract-infographic-data.py`**:
    - the K11 funnel: volumes, mixes, widths, reductions and warnings, in the pinned shapes (PD-18), plus S-9's baseball-card totals;
    - K12 `delta_counts`;
    - K13 posture emission, executive-architecture included through its early-exit builder;
    - the allow-list emission (`compute_allow_list`, PD-17), executive-architecture included;
    - aggregated warnings (R-P6).
  - **Lane B2b, `extract-report-data.py`, `cover.typ`, `main.typ` and the Typst contract**:
    - K12 wiring (normalized badges);
    - K13.1 recommendations on the finding field (the prefix and placeholder on tier 1), **plus the placeholder on every data tier** (PD-19), and the drift warning;
    - K13 posture emission, the cover rendering the label and level from data, and the `main.typ` guard (placed between `:117` and `:147`);
    - the funnel caption, with the R-P5 clause;
    - the Typst contract's REQUIRED note and the report-assembler deprecation-note line;
    - #370's docstring (its two tests go to the tester);
    - the FR-K12.5 sweep of the remaining text sites;
    - `test_report_posture_contract.py`, only if K13-posture is in.
  - **Lane C2: infographic text.**
    - K11 tier text and width rule, keyed on `ghost`; the 0% note keyed on a numeric 0.0; removal of the contradicting text;
    - K13 posture text: the badge shows the label alone, the prompt, the reference prompt, placeholders, the spec reference, the agent's JSON contract and `schemas/infographic.yaml`;
    - K15 hardening in the five templates, the reference and executive-architecture (the PD-2 amendment and agent section), with the final wording (PD-17), within the scaffold rules;
    - K9.3 command detection.
  - **Tester**: K9–K13 regression tests, #370's two tests, sibling parity (including bracketed statuses) and the K15 static assertions A9–A11. **Wave-final:** the authorized golden regeneration, so the fast workflow is green entering Session 2.
  - **Architect checkpoint (P0, end of W2)**: parser semantics, the regenerated goldens by file name, and oracle attribution rules. Then the NEXT-SESSION handoff and the **TW-7 check**.
- **W3: integration and live verification.**
  - Commit and push; both CI legs and all fast-workflow jobs must be **visibly** green on #375.
  - The co-fired gates (`mmdc-preflight`, `catalog-drift`, `maestro-coverage`) must be green.
  - The oracle **post-snapshot** and `oracle-diff.md`, attributed **by field class × K-item with per-example counts** (PM §9.4). The expected movers are:
    - K10: none among the tracked examples (every `###` MAESTRO run is an untracked local `test-output` directory), so K10 is proven on synthetic fixtures;
    - the M5 examples;
    - `agentic-app`'s delta counts and badges (K12);
    - the posture and `allow_list` fields everywhere.
  - **K14 render set** (P-10.2, RC-P2), through the agent end to end, in a scratch clone on a scratch copy of the MAESTRO reference example:
    - (a) if K15 ships, its first-iteration renders double as K14's per-template renders;
    - (b) if K15 is carved, each of the six templates renders once, with no leakage check and no iteration;
    - (c) either way, at least one render uses the **fallback** model, and executive-architecture (3:4) lands on **one** portrait page of a scratch PDF;
    - (d) a blocked model is recorded as statically verified only.

    If 2K was restored and a 2K render exceeds about 45 s, 2K is dropped in one commit (P-10.3).
  - **K15 renders** (only if K15 ships): once per template, at most two iterations (TW-5). The goldens are re-regenerated only if an iteration changes prompt text.
  - Each record gives the status, time, dimensions, a visual check, the endpoint, model and date, extension-to-bytes agreement and the response key casing.
  - `code-reviewer` full-diff review, then an architect checkpoint.
- **W4: close-out.**
  - Docs sweep, including the **dated F-373 note in ADR-014** (PD-15).
  - PM release-notes text: the seven conditional notices of PD-7, generic per NFR-6.
  - CHANGELOG `Unreleased` prose.
  - The PR body:
    - the changed examples;
    - the 4b disposition ledger;
    - the live-render records;
    - the golden authorization list;
    - PD-8 described as #365-adjacent hygiene.
  - Draft the #364 handoff comment.
  - Confirm the `fix(373):` title.

**K14 early-ship.** K14 may ride a TW-7 early PR only under PM ruling P-9.1's three conditions:
- its static test is green;
- FR-K14.3's full render set is recorded, made from the early PR's own code (each template once, each chain model at least once, executive-architecture on one portrait PDF page); the only exception is a model blocked for the project key, recorded as statically verified only with notice 6 (P-10.1), and if both models are blocked, K14 does not ride early (P-10.4);
- its commits separate cleanly from the K13/K15 edits in shared files.

The early PR then carries A-1 and A-3 with Lane C1's commits. A render blockage follows PM rulings P-9.2 and P-10.1:
- ship the deterministic parts;
- leave FR-K14.3 open for the blocked model;
- file a follow-up;
- put a statically-verified note in the release notes.

**K11 carve unit (rev. 1, PM §9 item 3).** K11 is the inherent read, the status classifier's replacement of both row idioms, the clamp-once (Lane B1 step 3), the funnel (B2a), S-9's baseball-card totals, K11's template and caption text (C2, B2b), notice 4, and the funnel and baseball-card goldens for K11. If TW-0 or TW-1 carves it:
- the parser keeps today's unclamped residuals and substring idiom;
- `parse_score` still serves `_score_to_band` (K9);
- data-model §5's "after the clamp" reads as "today's unclamped counts" (data-model §3).

**Sessions** (clean-session phasing, per the feasibility check):
- the plan stage in this session;
- build Session 1: W0–W2, ending in a NEXT-SESSION handoff;
- build Session 2: W3–W4;
- then `/aod.deliver`.

## Review Resolutions

### Spec-review concerns (RC-1..RC-8, R-a..R-g)

All required changes were folded into spec.md before this plan. The plan realizes them as follows:
- **RC-1 (DoD pointer + M5 note)**: PD-7 carries the full notice set. W4 has the PM write it.
- **RC-2 (K14 doesn't bend the cut line)**: the W1 cut line is Lane A's A-1 only. K14 is Lane C1, with the early-ship conditions above.
- **RC-3 (non-blocking 400)**: PD-14, plus the error-table row in `contracts/gemini-request-and-scaffold.md`.
- **RC-4 (verification methods)**:
  - US-4a #1–#4 and US-3a #10 are static assertions in `test_gemini_request_contract.py`;
  - US-1 #3 is a fast-workflow test that runs the README loop (bash, and zsh when present) and asserts that the three blocks match, plus a one-time `/bin/bash` 3.2 and zsh record.
- **RC-5 to RC-8**: realized in the contracts. The D-1 note text is in `contracts/installer-cli.md`.
- **R-b**: the W0 smoke render, now eight calls.
- **R-g**: Typst never lands in W1, and it has its own job (PD-8).
- **R-d**: the deliver follow-through (PD-7).
- **R-a, R-c, R-e and R-f** are in the spec.

### Plan-review resolutions (rev. 1)

| Item | Resolution | Where |
|---|---|---|
| **H1** K12 bracketed statuses; unscoped assertion | Normalization; checks scoped to baseline runs with a Status column; warnings only; two fixtures | PD-16; data-model §6; extraction contract |
| **H2** allow-list field map | Per-template `finding_ids` from what each prompt renders; a common `component_names`; final wording | PD-17; data-model §8; gemini contract |
| **M1** containment misses physical destinations | `phys_dest` per entry and cleanup file; verified on 7 cases × 2 shells | PD-10; data-model §2.2; installer contract |
| **M2** CI/test ownership; the cut line depends on PD-8 | The ownership table; wiring commits A-1/A-2/A-3; three jobs; paths | PD-9, PD-20; this plan |
| **M3** PD-6 races C2; A8 too weak | PD-6 in W1 (B1); strengthened A8, verified on the templates and the probe | PD-6; gemini contract A8 |
| **M4** volumes unavailable → false 0.0 | Nulls on both templates; one warning | PD-18; data-model §4.3 |
| **M5** degraded funnel shape unpinned | Four objects with `ghost`; three reductions; examples | PD-18; data-model §4.1–4.2; extraction contract |
| **M6** manual loop fails in stock zsh | Comment-free block, verified under zsh stdin and bash 3.2; static check; zsh variant | manifest contract |
| **M7** response keys | `inlineData`/`mimeType` (SDK spelling accepted); A1/A4; W0 casing; W3 through the agent | PD-14; gemini contract |
| **M8** bash 3.2 constraints | The constraints table; `local`; the call-site rule | PD-10; installer contract |
| **L1–L9** | Folded into the artifacts (see the revision summary); none carried | research, data-model, contracts |
| **RC-P1** the cut line is K1/K2 only | A-1 invokes only the completeness module; A-2 brings the pre-existing modules with PD-8 | PD-9, PD-20; W1 |
| **RC-P2** K14's standalone render set | Rules (a)–(d) | W3; gemini contract; quickstart §4 |
| **RC-P3** the eight-call W0 and the honored-size and latency rule | PD-3 per P-10.3 | PD-3; gemini contract; quickstart §4 |
| **RC-P4** installer wording | The help text and remedy verbatim; the optional items adopted | installer contract |
| **RC-P5** paths | README, the dev guide, `adapters/claude-code/**` (and `schemas/taxonomy/*.yaml` with a catalog-backed #370 test) | PD-9; manifest contract |
| **RC-P6** the full notice set | Seven conditional notices; polish-before-prepend; `gh release view` check | PD-7; quickstart §7 |
| **RC-P7** placeholder on every tier | PD-19 | data-model §7; extraction contract |
| **RC-P8** W0 blockage wording | The P-10.1 procedure | quickstart §4 |
| **R-P1** PR-body timing | Adopted and **confirmed** (the release body comes from the merged PR body) | PD-7 |
| **R-P2 / L2** 403 | **Walk on 403** (reconciliation 1) | PD-14 |
| **R-P3** exhausted chain | Error, with a summary naming the models tried | PD-14; gemini contract |
| **R-P4 / PD-2 cond. 3** wording | One merged final text (reconciliation 2) | PD-17, PD-2 |
| **R-P5** caption clause | Adopted, only if K11 ships | extraction contract |
| **R-P6** warning volume | Aggregated per class | data-model §4.5; extraction contract |
| **R-P7** `:71` wording | Adopted | manifest contract |
| **R-P8** PD-8 disclosure | Adopted | PD-8; W4 |
| **P-10.1 / P-10.2 / P-10.3** | Binding; realized in PD-3, PD-14, W0, W3 and quickstart §4 | as listed |

## Verification & Gates **(rev. 1)**

1. **W0 pre-state** (`specs/373-*/test-results-prestate.md`): literal totals for every newly gated module and for `tachi-pytest.yml`'s subset, from a clean clone. Plus the W0 smoke record (eight calls).
2. **The cut-line gate (A-1)**: the completeness test is green on the fixed manifest and red on each negative (the synthetic matrix). The fast workflow's **`manifest-completeness` job, the only job at A-1**, has run on #375 and is green.
3. **The fast workflow** (PD-9), three jobs, each green on committed HEAD:
   - `manifest-completeness`: `test_install_manifest_completeness.py`;
   - `extraction-fidelity`:
     - from A-2: `test_tachi_parsers.py`, `test_extract_infographic_data.py`, `test_extract_report_data.py` (only its five mmdc cases skip) and `test_extractor_contract_fixes.py`;
     - from A-3: `test_gemini_request_contract.py`;
     - from W2: `test_extraction_sibling_parity.py`;
   - `report-posture` (W2, only if K13-posture ships): `test_report_posture_contract.py`, with Typst and `TACHI_REQUIRE_TYPST=1`.
4. **The `tachi-pytest.yml` 2-OS matrix**: the K3 modules are green on bash 3.2 (BSD) and bash 5 (GNU), including the rev. 1 cases (containment through the clone's parent, a vendored clone, a wrong-type link, a dangling deprecated-command link, a no-link install on bash 3.2). The first GNU `cp` evidence is the ubuntu leg, and tests assert only installer-authored text. The existing 16 modules stay green.
5. **Co-fired gates** stay green:
   - `tachi-mmdc-preflight`: the extractor stays stdlib-only and raises nothing new before `render_mermaid_to_png`;
   - `tachi-catalog-drift`: #370 and K13 don't change loader behavior;
   - `tachi-maestro-coverage`: it fires on the parsers and extractors, which makes it K9/K10's net.
6. **The golden gate**: only the SC-8-authorized goldens change, each hunk is attributed to a K-item, and the baseball card changes for K11 only while K11 ships (PM ruling P-9.5). The regeneration is the tester's wave-final W2 commit, re-run in W3 only if K15 iterations change prompt text.
7. **The oracle gate**: `oracle-diff.md` attributes 100% of the data-layer diffs, grouped by field class × K-item with per-example counts. Run-specific fields (`generation_timestamp`, absolute paths) are normalized. No PDF baseline or tracked PNG changes (`git status` is clean of `examples/**` before each commit).
8. **Live evidence** (`[MANUAL-ONLY]`): the W0 smoke (eight calls), the K14 render set (P-10.2: six templates, the fallback model at least once, executive-architecture on one PDF page), the K15 per-template renders when K15 ships, and the 2K latency check. All are recorded in the PR, with no images committed.
9. **Deliver**:
   - the published release notes carry the applicable notices, verified verbatim with `gh release view` (PD-7);
   - the release-please patch PR is verified;
   - the #364 handoff comment is posted;
   - the ADR-014 note is merged.

## Risks (delta over PRD and spec; plan-stage additions, rev. 1)

- **GA model access for the project key is unverified.** K14 can't be carved, so a blockage would hold the bundle. *Mitigation:* the eight-call W0 smoke retires it before any K14 commit. PM rulings P-9.2 and **P-10.1** pre-decide the outcome, per model, and W1 is never held.
- **The newly gated modules may be red on the bare ubuntu runner for reasons besides mmdc**, such as a path, locale or font assumption. *Mitigation:* the W0 pre-state is recorded in a clean clone. Wiring commit A-2 is their first ubuntu run, **outside the cut line** (RC-P1), and it lands before any parser change. Anything red that is not attributable to this bundle is triaged there.
- **The pre-flight is correct on BSD but differs on GNU**, for example in `find` ordering or `readlink` output. *Mitigation:*
  - results are classified and sorted before printing;
  - only the portable primitives are used;
  - tests assert installer text only;
  - the ubuntu leg runs on every push;
  - K3 iterates locally on bash 3.2.57;
  - the rev. 1 bash constraints remove the 3.2-only crash modes.
- **Scaffold drift from the four items that edit the five templates** (K11, K13, K14, K15). *Mitigation:* PD-6 lands in W1, before any text edit. The strengthened A8 runs from W1. No fence is allowed under the prompt heading.
- **K15 non-determinism** (R-5): at most two iterations (TW-5); residual leakage becomes a follow-up issue. The allow-list is data referenced by field name, and its wording is scoped to IDs and names, so it does not suppress titles or metrics (PD-17).
- **A stale `report-data.typ` in adopters' existing run dirs** now fails compilation. This is intended (D-3), but new. *Mitigation:* the panic message names the fix, and release notice 5 says so.
- **Estimate growth on non-carvable items** (the PM's §10 read, with K14 above its ceiling and the rev. 1 additions: eight W0 calls, up to seven W3 renders under a K15 carve, the containment rework). *Mitigation:* the `/aod.tasks` bottom-up re-cost, TW-0 evaluated on the re-cost, TW-7 at the end of Session 1, and the carve order K15 → K11 → K13-posture.
- **(rev. 1) Adopter keys without entitlement to the primary model.** *Mitigation:* the chain walks on 403. The 429 message tells the adopter how to put the fallback model first.
- **(rev. 1) A malformed release-please PR-body edit can make the release parse fail.** *Mitigation:* PD-7 pins the edit to the notes region and to "the last action before merge", and the post-publish edit remains the backstop.
- **(rev. 1) Human availability for W3's visual checks** (PM §9 item 7). *Mitigation:* scheduled at `/aod.tasks`.

## Carried to /aod.tasks (rev. 1)

These are deliberately left to the team-lead's task stage; each is a scheduling or enumeration decision, not a design gap:
1. **TW-0 bottom-up re-cost and evaluation** (PM §9 items 1 and 6). K14 now includes the eight-call W0 smoke and up to seven W3 renders under a K15 carve. Also TW-1 to TW-4, and whether TW-0 carves K15.
2. **OQ-5 and TW-4**: confirm #370's recipe. Decide whether its second case loads the real MITRE catalog; if it does, wiring adds `schemas/taxonomy/*.yaml` to `paths:`.
3. **Per-module test-case enumeration**, including every rev. 1 case listed in the contracts.
4. **Agent assignment per lane** and the 80% load check, with the ownership table as the constraint.
5. **The oracle attribution format** (field class × K-item, per-example counts) and its 12 × 6 run list (tracked examples only).
6. **Scheduling the maintainer** for W3's visual checks (PM §9 item 7).
7. **Final user-facing wording**: the release notices (PM, W4), the README K3 section (reusing the help text), and the ADR-014 note.
8. **The golden-regen commit's exact file list**, derived from which K-items survive TW-0 (SC-8's by-name authorization).
9. **Deliver follow-through**: PD-7's ordering and verification, and the #364 handoff comment (PM §9 item 9).
10. **Architect re-review rulings and items (rev. 2).** These are binding for `tasks.md`; the details are in `.aod/results/architect-373-plan-rereview.md` §3 and §6.
    - **AR-2.** The W0 escalation for an "other status" (a refusal other than 404 or 403) is non-blocking. Lane C1 commits K14 with the 404/403 walk set, and the architect amends it, if needed, by the end-of-W2 checkpoint. The 3:4-at-default-size check stays blocking, but only for executive-architecture's configuration.
    - **AR-3.** K12 normalizes at the parser boundary in B1 during W1: `delta_status_by_id`, the tier-3 `parse_threats_findings` statuses and `compute_delta_counts`. R-P6's parse-time warning aggregation is B1's too. `compute_allow_list` lives in `extract-infographic-data.py`. So `tachi_parsers.py` has **no W2 writer**.
    - **N3.** Each fixture tree joins `paths:` in the wiring commit of the first module that reads it: `tests/scripts/fixtures/exec_arch/**`, `golden/**`, `fidelity_373/**`, and `report_data/**` if used.
    - **N4.** Gate `test_executive_architecture_payload.py` in A-2, with its W0 totals recorded. W0 also records the roughly 20 ungated parser- and extractor-consuming modules, and the W2/W3 checkpoints re-run them in the scratch clone and attribute any delta.
    - **N9.** A K14 early-ship PR carries A-2 as well as A-1 and A-3. Name a triage owner for any pre-existing red in A-2, and state whether B1 may commit while that red is open.
    - **The A10 strip rule, verbatim.** Split on blank lines between the markers, drop the paragraph after `IMPORTANT:`, and hash the rest.
    - **Task-level items:**
      - N6: normalization order (strip the emphasis run, then one `[…]` pair, then the emphasis run again; fixtures for `**[NEW]**` and `` `[NEW]` ``);
      - N7: accept and attribute `has_baseline`'s stateless false positive;
      - N8: optionally assert exactly one line-start `FOOTER` after the marker, and pin whether PD-6 keeps the bare `^DATA CONTENT` fallback;
      - N10: the `ALLOWED IDS AND NAMES` line is written only for the five scaffolded templates and the reference path; watch its length on large runs at W3;
      - N11: optionally refuse a clone located under a directory entry;
      - N13: align the funnel `source` strings with the one-row-set wording.

    N1 (identity containment, AR-1) and N12 (pin `/bin/bash`) are already folded into `contracts/installer-cli.md` and `data-model.md` §2.2.

## Complexity Tracking

*No constitution violations; the table is intentionally empty.*
