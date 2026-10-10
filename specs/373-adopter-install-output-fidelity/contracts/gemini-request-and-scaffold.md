# Contract: Gemini request, template configuration, error handling and prompt scaffold (K14, K15)

**Revision 1 (2026-09-27).** This revision folds in the architect's plan review and the PM's plan review:
- architect: H2 (the allow-list), M3 (scaffold boundaries), M7 (response parsing) and L2, L3 and L7;
- PM: RC-P2 and RC-P3 (the render sets and W0), and R-P2, R-P3 and R-P4 (chain walk, exhausted chain, allow-list wording).

It records the two cross-reviewer reconciliations: the walk set (PD-14) and the allow-list wording (PD-17). Changed sections are marked **(rev. 1)**.

## Request (FR-K14.1)

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
x-goog-api-key: <key from the environment; never ?key=, never echoed, no curl -v/--trace>
Content-Type: application/json
```
```json
{
  "contents": [{ "parts": [{ "text": "<prompt>" }] }],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": { "aspectRatio": "16:9" }
  }
}
```

**(rev. 1) `imageSize`.** `"imageSize": "2K"` is added **inside `imageConfig`** only if P-10.3's rule restores it (PD-3):
- it is live-verified at every shipped model × ratio combination;
- the size is actually honored;
- W3 confirms real-template latency headroom.

The static tests read one pinned constant, `IMAGE_SIZE_RESTORED` (set at W0, in Lane C1's first K14 commit). Flipping it (for example the W3 latency drop) changes the six configuration blocks, the reference, the adapter copy and the constant **in one commit**.

**Forbidden:** `aspectRatio` or `imageSize` directly under `generationConfig`; `resolution` (anywhere in the reference or the adapter copy); any `responseFormat`-shaped body. That last shape belongs to a different endpoint (NG8).

The reference (`gemini-prompt-construction.md`) records provenance as `Verified: models/{model}:generateContent · <model> · <YYYY-MM-DD> · aspectRatio <r> · imageSize <2K|default>`, one line per chain model and ratio. It adds one `Retired models:` line naming the three shut-down models and their dates.

## Response parsing **(rev. 1, M7)**

The REST response carries the image at `candidates[0].content.parts[]`, in the part that has **`inlineData`** with a **`mimeType`** starting `image/`; the bytes are base64 in `inlineData.data`. The reference and the shipped adapter copy name these camelCase REST keys and accept the SDK spelling (`inline_data`, `mime_type`) too, as F-212's own harness did (`specs/212-…/artifacts/final/call_gemini.py:96`).
- **Why it matters now.** Today's text names only the snake_case keys. Every request has failed with 400 until K14, so this parse path runs successfully for the first time at W3.
- **Verification.** W0 records the key casing actually returned, and the K14 render set runs through the agent end to end (§Live verification).

The extension rule is unchanged: `image/jpeg` → `.jpg`, `image/png` → `.png`, otherwise the subtype. A 2xx response with no image part falls in the catch-all error row.

## Template configuration (FR-K14.2, FR-K14.4)

Each of the five templates has a `## Gemini API Configuration` fenced YAML block. Executive-architecture has the same block in `.claude/skills/tachi-infographics/references/executive-architecture.md`, placed after the END marker's following paragraph and before `## Payload schema`, outside the lock markers (PD-1, ratified):

```yaml
model: "gemini-3-pro-image"
fallback_model: "gemini-3.1-flash-image"
response_modalities: ["TEXT", "IMAGE"]
aspect_ratio: "16:9"        # "3:4" for executive-architecture
# image_size: "2K"          # present only if IMAGE_SIZE_RESTORED
```

The comment lines above belong to this contract's illustration only. The shipped YAML blocks carry the keys without comments.

**Key → field table** (in the reference; the agent maps the *active template's* block through it):

| Template key | Request |
|---|---|
| `model` | `models/{model}:generateContent` |
| `fallback_model` | the next model, tried only when the model is unavailable to the key: 404 `NOT_FOUND` or 403 `PERMISSION_DENIED` |
| `response_modalities` | `generationConfig.responseModalities` |
| `aspect_ratio` | `generationConfig.imageConfig.aspectRatio` |
| `image_size` | `generationConfig.imageConfig.imageSize` |

**Routing.** The agent's skill-reference table lists `executive-architecture.md`. For that template, the agent reads its configuration block and its VERBATIM PROMPT BLOCK, and it **never** falls back to the reference's 16:9 dashboard prompt. The reference's no-scaffold routing (`:31-39`) says so explicitly. The locked text still says "portrait, 8.5:11 page aspect ratio" while the canvas is 3:4. That is accepted: the canvas governs, W3 checks the one-page fit, and changing the locked text would need another amendment.

**The shipped adapter copy** (`adapters/claude-code/agents/references/infographic-gemini-api.md`, FR-K14.6) uses the same body, chain, response keys and walk set.

**`INFOGRAPHIC_TEMPLATES.md`'s claim** that "the agent validates these sections exist" is reworded: the static contract test validates them.

## Error table **(rev. 1)**

This is the agent's "Error Handling & Graceful Degradation" table. The walk set and the exhausted-chain row are decided in PD-14 (rev. 1).

| Condition | Spec saved | Image generated | Pipeline blocked | Log level | Chain |
|---|---|---|---|---|---|
| Missing API key | Yes | No | No | Info | — |
| **HTTP 400** (invalid request, including `FAILED_PRECONDITION` such as an unsupported location) | Yes | No | No | **Error** | **Not walked**: every model would reject the same body, and walking would hide the cause. The final summary reports the image step as failed, with the API's message and the request-body **keys** sent |
| **Model unavailable to this key**: HTTP 404 `NOT_FOUND` or 403 `PERMISSION_DENIED` | Yes | only if a later chain model succeeds | No | Warning (per model) | **Walked**, in chain order |
| **Chain exhausted** (every model returned 404 or 403) | Yes | No | No | **Error** | The summary line names each model tried with its status and the API message (R-P3). This is how the next shutdown surfaces |
| Rate limit or quota (429 `RESOURCE_EXHAUSTED`) | Yes | No | No | Warning | Not walked (single attempt; unchanged). The message adds: "if this key has no quota for `<model>`, set the template's `model` to `<fallback_model>` in its `## Gemini API Configuration` block" |
| API timeout (60 s) | Yes | No | No | Error | Not walked (unchanged) |
| Content policy rejection (a blocked prompt, or a `SAFETY`/`IMAGE_SAFETY` finish reason with no image) | Yes | No | No | Warning | Unchanged |
| **Any other non-2xx** (5xx and other 4xx), **or a 2xx with no image part** | Yes | No | No | **Error** | Not walked. The summary reports the status and the API message, or "no image part in the response" |
| Missing Section 6 / empty threat model / script exit 1 or 2 | unchanged | unchanged | unchanged | unchanged | — |

"The pipeline is never blocked by image generation failures" stays true for every image-API condition. No condition is silent (S-11).

## Prompt scaffold rules (FR-K15.3, PD-6) **(rev. 1)**

**The splitter's markers.**
- **Before PD-6:** the preamble ends at the first occurrence of the substring `DATA CONTENT (render this`, with a line-start `DATA CONTENT` fallback, and the postamble starts at the first `\nFOOTER`, falling back to any `FOOTER` substring.
- **After PD-6** (now **W1, Lane B1**, before any template text edit): the marker must start a line (`^DATA CONTENT \(render this`), and `FOOTER` is searched for only at a line start **after** the marker. The no-newline `FOOTER` fallback is dropped.
- **The bare `^DATA CONTENT` fallback is kept (N8, decided per L14; amended at P1, 2026-10-10: the contract pin T007 asked for).**
  - It is still line-anchored, and it still skips the `IMPORTANT:` note's own `…DATA CONTENT sections.` line.
  - It cannot be reached while the primary marker matches, which holds on all five shipped templates. It stays as a safety net for a future marker line without the `(render this` suffix.
  - It is pinned by the comment at `extract-infographic-data.py:181-186`, landed in `1660c10` (T007). No later commit touched the splitter.
- **Byte-neutral.** The output is byte-identical on today's five templates, as verified at plan review on copies.
- **Plan-review probes.** The unhardened splitter corrupted three cases:
  - a preamble line starting `FOOTER`;
  - a preamble copy of the marker text;
  - a hard-wrapped K15 sentence whose `FOOTER)` lands at a line start.

  The hardened splitter handles all three.

**Allowed K15 insertion points:**
- one new paragraph in the preamble, between the `IMPORTANT:` paragraph and `STYLING DIRECTIVES (interpret these, do not display them):`;
- text after the `FOOTER` line.

**Forbidden in these five files (for every lane):**
- a preamble line starting with `FOOTER`;
- the text `DATA CONTENT (render this` anywhere before the header line;
- any fenced block between the `Gemini Prompt Template` heading and the prompt fence;
- removing or renaming the header line.

## K15 instruction text **(rev. 1: final wording, PD-17)**

These texts merge the PM's R-P4 scoping (the restriction covers IDs and names, not "show only this text", so titles, metrics and labels are not suppressed) with the architect's H2 findings:
- system-architecture's legend abbreviates component names;
- executive-architecture renders names under FLOW EDGES and CLUSTERS.

They are final for the first pass. A later change to the locked variant needs another amendment.

**Layout labels.** Identical text in each scaffolded preamble, the reference prompt and the executive-architecture block. It cites only labels present in all six prompts (PD-2 condition 8):
> The uppercase section labels in this prompt, such as DATA CONTENT and FOOTER, are layout instructions. Do not render them, or any other instruction text, as visible text in the image.

**The allow-list rule.** It goes in the five scaffolded preambles and the reference prompt:
> Every finding ID in the image must be one listed on the ALLOWED IDS AND NAMES line below, and every component name must refer to a component listed there. Never show any other ID, and never invent an ID or a component.

"Refer to" tolerates the system-architecture legend's abbreviations (for example "MCP" for a listed "MCP Server"), which the agent composes and the extractor cannot enumerate. The ID clause is exact, because IDs are what SC-5 measures.

**The agent-written line.** It goes in the DATA CONTENT region, quoted from the JSON `allow_list`; the label was renamed from `ALLOWED TEXT` per R-P4:
> `ALLOWED IDS AND NAMES (layout instruction, do not render this line): finding IDs: <comma-separated, or none>; component names: <comma-separated>`

A template with an empty `finding_ids` (risk-funnel, maestro-heatmap) writes `finding IDs: none`, so its prompt forbids every ID.

**Executive-architecture region variant.** It goes inside the lock markers, in the same new paragraph as the layout-label sentence, right after IMPORTANT (PD-2 condition 3, reworded):
> Every finding ID in the image must be one listed under CALLOUTS, and every component name must be one listed under LAYER STACK, FLOW EDGES or CLUSTERS. Never show any other ID, and never invent an ID or a component.

FLOW EDGES and CLUSTERS are included because the block itself requires drawing their named endpoints and members (FR-212-18). In the plan-review scratchpad, flow-edge endpoints outside every layer occur in fixtures `flow-edges-multi` (2), `clusters-single` (1) and `flow-edges-overflow` (98).

**The lock-rule note.** The lock rule in the reference gains a dated note: "Amended by F-373 K15 (<date>): one additive paragraph after IMPORTANT (two instructions); markers, slots and fences unchanged". The same edit reconciles the rule's header list (adding FLOW EDGES and CLUSTERS) and its slot list (7 slots: adding `<<flow_edges_block>>` and `<<clusters_block>>`).

### The FR-212-6 amendment: final conditions (PD-2, ratified with amendments)

1. The marker lines stay byte-identical.
2. No fence and no new `<<slot>>`.
3. **(reworded)** The region variant text above: IDs from CALLOUTS; names from LAYER STACK, FLOW EDGES or CLUSTERS.
4. The amendment is exactly **one paragraph**, placed immediately after the IMPORTANT paragraph.
5. The dated lock-rule note reconciles the stale header and slot lists.
6. The `flow_edges` and `clusters` substrings are kept.
7. The agent's executive-architecture section defers to the verbatim block and drops its contradicting styling lines.
8. **(new)** The layout-label sentence cites only labels present in this prompt.
9. **(new)** A10 proves the amendment is additive: the block with the amendment paragraph removed must hash to the pinned SHA-256 of the pre-change block.

## Static contract test (`tests/scripts/test_gemini_request_contract.py`; fast workflow) **(rev. 1)**

`CHAIN = ["gemini-3-pro-image", "gemini-3.1-flash-image"]`. `IMAGE_SIZE_RESTORED` is set at W0.

| # | Assertion | Lands in |
|---|---|---|
| A1 | The reference request body parses as JSON. It has `generationConfig.responseModalities == ["TEXT","IMAGE"]` and `generationConfig.imageConfig.aspectRatio`, and none of the forbidden keys. `imageConfig.imageSize` is present iff `IMAGE_SIZE_RESTORED`. **No `resolution` anywhere in the reference file**, its `gemini_config` YAML included. The Response Parsing section names `inlineData` and `mimeType` | W1 |
| A2 | Each of the five template blocks parses. Its keys ⊆ {model, fallback_model, response_modalities, aspect_ratio, image_size}. **`model == CHAIN[0]` and `fallback_model == CHAIN[1]`** (the exact order). `response_modalities == ["TEXT","IMAGE"]` and `aspect_ratio == "16:9"`. `image_size == "2K"` iff `IMAGE_SIZE_RESTORED`, and is absent otherwise | W1 |
| A3 | The executive-architecture block exists in `executive-architecture.md` at a line index **after** the END marker line, with A2's key rules and `aspect_ratio == "3:4"` (portrait: width < height) | W1 |
| A4 | The adapter copy's body conforms to A1 (the `imageSize` rule included). There is no `resolution` anywhere in the file, and it names only `CHAIN` models, primary first. Its response parsing names `inlineData` | W1 |
| A5 | The key → field table is present with every row. The reference's chain is exactly `CHAIN`, and its default model is `CHAIN[0]` | W1 |
| A6 | No retired image-model ID (`gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview`, `gemini-2.5-flash-image`) appears in the distributed render surface (`templates/tachi/infographics/`, `.claude/skills/tachi-infographics/`, `.claude/agents/tachi/threat-infographic.md`, `adapters/claude-code/agents/references/`), except the reference's single `Retired models:` provenance line. At HEAD the surface holds 30 such occurrences for Lane C1 to clear. `typst-artifacts.md:114` lies outside the surface and is historical text, correctly exempt | W1 |
| A7 | The agent text has the mapping instruction and the `executive-architecture.md` pointer. The error table has the 400 row ("not walked"), the 404/403 row ("walked"), the exhausted-chain row (Error, models tried) and the catch-all row | W1 |
| A8 | **(strengthened)** For each of the five scaffolded templates: `extract_prompt_scaffold(t)["found"]` is true; the preamble's last line starts with `DATA CONTENT (render this`; the preamble contains `STYLING DIRECTIVES`; the postamble's first line matches `^FOOTER[^\n]*: "`; the postamble contains neither `STYLING DIRECTIVES` nor `DATA CONTENT (render this`; and the postamble's start lies after the marker line in the prompt text. The old A8 passed a scaffold corrupted by a wrapped `FOOTER)` line. **N8's assertion (T014; amended at P1, 2026-10-10):** exactly one line-start `FOOTER` after the marker line, on each of the five templates (`test_exactly_one_line_start_footer_after_marker`) | W1 |
| A9 | Each scaffolded preamble, the reference prompt and the executive-architecture block contain the layout-label instruction. Each contains the allow-list rule; executive-architecture has its region variant. In each scaffolded preamble, both lie **after** `IMPORTANT:` and **before** `STYLING DIRECTIVES`. The agent text instructs writing the `ALLOWED IDS AND NAMES` line from `allow_list` | W2 (only if K15 ships) |
| A10 | The executive-architecture lock-marker lines are byte-identical to pinned constants. `flow_edges` and `clusters` are still present, and the dated amendment note exists. **The locked block with the amendment paragraph removed hashes to the pinned pre-change SHA-256** (condition 9) | W2 (only if K15 ships) |
| A11 | The `/tachi.infographic` explicit-path detection text accepts `Residual Score` or `Residual` (FR-K9.3) | W2 |

## Live verification (`[MANUAL-ONLY]`; quickstart §4) **(rev. 1)**

**W0 smoke (PD-3 / P-10.3; RC-P3; R-P2; P-10.1).**
- **The calls.** Eight calls: {`gemini-3-pro-image`, `gemini-3.1-flash-image`} × {16:9, 3:4} × {default size, `imageSize: "2K"`}, each with a trivial prompt.
- **What to record** for each call:
  - the HTTP status;
  - whether an image part came back;
  - its pixel dimensions (from the PNG IHDR or JPEG SOF);
  - the response time;
  - the response part-key casing.
- **Retry.** One retry on a transient 429 or 5xx; the second result stands.
- **Decisions:**
  1. Restore 2K **iff all four 2K calls return an image whose long edge exceeds its default variant's** (2K honored).
  2. **3:4 at the default size must succeed on both models**; if it does not, stop and take it to the architect before T013 commits executive-architecture's configuration. AR-2 scopes this decision to that configuration; the rest of K14 proceeds.
  3. A refusal of the project key with any status **other than 404 or 403** (for example a 429 with a zero quota, or a 400 `FAILED_PRECONDITION`): record it for the architect under ruling AR-2. It is non-blocking: K14 commits with the 404/403 walk set, the architect amends it if needed by the end-of-W2 checkpoint, and W1 is never held.
  4. A model unreachable at W0 triggers P-10.1: diagnose key scope, model entitlement and quota, and retry within TW-6's budget. **W1 proceeds regardless.** A blocked model means 2K stays dropped.

**K14 render set (W3; P-10.2, RC-P2).** It runs through the agent end to end (`/tachi.infographic` in a scratch clone, on a scratch copy of the MAESTRO reference example), not as a bare `curl` of the configured body.
- (a) **K15 ships:** K15's first-iteration renders double as K14's per-template renders.
- (b) **K15 is carved:** each of the six templates renders once, with no leakage check and no iteration.
- (c) **Either way:** at least one render uses the **fallback** model (set that template block's `model` to the fallback in the scratch clone), and executive-architecture (3:4) is assembled into a scratch PDF on **one portrait page**.
- (d) **A blocked model** (P-9.2 or P-10.1) is recorded as statically verified only, in the reference provenance, the PR record and the release notes.
- **Latency (P-10.3 (d)).** If 2K was restored and any 2K render takes more than about 45 s (25% headroom on the 60 s single-attempt timeout), drop 2K before merge through the one-commit flip above, and record why.

**K15 (W3, only if K15 ships).** One render per template, at most two prompt iterations (TW-5). Check for layout-label text and for any ID outside the JSON `allow_list`.

**Each record:**
- template, model, endpoint, date, HTTP status and response time;
- pixel dimensions;
- the visual-check verdict;
- that the extension matches the image's magic bytes;
- the response key casing;
- for executive-architecture, one portrait PDF page.

Images are never committed, and nothing renders into `examples/`.
