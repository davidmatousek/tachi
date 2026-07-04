# SC-003 Verification Record — F-292 T017 / D-1 Emission-Level Gate

**Feature**: #295 | **User Story**: US1 (Phase 3, T003–T009) | **Date**: 2026-07-03
**Owner**: security-analyst | **Attempt cap**: 2 live runs — **both consumed, both concluded** (no M-1 escape hatch invoked)

**Verdict: PASS**

---

## 1. Anchor (immutable, pre-F-292)

| Field | Value |
|---|---|
| Anchor ref | `0629fa2~1` |
| Resolved commit SHA | `3f107e3f1e5ffa37efa40793629136b34f2b4cea` |
| F-292 squash-merge commit | `0629fa2` (2026-05-14, PR #293, v4.36.0) |
| Anchor commit date | 2026-05-10 |
| Authoritative artifact | `examples/agentic-app/sample-report/threats.sarif` via `git show` |

**Command** (T001, re-verified T003/T006):
```bash
git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif \
  | jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))]'
```

**Result**: non-empty, cardinality 4, findingIds exactly `["OI-1","OI-2","OI-3","OI-4"]`. Committed to `test-results/anchor-oi-subset.json`. False-pass guard (contract §2) satisfied.

---

## 2. Corrected extraction filter (authoritative)

```bash
jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))]' <input.sarif>
```

Per `contracts/oi-extraction-contract.md` §1: the OI discriminator is `partialFingerprints["findingId/v1"]` — **never** `ruleId` (real ruleIds are `tachi/*`-family; the archived §3 filter matches zero results on every SARIF file and false-passes empty-vs-empty). This filter applies uniformly to both the anchor and fresh sides regardless of path (contract §3).

---

## 3. Fresh-side narrative: two attempts, both concluded, no M-1

### Attempt 1 (primary path, per plan D-A) — NO_FINDINGS, treated as gate ERROR

**Command / dispatch**: single-agent `tachi-output-integrity` dispatch with orchestrator-shaped context (component set + full `examples/agentic-app/architecture.md` + OI analysis scope). Dispatch payload persisted verbatim at `test-results/t017-dispatch-payload.md`.

**Result**: zero YAML finding blocks returned. The agent's verbatim return (persisted at `test-results/t017-fresh-findings.yaml`) was a `NO_FINDINGS` sentinel with a two-signal-gate rationale: none of the four dispatched components (LLM Agent Orchestrator, Specialist Agent, Long-Running Learning Loop, Clinical Advisory Sub-Agent) satisfied **both** (a) a literal output-integrity trigger-keyword match and (b) a structural downstream-execution-sink data flow, per the agent's own FR-011 both-signal requirement.

**Disposition**: Per contract §2, "any empty extraction ⇒ gate ERROR — halt; never interpret as zero emissions = PASS." An empty fresh-side extraction is unconditionally a gate ERROR regardless of how well-reasoned the zero-finding rationale is — the false-pass guard cannot distinguish, from the fresh side alone, "correctly found zero" from "the dispatch context under-triggered." This forced the pre-decided fallback (contract §3 / plan D-A).

**Methodology learning (D-A, recorded for future verification-run planning)**: Attempt 1's zero is **not** evidence of an emission regression. Independent proof: the committed `examples/agentic-app/sample-report/threats.md` at HEAD (regenerated 2026-06-02, post-F-292, by a full pipeline run) carries OI-1 through OI-4 with full descriptive content — proving a properly-scoped run reliably emits these four findings on this architecture. Attempt 1's NO_FINDINGS is therefore a comparison-path artifact: the single-agent primary path (chosen per D-A specifically to avoid full 14-agent orchestrator dispatch / context overflow risk, resolving PRD OQ-5 / Architect M-a) received a narrower payload (four named components + a two-signal gate) than the full orchestrator pipeline's Phase 1–3 context (DFD classification, sink/flow tagging resolved upstream). For **this** architecture and **this** detection task, the single-agent primary path under-triggers relative to full-pipeline dispatch, even though the ground truth is a real, stable 4-finding emission. This is a genuine input for future D-A-style path selection: either the single-agent dispatch payload needs richer sink/flow context to reliably trigger the both-signal gate, or the scoped-full fallback should be considered primary for OI-comparison-style verification runs specifically.

### Attempt 2 (fallback path, per contract §3 / plan D-A) — non-empty, valid

**Command**: scoped-full `tachi-orchestrator` run, Phase 5 skipped, stateless (no baseline).

**Run directory** (gitignored, not committed): `examples/agentic-app/test-output/t017-fallback-2026-07-03T12-30-15/`

**Provenance**: 79 raw findings; 71 SARIF results; populator ran (`affected_assets: []` on every result — no asset tags present in this architecture).

**Native artifacts copied to committed evidence locations**:
- `specs/295-f292-verification-runs/test-results/t017-fallback-native-threats.sarif`
- `specs/295-f292-verification-runs/test-results/t017-fallback-threats.md`

**Corrected-filter extraction**:
```bash
jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))]' \
  specs/295-f292-verification-runs/test-results/t017-fallback-native-threats.sarif \
  > specs/295-f292-verification-runs/test-results/fresh-oi-subset.json
```

**Result**: non-empty, cardinality 4, findingIds exactly `["OI-1","OI-2","OI-3","OI-4"]`. False-pass guard (contract §2) satisfied. Attempt cap (2) reached; attempt 2 succeeded — **M-1 escape hatch was never triggered** (M-1 applies only to 2× tooling *failure*; here attempt 2 produced a valid, gate-evaluable extraction).

### Machinery evidence: false-pass guard demonstrated on attempt-1 output

Per T006, the T005 assembler tool was run against the attempt-1 file to demonstrate the fail-closed guard working end-to-end:

```bash
python3 specs/295-f292-verification-runs/tools/assemble_oi_sarif.py \
  specs/295-f292-verification-runs/test-results/t017-fresh-findings.yaml
```

**Verbatim stderr + exit code**:
```
ERROR: YAML parse error in specs/295-f292-verification-runs/test-results/t017-fresh-findings.yaml: while scanning an alias
  in "<unicode string>", line 7, column 400:
     ... ponents yields zero qualifiers: **LLM Agent Orchestrator** has n ... 
                                         ^
expected alphabetic or numeric character, but found '*'
  in "<unicode string>", line 7, column 401:
     ... onents yields zero qualifiers: **LLM Agent Orchestrator** has no ... 
                                         ^
EXIT CODE: 1
```

Non-zero exit, explicit stderr message, **no empty-but-valid SARIF ever printed to stdout** — confirming the assembler's fail-closed contract (`assemble_oi_sarif.py` docstring §2 / contract §2) holds even against a genuinely non-YAML sentinel payload (the NO_FINDINGS prose contains markdown `**bold**` which is invalid bare-YAML, triggering a parse error rather than the "zero blocks parsed" path — both are fail-closed outcomes; neither produces a false pass).

### Deterministic re-verification (T006)

Both extractions were independently re-derived from their respective source artifacts and diffed against the committed subset files:

```bash
# Anchor re-derivation
git show 0629fa2~1:examples/agentic-app/sample-report/threats.sarif \
  | jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))]' \
  > /tmp/anchor-reverify.json
diff <(jq -S . /tmp/anchor-reverify.json) <(jq -S . test-results/anchor-oi-subset.json)
# → IDENTICAL (empty diff)

# Fresh re-derivation
jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))]' \
  test-results/t017-fallback-native-threats.sarif > /tmp/fresh-reverify.json
diff <(jq -S . /tmp/fresh-reverify.json) <(jq -S . test-results/fresh-oi-subset.json)
# → IDENTICAL (empty diff)
```

Both sides: cardinality 4, findingId set `{OI-1, OI-2, OI-3, OI-4}` — reproducible, deterministic, matching the committed subset files exactly.

---

## 4. Both OI subsets

| Side | File | Cardinality | findingIds |
|---|---|---|---|
| Anchor | `test-results/anchor-oi-subset.json` | 4 | `OI-1`, `OI-2`, `OI-3`, `OI-4` |
| Fresh (fallback native) | `test-results/fresh-oi-subset.json` | 4 | `OI-1`, `OI-2`, `OI-3`, `OI-4` |
| Attempt-1 raw (empty) | `test-results/t017-fresh-findings.yaml` | 0 (NO_FINDINGS sentinel) | — |

---

## 5. D-1 hard gate — sink/flow identity table

Primary identifier = `locations[].logicalLocations[].name` (structural component identifier, present both sides). Secondary = quoted flow name from the `message.text` lead clause (verbatim both sides; punctuation style — `"…"` on anchor vs `` `…` `` on fresh — is phrasing drift, not an identity signal).

| Finding | Primary (anchor) | Primary (fresh) | Match | Secondary (anchor, verbatim) | Secondary (fresh, verbatim) | Match |
|---|---|---|---|---|---|---|
| OI-1 | `LLM Agent Orchestrator` | `LLM Agent Orchestrator` | Y | `"Response (HTTPS)"` | `` `Response (HTTPS)` `` | Y |
| OI-2 | `LLM Agent Orchestrator` | `LLM Agent Orchestrator` | Y | `"Tool Call Request (JSON-RPC)"` | `` `Tool Call Request (JSON-RPC)` `` | Y |
| OI-3 | `LLM Agent Orchestrator` | `LLM Agent Orchestrator` | Y | `"Tool Call Request (JSON-RPC)"` | *(no explicit quote — paraphrased: "instruct the Tool Server to fetch a URL synthesized from LLM output")* | Y — **by corroboration**, see note |
| OI-4 | `Clinical Advisory Sub-Agent` | `Clinical Advisory Sub-Agent` | Y | `"Clinical Summary + Recommendations"` | `` `Clinical Summary + Recommendations` `` | Y |

**OI-3 transparency note**: the fresh side's message lead does not contain an explicit quoted flow name for OI-3 (unlike OI-1/OI-2/OI-4, which all quote a flow name verbatim on both sides). It paraphrases the same mechanism in prose ("instruct the Tool Server to fetch a URL synthesized from LLM output") without naming the `Tool Call Request (JSON-RPC)` flow explicitly. This is resolved as a match **by corroboration**, not a silent pass: (a) the primary structural identifier matches (`LLM Agent Orchestrator` both sides); (b) the same document's OI-2 finding explicitly quotes `Tool Call Request (JSON-RPC)` as the Orchestrator→Tool-Server channel on *both* sides identically; (c) the architecture has exactly one Orchestrator→Tool-Server flow, so the fresh OI-3 paraphrase cannot plausibly refer to a different, conflicting flow. No alternate or conflicting flow name is asserted anywhere in the fresh OI-3 text — the signal is absent, not contradictory. This nuance is disclosed here rather than silently folded into a bare "Y."

**Identity table result: all 4 findings — primary AND secondary identity matched (4/4), no mismatch.**

---

## 6. Diff (anchor vs fresh, normalized)

```bash
diff <(jq -S . test-results/anchor-oi-subset.json) <(jq -S . test-results/fresh-oi-subset.json)
```

Full normalized diff (all four findings show the same delta pattern — `uri`, message prose, `ruleId`, `primaryLocationLineHash`, and a properties-object reshape; see §7 for attribution of each class):

```diff
15c15
<             "uri": "examples/agentic-app/sample-report/threats.md"
---
>             "uri": "examples/agentic-app/test-output/t017-fallback-2026-07-03T12-30-15/architecture.md"
24,25c24,25
<       "markdown": "Use `textContent` (not `innerHTML`) for all LLM response insertion into the DOM. ..."
<       "text": "Improper output handling — client-side XSS via LLM response rendered in user browser: ... FR-011 two-part gate confirmed: ..."
---
>       "markdown": "Render with `textContent` (never `innerHTML`); ..."
>       "text": "The Orchestrator's `Response (HTTPS)` sends LLM-generated content directly to the User. ..."
28d27
<       "baselineRunId": "2026-04-19T03-20-30",
30c29
<       "primaryLocationLineHash": "9d1908c84077a5e9"
---
>       "primaryLocationLineHash": "bc8145867ba52dd5"
33,35c32
<       "baselineState": "unchanged",
<       "impact": "HIGH",
<       "likelihood": "HIGH",
---
>       "affected_assets": [],
37,38d33
<       "owasp_id": "LLM-05",
<       "severity": "Critical",
40,43d34
<         "security",
<         "ai",
<         "llm",
<         "output-integrity",
47c38
<     "ruleId": "tachi/ai/llm"
---
>     "ruleId": "tachi/ai/llm-threats"
```

(Pattern repeats identically in kind for OI-2, OI-3, OI-4 — full raw diff available by re-running the command above against the committed subset files; omitted here for brevity, no additional delta *classes* appear beyond those itemized in §7.)

---

## 7. Attribution (fail-closed — every non-gate delta mapped to a class)

| # | Delta | Anchor | Fresh | Class | Evidence / commit SHA |
|---|---|---|---|---|---|
| 1 | `ruleId` | `tachi/ai/llm` | `tachi/ai/llm-threats` | **Pre-existing cross-tier ruleId naming gap** (orchestrator live-authoring spec vs regeneration-script canonical mapping) — not introduced since anchor | `.claude/skills/tachi-orchestration/references/sarif-specification.md:26` documents `tachi/ai/llm-threats` (fresh conforms exactly); `scripts/sarif_common.py:36-38` maps LLM/OI/MI → `tachi/ai/llm` (anchor conforms to this instead). Bounded walk `git log --oneline 0629fa2..HEAD -- .claude/agents/tachi/ .claude/skills/tachi-orchestration/ scripts/sarif_common.py schemas/finding.yaml` returned exactly 4 commits (`3d3d29f` F-260b 2026-06-01, `ac07085` F-098 2026-06-02, `60dd3b5` F-315 2026-06-03, `0e5ee1c` #311 2026-06-04) — none touches the ruleId mapping. The gap predates the anchor-to-HEAD window; it is a standing inconsistency between two independently-maintained tables, not new drift. |
| 2 | `primaryLocationLineHash` (per finding) | e.g. `9d1908c84077a5e9`, `dfa22757977c9e02`, `6fbbb28e39fb5f3c` (three *different* hashes despite identical ruleId+component) | `bc8145867ba52dd5` (shared across OI-1/2/3 — same ruleId + component) | **Derivative of #1** — hash = `SHA256(ruleId\|component_name)[:16]` per `sarif-specification.md` "Fingerprint Computation". Computed live: `SHA256("tachi/ai/llm-threats\|LLM Agent Orchestrator")[:16]` = `bc8145867ba52dd5` — exact match to all 3 fresh values, confirming fresh is spec-conformant and correctly dedup-hashes same-ruleId/same-component findings per spec intent. `SHA256("tachi/ai/llm\|LLM Agent Orchestrator")[:16]` = `90aa618ea4844ff5` — matches **none** of the anchor's 3 distinct values, confirming the anchor was generated under a different (or no) canonical hash formula, itself a pre-anchor artifact. | Computed inline (see command below) |
| 3 | `baselineState`, `baselineRunId` | present (`"unchanged"`, `"2026-04-19T03-20-30"`) | absent | **Run-configuration**: this fallback run was explicitly **Phase 5 skipped, stateless (no baseline)** per plan D-A / task scope — baseline correlation machinery never executed, so these fields were correctly never computed. `.claude/skills/tachi-orchestration/references/baseline-correlation.md`: "No baseline found: Operate in stateless mode (identical to pre-baseline behavior)." | Task run configuration (this record §3); baseline-correlation.md |
| 4 | `severity`, `likelihood`, `impact`, `owasp_id`, extended `tags` (`security`, `ai`, `llm`, `output-integrity`) | present | absent (fresh retains only `maestro-layer:L1`) | **Legacy/extra result-property richness in anchor, not required by the current documented spec** — not introduced since anchor | `.claude/skills/tachi-orchestration/references/sarif-specification.md` "Complete field mapping reference" (lines 137-153) and "JSON Structural Self-Check" (lines 575-587) — neither lists these as required (or optional) result properties. Fresh conforms exactly to what is currently documented. Bounded walk (same range/paths as row 1) found no commit removing such fields from the spec — the anchor's extra richness (or the spec's simplification relative to it) predates the 0629fa2..HEAD window. |
| 5 | `properties.affected_assets` | absent | present (`[]`) | **F-260b** (named contract class) | commit `3d3d29f` "feat(302): asset-tag output wiring (F-260b, BLP-04 Wave 2) (#303)", 2026-06-01 — in-window |
| 6 | `properties["maestro-layer"]` + `tags` entry `maestro-layer:L1`/`L7` | present, matches | present, matches | **F-098/#311** (named contract class) — **non-delta**, values identical both sides, no attribution burden | noted for completeness only |
| 7 | `locations[].physicalLocation.artifactLocation.uri` | `examples/agentic-app/sample-report/threats.md` | `examples/agentic-app/test-output/t017-fallback-2026-07-03T12-30-15/architecture.md` | Structural — each side's own real input file path; not part of the D-1 gate surface, not a drift "class" | self-evident from run configuration |
| 8 | `message.text` / `message.markdown` prose | full LLM-authored prose | condensed LLM-authored prose | **Drift bucket by design** (contract §4: "Message prose is drift by design: two LLM sessions phrase the same emission differently") | no attribution required |

**Hash verification command** (row 2):
```bash
python3 -c "
import hashlib
print(hashlib.sha256('tachi/ai/llm|LLM Agent Orchestrator'.encode()).hexdigest()[:16])
print(hashlib.sha256('tachi/ai/llm-threats|LLM Agent Orchestrator'.encode()).hexdigest()[:16])
"
# → 90aa618ea4844ff5   (matches none of anchor's 3 distinct hashes)
# → bc8145867ba52dd5   (matches all 3 of fresh's hashes, exactly)
```

**Attribution result: all 8 delta rows mapped to a named or explained class. Zero unattributable deltas.**

---

## 8. Gate verdict

| Gate field | Result |
|---|---|
| OI finding count | 4 = 4 → **MATCH** |
| findingId set | `{OI-1,OI-2,OI-3,OI-4}` = `{OI-1,OI-2,OI-3,OI-4}` → **MATCH** |
| Per-finding sink/flow identity | 4/4 primary + 4/4 secondary (1 by corroboration, disclosed) → **MATCH** |
| Attribution | 8/8 non-gate deltas attributed, 0 unattributable → **CLEAN** |

## **VERDICT: PASS**

Per contract §6: PASS ⇒ this record + T017 checkbox on #295 + FR-008 contract-defect filing (always). All three actions completed (checkbox: §10 below; filing: §9 below).

---

## 9. Filings

| Issue | Title | Trigger | Status |
|---|---|---|---|
| [#354](https://github.com/davidmatousek/tachi/issues/354) | `defect(292): cross-link-no-emission-contract.md §3/§6 — broken ruleId filter + non-executable invocation` | ALWAYS (FR-008, contract §3 dual defect) | Filed |
| [#355](https://github.com/davidmatousek/tachi/issues/355) | `defect: examples/agentic-app/sample-report/threats.md duplicates output-integrity findings under legacy LLM-5/6/7 and current OI-1/2/3 IDs` | Discovered-defect (duplicate-ID claim verified true — see §11) | Filed |

FR-007 conditional defect Issue (T007 verdict = FAIL) — **not applicable**; verdict is PASS.

---

## 10. Issue #295 linkage

- T017 checkbox flipped `- [ ]` → `- [x]` on Issue #295 (T026/US2 checkbox left unchanged — out of scope for this record).
- Comment posted on #295 linking this record path, verdict, and commit SHA.

---

## 11. Duplicate-ID discovered-defect verification (T009 item 3)

**Claim**: the committed `examples/agentic-app/sample-report/threats.md` at HEAD duplicates output-integrity content under both legacy `LLM-5/6/7` IDs and current `OI-1/2/3` IDs (F-292's prefix carve-out allegedly never removed the old rows).

**Verified: TRUE.** Grep evidence against HEAD:

```bash
grep -n "LLM-5\|LLM-6\|LLM-7\|OI-1\|OI-2\|OI-3\|OI-4" examples/agentic-app/sample-report/threats.md
```

- Main findings table: lines 315–317 (`LLM-5`/`LLM-6`/`LLM-7`) describe the same three mechanisms (client-side XSS via Orchestrator response; server-side execution via Tool Call Request; SSRF via LLM-synthesized URL) as lines 334–336 (`OI-1`/`OI-2`/`OI-3`). `OI-4` (line 337, Clinical Advisory Sub-Agent) has no legacy counterpart — a genuinely new addition, not a duplicate.
- Correlated/cross-reference table: lines 638–639, 646–647, 672, 676–677 list both ID sets as separate rows for the same threats.
- Affected Assets table: lines 756–757, 764–765, 790, 794–795 list both ID sets as separate rows.
- Baseline registry (line 63) counts both ranges additively: "LLM-1 through LLM-14, OI-1 through OI-4" — if OI-1/2/3 truly supersede LLM-5/6/7, the true unique count is 3 lower than stated.

Filed as [#355](https://github.com/davidmatousek/tachi/issues/355) (fix-vs-file, FR-020 — no inline edit performed by this feature).

---

## 12. SC-005 (procedure repair) statement

SC-005 requires: "the false-pass hazard is retired — corrected extraction filter committed in the verification record and the contract-§3 defect Issue filed; no future consumer can reuse the broken procedure unwarned."

**Satisfied**:
- Corrected filter (`partialFingerprints["findingId/v1"]`-based) is committed in `contracts/oi-extraction-contract.md` §1 and exercised end-to-end in this record (§2, §3, §6).
- Contract-§3 defect Issue [#354](https://github.com/davidmatousek/tachi/issues/354) is filed, documenting both confirmed defects (zero-match `ruleId` filter; non-executable stdout-JSON invocation) and delegating the archived artifact's disposition (OQ-4) to that Issue.
- The archived `specs/292-output-integrity-cross-sink-refinement/contracts/cross-link-no-emission-contract.md` is **not edited** by this feature (no inline fix, per FR-020 fence) — its broken §3/§6 procedure is superseded for execution purposes by `contracts/oi-extraction-contract.md`, and #354 now carries forward the decision of whether to annotate or correct the archived file itself.
- A future consumer who opens the archived contract will find its defects tracked in a linked, open Issue rather than silently re-encountering the same false-pass — the hazard is retired for any reader who follows the Issue trail, though the archived file's own text is not yet marked superseded in-place (that is #354's OQ-4 decision to make).
