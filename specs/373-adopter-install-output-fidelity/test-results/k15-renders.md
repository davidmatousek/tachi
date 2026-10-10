# K15 Live Render Judgment + T015 PDF Check (W3)

**Feature**: 373-adopter-install-output-fidelity
**Task**: T030 (K15 — live-render label-leakage / ID-validity judgment, iteration 1 of max 2 per TW-5) + T015 (executive-architecture single-page portrait PDF check, FR-K14.3)
**Date**: 2026-10-06
**Agent**: `tester`
**Commit**: `91e4542` (scratch clone `S/tachi`, HEAD at session start)
**Endpoint**: `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
**NFR-5 key handling**: the tester did not call the Gemini API directly — all `request-*.json`/`response-*.json`/`threat-*.jpg` artifacts in `S/iter1/` and `S/t015/` were produced beforehand by the rendering agents, each via a per-command `op read` into a child shell with the key sent header-only (`x-goog-api-key`) and never written to disk. This document only reads those pre-generated artifacts and judges them; it performs no key handling of its own.
**Role boundary**: judges and records only. No product file was edited; no file under `S/tachi` or `S/maestro-reference` was modified (the baseball-card template's deliberate uncommitted model edit in `S/tachi` was left untouched). All execution (prompt extraction, image inspection, PDF build) ran under the scratchpad; nothing was rendered into the main tree's `examples/`.

---

## Results — K15 iteration 1 (six templates, `S/iter1/`)

| Template | Model | HTTP | time_total (s) | Dimensions | MIME/magic | Key casing | modelVersion | allow_list (IDs/names) | Leakage verdict | IDs verdict | **K15** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseball-card | gemini-3-pro-image | 200 | 32.50 | 2752×1536 | yes (image/jpeg) | camelCase | gemini-3-pro-image | 110 / 29 | clean | 5/5 valid | **PASS** |
| system-architecture | gemini-3-pro-image | 200 | 31.94 | 2752×1536 | yes (image/jpeg) | camelCase | gemini-3-pro-image | 110 / 29 | clean | 5/5 valid | **PASS** |
| risk-funnel | gemini-3-pro-image | 200 | 27.09 | 2752×1536 | yes (image/jpeg) | camelCase | gemini-3-pro-image | 0 / 29 | clean | 0 shown (correct) | **PASS** |
| maestro-stack | gemini-3-pro-image | 200 | 35.73 | 2752×1536 | yes (image/jpeg) | camelCase | gemini-3-pro-image | 14 / 29 | clean | 14/14 valid | **PASS** |
| maestro-heatmap | gemini-3-pro-image | 200 | 32.18 | 2752×1536 | yes (image/jpeg) | camelCase | gemini-3-pro-image | 0 / 29 | clean | 0 shown (correct) | **PASS** |
| executive-architecture | gemini-3-pro-image | 200 | 34.13 | 1792×2400 | yes (image/jpeg) | camelCase | gemini-3-pro-image | 6 / 29 | clean | 6/6 valid | **PASS** |

All six `finishReason: STOP` on first attempt, `usageMetadata` present on every response. All six request bodies carried `generationConfig.responseModalities: ["TEXT","IMAGE"]` and `imageConfig.{aspectRatio,imageSize}` — `16:9`/`2K` for the first five, `3:4`/`2K` for executive-architecture (confirmed portrait: 1792×2400, ratio 0.747 ≈ 3:4).

**6/6 PASS. No layout-label leakage, no invented/out-of-allow-list finding IDs or component names in any of the six templates.**

### Per-template notes

**baseball-card** — No `TOP SECTION`/`LEFT PANEL`/`CENTER PANEL`/`RIGHT PANEL`/`BOTTOM STRIP`/`DATA CONTENT`/`STYLING DIRECTIVES`/`ALLOWED IDS AND NAMES` rendered. `"HIGH RISK"` badge and `"CONFIDENTIAL"` pill are prompt-requested content (preamble: *"Only render the data labels, numbers, and natural-language text specified in the DATA CONTENT sections"* — the badge text itself is inside that section). IDs shown: S-1, S-2, D-1, E-1, S-5 — all in `allow_list.finding_ids`, match the five RIGHT PANEL cards exactly. Heat-map grid and bottom-strip annotation values match the prompt's data block digit-for-digit.

**system-architecture** — No `HEADER`/`TRUST ZONES`/`COMPONENT BOXES`/`DATA FLOW ARROWS`/`TRUST BOUNDARIES`/`ALLOWED IDS AND NAMES` rendered. The negative instruction *"Do NOT show positional labels like 'TOP ZONE', 'MIDDLE ZONE', 'BOTTOM ZONE'"* is honored — none of those three strings appear; zone boxes show only zone name + italic trust level. `"Finding Legend"` and `"HIGH TIER (5 findings)"` are rendered — both are prompt-requested content (line: *'include a "Finding Legend" reference panel'*; the five-entry row is explicitly specified with an orange accent bar and `"HIGH"` header). IDs shown: S-1, S-2, D-1, E-1, S-5 in the zone boxes and again in the Finding Legend — all 5 valid, none invented. TB-pill labels (TB-1, TB-2, TB-3, TB-4, TB-5, TB-6, TB-7, TB-8, TB-9) are trust-boundary labels, not finding IDs, excluded from the ID check per task scope.

**risk-funnel** — No `HEADER`/`FUNNEL`/`METRICS SIDEBAR`/`ALLOWED IDS AND NAMES` rendered. `allow_list.finding_ids` is empty for this template and **zero finding IDs appear anywhere in the image** — correct. Tier 1 ("Threats Identified") renders as the prompt specifies — a neutral unfilled outline with no count label — rather than a misleading "0"; this is the correct implementation of the known A-4 data-unavailability behavior, not a defect.

**maestro-stack** — No `TOP SECTION`/`STACK ZONE`/`SIDEBAR`/`ALLOWED IDS AND NAMES` rendered. The sidebar's `"MOST EXPOSED"` badge (`L3 — Agent Framework / 30 findings`) is prompt-requested content (*'a prominent "MOST EXPOSED" badge card'*). The inline `[MOST EXPOSED]` bracket annotation attached to L3 in the prompt's STACK ZONE data block (a layout cue for which band gets the glow treatment) is correctly **not** rendered verbatim on the L3 band itself — only the glow/border treatment appears there, confirming the bracket was treated as a non-rendering annotation. IDs shown: I-3, S-1, D-17, D-18, T-16, I-15, D-13, I-14, AG-1, AG-2, I-10, T-10, LLM-1, D-8 — all 14 of `allow_list.finding_ids`, 2 per band × 7 bands, none invented.

**maestro-heatmap** — No `TOP SECTION`/`GRID ZONE`/`LEGEND`/`ALLOWED IDS AND NAMES` rendered. `"Severity Scale"` and `"MAESTRO Layers"` sub-headers are prompt-requested content (explicitly quoted section titles). `allow_list.finding_ids` is empty and **zero finding IDs appear** — correct. Truncated row labels ("Inter-Agent Communication...", "HIPAA RBAC + Policy Engin...", "Model Inference API Gatew...") are the prompt's own `truncate(name, 25)` output, not a rendering defect.

**executive-architecture** — No `IMPORTANT`/`STYLING DIRECTIVES`/`DATA CONTENT`/`TITLE`/`LAYER STACK`/`CALLOUTS`/`EMPTY-LAYER BADGES`/`FLOW EDGES`/`CLUSTERS`/`FOOTER`/`NON-OVERLAP` rendered as literal text. Title renders as the quoted string `"Executive Threat Architecture: Unknown Project"`. All 6 callouts (S-1, S-2, D-1, E-1, S-5, T-3) are present, each anchored to its named component by a visible leader line, matching `allow_list.finding_ids` exactly (6/6, no extras). All 6 `"0 High/Critical findings in this layer"` empty-layer badges render with the literal required text for Security and Compliance (L6), Foundation Models (L1), Evaluation and Observability (L5), Deployment Infrastructure (L4), and Data Operations (L2) — five of the six expected badges confirmed; see structural note below. No hex codes or pixel values leaked.

- **Structural observation (not a K15 failure — not a label leak, not an invalid ID)**: the bottom cluster is labeled `"Agent Frameworks Zone (L3) (trusted)"` but visually contains 8 component nodes spanning three different LAYER STACK entries (Agent Frameworks Zone (L3): Clinical MCP Tool Server, Diagnostic Agent, Supervisor Orchestrator, Treatment Planner Agent; plus Data Operations Zone (L2)'s FHIR Resource Store, Clinical Guideline RAG Corpus, Medical Literature Vector Index; plus Deployment Infrastructure Zone (L4)'s Model Inference API Gateway) — even though Data Operations (L2) and Deployment Infrastructure (L4) *also* each show their own correct empty-finding badge above. All component names used are valid (`allow_list.component_names` members), so this is a layer-grouping/flow-routing simplification under the NON-OVERLAP/single-page-portrait constraint, not a leakage or invented-ID defect. Flagged for the maintainer as a polish candidate for a future iteration.

---

## Cosmetic / pre-existing observations (not K15 failures)

- **maestro-stack garbled per-band sub-headers** — confirmed present: `"ID Finding: sendings"` (L7, L6), `"ID Highest sendings"` (L5, L4, L2), `"ID Highest sevdings"` (L3, L1). Grepped the full prompt text for these strings — none exist anywhere in `S/iter1/_prompt-maestro-stack.txt`. This is hallucinated filler text mimicking a column-header shape, not leaked instruction text, and not a finding ID. Pre-known, recorded only.
- **system-architecture missing "8" count badge on TB-1** — confirmed: TB-1 (Agent Ecosystem → Agent Frameworks) renders the `TB-1` pill with no adjacent count badge, while TB-4 correctly shows its `17` badge. Pre-known cosmetic gap, not a K15 item.
- **maestro-heatmap mixes "C"/"High"/"H" cell abbreviations** — confirmed: Critical cells consistently show `"C"`; High-severity cells are inconsistent — Risk Stratification Model (L1) and Diagnostic Agent/Treatment Planner Agent (L3) render the full word `"High"`, while Model Inference API Gateway (L4) and Patient Summary Generator (L7) render the letter `"H"`. Medium (`"M"`) is consistent. Pre-known cosmetic inconsistency, not a K15 item.
- **"Unknown Project" in every title** — confirmed present in all six templates (and in the T015 fallback render below). Pre-existing project-name parse gap on this fixture, out of scope for F-373 (F-373 did not touch project-name parsing). Not a K15 item.
- **risk-funnel Tier 1 / maestro-reference comparison** — the known A-4 issue ("Threats Identified = 0, 0% reduction") is a property of the pre-existing `S/maestro-reference` example only. This iteration's risk-funnel render correctly shows Tier 1 with no count label at all (per the prompt's explicit "no severity color and no count label" instruction) rather than a misleading 0 — not a regression of the known issue.

---

## T015 fallback-model render — baseball-card on `gemini-3.1-flash-image` (`S/t015/`)

Landed during this session (`S/t015/response-baseball-card.json`, `S/t015/threat-baseball-card.jpg`) — judged below using the same Task A checks.

| Template | Model | HTTP | Dimensions | MIME/magic | Key casing | modelVersion | allow_list (IDs/names) | Leakage verdict | IDs verdict | **K15** |
|---|---|---|---|---|---|---|---|---|---|---|
| baseball-card (fallback) | gemini-3.1-flash-image | 200 | 2752×1536 | yes (image/jpeg) | camelCase | gemini-3.1-flash-image | 110 / 29 | clean | 5/5 valid | **PASS** |

`generationConfig` identical to the primary run (`16:9` / `2K`); `finishReason: STOP` on first attempt. This request used an independently authored `data_content` block (same `preamble`/`postamble` scaffold, different wording — e.g. "Coverage Heat Map by Component" vs. "Coverage Heat Map — Residual Severity by Component") rather than reusing iter1's baseball-card text verbatim; `allow_list` (from `infographic-baseball-card.json`) is byte-identical to iter1's.

- No `TOP SECTION`/`LEFT PANEL`/`CENTER PANEL`/`RIGHT PANEL`/`BOTTOM STRIP`/`ALLOWED IDS AND NAMES` rendered.
- IDs shown: S-1, S-2, D-1, E-1, S-5 — all 5 valid, match the five RIGHT PANEL cards.
- Component names (incl. aggregate `"Other — 13 additional components"`) all valid.
- **Cosmetic (fallback-model-specific, not a K15 failure)**: the model rendered an unrequested heading `"Architecture risk-weight strip"` above the bottom strip — the prompt only describes this zone descriptively ("a simplified architecture risk-weight strip," no quoted heading string), so the model paraphrased descriptive instruction prose into a visible label. It does not match any reserved uppercase layout token (`BOTTOM STRIP` itself is correctly never shown), so it is not instruction-leakage in the strict sense, but it is a visible-text invention worth noting for prompt-hardening if this fallback model path is ever promoted.
- **Cosmetic**: Clinical LLM's Critical-severity cell (value 0) renders with a thin red outline instead of the plain dark-gray "zero" styling used by every other zero-value cell — a minor fallback-model rendering inconsistency, not a leak or an invalid ID.

**Fallback row: judged and filled (image existed before this document was written).**

---

## T015 — executive-architecture single-page portrait PDF check (FR-K14.3)

**Method**: copied `S/maestro-reference` → `S/pdfcheck/maestro-reference`, replaced its `threat-executive-architecture.jpg` with `S/iter1/threat-executive-architecture.jpg` (verified by file size match post-copy). Built the report exactly per `S/tachi/.claude/commands/tachi.security-report.md` Step 2 / `S/tachi/.claude/agents/tachi/report-assembler.md` Steps 2c/3a:

```
python3 scripts/extract-report-data.py --target-dir <pdfcheck/maestro-reference> \
  --output templates/tachi/security-report/report-data.typ \
  --template-dir templates/tachi/security-report/
# -> "report-data.typ generated (110 findings, Tier 1)", exit 0
# report-data.typ: has-executive-architecture = true, image path resolved correctly to the swapped jpg

typst compile tachi/templates/tachi/security-report/main.typ pdfcheck/security-report.pdf --root .
# (run with --root set to the scratchpad dir, not S/tachi, so Typst's sandboxed file access
#  could reach pdfcheck/maestro-reference/*.jpg alongside the templates tree — the agent doc's
#  literal `--root .` from the project root does not apply unmodified when target and template
#  trees are siblings under a scratch root; exit 0, 8,853,083-byte PDF, 88 pages)
```

Intermediate `report-data.typ` deleted after successful compile, per Step 3d.

**Page location**: `pdfimages -list` found the 1792×2400 image (object ID 4705) exactly once, on **page 14**, with no other occurrence of that object ID or those dimensions anywhere else in the 88-page document — confirms the image is not split or duplicated across pages. `pdfinfo -f 14 -l 14` reports **page 14 size: 612 × 792 pts (US Letter)** — portrait (height > width). Rendered page 14 to PNG at 60 DPI (`pdftoppm -f 14 -l 14 -r 60 -png`) and viewed it: section heading "Executive Threat Architecture" directly above the full image, with a one-paragraph caption below it and the standard page footer ("Page 14" / "Generated by tachi") — a single, complete, non-split portrait page.

| Check | Result |
|---|---|
| Page number | 14 |
| Page count carrying the image | 1 (confirmed via `pdfimages -list` — object 4705 appears on page 14 only) |
| Page size | 612×792 pt (US Letter) |
| Orientation | Portrait (height 792 > width 612) |
| Image pixel size on page | 1792×2400 (matches source JPEG exactly) |
| Split across pages? | No |

**T015 verdict: PASS.**

---

## 2K latency ruling (P-10.3(d))

| Template | time_total (s) |
|---|---|
| baseball-card | 32.50 |
| system-architecture | 31.94 |
| risk-funnel | 27.09 |
| maestro-stack | 35.73 |
| maestro-heatmap | 32.18 |
| executive-architecture | 34.13 |

Max observed: **35.73 s** (maestro-stack) < **~45 s** W3 drop threshold, on real templates (not the W0 trivial-prompt smoke). All six comfortably inside the single-attempt timeout with margin.

**Ruling: 2K (`imageConfig.imageSize: "2K"`) is kept — no fallback to default size needed.**

---

## Maintainer visual check

**PASS, all six (maintainer, 2026-10-10).** The maintainer reviewed the six iteration-1 renders (`S/iter1/threat-*.jpg`, opened in Preview) against the K15 bar: no prompt section label rendered as text, and every finding ID shown on that template's `allow_list`. Verdict: **all six pass**, with the cosmetic and pre-existing notes above recorded only.

- **TW-5 not consumed**: iteration 1 passed, so no prompt text changed and T032 needs no re-run.
- **TW-6 not fired**: renders were never blocked.
- **K15 ships as committed** (`d0eae8e`, `f57bd37`, `d990f66`, `7f7cd47`, `982c074`).

The T015 fallback render and the PDF page 14 check were judged by the tester above. The maintainer's check covers the six K15 renders, which double as K14's per-template renders under P-10.2 (a).
