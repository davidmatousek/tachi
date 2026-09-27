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
- **K10's reach.** Six shipped run directories use `### Risk by MAESTRO Layer` (three carry PDFs, two carry `.pdf.baseline`), so K10 changes their data. No shipped example has a Resolved Findings section.
- **Funnel widths.** A 10% floor (~144 px of a ~1440 px funnel zone) cannot hold a tier label. The template's own Tier 4 is ~30%. The golden fixture is STEP-bound (100/90/80/70 at any FLOOR ≤ 30), so a strong-reduction fixture is needed to exercise FLOOR.

## Architecture Constraints

- **No new ADR.** D-1, D-2 and D-3 are feature decisions inside established precedents: ADR-022 (fail loud on prerequisites), ADR-021 (deterministic PDF comparison), ADR-037/046 (test-checked cross-format consistency, deterministic extraction tier), ADR-047 (single-authority sections) and ADR-039 (fixture scope). The patch-bundle "no ADR" precedent (F-302/F-311/F-185) applies. A second installer adopting symlink logic would warrant an ADR under the Two Instantiation Rule.
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
