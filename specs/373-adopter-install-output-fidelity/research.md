# Research Summary: Adopter Install + Output Fidelity Fixes (Feature 373)

**Date**: 2026-09-27 · **Branch**: `373-adopter-install-output-fidelity` (base content v4.48.0 `63438d7`) · **PRD**: `docs/product/02_PRD/373-adopter-install-output-fidelity-2026-09-27.md` (v1.2)

**Method.** Four parallel research legs, all read-only in the working tree. Experiments ran only in the session scratchpad, against copies. No pytest, extractor, installer or render ran in the repo, and no Gemini call was made with a key. Full leg reports (gitignored):
- `.aod/results/research-373-kb.md`: knowledge base, delivery retros and KB entries recovered from git history
- `.aod/results/research-373-codebase-installer.md`: installer, CI and test conventions, with 10 scratchpad `cp`/bash experiments
- `.aod/results/research-373-codebase-extraction.md`: extraction, report and render surfaces
- `.aod/results/research-373-architecture-web.md`: ADRs, the constitution and external sources

The orchestrator also checked two claims directly: the Gemini `generateContent` schema (the public discovery document) and the Gemini model deprecation table.

---

## Headline findings

1. **Every configured image model is shut down or about to be.** Per the Gemini deprecations page (checked 2026-09-27), the templates' `model: gemini-3-pro-image-preview` and `fallback_model: gemini-3.1-flash-image-preview` shut down on **2026-06-25**. The reference's `default_model: gemini-2.5-flash-image`, the only GA model in its fallback chain, shuts down on **2026-10-02**. Google's replacements are **`gemini-3-pro-image`** and **`gemini-3.1-flash-image`** (GA 2026-05-28, no shutdown announced). Without a model update, every render fails after 2026-10-02 even with K14's request-body fix. The PRD's central delivery date is 2026-10-02.
2. **No code reads the templates' Gemini configuration blocks.** The agent sends the reference's hard-coded body (16:9 plus `imageSize`) for every template, executive-architecture included. The reference's no-scaffold routing sends executive-architecture to a template file that does not exist, and then to a 16:9 fallback prompt. So K14 must *create* the key-to-field mapping, not just fix values (this corrects the premise of PRD FR-K14.2).
3. **The installer can't write through nested links, even with the flag.** On BSD `cp -r`, a symlinked subdirectory nested in a copied subtree aborts the copy ("Not a directory"), and so does a nested symlinked file ("Permission denied"), leaving a partial install. Links at or above an entry's destination (ancestors, or the entry itself) are written through. D-1's "a leaf-file link is written through" holds only for the single-file branch.
4. **A destination inside the tachi source aborts `cp`**, with "identical (not copied)", leaving a partial install. The self-install guard compares logical paths, so an alias to the clone bypasses it. Refusal regardless of the flag, on physical paths, fixes both.
5. **The K1 omission is the third occurrence** (after two 2026-04-12 fixes that each added prose warnings but no guard). No prior manifest fix told adopters to re-install. The completeness gate and the release-note notice are both load-bearing.

---

## Knowledge Base Findings

The live KB is partial: two `/aod.update` syncs wiped entries, which were recovered from git history (`f74ba0f`, `84f45bc`). "KB-037" is ambiguous (two different entries share the ID), so cite the test or the ADR, not the bare ID.

- **Installer.** F-066 promised "restore the source repo on 100% of exit paths" (SC-005) and bash 3.2 portability, but no automated installer test exists. FR-K3.5/K3.6 close a promise that was never tested. AOD has a bash 3.2 symlink-refusal idiom (`[ -L ]` not gated on `[ -e ]`), but tachi must not source AOD files. Mirror the idiom inline.
- **Safe destructive cleanup** (KB Entry 21): deletion is default-off and its safety negatives are written as tests first. D-1's "the flag authorizes copies only" fits.
- **Strict-leg testing** (F-250/F-256): tests must pin `/bin/bash` and `LC_ALL=C`. Dev Macs put Homebrew bash 5.3 first on `PATH`. Assert installer-authored text only, never `cp`/`readlink` wording (BSD "identical" vs GNU "same file").
- **The harness clones committed HEAD.** Tests must be network-free: `install.sh` runs `git fetch --tags` after copying, so it must never run against the live checkout.
- **Contract drift, round 2** (`fix(209)`): K9–K13 repeat the #209 class. Require sibling-parity tests (one fixture, same values on both surfaces) and template-order fixtures.
- **4b→4c is a re-meaning migration** (F-142, KB Entry 23). Sweep per occurrence with a disposition, not by substitution.
- **Stdlib-only at import** (KB-037 @`f74ba0f`, ADR-037 D-8): the existing guard test checks only `yaml` and globs every `scripts/*.py`. It is red today on a non-distributed CI tool and runs outside the gate. NFR-2 needs a manifest-scoped enforcement.
- **Determinism** (PAT-014/015, ADR-017): pin the numeric semantics (precision, rounding, types) and use the largest remainder method for percentage mixes.
- **Silent fallbacks** (KB-029, ADR-022): the infographic agent's error table has no HTTP 400 row, so a request shape that failed 100% of the time shipped unnoticed. `INSTALL_MANIFEST.md` still claims that missing scripts make agents silently fall through to inline extraction, which has been stale since hard-fail preflights landed.
- **Funnel origin** (F-053): the width rule's ambiguity dates from F-053. With forced narrowing, keep the "0% risk reduction" sidebar note.
- **Release reach**: release-please never moves the CHANGELOG's Unreleased prose into a release section, so a prose-only notice never reaches the published notes.
- **CI**: the new workflow must visibly run on the first PR (F-315's dormant-workflow lesson). Workflows that co-fire on this diff (`tachi-mmdc-preflight`, `tachi-catalog-drift`, `tachi-maestro-coverage`) must stay green.

## Codebase Analysis

**Installer (48 PRD pointers confirmed, 2 corrected):**
- `install.sh` has three long-only flags, parsed by a hand-rolled `while/case` loop. Help text lives in two places (the header comment and `usage()`). Release-please markers are at `:13,19,43` and `README.md:120,471`.
- The pre-flight belongs between the `--version` checkout (`:125`) and the cleanup (`:128`). `ORIGINAL_REF` is set before the trap, so the trap's restore also runs on an early `die`.
- The trap's restore must be `if ! git … checkout …; then warn; fi`. A bare failing command under `set -e` aborts the trap silently and flips the exit code.
- Manifest parsing uses exact marker equality. A corrupted BEGIN marker makes the installer copy nothing and still exit 0.
- **No test invokes `install.sh`, and there is no command-level `git` shim.** A demonstrated `/bin/sh` shim fails only the restore checkout. Throwaway-repo precedent: `_build_tiny_upstream`.
- All three manual install blocks fail on a fresh project (the first `cp` has no parent directory). The portable, idempotent form is `mkdir -p DST && cp -R SRC/. DST/`.
- The K2 regex over the pinned distributed globs hits exactly the four scripts, and `populate-affected-assets.py` is the only one missing. Import closure: `tachi_parsers` only.
- CI: `tachi-pytest.yml` runs 22–29 min (macOS 3.2.57 and ubuntu 5.2.21) under the F-250 lock-step rule. The dual-trigger precedents are `tachi-catalog-drift.yml` and `tachi-permissions-verify.yml`. `tachi-maestro-coverage.yml` is PR-only. The shared extractor fixtures live in the **root** `tests/conftest.py`, which no workflow lists.

**Extraction and render (88 pointers checked: 87 confirmed, 1 corrected, plus 3 claim-level corrections):**
- `parse_markdown_table` has 21 call sites (15/2/2/2 across the four files): 9 `##`, 6 `###`, 3 `####`, 3 substring. `_find_table_with_column` has its own section end and is unaffected.
- The status idiom has three sites and two idioms. The duplicate of `:1202-1208` is **`:1253-1260`** (fallback derivation). `:1244` is the Section-1 *summary-row* classifier, which must skip non-status rows.
- The golden fixture already trips the Section-1 comparand: Section 1 says 26.9% while the rows sum to 20.1%. The baseball card also reads Section 1's `risk_reduction` and its inherent/residual totals (`extract-infographic-data.py:1909-1915`), so after K11 the two images would disagree unless both use the row-derived values.
- Recommendation text has **three** consumers: the roadmap, the finding cards (`findings-detail.typ:95`) and the attack-path remediation (`_get_finding_mitigation`). The roadmap cell is 2.6in at 9pt. Existing placeholder register: `--` (missing key), `—` (not applicable), "No remediation actions identified" (empty table). "Not available" / "Not assessed" are unused.
- **Scaffold splitter.** The primary marker is the *unanchored* substring `DATA CONTENT (render this`, matched at its first occurrence. `FOOTER` is matched at the first line start *anywhere*, the preamble included. Scratchpad probes: a hardening paragraph between `IMPORTANT:` and `STYLING DIRECTIVES`, or after the FOOTER line, is safe. A preamble line starting `FOOTER`, a preamble copy of the marker text, or an extra fence under the prompt heading breaks the scaffold silently.
- **The allow-list source.** The finding-ID set at `:1893` is *all* IDs, validation-only and not emitted. The allow-list must be the per-template set the payload renders (`top_findings`, callouts, per-layer summaries, legend).
- **The report-assembler's inline-extraction fallback is deprecated and forbidden.** The carry-forward's intent is met by the Typst contract plus the `main.typ` fail-loud guard.
- **The FR-212-6 lock.** No code parses the locked block and no byte pin exists; only substring checks in `test_executive_architecture_payload.py`. An additive amendment is mechanically safe under conditions. The agent's own executive-architecture section contradicts the lock and never points to `executive-architecture.md`.
- **A shipped copy of the defective body:** `adapters/claude-code/agents/references/infographic-gemini-api.md` is inside a manifest directory. Legacy copies under the root `agents/` tree and the copilot/cursor/generic adapters are not distributed.
- **The "Section 4b" sweep: 16 change sites in 7 files** (the PM's count, re-verified at spec review; the leg report says 8). The highest impact is the producer checklist, `output-schemas.md:275`, which the orchestrator must run and which tells it to write 4b. That is the likely source of legacy `## 4b.` outputs.
- **K10's reach.** Six run directories use `### Risk by MAESTRO Layer` (three carry PDFs, two carry `.pdf.baseline`). All six are **untracked** local `test-output` runs (verified at plan review with `git ls-files`), so K10 moves no tracked example's data and is proven on synthetic fixtures. No tracked example has a Resolved Findings section.
- **Funnel widths.** A 10% floor (~144 px of a ~1440 px funnel zone) cannot hold a tier label. The template's own Tier 4 is ~30%. The golden fixture is STEP-bound (100/90/80/70 at any FLOOR ≤ 30), so a strong-reduction fixture is needed to exercise FLOOR.

## Architecture Constraints

- **No new ADR.** D-1, D-2 and D-3 are feature decisions inside established precedents: ADR-022 (fail loud on prerequisites), ADR-021 (deterministic PDF comparison), ADR-037/046 (test-checked cross-format consistency, deterministic extraction tier), ADR-047 (single-authority sections) and ADR-039 (fixture scope). The patch-bundle "no ADR" precedent (F-302/F-311/F-185) applies. ADR-017 (the deterministic extraction tier and shared parser module) is K9–K13's direct parent. ADR-014 (Gemini optional image generation) gets a dated F-373 note rather than a new ADR (plan PD-15). If a second installer surface ever adopts a symlink policy, revisit it with an ADR then.
- **Constitution.** Principles III (backward compatibility → NFR-4), VI (testing → NFR-1/NFR-7), VII (DoD → §8), VIII (fail loudly → FR-K3.5, D-3 stale data, the new HTTP 400 path) and IX (feature branches) are all honored. The governance tier is `standard`.

## Industry Research

- **Gemini `generateContent` schema** (public discovery document, 2026-09-27):
  - `GenerationConfig.imageConfig` ("An error will be returned if this field is set for models that don't support these config options") holds `aspectRatio` and `imageSize`;
  - `responseModalities` is a sibling field;
  - supported `aspectRatio` values: 1:1, 1:4, 4:1, 1:8, 8:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9. The PRD's 10-value set is a subset, and 3:4 is supported;
  - `imageSize` accepts `512`, `1K`, `2K` or `4K`, with 1K the default.

  This **confirms the PRD's live-verified form**. The web leg's claim that the form is `responseFormat.image.aspectRatio` (and that `imageConfig` is "incorrect") is wrong for this endpoint. The public image-generation guide now documents a different, newer endpoint (`/v1beta/interactions`, `response_format.aspect_ratio`). Record the endpoint alongside the verified form.
- **Model lifecycle:** see headline finding 1. With a chain of only Gemini 3 GA models, every model accepts `imageSize`, so the PRD's reason to drop it (one body valid across a chain that included `gemini-2.5-flash-image`) weakens. Resolution is 1K by default without it.
- **Prompt-text leakage:** state that section labels are layout, not text; quote the exact allowed strings; forbid others. This layered approach matches FR-K15.1/K15.2.
- **Symlinked destinations:** CWE-59/CWE-61. Deny-by-default with an explicit opt-in is a recognized pattern (rsync `--keep-dirlinks`, tar `--keep-directory-symlink` and Ansible `follow` are the destination-side analogs). Python's `follow_symlinks` means "operate on the link's target". Portable primitives: `[ -L ]`, `cd -P`/`pwd -P`, plain `readlink`. TOCTOU is out of scope for a same-user installer.
- **Risk funnel by volume:** summed scores, with counts kept as labels, is a recognized security-dashboard practice.

## Recommendations for Spec

- **Keep:** D-1 to D-4 and the v1.1 rulings as binding. Keep `--follow-symlinks` (long-only, boolean, no short alias; runner-up `--allow-symlinked-dest`) and the known-good `generationConfig.imageConfig` form.
- **Rule in spec:**
  - Refuse links nested in a copied subtree even with the flag.
  - Refuse source-tree containment on physical paths, including the project root.
  - Placeholder: `No recommendation available`, applied to all three recommendation consumers.
  - The baseball card uses the row-derived `risk_reduction` and totals.
  - Update the image model chain to the GA replacements, and live-verify every chain model.
  - Fix the shipped adapters copy of the body.
  - Make HTTP 400 loud, without walking the chain.
  - Accept the K9 aliases in the infographic command's controls detection.
  - Enforce NFR-2 through a manifest-scoped import assertion.
- **Test design:** `/bin/bash` + `LC_ALL=C`; network-free throwaway sources; tree snapshots; non-vacuous cardinality floors; sibling parity; template-order fixtures; a strong-reduction funnel fixture; marker-uniqueness and entry-hygiene checks.
- **CI:** the new workflow copies `tachi-catalog-drift.yml`'s dual-trigger anchor. `paths:` add both conftests, `pyproject.toml` and `examples/**`. The five mmdc cases skip inside their fixture. The stale-data Typst test must not skip silently in CI.
- **Leave to `plan.md`:**
  - P-1 (option A recommended: a `## Gemini API Configuration` section in `executive-architecture.md`, outside the lock);
  - P-2 (safe under the listed conditions);
  - STEP/FLOOR (10/30 recommended) and numeric semantics;
  - whether to restore `imageSize: "2K"` for an all-Gemini-3 chain (P-4, reopened);
  - splitter hardening;
  - the release-notes mechanism.
- **Leave to `/aod.tasks`:** K14's scheduling. *Superseded at spec review:* PM ruling P-9.1 keeps the cut line K1/K2-only, and K14 rides a TW-7 early PR only under three conditions. The 2026-10-02 date constrains *which models* K14 targets, not when it ships, because the stock path already fails on every request. Out of scope as follow-up candidates: a frontmatter `delta_counts` comparand, a provenance check before the deprecated-command `rm`, a populator presence preflight, and the legacy non-distributed adapter copies.

## PRD Corrections Found by Research

| PRD text | Correction |
|---|---|
| D-1: "a leaf-file link is written through" | True for the single-file branch only. A nested file link inside a copied directory aborts BSD `cp -r` ("Permission denied") |
| FR-K14.2: "the agent maps their flat values into the request body" | No mapping exists. Every template gets the reference's hard-coded body |
| FR-K14.1 / R-4 / C-9: preview model IDs as an availability risk | Both preview models shut down on 2026-06-25, and `gemini-2.5-flash-image` shuts down on 2026-10-02. The GA replacements are `gemini-3-pro-image` and `gemini-3.1-flash-image` |
| §13 L-N3: "both call sites (`:1202-1208` and `:1244`)" | The duplicate idiom is `:1253-1260`. `:1244` is the Section-1 summary classifier (a different idiom that skips non-status rows) |
| §13 M-N2 / FR-K15.3: "a line starting `DATA CONTENT`" | The primary marker is an unanchored substring at its first occurrence, and `FOOTER` matches at the first line start anywhere, the preamble included |
| FR-K15.2: the allow-list from the finding-ID set (`:1893`) | That set holds all IDs, is validation-only and is not emitted. Use the per-template rendered set |
| §13 L-N6: "the report-assembler's inline-extraction fallback must emit both" | No active fallback exists; it is deprecated and forbidden. The intent is met through the Typst contract and the `main.typ` guard |
| NFR-7: the new workflow's `paths:` | Add the root `tests/conftest.py` and `pyproject.toml`. `tachi-maestro-coverage.yml` is PR-only, so the dual-trigger precedent is catalog-drift/permissions-verify |
| NFR-2: "KB-037, enforced by `test_pyyaml_deferred_import.py`" | That test is yaml-only, red out of gate, and scoped to all of `scripts/`. KB-037 is an ambiguous ID |

---

## Plan-Stage Decisions (Phase 0 of `/aod.project-plan`)

Each entry gives a Decision, its Rationale and the Alternatives considered. These resolve every plan input the spec registered (spec.md § Rulings).

**Revision 1 (2026-09-27).** The architect's plan review (`.aod/results/architect-373-plan.md`, CHANGES_REQUESTED) and the PM's plan review (`.aod/results/product-manager-373-plan.md`, APPROVED_WITH_CONCERNS) are folded in.
- **Ratification.** PD-1 is **ratified**. PD-2 is **ratified with amendments** (conditions 3, 8 and 9). PD-15 is **ratified** on the ADR-014 note condition.
- **Revised in place** (marked **(rev. 1)**): PD-3, PD-5 to PD-10, PD-12 to PD-15.
- **Added:** PD-16 to PD-20.
- **Binding PM rulings** from the plan review: P-10.1 (render blockage per model), P-10.2 (SC-5 under a K15 carve) and P-10.3 (PD-3's restore rule).

### PD-1: where executive-architecture's request configuration lives (P-1). **RATIFIED**
- **Decision:** add a `## Gemini API Configuration` section to `.claude/skills/tachi-infographics/references/executive-architecture.md`, outside the FR-212-6 lock markers: after the VERBATIM PROMPT BLOCK section, before `## Payload schema`. It uses the other five blocks' YAML shape: `model`, `fallback_model`, `response_modalities`, `aspect_ratio: "3:4"`, and `image_size` only if PD-3 restores it. The agent's skill-reference table and its executive-architecture section point to this file.
- **Rationale:**
  - One heading and one shape mean one parser in the static contract test and one mapping rule for the agent.
  - This reference *is* the template's "template file", since none exists under `templates/tachi/infographics/`.
  - It needs no amendment to the lock, and it sits beside the orientation directive it implements.
- **Ratification notes:**
  - A3 asserts that the block's line index falls after the END marker.
  - The locked text keeps "portrait, 8.5:11 page aspect ratio" while the canvas is 3:4. That is accepted: the canvas governs, W3 checks the one-page fit, and changing the locked text would need a second amendment.
- **Alternatives:**
  - (B) `schemas/infographic.yaml`: a second config home, and it mixes request config into an output-spec schema.
  - (C) a per-template table in `gemini-prompt-construction.md`: it breaks "each template owns its config".
  - (D) agent prose: not a data contract.

### PD-2: the sanctioned FR-212-6 amendment (P-2). **RATIFIED WITH AMENDMENTS**
- **Decision:** one additive amendment inside the lock markers, carrying the two K15 instructions. Conditions (final):
  1. marker lines stay byte-identical;
  2. no fence and no new `<<slot>>`;
  3. **(reworded)** the allow-list is phrased by region, merged with the PM's R-P4 scoping (PD-17): *"Every finding ID in the image must be one listed under CALLOUTS, and every component name must be one listed under LAYER STACK, FLOW EDGES or CLUSTERS. Never show any other ID, and never invent an ID or a component."*;
  4. the amendment is exactly **one paragraph**, placed immediately after the block's IMPORTANT paragraph;
  5. a dated "amended by F-373 K15" note in the lock rule, which also reconciles the rule's stale header list (adding FLOW EDGES and CLUSTERS) and slot list (7 slots);
  6. the `flow_edges` and `clusters` substrings are kept;
  7. the agent's executive-architecture section defers to the verbatim block and drops its contradicting styling lines;
  8. **(new)** the layout-label sentence cites only labels present in this prompt ("such as DATA CONTENT and FOOTER"), not TOP SECTION or LEFT PANEL;
  9. **(new)** A10 proves the amendment additive: the locked block with the amendment paragraph removed must hash to the pinned SHA-256 of the pre-change block.
- **Rationale:**
  - No code parses the block, and no byte pin exists (only substring checks), so the amendment is mechanically safe.
  - The lock's purpose, no *runtime* recomposition, is preserved because the amendment is static text.
  - Condition 3 must name FLOW EDGES and CLUSTERS because the block requires drawing their named endpoints and members (FR-212-18). The plan review found flow-edge endpoints outside every layer in three fixtures.
  - Condition 9 turns "one additive amendment" into an enforced invariant.
  - Getting the wording right now matters: any later change needs another amendment.
- **Alternatives:** carve executive-architecture from K15 (TW-3 partial carve). That would leave the one portrait image unhardened.

### PD-3: `imageSize` (P-4, reopened), settled by P-10.3's rule **(rev. 1, RC-P3)**
- **Decision.**
  - **The W0 smoke.** It sends **eight** calls: {`gemini-3-pro-image`, `gemini-3.1-flash-image`} × {16:9, 3:4} × {default size, `imageSize: "2K"`}, each with a trivial prompt, run in the scratchpad per NFR-5. For each call it records the HTTP status, whether an image came back, the pixel dimensions, the response time and the response part-key casing. A transient 429 or 5xx gets one retry, and the second result stands.
  - **Restore `image_size: "2K"` iff** all four 2K calls return an image whose long edge exceeds its default variant's, so 2K was honored.
  - **3:4 at the default size must succeed on both models regardless.** If it does not, stop and take it to the architect before T013 commits executive-architecture's configuration. AR-2 scopes this decision to that configuration; the rest of K14 proceeds.
  - **W3 latency check.** If 2K was restored and any real-template 2K render takes more than about 45 s (25% headroom on the agent's 60 s single-attempt timeout), drop 2K before merge. The drop is one commit flipping the six blocks, the reference, the adapter copy and the static pin `IMAGE_SIZE_RESTORED`, and the reason is recorded.
  - A blocked model means 2K stays dropped (P-9.4, P-10.1).
- **Rationale:**
  - P-10.3 refines P-9.4 so the rule covers what ships: both ratios, the size actually honored, and latency headroom.
  - W0 settles the question before K14 commits, where a check inside TW-5's budget would vanish with a K15 carve.
- **Alternatives:** always drop (loses 2K for no current reason); always restore (unverified, and the API errors on unsupported options); verify 16:9 only (misses executive-architecture's 3:4).

### PD-4: funnel constants (ratified)
- **Decision:** **STEP = 10, FLOOR = 30** (FLOOR + 3·STEP = 60 ≤ 100). Widths are integers: compute W2·V_k/V2, clamp to [lo, hi], then round half-up. Because lo and hi are integers, rounding after the clamp preserves the bounds. `W_{k−1}` is the emitted, rounded width. **(rev. 1)** The clamp bounds are `Decimal`: `min(max(x, 40), 80)` returns a bare `int` when a bound wins, and a following `.quantize()` then raises (reproduced at plan review).
- **Verified at plan review:** golden fixture widths 100/90/80/70 (STEP-bound); strong-reduction fixture 100/90/54/30 (FLOOR-bound).
- **Rationale:**
  - A 10% floor (~144 px of a ~1440 px funnel zone) can't hold an 18px tier label (~31% stacked with its data).
  - The template's own nominal Tier 4 is ~30%.
  - STEP = 10 keeps today's value and gives a 100/90/80/70 ghost cascade.
  - The PM accepted the product consequence: only the band between the STEP and FLOOR bindings is proportional, so the annotations carry the exact numbers.
- **Alternatives:** FLOOR = 10 (illegible), FLOOR = 25 (marginal for the longest ghost CTA, ~29%).

### PD-5: numeric semantics (TW-1) **(rev. 1)**
- **Decision:**
  - scores are parsed from their source strings with **`parse_score`**, which returns a `Decimal` or `None`. It catches `decimal.InvalidOperation` (not a `ValueError` subclass), `ValueError` and `TypeError`, and rejects `NaN` and `Infinity`;
  - volumes are summed in `Decimal` and emitted quantized to 0.1 (ROUND_HALF_UP) as JSON numbers (`float(q)`);
  - reductions are `(V_a − V_b) / V_a × 100`, computed **from the emitted, quantized volumes** (quantize, then derive, so any reader can reproduce them), and emitted quantized to 0.1;
  - with volumes available, a zero denominator gives 0.0. **When volumes are unavailable, reductions are null** (PD-18);
  - `risk_reduction` **is** the Tier 2→4 value, one computation assigned to both templates;
  - the baseball card's `inherent_score` and `residual_score` are the emitted V2 and V4;
  - a severity mix is **integer counts per band** (`critical`, `high`, `medium`, `low`), with no percentages, so no largest-remainder step is needed;
  - the Section 1 comparand warns when a total or the reduction differs from the row-derived value by more than 0.1.
- **Verified at plan review** on the golden fixture: V2, V3 and V4 = 209.8, 187.8 and 167.6; reductions 10.5 and 10.8; `risk_reduction` 20.1. Section 1 reads 26.9, so the comparand warns. Controls scores and composites are 1-dp by contract, so quantize-then-derive and derive-then-quantize agree on conformant input.
- **Rationale:** exact, stdlib-only (NFR-2) and order-independent. Counts avoid the percentage-rounding problem entirely.
- **Alternatives:** floats with `round()` (banker's rounding and operation-order drift, KB PAT-014); integer tenths (equivalent, but less clear for 2-decimal inputs).

### PD-6: scaffold splitter hardening **(rev. 1, M3)**
- **Decision:** yes, in **W1, by Lane B1** (the only W1 writer of the extractors), before any template text edit lands.
  - The primary marker is anchored to line start (`^DATA CONTENT \(render this`).
  - `FOOTER` is searched for only at a line start after the marker.
  - The no-newline `FOOTER` fallback is dropped.
  - For today's five templates, the scaffold output must be byte-identical, so the hardening commit alone changes no golden (verified at plan review).
  - A8 is strengthened so that it catches a corrupted scaffold (`contracts/gemini-request-and-scaffold.md`).
- **Rationale:**
  - About five lines permanently remove the silent-breakage modes. At plan review, the unhardened splitter corrupted three probes: a preamble line starting `FOOTER`, a preamble copy of the marker, and a **hard-wrapped K15 sentence whose `FOOTER)` lands at a line start**. The old A8 passed the last one.
  - K11, K13, K14 and K15 all edit these files, and adopters may customize templates.
  - In W2 the hardening would race Lane C2's text edits.
- **Alternatives:** the test alone (guards the shipped templates only); W2 in Lane B2a (the original placement, which races C2).

### PD-7: the release-notes mechanism (SC-6) **(rev. 1, RC-P6, R-P1)**
- **The notice set** (the PM finalizes the generic wording in W4, per NFR-6):

| # | Notice | Condition |
|---|---|---|
| 1 | Update the tachi clone first, then re-run `install.sh`. It names the three skills and the Affected Assets populator | always |
| 2 | The D-1 behavior note (`contracts/installer-cli.md`) | always |
| 3 | M5: findings the controls report gives no recommendation for show the threat model's mitigation, marked `Threat-model mitigation:` | always |
| 4 | The funnel narrows by risk volume, **and** the Risk Reduction figure on the funnel and the baseball card is now computed from the controls rows, so it can differ from the controls report's summary | only if K11 ships |
| 5 | A `report-data.typ` compiled outside `/tachi.security-report` now stops with a regenerate instruction | only if K13-posture ships |
| 6 | The render path is statically verified only, per blocked model | only if P-9.2 or P-10.1 fires |
| 7 | Replace a symlinked destination before re-running | only if TW-7 ships Lane A without K3 |

- **Delivery:**
  1. **Before merging the release-please PR, edit its body** so the notices are present at publish and in watchers' notification emails (R-P1). *Confirmed at plan review:* release-please v4 builds the GitHub release from the merged release PR's body. v4.48.0's published body is byte-identical to PR #371's notes region (except one trailing blank line), consistent with release-please's `buildRelease` parsing the merged PR body. The edit must go **inside the notes region**: after the `## [x.y.z](…) (date)` heading line and before the first `###` section, leaving the `:robot:` header, both `---` separators and the footer intact. A malformed body can make the parse fail and skip the release. It must also be the **last action before the merge**, because release-please regenerates the body on every push to `main` while the PR is open.
  2. **After publish**, `gh release edit vX.Y.Z --notes-file <file>` prepends (or re-asserts) an **"Upgrading"** section (the F-121 form) above release-please's notes. This is the durable backstop.
  3. **Ordering:** if `scripts/polish-release-notes.sh` is used, run it **before** the prepend, never after, because its LLM rewrite could paraphrase the notices away.
  4. **Verify SC-6** with `gh release view vX.Y.Z --json body -q .body`: the Upgrading section must appear verbatim.

  The hand-curated CHANGELOG `Unreleased` prose carries the same text. `/aod.deliver` has a follow-through item if the release PR merges later.
- **Rationale:** a post-publish edit is durable but does not re-notify watchers; the pre-merge edit reaches the notification; the two together cover both.
- **Alternatives:** CHANGELOG prose only (never reaches the published notes); the pre-merge edit only (it can be regenerated away).

### PD-8: the mmdc skip and Typst provisioning **(rev. 1)**
- **Decision:**
  - The mmdc skip sits inside the `agentic_app_report_typst` fixture (`shutil.which("mmdc") is None` → `pytest.skip`, **before** the extractor call), so exactly the five image-flag cases skip (verified: the fixture is module-scoped and used only by the five parametrized cases).
  - The same edit makes the fixture run the extractor on a **temporary copy** of the whole `sample-report` directory (`tmp_path_factory`, because the fixture is module-scoped; the images are copied too, so the flags it compares are unaffected). Local runs then stop rewriting tracked PNGs.
  - **Owner and wave (rev. 1):** Lane A, in wiring commit A-2, which lands immediately after the cut line and before any Lane B1 commit, together with gating the four pre-existing modules (RC-P1, PD-20).
  - Typst comes from `typst-community/setup-typst@v5`, with `TACHI_REQUIRE_TYPST=1` set, in the fast workflow's **separate `report-posture` job** (PD-9). The stale-data test then fails rather than skips when Typst is missing.
  - It lands with the K13-posture stale-data test in W2, never in W1. If K13-posture is carved, no Typst is added.
  - The stale-data test reuses the T010 harness (`test_coverage_attestation.py`) on an mmdc-free fixture. Its positive control asserts that the panic text is **absent**, not that the compile exits 0, so a Typst release or a relative image path cannot redden it. That also makes a Typst version pin unnecessary, as in the `tachi-mmdc-preflight.yml` precedent.
  - The PR describes the temporary-copy change as **#365-adjacent hygiene, not a #365 fix** (R-P8).
- **Rationale:**
  - the repo's skip-when-absent idiom for bare runners;
  - a presence guard for gates (KB E2);
  - removing a live PNG hazard at the edit site we already touch;
  - job isolation, so a Typst download failure can never redden the manifest gate.
- **Alternatives:** install mmdc in CI (heavy new machinery, against NFR-7's "fast"); leave the fixture in place (keeps the #365 hazard for local runs); Typst in the shared job (a Typst setup flake would redden K1/K2's gate).

### PD-9: the fast workflow **(rev. 1, RC-P1, RC-P5, M2)**
- **Decision:** `.github/workflows/tachi-install-fidelity.yml`, cloned from `tachi-catalog-drift.yml`:
  - one `&fidelity_paths` anchor shared by `pull_request` and `push: [main]`;
  - `contents: read`;
  - Python 3.11 with `pytest>=8`, `pytest-timeout>=2` and `pyyaml>=6`;
  - `timeout-minutes: 10` per job.
  - **Three jobs**, so each gate's signal stays independent:

| Job | Modules | Lands |
|---|---|---|
| `manifest-completeness` | `test_install_manifest_completeness.py` only | **W1 cut-line commit (A-1)**: the only module the cut-line commit invokes |
| `extraction-fidelity` | the four pre-existing modules (`test_tachi_parsers.py`, `test_extract_infographic_data.py`, `test_extract_report_data.py`, `test_extractor_contract_fixes.py`); then `test_gemini_request_contract.py`, then `test_extraction_sibling_parity.py` | the pre-existing four in **A-2** with PD-8's mmdc skip; each later module in its own lock-step wiring commit |
| `report-posture` | `test_report_posture_contract.py`, with `setup-typst@v5` and `TACHI_REQUIRE_TYPST=1` | W2, only if K13-posture ships |

  - **`paths:`** Each path lands in the lock-step commit that adds the test reading it (RC-P5; the F-250 rule):
    - the cut line brings `INSTALL_MANIFEST.md`, `.claude/skills/**`, `.claude/commands/tachi.*.md`, `.claude/agents/tachi/**`, `templates/tachi/**`, `scripts/*.py`, `scripts/install.sh`, **`README.md`**, **`docs/guides/DEVELOPER_GUIDE_TACHI.md`**, both conftests, `pyproject.toml`, the module and the workflow file;
    - A-2 adds `examples/**` and the four modules;
    - A-3 adds **`adapters/claude-code/**`** (A4 and A6 pin the shipped adapter copy) and the contract module;
    - the #370 tests add `schemas/taxonomy/*.yaml` **only if** they load the real catalogs, which the second recipe case needs to pin the FR-024 "full catalog" promise.
- **Rationale:**
  - **RC-P1: nothing but K1/K2's own test may redden the cut-line commit's run.** The pre-existing modules are red on bare ubuntu until PD-8 lands.
  - Separate jobs keep that property after the cut line too.
  - Paths name everything the tests read.
- **Alternatives:** widen `tachi-pytest.yml` (22–29 min; rejected in the PRD); one job for everything (a red extraction test hides the K1/K2 result; a Typst flake reddens it).

### PD-10: the K3 pre-flight (bash 3.2) **(rev. 1, M1, M8, L6, RC-P4)**
- **Decision:** the full algorithm is in `contracts/installer-cli.md`. In outline:
  - Resolve the physical roots `TARGET_P` and `SRC_P` with `cd -P … && pwd -P`, after `unset CDPATH`, and enforce project-root containment (S-2).
  - **The checked set.** Enumerate it from the checked-out manifest: ancestors, the entry itself, a `find -mindepth 1` walk of each directory entry's source subtree mapped into the target, and the cleanup files with their ancestors. **Each component keeps every origin it has**, so enumeration order never matters.
  - **Link classes**, by precedence (data-model §2.1):
    1. `cleanup-only`, where the deprecated file itself is the link: refused without the flag, skipped with it, whatever its target;
    2. `unresolvable`: `resolve` fails (dangling, or more than 40 hops), or the target has the **wrong type** (a file where a folder is needed, or the reverse);
    3. `nested`, when any origin is `subtree`;
    4. `inside` or `outside`.
  - **Destination containment (M1)** replaces the per-link `source-tree` class. For every entry, and for every cleanup file that is not itself a link, `phys_dest` gives the physical destination: `resolve` of the deepest existing component, plus the rest. If it is `SRC_P` or inside it, the install is refused regardless of the flag. This catches links straight into the clone, links to an ancestor of the clone (for example `templates → ..`, reproduced at plan review) and a clone vendored at a destination path.
  - **Implementation constraints (M8, reproduced on bash 3.2.57 and 5.3.9):**
    - `resolve` and `phys_dest` are called only in a conditional, never as `local x=$(…)`, which masks the failure and would follow a dangling link;
    - helper variables are `local`;
    - no possibly-empty array is expanded under `set -u` (bash 3.2 treats that as unbound);
    - enumeration uses `done < <(…)`, never `| while` (which loses the state);
    - report lines are sorted with `LC_ALL=C`.
  - **Messages** use the PM's RC-P4 texts: the help text, the flag-eligible remedy that "only copies and never deletes through a link" and names "a real directory or file", `[broken or looping link]`, `-> <resolved>` on nested lines, and the clone path in the containment message.
- **Rationale:**
  - only verified-portable primitives (`[ -L ]`, `cd -P`, `pwd -P`, plain `readlink`, and `find -mindepth`, which is not POSIX but is present in both BSD and GNU);
  - a hop limit makes looping links deterministic;
  - containment by physical destination is what FR-K3.7 actually requires;
  - the checked set is about 220 paths at HEAD (not ~10³), so the cost is negligible.
- **Alternatives:** `readlink -f` or `realpath` (not portable to macOS bash 3.2's userland on older systems); Python (the installer must stay pure bash); classifying link targets only (the original contract, which misses FR-K3.7's non-link and ancestor-link cases).

### PD-11: the ref restore (ratified; verified)
- **Decision:**
  - The trap records the exit status on entry.
  - It restores with `if ! git -C "$SOURCE_DIR" checkout "$ORIGINAL_REF" --quiet; then <warning>; fi` and exits with the recorded status.
  - The warning names the ref and the exact restore command.
  - The misleading `:111` comment is corrected.
- **Verified at plan review** on `/bin/bash` 3.2.57 and on bash 5.3.9. The status is preserved across a normal exit, `die`, a `set -e` failure, `exit 3`, pipefail and a failed command substitution, and the warning prints exactly when the restore fails.
- **Rationale:** a bare failing command inside an EXIT trap under `set -e` aborts the trap silently and flips the exit code (reproduced).

### PD-12: test layout and gating **(rev. 1)**
- **Decision:**

| Module | Gating workflow (job) | Covers |
|---|---|---|
| `tests/scripts/test_install_manifest_completeness.py` | fast (`manifest-completeness`) | K1, K2, S-13, the manual loop (bash, and zsh when present) |
| `tests/scripts/test_install_sh_symlink_preflight.py` + helper `tests/scripts/install_sh_helpers.py` | `tachi-pytest.yml` | K3 symlink and containment cases, including the rev. 1 additions |
| `tests/scripts/test_install_sh_ref_restore.py` | `tachi-pytest.yml` | K3 ref restore |
| existing `test_tachi_parsers.py`, `test_extract_infographic_data.py`, `test_extract_report_data.py`, `test_extractor_contract_fixes.py` | fast (`extraction-fidelity`), from A-2 | K9–K13, extended in place |
| `tests/scripts/test_extraction_sibling_parity.py` | fast (`extraction-fidelity`) | one fixture, both extractors, including bracketed statuses |
| `tests/scripts/test_gemini_request_contract.py` | fast (`extraction-fidelity`) | K14 plus K15 static assertions |
| `tests/scripts/test_report_posture_contract.py` | fast (`report-posture`, with Typst) | the D-3 stale-data panic |
| `test_extract_report_data.py` | fast (`extraction-fidelity`) | #370's two tests |

- **Fixtures:** synthetic fixtures live under `tests/scripts/fixtures/fidelity_373/`. Symlink sandboxes are built at test time in `tmp_path`.
- **Harness details (rev. 1):**
  - the end-to-end source copy is **manifest-driven**;
  - the throwaway `--version` repo keeps `install.sh` identical across the tagged and HEAD commits, and supplies a git identity under `GIT_CONFIG_GLOBAL=/dev/null`;
  - see `contracts/installer-cli.md` and `contracts/manifest-completeness.md`.
- **Ownership:** each module has one writer per wave, and CI files have one owner (PD-20).
- **Rationale:** follows the naming conventions (`test_<subject>.py`, `*_helpers.py`), keeps the heavy matrix for installer portability only, and gates the rest cheaply.

### PD-13: data-contract names **(rev. 1)**
- **Decision:**
  - **Posture:** `metadata.risk_posture_level` and `metadata.risk_posture_label` (beside `metadata.risk_posture`), in every infographic JSON. Executive-architecture gets them through its early-exit builder `_build_executive_architecture_payload` (`extract-infographic-data.py:1869`).
  - **Funnel tiers:** `template_data.funnel_tiers[]` is always four objects, carrying `{tier, label, source, ghost, count, volume, severity_mix, width}` (PD-18).
  - **Reductions:** `template_data.reduction_percentages[]` is always three entries, with `percentage` a number (1 dp) or null.
  - **Allow-list:** a top-level `allow_list: {finding_ids: [...], component_names: [...]}`, sorted and unique, in every template, executive-architecture included (PD-17).
  - **Typst:** `#let risk-posture-level` and `#let risk-posture-label`.
- **Rationale:** follows the existing placement (`metadata.risk_posture`, `template_data.*`) and Typst's kebab-case variables. `ghost` makes the template's rendering key explicit instead of relying on a `null` entry, which cannot carry a width.

### PD-14: the model chain, chain-walk semantics and error rows **(rev. 1: reconciliation 1)**
- **Decision:**
  - **The chain.** The primary model is `gemini-3-pro-image`, with `gemini-3.1-flash-image` as the fallback. This applies to the reference, the five blocks, executive-architecture's configuration and the adapter copy.
  - **Walked** when a model is unavailable **to the key**: HTTP 404 `NOT_FOUND` **or 403 `PERMISSION_DENIED`**.
  - **Not walked:**
    - a 400 (including `FAILED_PRECONDITION`) is the loud error row;
    - 429 and timeouts keep today's single attempt. The 429 message tells the adopter to put the fallback model first in the template block when the key has no quota for the primary;
    - every other non-2xx, and a 2xx with no image part, falls in a catch-all Error row with the status and the API message.
  - **Chain exhausted** (every model returned 404 or 403): logged at **Error**, and the final summary names each model tried with its status and message (R-P3).
  - **The reference records** each model's verified-render date, per ratio.
  - **The response is parsed** from `inlineData` and `mimeType` (camelCase REST); the SDK's `inline_data` and `mime_type` are accepted too (M7).
- **Reconciling PM R-P2 (walk on 403) with the architect's L2 (403 in a no-walk catch-all). The decision is to walk on 403.**
  - A 403 is either a model not entitled to this key, where walking can succeed, or a key-level block (a disabled API or a restricted key), where the fallback fails the same way.
  - Walking costs at most one extra request, and it cannot hide the cause: an exhausted chain is logged at Error with every model's status and message.
  - A 400 is different. Every model rejects the same malformed body, and walking would attribute the failure to the fallback.
  - At W0, a refusal of the project key with any status **other than 404 or 403** (for example a 429 with a zero quota, or a 400 `FAILED_PRECONDITION`) is recorded for the architect under ruling AR-2. It is non-blocking: Lane C1 commits K14 with the 404/403 walk set, the architect amends it if needed by the end-of-W2 checkpoint, and W1 is never held.
- **Rationale:** these are Google's named GA replacements, with no shutdown announced. G4 is about the adopter's key, not only ours. Walking the chain on a 400 would mask a malformed body.

### PD-15: no ADR **(rev. 1: RATIFIED on condition)**
- **Decision:** no new ADR. **Condition:** a dated "Note (F-373)" is added to **ADR-014** (Gemini API optional image generation) in **W4**, as part of the docs sweep, in the form of its existing 2026-03-28 Feature 039 note. It records:
  - the GA chain replacing the preview models its Decision section names (`ADR-014:38`, both shut down 2026-06-25);
  - the walk set (404 or 403);
  - the loud but non-blocking HTTP 400 row;
  - the exhausted-chain Error row.
- **Rationale:**
  - D-1 to D-3 are feature decisions inside ADR-022 (fail loud), **ADR-017** (the deterministic extraction tier and the shared parser module, the direct parent of K9–K13), ADR-037/046 and ADR-021.
  - The FR-212-6 amendment is recorded in the lock rule itself (PD-2).
  - The patch-bundle precedent applies (F-302/F-311/F-185).
  - ADR-014 is the decision record this bundle's render-path changes touch, so it gets a note rather than a successor ADR.
  - If a second installer surface later adopts symlink policy, an ADR is revisited then.

### PD-16: K12 delta-status normalization and scoped checks (new, H1)
- **Decision** (data-model §6):
  - `delta_status_by_id` normalizes each status before matching: whitespace, one surrounding `[`…`]` pair and `*`/`_` markers are stripped, then the value is upper-cased. `[NEW]` therefore counts as `NEW`.
  - It returns whether Section 7 has a Status column.
  - The two consistency checks warn and **never raise**:
    - the map is empty although Section 7 has rows;
    - the map's ID set differs from the tier's finding IDs.
  - Both run only on a baseline run **whose Section 7 has a Status column**.
  - A baseline run without the column gets one "delta counts unavailable" warning.
  - Fixtures: bracketed statuses on a baseline run (exact counts); a Status-less Section 7 on a non-baseline run (no warning, no exception).
- **Rationale:**
  - The orchestrator prescribes bracketed lifecycle tags (`orchestrator.md:64`, `:288`), and both shipped baseline examples (`agentic-app`, `agentic-app/sample-report`) carry `[NEW]` and `[UNCHANGED]`. Bare-only matching would count 0 exactly where K12 matters, while the synthetic bare-`NEW` fixture passed.
  - An unscoped "non-empty map" assertion fires on `maestro-reference`, the live-render example (111 Section 7 rows, no Status column), because the report path calls the map on every Tier 1/2 run.
- **Oracle attribution:** `agentic-app`'s delta counts and PDF badges change under K12.
- **Spec touch:** FR-K12.1, FR-K12.2 and US-3a #7 (listed in the revision summary).
- **Alternatives:** keep bare-only matching (K12 stays wrong on real baseline output); raise on an empty map (breaks legacy tables).

### PD-17: K15 allow-list derivation and final instruction wording (new, H2; reconciliation 2)
- **Decision** (data-model §8):
  - `finding_ids` is exactly the set of IDs each template's prompt renders:

| Template | `finding_ids` |
|---|---|
| baseball-card | the **full tier finding-ID set** (its bottom strip annotates crossings and correlations with any finding's ID) |
| system-architecture | the **full tier finding-ID set** (ID pills per component, IDs along boundaries, and a legend of every Section 3 finding) |
| maestro-stack | `per_layer_summaries[].top_findings[].id` |
| maestro-heatmap, risk-funnel | `[]` (they render no IDs) |
| executive-architecture | `callouts[].finding_id` |

  - `component_names` is one common set: the run's known component names.
- **Final wording** (reconciling the PM's R-P4 with the architect's H2):
  - **Scaffolded templates and the reference prompt:** *"Every finding ID in the image must be one listed on the ALLOWED IDS AND NAMES line below, and every component name must refer to a component listed there. Never show any other ID, and never invent an ID or a component."*
  - **The agent writes:** `ALLOWED IDS AND NAMES (layout instruction, do not render this line): finding IDs: <…, or none>; component names: <…>`.
  - **The locked executive-architecture variant** is PD-2 condition 3.
  - **The layout-label sentence, for all six:** *"The uppercase section labels in this prompt, such as DATA CONTENT and FOOTER, are layout instructions. Do not render them, or any other instruction text, as visible text in the image."*
- **Rationale:**
  - R-P4's scoping ("every finding ID … must come from") avoids "show only this text" suppressing titles, metrics and labels.
  - The ID clause is exact, because SC-5 measures IDs.
  - The names clause says "refer to" for the scaffolded templates, because the system-architecture legend abbreviates names by design (`:371`), which the extractor cannot enumerate.
  - It is exact for the locked variant, whose regions list full names.
  - The earlier `top_findings`-only map would have forbidden most of what system-architecture and maestro-stack render, contradicting FR-K15.2's own "per-layer summaries, the legend".
- **Spec touch:** FR-K15.1, FR-K15.2, US-4b #2, and the Terminology and Key Entities rows.
- **Alternatives:** keep the map (contradictory prompts); redesign the templates to render fewer IDs (a visual change, NG6).

### PD-18: funnel entries in degraded modes, and unavailable volumes (new, M4, M5)
- **Decision** (data-model §4; examples in `contracts/extraction-data-contract.md`):
  - `funnel_tiers` is always four objects. A ghost tier is `ghost: true` with `count`, `volume`, `severity_mix` and `source` all `null`, and a cascade `width`.
  - In 3-tier mode, JSON tier 2 is "Unmitigated Risk" with volume V2.
  - `reduction_percentages` is always three entries. (0→1) is 0.0 by definition, but `null` when tier 1 is a ghost: a ghost wins over "by definition".
  - **Volumes unavailable** (4-tier, when no controls row carries an inherent score, for example a SARIF-only risk-scores run with a controls table lacking the Inherent column, or when V2 = 0):
    - every `volume` is `null`, (1→2) and (2→3) are `null`, and widths cascade;
    - `risk_reduction`, `inherent_score` and `residual_score` are `null` on **both** the funnel and the baseball card;
    - one warning.
  - Templates key ghost rendering on `ghost`, and the "0% risk reduction" note on a numeric 0.0 only.
- **Rationale:**
  - Two parallel W2 lanes (B2a emits, C2 renders) need one pinned shape.
  - Emitting 0.0 for unmeasured risk would claim that controls had no effect, and would overwrite the baseball card's Section 1 figure with a false one.
- **Spec touch:** FR-K11.3, FR-K11.5 and the V2 = 0 edge case.
- **Alternatives:** keep `null` tier entries (no place for the ghost width); emit 0.0 (a false claim).

### PD-19: the recommendation placeholder on every data tier (new, RC-P7)
- **Decision** (data-model §7): after resolution, an empty recommendation text becomes `No recommendation available` on **every** data tier. The prefix fallback stays tier-1 only.
  - **Tier 3:** the finding-level `mitigation` takes the placeholder, so the card, the roadmap and the attack path agree.
  - **Tier 2:** it has no recommendation source, and its surfaces keep today's non-blank behavior (the card's missing-key `—`, the roadmap's threat text, `_build_remediation`'s generic step). An empty roadmap text also takes the placeholder.
- **Rationale:** FR-K13.1's "MUST NOT be blank" has no tier condition. The PM prefers the one-line fix over narrowing the spec.
- **Spec touch:** FR-K13.1.

### PD-20: ownership of test modules and CI files; wiring commits (new, M2, RC-P1)
- **Decision:**
  - Every test module, fixture tree and CI file has **one writer per wave** (the table in `plan.md` § Lane and file ownership).
  - `.github/workflows/tachi-install-fidelity.yml` is written only by Lane A, in every wave.
  - A module's author writes the module. Lane A's **wiring commit** bundles that module with its workflow entries (paths and invocation) in one lock-step commit.
  - The author never commits a module separately, so the module is never ungated.
  - The W1 order: **A-1**, the cut line (the completeness module only); **A-2**, immediately after and before any Lane B1 commit (the four pre-existing modules plus PD-8's fixture edit); **A-3**, when Lane C1's contract module is ready.
  - `tachi-pytest.yml` is written only by Lane A′ in W1, and by Lane A in W2.
  - The tester owns `test_extract_report_data.py` in W2, #370's two tests included.
  - The authorized goldens are regenerated as a wave-final W2 commit by the tester (PD-12, SC-8).
- **Rationale:**
  - Lock-step (NFR-7) and "lanes share no files within a wave" can then both hold.
  - The cut line is K1/K2-only (RC-P1).
  - The fast workflow is green again at the end of W2 rather than red until W3.
- **Alternatives:** marker-based module selection (it still needs per-module path edits, and it departs from the repo's explicit-list convention); per-lane workflow edits (the shared-file conflict M2 found).
