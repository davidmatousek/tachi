---
prd:
  number: "333"
  topic: citation-url-remediation
  created: 2026-06-29
  status: Approved
  type: feature
triad:
  pm_signoff: { agent: product-manager, date: 2026-06-29, status: APPROVED, notes: "Author sign-off. Scope = BLP-06 Wave 1 (P0) citation integrity: remediate the 41 dead citation URLs the F-183 monitor surfaced (#332 tracker), in 3 fix-classes — ~38 MITRE ATLAS, 1 NIST AI RMF DOI (→73 records), 4+ OWASP GenAI. v1.1 folds in all Triad corrections (Architect + Team-Lead both APPROVED_WITH_CONCERNS, zero blockers): FR-2 reframed so host-scoped re-classify is the PREFERRED path on the existing R7 evidence and flat-`atlas-data`-blob re-point is a named NFR-1 anti-pattern (Architect HIGH-1 + Team-Lead C1, both in-tree verified the flat-frozenset classifier + GitHub-runner anti-bot 404); FR-6 acceptance hardened with a landing-content spot-check (Arch MED-1) + `--no-cache` full-sweep requirement + dispatch-input gap note (Arch MED-2); true edit surface ~133 occurrences / 36 distinct stated, not the ~38 finding count (Arch MED-3); OWASP dead-set adjudication widened to year-suffixed `llm0X2025` variants + 2 Agentic resource pages (TL C5); #325 reclassified from fold-iff to DEFER-standalone (TL C3 verified #325's edges cite a LOCAL file, not the dead DOI); FR-7 kept verbatim but expected outcome noted as 'no rendering exposure' for string-only edits (Arch LOW-1 / TL C4); re-classify logic must be unit-tested over a synthetic 404, never a live fetch (Arch LOW-2). Honors source-of-truth positioning + ADR-021 determinism boundary." }
  architect_signoff: { agent: architect, date: 2026-06-29, status: APPROVED_WITH_CONCERNS, notes: "APPROVED_WITH_CONCERNS — no blockers; advance to /aod.plan. Verified EVERY load-bearing claim against code: R7 anti-bot determination (mitre-atlas.yaml:18-26), classifier semantics (check-citation-urls.py:288 `_HARD_ROT_STATUSES={400,404,410,451}` / :290 `_NEEDS_REVIEW_STATUSES={401,403,429}` → a 404 sails past the bot-guard), ORDERED_FRAMEWORKS membership (extract-report-data.py:1077), render path reads IDs/counts not URL strings (:1152+), `test_citation_shape()` regex-only/no-fetch (:286), workflow schedule+dispatch-only (tachi-citation-linkrot.yml:11-17). 1 HIGH + 3 MED + 2 LOW, all plan-stage guardrails on HOW (not whether). HIGH-1: FR-2's two paths are NOT co-equal — flat `atlas-data` raw URL is a 1.5MB un-anchored blob (no per-ID fragment), satisfies FR-1/FR-6 but is NFR-1's exact wrong-but-2xx trap; R7 evidence makes host-scoped re-classify the technically correct fix; re-point-to-flat-file is a named anti-pattern. MED-1 add landing-content spot-check to acceptance (FR-6 self-close is necessary-not-sufficient). MED-2 acceptance run must be `--no-cache` full sweep (TTL `should_skip` default 21d could self-close on stale data; dispatch input exposes only `--inject-sentinel-rot`). MED-3 true occurrence surface ~133 (37 url: + 96 citation:, 36 distinct), not ~38. LOW-1 FR-7 #185 parallel overstated for string-only edits (keep verbatim, guards the add/remove-record edge). LOW-2 re-classify must be unit-tested over a synthetic 404, not a live fetch (ADR-021). All folded into v1.1. Details: .aod/results/architect-333.md." }
  techlead_signoff: { agent: team-lead, date: 2026-06-29, status: APPROVED_WITH_CONCERNS, notes: "FEASIBLE WITH MODIFICATIONS; zero blockers. Revised effort: floor 1.5 / planning 3.0 / ceiling 5.0 eng-days — the PRD's 2.5d top-end is OVERRIDDEN (too low once the re-classify code-path is priced in). In-tree verification: ATLAS pattern is perfectly uniform (36 distinct IDs, 37 url: lines, 98 crosswalk refs — R4 'IDs diverge' downgraded to LOW for the pattern); the classifier is flat global frozensets with NO host-scoping, and the linkrot workflow `runs-on: ubuntu-latest` — so FR-6 self-close needs 2xx from the RUNNER's egress, which a same-host re-point won't achieve → re-classify is the most-likely path (~0.75-1.25d for a host-keyed override + offline test). 6 concerns (1 HIGH, 2 MED, 2 LOW, 1 INFO): C1(HIGH) estimate→3.0d central; C2(MED) split-valve pre-authorized — balloon=classify_one() refactor→split to BLP-06 Wave 2, stay=bounded override map+one test; C3(MED) #325 does NOT fold — its 4 edges cite a LOCAL file not the dead DOI → DEFER standalone; C4(LOW) FR-7 likely clears (counts not strings); C5(LOW) OWASP dead-set messier than 4 (year-suffixed + 2 agentic pages); C6(INFO) F-338 also edits tachi-pytest.yml, run F-333's test post-338 if near-simultaneous. Disjointness from branch 338 confirmed by diff (zero overlap). Build plan: W0 web-researcher fan-out (gated by architect fork sign-off) → W1 senior-backend-engineer parallel edits → W2 tester → code-reviewer → FR-6 dispatch-await (last, async). Details: .aod/results/team-lead-333.md." }
source:
  idea_id: 333
  story_id: null
---

# Citation-URL Remediation — Close the Link-Rot the Monitor Opened (BLP-06 Wave 1)

**Status**: Approved (2026-06-29 — PM author sign-off + Architect APPROVED_WITH_CONCERNS + Team-Lead APPROVED_WITH_CONCERNS; v1.1 folds in all Triad corrections, zero blockers)
**Created**: 2026-06-29
**Author**: product-manager
**Reviewers**: architect, team-lead
**Priority**: P0 — BLP-06 Wave 1 (Citation Integrity), the initiative headline
**Evidence**: Issue [#333](https://github.com/davidmatousek/tachi/issues/333) (`type:retro`, Origin Feature 183), tracking live issue [#332](https://github.com/davidmatousek/tachi/issues/332) (41 confirmed-rot findings). Strategic home: `_internal/strategy/BLP-06-integrity-and-hardening.md` §Wave 1.

---

## Executive Summary

### The One-Liner
Correct (or correctly re-classify) the **41 citation URLs** the #183 monitor flagged as dead across the taxonomy catalogs — in **three fix-classes that require research before any edit** — so the live tracker **#332 self-closes** on a subsequent scheduled monitor run and tachi's machine-readable source-of-truth contract stops shipping (or stops *appearing* to ship) dead authority links.

### Problem Statement
Feature 183's citation link-rot monitor — working exactly as designed — produced its first live signal on 2026-06-15: **41 citation URLs returning HTTP 404**, tracked in the self-healing issue #332. Because tachi is positioned as the **upstream machine-readable contract that downstream AI-security tools consume** ([`tachi_source_of_truth`]), a citation that resolves to a 404 erodes the evidentiary value of every crosswalk edge that cites it — the analyst clicks through to verify a mapping and lands on nothing.

The 41 findings group into three fix-classes — but **only one is unambiguously real link-rot**. The headline complexity of this feature is that fix-class 1 collides with a previously-documented determination:

| # | Fix-class | Count (findings) | Root cause (as filed in #333) | Status / complication |
|---|---|---|---|---|
| 1 | **MITRE ATLAS technique URLs** | ~38 | `https://atlas.mitre.org/techniques/AML.Txxxx` 404; "ATLAS URL scheme changed" | ⚠️ **Contested.** `schemas/taxonomy/mitre-atlas.yaml` header (R7 TRIPWIRE, T020, 2026-04-17) already determined these pages 404 to automated clients as **anti-bot gating**, *not* a stability issue — URL pattern verified stable against MITRE's authoritative `atlas-data` repo. Must be re-adjudicated, not assumed. **Both Triad reviewers (in-tree verified) judge re-classify the likely correct fix — see FR-2.** |
| 2 | **NIST AI RMF DOI** | 1 URL → 73 records | `https://doi.org/10.6028/NIST.AI.100-1` redirects to a now-404 `nvlpubs.nist.gov` PDF; target moved | Likely real; one URL fix cascades to **73** records in `nist-ai-rmf.yaml` (`:49` + citing records). |
| 3 | **OWASP GenAI LLM URLs** | 4+ | `genai.owasp.org/llmrisk/llm02\|llm03\|llm05/...` + `resource/agentic-ai-top-10-vulnerabilities/` 404; site restructured | Likely real but **partial and messier than 4** — `llmrisk/llm01-prompt-injection/` is cited and *not* dead (regression guard); the crosswalk also carries year-suffixed `llm0X2025` variants + 2 distinct Agentic resource pages. FR-1 must adjudicate the actual dead-set. |

### The Central Research Fork (fix-class 1)
The #333 evidence asserts the ATLAS 404s are "verified real (not bot-blocks): both the checker UA and a browser UA get identical 404s." The #183 monitor's classifier treats `401/403/429` as needs-review (bot-block guard) but `404/410` as **confirmed rot** (verified: `check-citation-urls.py` `_HARD_ROT_STATUSES={400,404,410,451}` vs `_NEEDS_REVIEW_STATUSES={401,403,429}`) — so an anti-bot **404** (as opposed to a 403) sails straight past the guard and is reported as real rot. The mitre-atlas.yaml R7 note says exactly that pattern was observed in 2026-04 (even the seed `AML.T0051` page + the matrix index 404 via the same client, while the homepage loads) and judged a *client limitation*. **These two determinations cannot both be acted on blindly.** Resolving which is correct — via MITRE's authoritative `atlas-data` repo as the source of truth for technique-ID existence — is the single hardest and highest-leverage task in this feature, because it forks the remediation. **The decisive constraint (both reviewers, in-tree): the monitor runs on a GitHub-hosted runner (`runs-on: ubuntu-latest`), so #332 self-close requires a `2xx` from that runner's egress — and re-pointing to any *other path on the same `atlas.mitre.org` host* will still 404 that runner.** Therefore:

- **Preferred — re-classify (host-scoped).** The R7 evidence on file points hard here: the technique IDs are valid and `atlas.mitre.org/techniques/AML.Txxxx` *is* the correct human-facing canonical (it renders in a browser; only the headless client 404s). The only defect is the monitor's classifier. Fix = keep the citations as-is, narrow the #183 monitor so `atlas.mitre.org` 404s are treated as needs-review (host-scoped per NFR-5), preserving per-technique granularity, the correct human URL, and real-rot detection on every other host. Smaller, more reversible, and it sidesteps the NFR-1 trap below.
- **Anti-pattern — re-point to the flat `atlas-data` raw blob.** Re-pointing all 36 distinct ATLAS URLs to `raw.githubusercontent.com/.../techniques.yaml` *is* monitor-reachable (so it would satisfy FR-1/FR-6) but it is a single un-anchored 1.5 MB file with no per-technique fragment — an analyst clicking `AML.T0024` lands on a raw dump where they cannot find T0024. That is **NFR-1's exact "wrong-but-2xx, silently misleads" failure, self-inflicted by the fix.** Not a co-equal option; permitted only if FR-1 turns up evidence overturning R7 (unlikely).
- **Non-starter — re-point to another `atlas.mitre.org` path.** Cannot pass FR-6 (the runner 404s the whole host).
- **Real rot (per-ID).** If FR-1 finds a technique ID genuinely retired/moved, that record is real rot → re-point to its new canonical location (or mark `confidence: low` + TODO).

This fork is **the** reason fix-class 1 is research-first, not a bulk find-replace.

### Proposed Solution
A real AOD feature (full lifecycle) that, per fix-class:

1. **Researches the new canonical URL (or re-classification) for each fix-class** against authoritative sources — for ATLAS, the MITRE-owned `atlas-data` techniques.yaml; for NIST, the current AI RMF (AI 100-1) canonical landing page; for OWASP, the restructured GenAI site — verifying each candidate with **both** an automated-client UA and a browser UA, following redirects to final status, **and confirming the monitor's own runner client gets a 2xx** (the only thing that makes #332 self-close).
2. **Applies the corrections.** For NIST (FR-3) and OWASP (FR-4): data-only edits to `nist-ai-rmf.yaml` and the affected `crosswalk.yaml` citation strings — bulk find-replace once the pattern per class is confirmed. For ATLAS (FR-2): apply the path FR-1's evidence supports — **most likely the host-scoped re-classify code change** to `scripts/check-citation-urls.py`, not a data edit.
3. **Lets the #183 monitor be the acceptance gate**: #332 must self-close on a subsequent scheduled (or `workflow_dispatch`) run — driven by a **`--no-cache` full sweep** and corroborated by a **landing-content spot-check** (a green #332 is necessary but not sufficient — a wrong-but-2xx fix would also close it).

### Adjacent Scope (#325) — DEFER (standalone)
Issue [#325] tracks **4 citation-unsupported `tachi-control-category → nist-ai-rmf` edges** (F-180 T029 survivors). The Team-Lead's in-tree check (C3) found these edges cite a **local repo file** (`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`), **not** the dead DOI — so the FR-3 NIST fix does **not** resolve them, and they are a different defect class (citation-support, not link-rot). **Decision: DEFER #325 to a standalone item** (or a later BLP-06 wave); do not fold. Formalized at `/aod.plan` with this evidence.

### Success Criteria
1. Every in-scope citation URL is corrected or correctly re-classified, verified `2xx`-to-the-runner-client (or correctly moved to needs-review) for each fix-class.
2. **#332 self-closes on a subsequent `--no-cache` scheduled / `workflow_dispatch` monitor run** — the real, end-to-end acceptance signal (not a local assertion).
3. A **landing-content spot-check** confirms a sampled corrected URL renders the cited technique/control, not a generic page (guards against a wrong-but-2xx self-close).
4. The fix-class-1 fork (real rot vs. anti-bot 404) is resolved with evidence cited in the delivery record, not assumed.
5. The offline `test_citation_shape()` URL-syntax guard still passes; any re-classify logic is unit-tested over a **synthetic 404** (never a live fetch).
6. No new runtime dependency; the determinism boundary (no network in `pytest`/PR path) is preserved.
7. If any corrected citation string appears in a byte-identity-baselined artifact (the #185 trap), baselines are regenerated and remain green — *expected outcome: no exposure* (the report aggregator reads record IDs/counts, not URL strings).

### Timeline & Milestones
**Estimated effort: 3.0 engineer-days central** (floor 1.5 / ceiling 5.0; Team-Lead-revised — the PRD's initial 1.5–2.5d optimistic top-end is overridden because the ATLAS fix most likely resolves to a classifier *code* change, not a YAML edit). Traces 1:1 to `specs/333-citation-url-remediation/feasibility-check.md`.

| Milestone | Effort (of 3.0d) | Content |
|---|---|---|
| **M1 — Research & adjudication** (Wave 0) | ~1.0d | FR-1 `web-researcher` fan-out over 3 fix-classes (verify 36 ATLAS IDs in `atlas-data`, runner-egress reachability; NIST AI 100-1 canonical; OWASP real dead-set). Architect signs the fork resolution. **Gates everything.** |
| **M2 — Apply corrections** (Wave 1) | ~1.25d | FR-3 NIST cascade (73 records) ∥ FR-4 OWASP re-point ∥ FR-2 ATLAS (re-classify path likely: host-scoped 404→needs-review + offline test). FR-7 rendering-exposure check. |
| **M3 — Validation & gate** (Wave 2) | ~0.75d (+~0.5d wall-clock) | FR-8 offline tests + synthetic-404 classifier unit test → code review (NFR-5 discipline) → **FR-6 dispatch monitor + await #332 self-close** (strictly last, async). |
| **Dev Complete** | **3.0d** | All 41 in-scope citations resolved; #332 self-closed on a dispatched run; landing spot-check passed. |

**Split valve (Team-Lead C2, pre-authorized)**: keep FR-2 in-scope, but if host-scoping requires a `classify_one()` control-flow/config refactor (vs. a bounded host-keyed status-override map + one test), split the classifier work to a BLP-06 Wave 2 sibling and ship F-333 with the data-only fixes.

---

## Strategic Alignment

### Product Vision Alignment
tachi's vision positions it as "a new scanning column alongside SAST, SCA, and Secrets" whose authority rests on a **machine-readable taxonomy contract** downstream tools consume. A crosswalk edge's value is its *traceable, verifiable* mapping to an authoritative source. Citation remediation directly defends that contract — and does so by **eating the dogfood the #183 monitor cooked**: the same feature that proved cited authority URLs can rot is now closing the loop it opened.

### Roadmap Fit
This is **BLP-06 Wave 1 — the initiative headline (P0)**. BLP-06 is the first *subtractive* (maintenance/consolidation) initiative; Wave 1 is its highest-value item because it is the only one that fixes a defect *adopters can see* in shipped output and self-closes a tracked live issue (#332). Disjoint from Waves 2–3 (CI hardening, bug closures), which touch different files (write-set disjointness from branch `338-restore-substitution-hardening` confirmed by diff).

### Predecessor Relationship
Endogenous follow-on of **BLP-05 Wave 3 / Feature 183** (the monitor) and the crosswalk-building features that introduced the citations: **#186** (MITRE ATLAS catalog), **#184** (NIST AI RMF / 600-1 surfaces), and F-180 (the crosswalk itself). Reinforces BLP-05's explicit thesis that *cited authority URLs must stay live*.

---

## Target Users & Personas

### Primary Persona: Tachi Taxonomy Steward / Maintainer
Owns `schemas/taxonomy/`. Received the #332 signal and needs every confirmed-rot citation corrected (or correctly re-classified) so the crosswalk's cited authority is live again and the tracker self-closes — without introducing a wrong-but-alive redirect that masks the breakage.

### Secondary Persona: Downstream AI-Security Tool / Analyst Traversing the Crosswalk
Consumes the taxonomy as evidence. When they click a citation to verify a mapping, a 404 undermines trust in the entire crosswalk. This feature restores the click-through.

### Tertiary Persona: tachi Maintainer of the #183 Monitor
If the fix-class-1 resolution is the (likely) anti-bot 404 re-classification, this persona needs the monitor's classifier narrowed precisely (host-scoped needs-review) so it stops reporting false positives without going blind to real rot on other hosts.

---

## User Stories

### US-1: Corrected ATLAS Citations (or Correct Re-classification)
**As a** taxonomy steward, **I want** the ~38 MITRE ATLAS technique citations adjudicated against MITRE's authoritative `atlas-data` repo and then (most likely) the monitor narrowed so its anti-bot 404s on `atlas.mitre.org` stop being reported as rot — or, if evidence overturns R7, the citations re-pointed to a runner-reachable canonical — **so that** the crosswalk cites live authority for every ATLAS technique and the monitor stops flagging them, based on evidence, not a guess about the URL scheme.

**Acceptance**: Each of the ~38 ATLAS technique IDs is confirmed present in `atlas-data`; the chosen fix yields `2xx`-to-the-runner (re-classify: no longer reported as rot; re-point: resolves at the new canonical); the delivery record states which fork was taken and why.

### US-2: Corrected NIST AI RMF Citation
**As a** taxonomy steward, **I want** the single dead `doi.org/10.6028/NIST.AI.100-1` citation re-pointed to NIST's current canonical AI RMF landing page, **so that** all 73 citing records in `nist-ai-rmf.yaml` resolve again from one fix.

**Acceptance**: The replacement URL resolves `2xx` to the runner client; the citation points at the intended document (AI 100-1, the core RMF — distinct from AI 600-1, the GenAI profile, separately catalogued in `nist-ai-600-1.yaml`); all 73 records reflect the corrected URL.

### US-3: Corrected OWASP GenAI Citations
**As a** taxonomy steward, **I want** the dead OWASP GenAI URLs (LLM02/LLM03/LLM05 + the Agentic resource pages, including any year-suffixed variants FR-1 confirms dead) re-pointed to their restructured canonical locations, **so that** the OWASP citations resolve again.

**Acceptance**: Each confirmed-dead URL resolves `2xx` to the runner client at its new canonical location; the still-live `llm01-prompt-injection/` citation is left unchanged (regression guard).

### US-4: Tracker Self-Closes (End-to-End Acceptance)
**As a** maintainer, **I want** the #332 tracking issue to self-close on a subsequent `--no-cache` scheduled / `workflow_dispatch` monitor run after the fixes land, **so that** I have an automated, end-to-end confirmation that the rot is genuinely cleared — not just a local edit that looks right.

**Acceptance**: A `--no-cache` monitor run after the fix finds zero confirmed rot and auto-closes #332 with its recovery comment; a landing-content spot-check corroborates a sample.

---

## Functional Requirements

### FR-1: Per-Fix-Class Canonical-URL Research & Verification (research-first, load-bearing)
For each of the three fix-classes, identify the correct remediation **before any edit**, grounded in authoritative sources:
- **ATLAS (~38)**: adjudicate the R7 fork against MITRE's authoritative `atlas-data` techniques.yaml (`https://raw.githubusercontent.com/mitre-atlas/atlas-data/main/data/techniques.yaml`). Confirm each technique ID still exists; determine whether the resolution is re-classify (likely) or, only if R7 is overturned, re-point.
- **NIST (1)**: identify NIST's current canonical landing page for AI 100-1 (the core RMF), confirming intent vs. AI 600-1 (the GenAI profile).
- **OWASP (4+)**: locate the restructured canonical locations for LLM02/LLM03/LLM05 and the Agentic resource page(s), and **adjudicate the actual dead-set** — the crosswalk carries year-suffixed `llm0X2025` variants and 2 distinct Agentic resource pages; verify which are actually dead vs. the headline 4.

Every candidate URL MUST be verified with **both an automated-client UA and a browser UA**, with redirects followed to final status, **and confirmed to return `2xx` from the #183 monitor's GitHub-runner egress** (the only outcome that makes #332 self-close). Record the evidence per fix-class for the delivery record (Success Metric 4).

### FR-2: Apply ATLAS Fix-Class Resolution
Based on FR-1's adjudication, apply the chosen path for the ~38 ATLAS citations. The paths are **not co-equal**:
- **Re-classify (PREFERRED, likely).** If the IDs are valid but `atlas.mitre.org` 404s the runner (anti-bot, per R7), apply a **narrow, host-scoped** adjustment to the #183 monitor's classifier in `scripts/check-citation-urls.py` so the affected host's 404s are treated as needs-review (not confirmed rot), preserving real-rot detection on every other host (NFR-5). Citations stay as-is (correct human-facing canonical). This is the smaller, more reversible fix and avoids the NFR-1 trap.
- **Re-point (ANTI-PATTERN — flat blob).** Re-pointing all 36 distinct URLs to the un-anchored `atlas-data` raw file is a named NFR-1 anti-pattern (wrong-but-2xx; misleading landing). Permitted only if FR-1 evidence overturns R7.
- **Re-point (NON-STARTER — same host).** Another `atlas.mitre.org/...` path cannot pass FR-6.
- **Per-ID real rot.** Any ID FR-1 finds genuinely retired/moved → re-point to its new canonical (or `confidence: low` + TODO).

On the re-point path, the true edit surface is **~133 occurrences** (37 `url:` fields in `mitre-atlas.yaml` + ~96–98 `citation:` lines in `crosswalk.yaml`, 36 distinct URLs) — all must change consistently or the catalog goes split-brain and #332 won't fully close. On the re-classify path, **zero data edits**. Update the relevant header comments (FR-033 URL-pattern note, R7 TRIPWIRE note) to record what changed and why.

### FR-3: Apply NIST AI RMF DOI Fix
Replace the single dead `https://doi.org/10.6028/NIST.AI.100-1` citation in `schemas/taxonomy/nist-ai-rmf.yaml` (`:49` + citing records) with the verified canonical URL; the fix cascades to all **73** citing records. Confirm the citation points at the intended AI 100-1 document.

### FR-4: Apply OWASP GenAI Fix
Re-point the confirmed-dead `genai.owasp.org` citations in `crosswalk.yaml` (LLM02/LLM03/LLM05 + the Agentic resource page(s), plus any year-suffixed `llm0X2025` variants FR-1 confirms dead) to their restructured canonical locations. Leave the still-live `llm01-prompt-injection/` citation unchanged (regression guard).

### FR-5: #325 — Deferred (standalone)
The 4 citation-unsupported `tachi-control-category → nist-ai-rmf` edges (#325) are **OUT of this feature's scope**: the Team-Lead's in-tree check confirmed they cite a local file (`.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`), not the dead DOI, so the FR-3 fix does not resolve them, and they are a distinct defect class (citation-support, not link-rot). Run #325 standalone or in a later BLP-06 wave. (Decision formalized at `/aod.plan`.)

### FR-6: Monitor-Driven Acceptance (+ landing spot-check + full sweep)
The feature is NOT done on local edit. Acceptance requires:
- A subsequent scheduled or `workflow_dispatch` run of the #183 monitor, run as a **`--no-cache` full sweep**, to find zero confirmed rot for the in-scope URLs and **self-close #332**. (The TTL ledger's `should_skip` — default 21 days — could otherwise skip a URL on a pre-rot `last_ok` and self-close on stale data; the existing `workflow_dispatch` input exposes only `--inject-sentinel-rot`, not `--no-cache`, so the plan must arrange the full sweep — e.g., a dispatch-input addition or a cleared ledger.) Benign for the dead-then-fixed URLs, which carry no `last_ok`, but the gate must not rely on that subtlety.
- A **landing-content spot-check**: confirm a sampled corrected URL renders the cited technique/control, not a generic page (a green #332 is necessary but not sufficient — a wrong-but-2xx fix self-closes it too).

The deliver stage MUST trigger/await at least one such run and record the run URL + self-close comment as evidence.

### FR-7: ORDERED_FRAMEWORKS Rendering-Exposure Check (the #185 watch-out)
`mitre-atlas` and `nist-ai-rmf` are `ORDERED_FRAMEWORKS` members (verified: `extract-report-data.py:1077`). A *record* edit there normally pulls a CA-baseline regen + coverage-pin lane ([`tachi_changelog_release_model`] / KB Entry 15). **Expected outcome here: NO rendering exposure** — the report aggregator consumes record IDs and counts, never `url:`/`citation:` strings (verified render path), so a pure string edit (or a re-classify code change) is not byte-baseline-exposed. This MUST still be **verified at plan stage** (cheap; don't assume): check whether the corrected citation strings appear in any baselined PDF page or coverage artifact. If they do (or if FR-2 ever drifts into adding/removing a catalog *record* — the edge this FR guards), the regen lane applies and baselines MUST be regenerated and remain green.

### FR-8: Syntactic-Integrity & Determinism Preservation
All edits MUST keep the offline `test_citation_shape()` URL-syntax guard green (`tests/schemas/test_taxonomy_integrity.py:286`, regex-only, no fetch). No edit may introduce a network call into `tests/` or any `pull_request`/`push`-triggered job — the ADR-021 determinism boundary stands. Any monitor-classifier change (FR-2 re-classify path) stays inside the scheduled-only workflow surface and is **unit-tested over a synthetic 404 `Classification`** (the pure, table-driven `_verdict_for_status` + the existing offline `--inject-sentinel-rot` precedent) — **never** a live-fetch test (which would itself breach ADR-021).

---

## Non-Functional Requirements

### NFR-1: Evidence-Before-Edit (no guessing)
No citation is edited on a hunch. Each fix-class's replacement (or re-classification) is justified by an authoritative source and a dual-UA reachability check confirmed against the runner client. The risk this NFR exists to kill is a redirect that *looks* alive but lands on a generic/un-anchored page — a wrong-but-2xx URL is worse than a known-404 because it silently misleads the analyst (this is exactly why the flat-`atlas-data`-blob re-point is an anti-pattern, FR-2).

### NFR-2: Zero New Runtime Dependency
Data-only YAML edits (NIST/OWASP), and on the likely FR-2 path a stdlib-only monitor tweak. No new runtime dependency.

### NFR-3: Determinism Boundary Intact
The #183 NFR-1 invariant is inherited: reachability validation stays scheduled-only and off the `pytest`/PR path. This feature must not weaken it; any classifier change stays in the scheduled-only surface.

### NFR-4: Minimal, Reversible Edits
Prefer the smallest change that resolves each class (a single cascading pattern fix per class where possible; a bounded host-override map for the classifier). Update explanatory header comments so the next reader understands what changed and why — the comments are load-bearing institutional memory.

### NFR-5: Signal-Quality Preservation (monitor changes)
If FR-2 takes the re-classify path, the monitor change MUST be **host-scoped, documented, and reversible** — it may **not** broaden into "treat all 404s as needs-review," which would blind the monitor to real rot on other hosts.

---

## Success Metrics

| Metric | Target |
|---|---|
| In-scope citations resolved/re-classified | 41 / 41 |
| #332 self-close on a subsequent `--no-cache` monitor run | **Yes** (the end-to-end acceptance gate) |
| Landing-content spot-check on a sampled corrected URL | **Pass** (renders the cited item, not a generic page) |
| Fix-class-1 fork resolved with cited evidence | Documented in delivery record |
| Wrong-but-2xx (misleading redirect / un-anchored blob) introductions | **0** |
| Offline `test_citation_shape()` regressions | **0** |
| Re-classify logic validated by a live-fetch test | **0** (synthetic-404 unit test only) |
| New runtime dependencies | **0** |
| Byte-identity baseline regressions (if rendering-exposed) | **0** (expected: no exposure; regen green if FR-7 finds any) |

---

## Scope & Boundaries

### In Scope (P0)
- FR-1 research/verification for all three fix-classes (incl. runner-egress reachability).
- FR-2 ATLAS resolution (host-scoped re-classify, likely) / FR-3 NIST / FR-4 OWASP corrections.
- FR-6 monitor-driven acceptance (#332 self-close via `--no-cache` sweep) + landing spot-check.
- FR-7 ORDERED_FRAMEWORKS rendering-exposure check + conditional baseline regen.
- Updated explanatory header comments in any edited YAML.

### Out of Scope
- ❌ **#325** — its 4 NIST edges cite a local file, not the dead DOI; different defect class. Deferred to standalone (FR-5).
- ❌ **Net-new monitoring capability** — the #183 monitor is shipped; this feature consumes its output (a narrow FR-2 re-classify tweak is the only monitor touch).
- ❌ **Auto-replacement tooling** — remediation is human-triaged research + edit, not an automated URL-rewriter.
- ❌ **General docs/markdown link fixing** — scope is `schemas/taxonomy/*.yaml` citations only.
- ❌ **Wayback/archival snapshotting** of citations — possible future enhancement, not here.
- ❌ **Schema/field changes** to the taxonomy record shape — citation *values* (and classifier logic) only.
- ❌ **BLP-06 Waves 2–3** (CI hardening #329/#338/etc.; bug closures #217/#295) — separate features. If FR-2 balloons into a `classify_one()` refactor, the classifier work splits to a Wave 2 sibling (split valve, §Timeline).

### Assumptions
- MITRE's `atlas-data` repo remains the authoritative source for ATLAS technique-ID existence and returns 2xx to automated clients.
- NIST and OWASP publish discoverable current canonical locations for the moved documents.
- The #183 monitor's `workflow_dispatch` is available to drive FR-6 acceptance on demand (confirmed in-tree).

### Constraints
- Inherits the ADR-021 determinism boundary (FR-8/NFR-3).
- Must respect the #185 consequence-scope lesson (FR-7) — verify rendering exposure, don't assume.
- Edits must keep `test_citation_shape()` green.

---

## Risks & Dependencies

### Technical Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R1 | **Fix-class-1 misadjudication** — treating anti-bot 404s as real rot (or vice-versa), per the R7 collision. Re-pointing to any `atlas.mitre.org` path still 404s the runner → #332 never self-closes. | **HIGH** | FR-1 adjudication against `atlas-data`; verify the chosen fix yields 2xx *to the runner*; prefer the re-classify path (FR-2); FR-6 monitor run is the gate — if #332 doesn't self-close, the fork was resolved wrong. |
| R2 | **Wrong-but-alive redirect / un-anchored blob** — a replacement URL returns 2xx but lands on a generic/changed page (esp. the flat `atlas-data` file), silently misleading analysts. | HIGH | NFR-1 evidence-before-edit; flat-blob re-point named an anti-pattern (FR-2); FR-6 landing-content spot-check; dual-UA verification of landing content. |
| R3 | **Hidden regen lane** — a corrected citation string appears in a byte-identity-baselined PDF artifact (the #185 trap). | LOW (expected) | FR-7 plan-stage check; render path verified to read IDs/counts not URL strings → expected no exposure; regen if a string surfaces. |
| R4 | **ATLAS IDs diverge** — some IDs retired/renamed rather than one clean pattern. | LOW | Pattern verified perfectly uniform in-tree (36 distinct, no sub-technique dots/trailing slash); FR-1 per-ID existence check handles any outlier individually. |
| R5 | **NIST citation-intent ambiguity** — AI 100-1 (core RMF) vs AI 600-1 (GenAI profile); fixing to the wrong document. | MED | FR-3 intent confirmation; AI 600-1 is separately catalogued, so the `nist-ai-rmf.yaml` citation must target AI 100-1. |
| R6 | **Monitor false-positive recurrence** — re-classify taken too broadly blinds the monitor to real rot. | MED | NFR-5 host-scoped, documented, reversible classifier change only; split valve if it needs a refactor. |
| R7 | **OWASP re-restructure** — GenAI site moves again, re-rotting the new URLs. | LOW | Accept; the #183 monitor re-flags and this loop repeats — the monitor working as designed. |

### Dependencies
- **Feature 183 (DELIVERED)** — the monitor + #332 tracker; provides the acceptance gate (FR-6) and, on the re-classify path, the classifier surface (`scripts/check-citation-urls.py`, `.github/workflows/tachi-citation-linkrot.yml`).
- **Features 186 / 184 / F-180** — introduced the affected ATLAS, NIST, and crosswalk citations.
- **MITRE `atlas-data` repo / NIST / OWASP GenAI sites** — authoritative sources for FR-1 research.
- **No collision** with in-flight branch `338-restore-substitution-hardening` (disjoint write-set, confirmed by diff). One INFO note: F-338 edits `tachi-pytest.yml`, in which a re-classify unit test would run — run F-333's test against post-338 `main` if merges are near-simultaneous.
- No dependency on BLP-06 Waves 2–3.

---

## Definition of Done

- [ ] FR-1 research complete: canonical URL (or re-classification) confirmed for all 3 fix-classes, each verified dual-UA + **runner-egress** 2xx, evidence recorded for the delivery record.
- [ ] FR-2 ATLAS resolution applied (host-scoped re-classify likely; re-point only if R7 overturned), header comments updated.
- [ ] FR-3 NIST DOI citation corrected; 73 records reflect the fix; intent (AI 100-1) confirmed.
- [ ] FR-4 OWASP dead-set corrected (incl. any confirmed year-suffixed variants); live `llm01` citation untouched.
- [ ] FR-5 #325 confirmed deferred (standalone), not folded.
- [ ] FR-7 ORDERED_FRAMEWORKS rendering-exposure checked; baselines regenerated + green only if a string surfaces (expected: none).
- [ ] FR-8 `test_citation_shape()` green; no network in `pytest`/PR path; any re-classify logic unit-tested over a synthetic 404.
- [ ] **FR-6: a subsequent `--no-cache` scheduled / `workflow_dispatch` monitor run self-closes #332** (run URL + self-close comment recorded) AND a landing-content spot-check passes.
- [ ] Triad sign-off recorded; CHANGELOG / closure docs updated at deliver; `feat(333):`/`fix(333):` PR yields a release-please PR ([`aod_deliver_release_gate`]).

## Open Questions

### Resolved at Definition (Triad review)
- **Fix-class-1 fork** → **re-classify (host-scoped monitor narrowing) is the preferred path** on the existing R7 evidence; flat-blob re-point is an anti-pattern; same-host re-point is a non-starter. FR-1 confirms against `atlas-data`. *(Architect HIGH-1 / Team-Lead C1)*
- **#325 placement** → **DEFER standalone** (its edges cite a local file, not the dead DOI; the NIST fix won't resolve them). *(Team-Lead C3)*
- **Effort** → **3.0 eng-days central** (floor 1.5 / ceiling 5.0), overriding the PRD's 2.5d top-end. *(Team-Lead C1)*

### To Resolve at Plan / Build
- **Rendering exposure** → expected none (render path reads IDs/counts, not URL strings); verify cheaply at plan. *(FR-7)*
- **Monitor change ownership / split valve** → keep FR-2 in-scope; split the classifier work to BLP-06 Wave 2 *only if* host-scoping needs a `classify_one()` refactor (vs. a bounded override map + one test). *(Team-Lead C2)*
- **`--no-cache` acceptance mechanism** → add a `workflow_dispatch` input or clear the ledger so the acceptance run is a full sweep. *(Architect MED-2 / FR-6)*

---

## References

### Product Documentation
- `docs/product/01_Product_Vision/product-vision.md` — vision (taxonomy contract authority).
- `_internal/strategy/BLP-06-integrity-and-hardening.md` §Wave 1 — strategic home.

### Related PRDs / Features
- `docs/product/02_PRD/183-citation-url-link-rot-monitoring-2026-06-14.md` — the monitor that surfaced #332 (predecessor; provides the acceptance gate).
- `docs/product/02_PRD/186-mitre-catalog-expansion-2026-06-07.md` — introduced the ATLAS citations (fix-class 1).
- `docs/product/02_PRD/184-nist-ai-600-1-surface-c-transcription-2026-06-10.md` — NIST surfaces; #325 origin (deferred).
- `docs/product/02_PRD/180-taxonomy-crosswalk-collection-2026-04-17.md` — the crosswalk + canonical-URL conventions.

### Technical Documentation
- `schemas/taxonomy/mitre-atlas.yaml` — fix-class 1 target; **header R7 TRIPWIRE note (lines 18–26) is the central context**.
- `schemas/taxonomy/nist-ai-rmf.yaml:49` — fix-class 2 target (`url: https://doi.org/10.6028/NIST.AI.100-1`).
- `schemas/taxonomy/crosswalk.yaml` — fix-class 1 + 3 citation strings (`:39` live llm01; `:49/:59/:79` dead llm02/03/05).
- `scripts/check-citation-urls.py` — the monitor classifier (`_HARD_ROT_STATUSES` / `_NEEDS_REVIEW_STATUSES`); FR-2 re-classify surface.
- `.github/workflows/tachi-citation-linkrot.yml` — scheduled-only workflow (`:11–17`); `workflow_dispatch` for FR-6.
- Issue #332 body — the canonical 41-finding list with per-URL source-location back-references.
- `tests/schemas/test_taxonomy_integrity.py:286` — `test_citation_shape()` (the offline syntax guard to keep green).
- `specs/333-citation-url-remediation/feasibility-check.md` — Team-Lead estimate + build wave plan.
- `.aod/results/architect-333.md`, `.aod/results/team-lead-333.md` — full Triad review records.

---

## Approval & Sign-Off

| Role | Agent | Status | Date |
|---|---|---|---|
| PM | product-manager | APPROVED (author) | 2026-06-29 |
| Architect | architect | APPROVED_WITH_CONCERNS | 2026-06-29 |
| Team-Lead | team-lead | APPROVED_WITH_CONCERNS | 2026-06-29 |

---

## Version History

| Version | Date | Author | Changes |
|---|---|---|---|
| v1.0 | 2026-06-29 | product-manager | Initial draft. Feature workflow (parallel Architect + Team-Lead review). Grounded in #332's 41 findings, the mitre-atlas.yaml R7 TRIPWIRE collision (central research fork), the partial-OWASP signal (llm01 still live), and the #185 ORDERED_FRAMEWORKS consequence-scope lesson. BLP-06 Wave 1, P0. |
| v1.1 | 2026-06-29 | product-manager | Folds in all Triad corrections (both APPROVED_WITH_CONCERNS, zero blockers): FR-2 reframed — host-scoped **re-classify is the preferred path** on R7 evidence, flat-`atlas-data`-blob re-point named an NFR-1 anti-pattern, same-host re-point a non-starter (Arch HIGH-1 / TL C1, both in-tree verified the flat-frozenset classifier + GitHub-runner anti-bot 404); FR-6 hardened with a landing-content spot-check (Arch MED-1) + `--no-cache` full-sweep requirement + dispatch-input gap (Arch MED-2); true edit surface stated as ~133 occurrences / 36 distinct (Arch MED-3); NIST cascade corrected 75→73 records; OWASP dead-set widened to year-suffixed + 2 Agentic pages (TL C5); **#325 reclassified fold→DEFER-standalone** (TL C3, edges cite a local file not the DOI); FR-7 kept verbatim, expected outcome noted as no exposure (Arch LOW-1 / TL C4); re-classify unit-tested over a synthetic 404 not a live fetch (Arch LOW-2); effort **3.0d central / 1.5 floor / 5.0 ceiling** with milestones + Wave 0/1/2 build plan + pre-authorized split valve (TL C1/C2); R4 downgraded to LOW (uniform pattern). Status → Approved. |
