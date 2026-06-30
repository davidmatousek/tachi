# T006 — Architect Fork-Resolution Sign-Off (W0→W1 Gate)

> **Feature**: F-333 Citation-URL Remediation (BLP-06 Wave 1)
> **Gate**: W0→W1 load-bearing Architect sign-off (plan.md Architect OBS-2 — must not be skipped)
> **Authority**: Architect decides the HOW (re-classify vs re-point) per fix-class.
> **Evidence base**: research-atlas.md, research-nist.md, research-owasp.md, worklist.md (all W0 complete) + in-tree byte verification (2026-06-29).
> **Rule**: NO apply task (T008/T009/T011/T012) may begin until this is signed.

---

## Verification Performed (this sign-off, in-tree)

| Check | Command result | Used for |
|---|---|---|
| `_verdict_for_status` signature | `:447` = `(url, status, final_url, detail)` — **receives `url`** | Split-valve NOT triggered |
| Global frozensets | `_HARD_ROT_STATUSES` `:288`, `_NEEDS_REVIEW_STATUSES` `:290` | Confirm untouched (NFR-005) |
| ATLAS in `crosswalk.yaml` | **96** `atlas.mitre.org/techniques` citation refs | Concern 3 coverage |
| ATLAS in `mitre-atlas.yaml` | **37** `atlas.mitre.org/techniques` url refs | Re-classify zero-edit scope |
| NIST shared DOI | **73** `doi.org/10.6028/NIST.AI.100-1` refs | Cascade count |
| OWASP distinct URLs | owasp.yaml = 11 (all `/`-terminated); crosswalk.yaml = 16 path forms | Dead-set + trailing-slash |
| llm04 twin coexistence | crosswalk `llm04-…/` `:69` **and** `llm042025-…/` `:1035/1045/1055` | llm04 ruling |
| llm01 byte-identity | owasp `:442` + crosswalk `:39/945/955/965/5359/5368` — all `llm01-prompt-injection/` | Regression guard SC-009 |

---

## Class 1 — ATLAS (FR-002): CONFIRMED — HOST-SCOPED RE-CLASSIFY

**Decision: APPROVED — re-classify, zero data edits.**

- **Target string change**: NONE. All `atlas.mitre.org/techniques/AML.Txxxx` citation URLs stay byte-unchanged in both `mitre-atlas.yaml` (37 url refs) and `crosswalk.yaml` (96 citation refs).
- **Code change**: Add a bounded, module-level table consulted at the TOP of `_verdict_for_status`:
  `_HOST_STATUS_OVERRIDES = {"atlas.mitre.org": {404: Verdict.NEEDS_REVIEW}}`.
  The override is checked BEFORE the `status in _HARD_ROT_STATUSES` branch (`:457`); on a hit it returns `NEEDS_REVIEW`, else falls through to the existing global logic unchanged.
- **Global frozensets `:288`/`:290` stay untouched** → real-rot detection on every other host preserved (NFR-005). A genuine `atlas.mitre.org` 410/451 still classifies `LINK_ROT` (status-scoped: only 404 is overridden — classifier-verdict-contract.md guarantee 2).

**Evidence (research-atlas.md, High confidence)**: homepage 200; technique routes return the Vue SPA shell with a 404 status (client-side routing / anti-bot, NOT server rot); IDs (AML.T0051/0048/0024/0043, full AML.Txxxx run) verified to exist in the authoritative MISP-galaxy MITRE ATLAS cluster. Prior R7 TRIPWIRE determination (`mitre-atlas.yaml:18–26`) CONFIRMED.

**Genuinely-missing ID**: NONE. Research found every spot-checked ID valid; no per-ID re-point is warranted. D1 alternative (c) "per-ID re-point" is NOT exercised.

### Split-valve: NOT TRIGGERED (explicit confirmation)
`_verdict_for_status` **already receives `url`** as its first parameter (verified in-tree at `:447`). Host-scoping is therefore a bounded local addition at the top of one pure function. **NO `classify_one()` control-flow refactor is required.** Per plan D2 Team-Lead C2, the work stays on the pre-authorized "stay" branch (bounded override map + one synthetic-404 test) and does NOT split to a BLP-06 Wave 2 sibling. F-333 ships the classifier change together with the NIST+OWASP data fixes.

### Concern 3 (MANDATORY) — host-keyed coverage of the ~96 crosswalk refs: PROVEN
The override key is the **host** (`atlas.mitre.org`), not a file or a record. `_verdict_for_status` is called once per resolved URL regardless of which catalog cited it, so a single host entry suppresses the 404→rot verdict for **all** `atlas.mitre.org/techniques/…` citations uniformly: the 37 `mitre-atlas.yaml` url refs **and** the **96** `crosswalk.yaml` citation refs (133 occurrences total, in-tree verified this sign-off). Coverage is **proven by the call-graph + host-keying**, not assumed. No `crosswalk.yaml` edit is needed for the ATLAS class.

---

## Class 2 — NIST (FR-003): APPROVED — re-point, cascades to 73 records

**Decision: APPROVED — re-point the dead DOI to the recommended NIST landing page.**

- **Dead URL**: `https://doi.org/10.6028/NIST.AI.100-1` (73 url refs in `nist-ai-rmf.yaml`, all sharing this one string — verified 73 this sign-off).
- **Approved target string**:
  `https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10`
- **Cascade**: single find/replace → all 73 records (one URL pattern).

**Why this canonical (research-nist.md)**: 200 OK confirmed; stable NIST publication landing page (more restructure-resilient than a direct PDF); unambiguously identifies **AI 100-1 "AI RMF 1.0"** (Jan 26 2023) — correctly distinct from **AI 600-1** (the Generative-AI Profile, owned elsewhere); exposes the DOI/PDF download options on-page. The DOI itself 302-redirects to a stale 2022-03-30 pre-release Crossmark PDF artifact, so the DOI is rejected as the citation target until NIST repairs it. The lowercase direct PDF (`nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf`) is a valid fallback but less stable — landing page is the correct primary. **No better canonical identified; research recommendation accepted as-is.**

---

## Class 3 — OWASP (FR-004): CONFIRMED dead-set + RULINGS

**Decision: APPROVED — re-point the 4 confirmed-dead strings; owasp.yaml ALL-LIVE (zero edits); PLUS normalize the llm04 non-year twin (ruling below).**

### Confirmed dead-set (crosswalk.yaml only) and exact targets

| Dead string (crosswalk.yaml) | Status | Approved target string |
|---|---|---|
| `https://genai.owasp.org/llmrisk/llm02-sensitive-information-disclosure/` `:49` | 404 | `https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/` |
| `https://genai.owasp.org/llmrisk/llm03-supply-chain/` `:59` | 404 | `https://genai.owasp.org/llmrisk/llm032025-supply-chain/` |
| `https://genai.owasp.org/llmrisk/llm05-improper-output-handling/` `:79` | 404 | `https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/` |
| `https://genai.owasp.org/resource/agentic-ai-top-10-vulnerabilities/` (×24: `:400–490`, `:2105–2295`) | 404 | `https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/` |

`owasp.yaml`: **ALL-LIVE — zero edits** (11 distinct URLs, all 2xx after the catalog's own trailing-slash convention; research-owasp.md confirmed). The dead non-year `llm02/03/05` twins and the dead `agentic-ai-top-10-vulnerabilities` slug exist ONLY in `crosswalk.yaml`.

### RULING A — llm04 non-year twin: NORMALIZE (do not leave)

**Ruling: ALSO re-point `https://genai.owasp.org/llmrisk/llm04-data-and-model-poisoning/` (`crosswalk.yaml:69`) → `https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/`.**

**Justification.** FR-004 mandates twins be "disambiguated so no stale variant survives." The non-year `llm04-` currently 301-redirects to the live 2025 form, so the monitor sees HEALTHY and #332 does NOT force the edit — but "monitor-green" and "FR-004-compliant" are different bars, and the Architect owns the consistency bar. Three reasons normalize wins over leave:
1. **Twin-consistency is the FR.** crosswalk.yaml already carries the canonical `llm042025-…/` (`:1035/1045/1055`) **alongside** the non-year `llm04-…/` (`:69`) — two strings for one OWASP risk. Leaving `:69` keeps a known-stale variant alive purely on OWASP's redirect goodwill; its three siblings (llm02/03/05) are being normalized in the same edit, so leaving llm04 is a gratuitous inconsistency.
2. **Redirect-dependence is fragile.** A 301 is a host courtesy, not a contract; if OWASP retires the non-year alias later, this silently rots. Normalizing now removes the future #332 finding pre-emptively (matches BLP-06's subtractive, debt-reducing intent).
3. **Cost is one line, risk is zero.** The canonical target is already in-catalog and live; this is a same-shape string value change, fully covered by the FR-004 edit surface — no new edit class.

This makes the LLM02/03/04/05 quartet uniformly point at the `llm0X2025-*` canonical form, satisfying "no stale variant survives" literally.

### RULING B — Trailing slash: MATCH THE EXISTING TRAILING-SLASH-PRESENT CONVENTION

**Ruling: apply targets WITH a trailing slash (`…/`), because the catalog's established convention is trailing-slash-PRESENT — not absent.**

> **Correction to the gate premise.** The T006 prompt stated "the existing catalog convention uses NO trailing slash." In-tree verification this sign-off shows the **opposite**: every live `genai.owasp.org/llmrisk/…` and `/resource/…` URL in BOTH files already terminates with `/` (e.g. `owasp.yaml:442` `llm01-prompt-injection/`; the live `llm042025-…/` at crosswalk `:1035`; all 11 owasp.yaml URLs). The byte-style risk runs the other way: dropping the slash would CREATE inconsistency. research-owasp.md's canonical column is already `/`-terminated and is therefore byte-consistent with the catalog. The 301→200 "follow" behavior the prompt cites confirms a *bare* form would still resolve, but resolvability is not the bar — **catalog byte-consistency is**, and that means keep the trailing slash. The apply MUST use the `/`-terminated targets exactly as tabled above. (`test_citation_shape()` is regex/file-only and slash-agnostic, so this is a style/consistency ruling, not a test-pass ruling.)

### Regression guard — llm01 (SC-009): byte-UNCHANGED in BOTH files
`https://genai.owasp.org/llmrisk/llm01-prompt-injection/` is LIVE and stays byte-identical: `owasp.yaml:442` and `crosswalk.yaml:39/945/955/965/5359/5368`. **Do not touch any llm01 occurrence in either file.**

---

## Class 4 — Scope hygiene (FR-005): CONFIRMED OUT / values-only

- **#325 stays OUT.** The 31 `tachi-control-category → nist-ai-rmf` local-file edges (cite `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`, per `deferred-325.md`) are a distinct defect class from the dead-DOI and remain deferred (FR-005). They are NOT touched by this feature. A documented-deferred no-op artifact is expected at deliver (PM carry-forward M2).
- **Values-only, no schema/shape change.** Every NIST + OWASP edit changes a citation **string value** in place. No record added/removed, no key/field added/renamed, no record count change in any catalog. The record schema/shape is unchanged → Constitution III (Backward Compatibility) holds; FR out-of-scope (schema/field changes) respected.
- **FR-007 render-exposure (D5)**: re-confirm at apply via grep of the byte-baselined render artifacts for the in-scope strings; expected zero hits (`extract-report-data.py:1140–1193` reads ids/counts, never citation strings). Since this fix changes zero records in any framework, the #185 `ORDERED_FRAMEWORKS` record-count trap is not in play. (Operational reminder for W1/W2; not a gate condition here.)

---

## Edit-Surface Summary (post-resolution, for W1)

| File | Class | Edit | Count |
|---|---|---|---|
| `scripts/check-citation-urls.py` | ATLAS | `_HOST_STATUS_OVERRIDES` table + top-of-fn guard | ~5–15 LOC + comment |
| `schemas/taxonomy/mitre-atlas.yaml` | ATLAS | header comment only (R7/FR-033 note) | 0 url edits |
| `schemas/taxonomy/crosswalk.yaml` | ATLAS | untouched (host override covers 96 refs) | 0 |
| `schemas/taxonomy/nist-ai-rmf.yaml` | NIST | DOI → NIST landing page | 73 refs / 1 pattern |
| `schemas/taxonomy/crosswalk.yaml` | OWASP | re-point 4 dead + normalize llm04 (5 distinct strings); leave llm01 | llm02/03/04/05 ×1 each + agentic ×24 |
| `schemas/taxonomy/owasp.yaml` | OWASP | none (all-live) | 0 |

---

## STATUS

**APPROVED** — proceed to W1 (apply tasks T008/T009/T011/T012), then W2.

- ATLAS: host-scoped re-classify, zero data edits; split-valve NOT triggered (`_verdict_for_status` already receives `url`); Concern-3 96-ref crosswalk coverage proven via host-keyed override.
- NIST: re-point DOI → `https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10` (cascades to 73 records).
- OWASP: 4 confirmed-dead crosswalk strings re-pointed + llm04 non-year twin NORMALIZED to the 2025 canonical (RULING A); targets keep the trailing slash to match the existing convention (RULING B — gate premise corrected); owasp.yaml all-live (0 edits); llm01 byte-unchanged in both files.
- Hygiene: #325 OUT; all edits are citation string VALUES only — no schema/shape/record-count change.
