---
prd:
  number: 206
  topic: misinformation-threat-agent
  created: 2026-04-23
  status: Approved
  type: feature
triad:
  pm_signoff: {agent: product-manager, date: 2026-04-23, status: APPROVED, notes: "PRD grounded in BLP-01 §7 F-2 spec and Issue #206; 3 user stories preserved verbatim with job-story restructuring; 10 success criteria covering DoD bullets including schema-bump 1.6→1.7 (FR-4), FR-7 three-callsite reconciliation of F-1 carry-over (MEDIUM-3 fix), R8 multi-feature concurrency hedge (MEDIUM-2 fix), architect-owned FR-7 edit ownership (MEDIUM-4 fix), AML.T0042 confirmed-absent at PRD time (H1 fix + R3 CLOSED), buffer-day budget model (HIGH-1 fix), delivery retrospective slotting (HIGH-2 fix), ADR-030 Decision 8 cross-ref in FR-6 (M1 fix). All 3 architect HIGH/MEDIUM fixes (H1/M1) and 4 team-lead HIGH/MEDIUM fixes (HIGH-1/HIGH-2/MEDIUM-2/MEDIUM-3/MEDIUM-4) applied inline before sign-off. Q-set distilled to 5 architect-owned questions with leanings captured. Ready for /aod.plan."}
  architect_signoff: {agent: architect, date: 2026-04-23, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 1 HIGH / 5 MEDIUM / 4 LOW. Original review confirmed: (a) schema bump 1.6→1.7 correctly framed per ADR-026 + ADR-030 Decision 8; (b) Heuristic A three-signal-class framing internally consistent with ADR-030 Decision 1 (F-1 scoped to execution sinks, leaving factual-integrity open for F-2); (c) CWE-345 + CWE-223 attributions rigorous and catalog-verified; (d) FR-7 LLM-quartet→quintet dispatch registration sound; (e) two-part emission gate correctly handles US-206-1 AC-4 purely-stylistic zero-finding case; (f) 5-pattern-category completeness covers OWASP LLM09:2025 canonical surface; (g) 24-file invariant accounting correct. H1 AML.T0042 resolved at PRD time (inline fix: confirmed absent from mitre-atlas.yaml; FR-5 hardened, Appendix updated, R3 CLOSED). Q-leanings: Q1 5 categories (defer 6th to catalog enrichment follow-on); Q2 12 trigger keywords (match F-1 precedent); Q3 Process only (defer Data Flow); Q4 Extend agentic-app (R2 fallback: advisory-app); Q5 Day 1 Wave 1.1 Proposed (match F-1). MEDIUM: M1 ADR-030 Decision 8 cross-ref added to FR-6; M2 ADR-031 re-states (not re-adjudicates) Heuristic A via ADR-030 Decision 1 cross-reference; M3 document CWE-1039 deliberate exclusion in ADR-031; M4 dispatch-table FP dry-run at Wave 2.0; M5 anti-indicator discipline in pattern catalog Wave 1.2. LOW: L1 SC-9 24-file accounting correct; L2 agentic-app regeneration target approved; L3 F-B consumer rendering; L4 Q5 sequencing approved. Strategic intent sound; three-signal-class discipline coherent; structural parity with F-1 is the correct risk posture. Full review at .aod/results/architect.md."}
  techlead_signoff: {agent: team-lead, date: 2026-04-23, status: APPROVED_WITH_CONCERNS, notes: "0 BLOCKING / 2 HIGH / 4 MEDIUM / 3 LOW. Calendar verified (cal 4 2026): 2026-04-23 Thu, 2026-04-24 Fri, 2026-04-27 Mon, 2026-04-28 Tue, 2026-04-29 Wed — all 7 weekday labels in Timeline correct. Dependencies on-disk verified: F-A1 (LLM09 + CWE-345 + CWE-223 in schemas/taxonomy/), F-A2 (schemas/finding.yaml v1.6 + source_attribution), F-B (coverage-attestation.typ), F-1 (output-integrity.md + ADR-030 Accepted) — ALL PRESENT. F-1 fully delivered 2026-04-19; no spillover into 2026-04-20 to 2026-04-29 window. F-2 ships solo in window (no competing F-3/F-4/F-5 Issues filed at stage:define or later; no open PRs). senior-backend-engineer load 60-70pct Day 1 / 40-50pct Day 2 — within 80pct ceiling. HIGH: HIGH-1 buffer-day budget model added (R5 polish at Day 2 PM; buffer reserved for R2 regen friction with Q4 fallback to advisory-app at 0.5 day); HIGH-2 delivery retrospective slotting added (Wave 2.3 PM if capacity, else buffer day — mirrors F-1 same-day-as-delivery pattern). MEDIUM: MEDIUM-1 consumers-list placement (architect adjudicates at plan time per F-1 precedent); MEDIUM-2 R8 multi-feature concurrency hedge added (4-surface additive-edit conflict if F-3/F-5 enter build concurrently); MEDIUM-3 FR-7 expanded to enumerate 3 F-1 carry-over callsites (dispatch-rules.md:120 + orchestrator.md:296 + orchestrator.md:370) reconciling quartet to quintet consistently; MEDIUM-4 architect named as FR-7 edit owner (mirrors F-1 HIGH-1 resolution). LOW: LOW-1/2/3 non-blocking cosmetic polish. Structural parity with F-1 Outcome B envelope (2 working days) is realistic; F-1 actually compressed to ~1 day autonomous so 2-day envelope is conservative. Ready for /aod.plan. Full review at .aod/results/team-lead.md."}
source:
  idea_id: 206
  story_id: null
---

# F-2 — LLM09 Misinformation Detection: Product Requirements Document

**Status**: Approved
**Created**: 2026-04-23
**Spec**: TBD (will land at `specs/206-misinformation-threat-agent/spec.md` after `/aod.plan`)
**Author**: product-manager
**Reviewers**: architect, team-lead
**Phase**: BLP-01 Tier 1 — second Tier 1 feature (parallel-eligible with F-3, F-5; follows F-1)
**Priority**: P1

---

## 📋 Executive Summary

### The One-Liner

Ship a new `misinformation` AI-tier threat agent that detects architectural conditions under which an LLM-integrated system is likely to emit **unverifiable, hallucinated, or ungrounded** factual content — closing the OWASP LLM09:2025 detection gap with logic that is deliberately **orthogonal** to both input-side `prompt-injection` (LLM01) and output-side `output-integrity` (LLM05).

### Problem Statement

Tachi ships 12 detection agents after Feature 201 (F-1 `output-integrity` merged 2026-04-19). `prompt-injection` covers the input side of the LLM boundary; `output-integrity` covers the output side when that output flows into a downstream execution sink (browser, SQL, shell, template engine, outbound HTTP, filesystem). Neither agent covers the case where the LLM emits **factually wrong** content to a consumer who treats it as authoritative — the **factual-integrity** signal class. OWASP LLM Top 10:2025 lists **LLM09 Misinformation** as a top-10 risk with a canonical attack class covering hallucination, ungrounded response, citation fabrication, and overreliance on model output in high-stakes contexts. Across tachi's 6 example architectures, zero findings cite LLM09; per the BLP-01 Coverage Matrix audit, LLM09 is **Planned (Gap)** today.

A security analyst evaluating an architecture where an LLM synthesizes medical summaries, generates legal citations, produces financial recommendations, or drives automated decisions gets **no signal from tachi** that the output's **factual correctness is architecturally unverifiable**. The same architecture that surfaces prompt-injection findings on the input side and (now) output-integrity findings on the sanitization side surfaces zero findings on the factual-grounding axis — an asymmetry that misrepresents the actual LLM09 attack surface and leaves adopters in compliance-sensitive domains (healthcare, legal, finance) hand-authoring the misinformation portion of their AI risk register.

Per **Heuristic A (signal-class taxonomy)** in `GUIDE-threat-coverage-research §11`, misinformation is a **distinct detection signal class** from both input-side injection and output-side sanitization. The signal is not "attacker-induced wrong output" (that's prompt-injection) nor "output crosses an unsanitized boundary into an execution sink" (that's output-integrity). The signal is "LLM emits factual / citation-bearing / decision-critical output without a declared grounding, verification, or confidence-calibration mechanism." The F-1 `output-integrity` PRD (201) and ADR-030 both explicitly **forward-reference** misinformation as an adjacent-but-distinct concern; F-2 is the feature that fulfills that forward reference.

### Proposed Solution

Author one new AI-tier threat agent and its companion skill-references directory, conforming exactly to the ADR-023 detection-variant lean pattern that the 12 existing threat agents already follow:

1. **`.claude/agents/tachi/misinformation.md`** — new lean agent file, ≤150 lines (AI tier cap, ≤180 hard ceiling), 5-section canonical shape: YAML frontmatter → metadata YAML → `## Purpose` → `## Skill References` table → `## Detection Workflow` (single `**MANDATORY**: Read` directive at workflow start). Optional 6th `## Example Findings` section per AI-tier convention. **Zero MAESTRO references** anywhere in the file or its companion (ADR-023 Decision 2 — orchestrator owns layer inheritance).
2. **`.claude/skills/tachi-misinformation/`** — new companion skill directory with `README.md` (consumers + purpose header) and `references/detection-patterns.md` (≥5 pattern categories with trigger keywords, applicable DFD element types, indicators per category, primary-source citations per category, and one worked example per category). Pattern categories cover the full LLM09 surface: **ungrounded factual emission**, **citation fabrication**, **overreliance / missing HITL on decision-critical output**, **retrieval-grounding gaps**, and **confidence-calibration absence**.
3. **Additive-only edit to `.claude/skills/tachi-shared/references/finding-format-shared.md`** — extend the `consumers:` frontmatter list to include `misinformation`. Per ADR-023 Decision 3, all existing `## ` headings remain byte-identical pre/post edit; the body is unchanged. This is the minimum-touch wiring that lets the orchestrator's finding-correlation surface treat `misinformation` as a registered producer.
4. **`schemas/finding.yaml`** — minor additive bump **1.6 → 1.7** to extend the `id.pattern` regex with the `MI` prefix. Verified at PRD time: `schemas/finding.yaml:18` enumerates 10 specific prefixes (`S|T|R|I|D|E|AG|LLM|AGP|OI`) — `MI` is absent. The bump is additive (regex broadens; existing IDs remain valid), follows the ADR-026 minor-bump rule for additive regex extensions, and is independent of prior 1.4→1.5 (F-A2) and 1.5→1.6 (F-1) lineage. The new agent emits `category: llm` (existing enum value, unchanged) with sequential `MI-{N}` finding IDs.
5. **`docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`** — public per-feature ADR documenting (a) the new-agent decision, (b) the Heuristic A signal-class rationale for distinctness from both `prompt-injection` (input) and `output-integrity` (F-1 output-handling), (c) the lean-agent shape conformance per ADR-023, (d) the explicit non-subsumption into F-1's scope per the Heuristic A signal-class analysis locked in ADR-030. Authored under the Proposed → Accepted dual-commit pattern that ADR-027 / ADR-028 / ADR-029 / ADR-030 established as the default protocol for BLP-01 features.
6. **Example regeneration** on an architecture that exercises the new flow (likely `agentic-app` extended with a factual-output component, or a newly-introduced example). The 5 non-factual-output baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021.

The new agent activates when any DFD `Process` element matches LLM trigger keywords AND the architecture exhibits **factual-output indicators** (e.g., `factual output`, `citation generation`, `recommendation engine`, `decision support`, `RAG`, `grounding`, `hallucination`, `advisory`, `medical`, `legal`, `financial`). When no component exhibits factual-output emission, the agent emits **zero findings — no speculation** (matching the established AI-agent convention and mirroring F-1's emission-gate discipline).

**Three things the solution is deliberately NOT:**

1. It is **not** a re-scoping of `prompt-injection` or `output-integrity`. Input-side, output-sanitization, and factual-integrity are three distinct detection signal classes per Heuristic A. `prompt-injection` owns input-handling; `output-integrity` owns output-sanitization; `misinformation` owns factual-grounding. All three agents may fire on a single LLM Process component when all three surfaces are present — that is correct behavior, not duplication.
2. It is **not** a new finding `category` value. Findings emit `category: llm` (existing enum), distinguished from `prompt-injection`'s `LLM-{N}` IDs, `output-integrity`'s `OI-{N}` IDs, and Feature 142's `AGP-{N}` IDs via the `MI-{N}` ID prefix.
3. It is **not** a runtime-behavior change for the infrastructure-tier consumer agents (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) — they read `category: llm` (existing enum value) and process `MI-{N}` findings through the same code paths they already use for `LLM-{N}` and `OI-{N}` findings. Two orchestrator-tier files **do** receive minimal additive edits (`orchestrator.md` dispatch list + `dispatch-rules.md` LLM quartet → quintet) — these are explicitly carved out from the 22-file detection-tier zero-edit invariant per the F-1 (Feature 201) precedent. Net change is **purely additive** to the dispatch surface.

### Success Criteria

- **SC-1** — `.claude/agents/tachi/misinformation.md` exists, is **≤150 lines** (AI tier cap; hard ceiling 180), and passes the ADR-023 structural-diff check: exactly **one** `**MANDATORY**: Read` directive under a `## Detection Workflow` section heading; **zero** MAESTRO references (grep-checkable across the agent file AND its companion `detection-patterns.md`).
- **SC-2** — Companion `.claude/skills/tachi-misinformation/references/detection-patterns.md` ships with **≥5 pattern categories**, each carrying (a) at least one worked example, (b) at least one primary-source citation (OWASP LLM09:2025 minimum), (c) trigger keywords, and (d) applicable DFD element types. Pattern categories collectively cover ungrounded factual emission, citation fabrication, overreliance / missing HITL on decision-critical output, retrieval-grounding gaps, and confidence-calibration absence.
- **SC-3** — `.claude/skills/tachi-shared/references/finding-format-shared.md` `consumers:` frontmatter is extended to include `misinformation` via an **additive-only edit**; all existing `## ` headings are byte-identical pre/post edit (ADR-023 Decision 3 grep check verifies this).
- **SC-4** — The new agent is invoked by orchestrator dispatch when at least one `Process` component in the architecture matches LLM keywords AND factual-output indicators; verified by **at least 1 new `MI-{N}` finding produced** against an example architecture exercising factual-output emission. Zero findings on architectures with no qualifying Process — no speculation.
- **SC-5** — Public per-feature **ADR-031** is committed under `docs/architecture/02_ADRs/` documenting (a) the new-agent decision, (b) the Heuristic A signal-class rationale for distinctness from both `prompt-injection` and `output-integrity`, (c) lean-agent shape conformance per ADR-023, (d) zero-MAESTRO-reference invariant proof, (e) explicit non-subsumption of LLM09 into F-1's `output-integrity` scope (confirms ADR-030's Heuristic A analysis that placed LLM09 as a separate feature). Authored under the dual-commit Proposed → Accepted pattern.
- **SC-6** — All 5 existing non-factual-output example PDFs regenerate **byte-identically** under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 (zero-impact-when-absent invariant — no qualifying Process in those baselines, so zero new findings emit, so the threats.md / risk-scores.md / compensating-controls.md content is unchanged, so the PDF is byte-identical). **The 6th baseline (`agentic-app`, regenerated by F-1)** is the expected mutation candidate and subject to SC-7.
- **SC-7** — Example regeneration lands on an architecture that exercises the new flow. Candidate architectures: (a) `agentic-app` extended with a factual-output component, (b) a newly-authored `examples/advisory-app/` or similar, (c) an extension of `mermaid-agentic-app`. Architect adjudicates at plan time. The regenerated example shows ≥1 `MI-{N}` finding with concrete grounding / verification mitigations and OWASP LLM09:2025 citation.
- **SC-8** — Zero new runtime dependencies — empty diff on `pyproject.toml`, `requirements*.txt`, `package.json`. Zero new developer dependencies — `pyyaml` and `pytest` already declared per Feature 128.
- **SC-9** — **22-file zero-edit invariant preserved** on the existing detection tier (ADR-023 lineage, extended by F-A1 / F-A2 / F-B / F-1): zero edits to the 12 existing threat-detection agent files (11 original + `output-integrity.md` from F-1) or to their 12 companion `detection-patterns.md` reference files. The new agent and its companion are **additions**, not edits to the existing 24 (22 original + 2 from F-1). **Carve-out**: orchestrator-tier files (`.claude/agents/tachi/orchestrator.md`, `.claude/skills/tachi-orchestration/references/dispatch-rules.md`) are explicitly **not** in scope of the invariant and ARE expected to receive minimal additive edits per FR-7.
- **SC-10** — **Source attribution** populated on every emitted `MI-{N}` finding using the F-A2 `source_attribution` schema field (Feature 189). Each finding cites at minimum `{taxonomy: owasp, id: LLM09, relationship: primary}`. Related CWE entries where applicable: `{taxonomy: cwe, id: CWE-345, relationship: related}` (Insufficient Verification of Data Authenticity — primary CWE mapping for misinformation and citation fabrication, verified present in `schemas/taxonomy/cwe.yaml`) and `{taxonomy: cwe, id: CWE-223, relationship: related}` (Omission of Security-relevant Information — applicable to missing disclosure / grounding labels, verified present in `schemas/taxonomy/cwe.yaml`). MITRE ATLAS `AML.T0042 Verify Attack` may be cited as `relationship: related` if verified present in the taxonomy catalog at plan time; otherwise the citation remains prose-only inside the pattern catalog per the F-A2 referential-integrity validator. **LLM09 has `cwe_refs: []` in `schemas/taxonomy/owasp.yaml`** — no CWE is inherited automatically from the catalog edge structure; each finding attaches CWE attribution at the finding level per the F-1 precedent.

### Timeline

Target window: **2026-04-27 (Monday) → 2026-04-28 (Tuesday)** with a **2026-04-29 (Wednesday) buffer**. Calendar verified at PRD time (`cal 4 2026`): 2026-04-23 = Thursday (today), 2026-04-24 = Friday, 2026-04-27 = Monday, 2026-04-28 = Tuesday, 2026-04-29 = Wednesday.

**Single-envelope sizing** — F-2 is simpler than F-1 because it has no Heuristic A subsumption question to adjudicate (ADR-030 already placed LLM09 outside F-1's scope). F-2 is a pure 5-pattern AI-tier agent on the detection-variant lean pattern with a precedent (F-1) to mirror structurally.

- **Realistic envelope**: **2 working days**, 1.5 days aspirational. 5 pattern categories, no gating-decision research. Delivery 2026-04-27 → 2026-04-28.
- **Buffer**: 2026-04-29 Wednesday reserved for regeneration friction (example architecture extension may surface fixture drift).

Day 1 AM parallelizes: (a) senior-backend-engineer starts the agent file skeleton + ADR-031 Proposed commit, (b) tester authors fixture architecture exercising factual-output indicators. Day 1 PM ships pattern authoring + `detection-patterns.md` first draft. Day 2 AM locks schema bump (1.6 → 1.7) + additive edits to `finding-format-shared.md` + orchestrator dispatch. Day 2 PM runs regeneration, byte-identity verification, and ADR-031 Accepted transition.

---

## 🎯 Strategic Alignment

### Product Vision Alignment

**Reference**: `docs/product/01_Product_Vision/product-vision.md`

Tachi's vision — automated threat modeling extending STRIDE with AI-specific threat agents for agentic applications — implies a *complete* LLM threat surface: input-side, output-sanitization-side, AND factual-integrity-side all modeled, reported, and mitigated. Post-F-1 the surface is partially symmetrical (input via `prompt-injection`, output via `output-integrity`), but the factual-integrity axis is unmodeled. F-2 closes the last Tier 1 factual gap: an adopter evaluating "does tachi cover the LLM threat surface end-to-end?" today must answer "no, factual integrity is missing"; post-F-2 the answer is "yes — input via `prompt-injection`, output-sanitization via `output-integrity`, factual-integrity via `misinformation`, with all three fired in concert on architectures where all three surfaces are present."

The value proposition is especially strong for adopters operating in **compliance-sensitive domains** (healthcare, legal, finance) where LLM09 coverage is not optional — regulators and auditors require an explicit misinformation threat model. Post-F-2 those adopters can cite tachi findings in their AI risk register instead of hand-authoring the LLM09 portion.

### BLP-01 Initiative Fit

**Reference**: `BLP-01 threat coverage` — F-2 is the **second Tier 1 feature** in the BLP-01 initiative (F-1 shipped 2026-04-19 as Feature 201). F-2 is parallel-eligible with F-3 (ASI07 Inter-Agent Communication) and F-5 (LLM10 Unbounded Consumption). F-4 (ASI09 Human-Agent Trust Exploitation) remained gated on F-1's Heuristic A resolution (ADR-030 Decision 2 chose Outcome B — split) and is now separately unblocked.

F-2's place in the BLP-01 chain:

```
F-A1 (Feature 180, delivered 2026-04-17) — taxonomy catalogs + crosswalk
  │
F-A2 (Feature 189, delivered 2026-04-17) — source_attribution schema contract
  │
F-B  (Feature 194, delivered 2026-04-18) — coverage attestation PDF section
  │
F-1 (Feature 201, delivered 2026-04-19) — output-integrity agent (LLM05 + ML09)
  │
F-2 (this PRD, #206) ◄────── SECOND TIER 1 FEATURE (parallel-eligible with F-3, F-5)
  │  New misinformation agent — distinct signal class from F-1 per Heuristic A
  │
F-3 (ASI07 Inter-Agent Communication, parallel-eligible)
F-4 (ASI09 Human-Agent Trust Exploitation, now unblocked via ADR-030 Outcome B)
F-5 (LLM10 Unbounded Consumption, parallel-eligible)
  │
F-6, F-7 (Tier 2 ML + Mobile bundles)
F-8 (Tier 3 Web/API attestation; ships last)
```

**F-2 does NOT gate any other feature.** Its delivery closes LLM09 on the Coverage Matrix and unblocks Tier 2 ML Top 10 bundle work (F-6) only insofar as LLM09 is one of ~5 Tier 1 items the Coverage Matrix wants Closed before ML Top 10 cross-citations are authoritative.

**F-2 is the first new producer of `source_attribution` citing LLM09** — every `MI-{N}` finding cites OWASP LLM09:2025 as primary plus CWE-345 / CWE-223 as related, extending F-1's end-to-end validation of the F-A2 contract on a second independent finding flow. The `llm` category enum is now the producer for three ID-prefix families (`LLM-{N}`, `OI-{N}`, `MI-{N}`) — a meaningful demonstration that the prefix-plus-category pattern scales without category-enum inflation.

### Recent ADR Lineage

- **ADR-023** (Threat Agent Skill References Pattern, Accepted 2026-04-11): defines the lean-agent detection variant that F-2's new agent file MUST conform to. Decision 1 (single-point load), Decision 2 (zero MAESTRO references), Decision 3 (additive-only shared-reference edits) are all directly invoked. SC-1 + SC-3 + SC-9 trace to this ADR.
- **ADR-021** (SOURCE_DATE_EPOCH determinism, Accepted earlier): SC-6 byte-identity gate on the 5 non-factual-output baselines uses this harness.
- **ADR-027** (Taxonomy Crosswalk Schema, Accepted 2026-04-17): F-2 cites OWASP LLM09 from `schemas/taxonomy/owasp.yaml`. The 5-value taxonomy enum (Decision 3) is the source of `taxonomy: owasp` in F-2's `source_attribution` records.
- **ADR-028** (Source Attribution Schema Extension, Accepted 2026-04-17): SC-10 is direct consumption of this contract — F-2 emits `source_attribution: [{taxonomy: owasp, id: LLM09, relationship: primary}, ...]` per finding. F-2 is the second agent in the codebase to populate the field as production behavior (F-1 is first).
- **ADR-029** (Coverage Attestation Report Section, Accepted 2026-04-18): F-2's findings will surface in F-B's per-finding attribution table and per-framework coverage matrix when the regenerated example is included in a security-report PDF run.
- **ADR-030** (Output Integrity Agent, Accepted 2026-04-19): F-2's ADR-031 explicitly cross-references ADR-030's Heuristic A signal-class analysis. ADR-030 Decision 2 chose Outcome B (split ASI09 → F-4) — the same signal-class discipline is why F-2 does not subsume into F-1; factual-integrity is a third distinct signal class beyond input-injection and output-sanitization.
- **Feature 201 precedent** (F-1 — first net-new agent authored under ADR-023): F-2 is the **second net-new agent** authored under the lean+skill-references pattern from authoring (not retrofit). Reuses F-1's dispatch-registration pattern, schema-bump pattern, and ADR-authoring pattern structurally identically.

### Roadmap Fit

- **Phase**: BLP-01 Tier 1 (AI/Agentic gaps, depth + breadth)
- **Week**: Week of 2026-04-27 — immediate follow-on to Feature 201 (F-1) delivery
- **Dependencies**:
  - F-A1 (Feature 180) — **SATISFIED** as of 2026-04-17 (verified: `schemas/taxonomy/` populated; OWASP LLM09 entry present with `url` and `name: Misinformation`)
  - F-A2 (Feature 189) — **SATISFIED** as of 2026-04-17 (verified: `schemas/finding.yaml` v1.6 carries `source_attribution`; parser round-trips)
  - F-B (Feature 194) — **SATISFIED** as of 2026-04-18 (verified: `templates/tachi/security-report/coverage-attestation.typ` exists; `has-source-attribution` boolean wired)
  - F-1 (Feature 201) — **SATISFIED** as of 2026-04-19 (verified: `.claude/agents/tachi/output-integrity.md` exists; schema at 1.6 with `OI` prefix registered; ADR-030 Accepted). F-2 is **not architecturally gated** on F-1 (per BLP-01 Heuristic A analysis misinformation is a distinct signal class), but F-1's delivery establishes the dispatch-registration and schema-bump patterns F-2 mirrors structurally.

---

## 🧑‍💼 Target Users & Personas

### Primary Persona: **Security Analyst Modeling an AI-Advisory System**

- **Role**: Application security engineer or external consultant performing threat modeling on an LLM-integrated system that emits factual claims, citations, or decision recommendations (medical summarizer, legal research assistant, financial advisory agent, clinical decision support, content-moderation classifier)
- **Goal**: Surface the factual-integrity threat surface — ungrounded output, citation fabrication, overreliance on auto-action, missing HITL, confidence-calibration absence — with concrete mitigations rooted in OWASP LLM09:2025 vocabulary
- **Pain Point Today**: Tachi reports input-side prompt-injection findings and (post-F-1) output-sanitization findings, but is **silent on factual grounding**. The analyst must hand-author the LLM09 portion of the threat model, citing OWASP LLM09:2025 manually, with no architectural-context-aware finding generation. In compliance-sensitive domains this is a blocker — auditors expect a concrete misinformation threat model bound to the architecture.
- **Value Delivered**: Per-component `MI-{N}` findings with named grounding / verification mitigations (mandatory RAG grounding with per-claim source attribution, model-confidence thresholds gating auto-action, HITL review gates on decision-critical output, output classifiers for unverifiable claims, citation-matching verification against retrieved sources) emitted automatically when the architecture exhibits factual-output emission. Coverage Matrix shows LLM09:2025 as Covered.

### Secondary Persona: **Developer Building a Customer-Facing AI Agent**

- **Role**: Backend or full-stack developer wiring an LLM into a customer-facing advisory, educational, informational, or decision-support application
- **Goal**: Address tachi findings without researching the grounding / verification pattern library from primary OWASP / NIST / ATLAS sources
- **Pain Point Today**: Generic advice ("ground the LLM") doesn't translate to a concrete architectural change. Developers want named mechanisms: "mandatory RAG with per-claim source attribution", "confidence-threshold gate (≥0.8) on auto-action", "HITL review queue for approve/deny/recommend outputs", "output classifier for unverifiable claims".
- **Value Delivered**: Each `MI-{N}` finding's `mitigation` field names specific grounding / verification mechanisms matched to the detected pattern category — ungrounded factual emission gets "mandatory RAG grounding with per-claim source attribution"; citation fabrication gets "verify retrieved source URIs against output citations pre-emission"; overreliance gets "HITL review gate on decision-critical output"; retrieval-grounding gaps get "declared retrieval-strength metric (hit-rate, recall@k)"; confidence-calibration absence gets "calibrated-confidence threshold (e.g., softmax temperature scaling + ECE monitor)".

### Tertiary Persona: **Adopter in a Compliance-Sensitive Domain (Healthcare, Legal, Finance)**

- **Role**: Tachi adopter in a regulated industry whose AI risk register must explicitly enumerate misinformation threats per regulatory or internal-governance requirement (e.g., HIPAA-adjacent clinical-decision-support, ABA-aligned legal research tools, SEC-aligned investment advisory tools)
- **Goal**: Cite tachi findings in the AI risk register instead of hand-authoring the misinformation threat section
- **Pain Point Today**: LLM09:2025 is Planned (Gap) in the Coverage Matrix. The adopter must enumerate misinformation threats manually, which is both time-consuming and auditor-questionable (hand-authored risk models lack the cross-architecture consistency that tachi-generated findings deliver).
- **Value Delivered**: Post-F-2 the adopter's threat-model PDF report carries a dedicated LLM09 section with per-component `MI-{N}` findings, each citing OWASP LLM09:2025 as primary and relevant CWEs (CWE-345, CWE-223) as related. The per-framework coverage matrix (F-B) shows LLM09:2025 as Covered. The AI risk register becomes a quote from the tachi PDF rather than a hand-written chapter.

### Quaternary Persona: **Tachi Maintainer Preserving the Detection-Tier Invariant**

- **Role**: Maintainer preserving backward compatibility, byte-identity baselines, and the 22-file zero-edit invariant (now 24 files post-F-1; becomes 26 post-F-2) established by Feature 082 / ADR-023 and extended by F-1
- **Goal**: Ship a second net-new threat agent without regressing any of the 5 byte-identity baselines, without touching any of the 24 existing detection-tier files (22 original + F-1's 2), and without drifting the additive-edit pattern that F-1 validated
- **Pain Point Today**: Even with F-1 precedent, second-new-agent authoring carries residual risk: consumer list placement drift in `finding-format-shared.md`, schema regex broadening without version bump, dispatch-rules LLM-list ordering drift. The patterns are one-execution-deep (F-1) and a second execution validates the pattern as repeatable.
- **Value Delivered**: F-2 adds one new agent file + one new companion skill directory + one additive frontmatter edit + one additive schema regex edit + two minimal additive orchestrator edits — **purely additive**. SC-3, SC-6, SC-9 collectively guarantee no detection-tier regression by construction. Post-F-2 the pattern is two-execution-deep (F-1 + F-2), which is sufficient to lift the pattern from "precedent" to "established convention" for F-3 / F-4 / F-5 authoring.

---

## 📖 User Stories

All three user stories are preserved from GitHub Issue #206 (which sourced them from BLP-01 §7, F-2). Job-story restructuring applied to align with the F-1 PRD (201) precedent; acceptance criteria preserved where they specify testable predicates.

### US-206-1: Ungrounded-Factual-Output Detection

**When** a security analyst threat-models an architecture where an LLM emits factual, citation-bearing, or decision-critical output without a declared grounding, verification, or confidence-calibration mechanism,
**I want** tachi to flag those components with concrete `MI-{N}` findings citing OWASP LLM09:2025,
**So I can** surface misinformation risk before the output reaches end users, downstream automated decisions, or regulatory-exposed systems.

**Acceptance Criteria**:

- **Given** an architecture that includes an LLM Process producing factual or citation-bearing output with no declared RAG grounding, citation verification, or confidence scoring, **when** the orchestrator dispatches `misinformation`, **then** an `MI-N` finding emits with `category: llm`, `references` citing `OWASP LLM09:2025`, and `source_attribution` containing `{taxonomy: owasp, id: LLM09, relationship: primary}` plus `{taxonomy: cwe, id: CWE-345, relationship: related}`.
- **Given** an architecture that includes a RAG pipeline but retrieved sources are **not labeled in the output** (the `detection-patterns.md` "citation fabrication" category), **when** `misinformation` runs, **then** a distinct `MI-N` finding surfaces the citation-fabrication surface with `source_attribution` carrying LLM09 primary plus CWE-345 related.
- **Given** an architecture where LLM output drives an automated decision (approve/deny/recommend, triage/classify, content-moderation ruling) with no human-in-the-loop or secondary verification, **when** `misinformation` runs, **then** a finding flags overreliance risk with a named HITL or verification-gate mitigation.
- **Given** an architecture where LLM output is **purely stylistic** (copy generation, summarization of user-supplied text with no factual-claim emission), **when** `misinformation` runs, **then** **zero findings** emit — no speculation. The agent's behavior matches the established AI-tier convention (zero-finding outcome on architectures lacking the trigger surface).

**Priority**: P0
**Effort**: M

### US-206-2: Named Grounding / Verification Mitigation Guidance

**When** a developer reads an `MI-{N}` finding and needs to address it in their application,
**I want** the `mitigation` field to name specific grounding, verification, HITL, or calibration mechanisms matched to the detected pattern category,
**So I can** close the gap without inventing a mitigation pattern from scratch or re-deriving from primary OWASP / NIST / ATLAS sources.

**Acceptance Criteria**:

- **Given** an `MI-N` finding for the **ungrounded factual emission** category, **when** the `mitigation` field is read, **then** it names at least one specific grounding mechanism — e.g., `mandatory RAG grounding with per-claim source attribution`, `retrieval-strength metric declaration (hit-rate, recall@k)`, or `confidence-calibration layer (temperature scaling + ECE monitor)`.
- **Given** an `MI-N` finding for the **citation fabrication** category, **when** the `mitigation` field is read, **then** it names `output-time citation verification against retrieved source URIs`, `strict citation-token constraint on decoder output`, or equivalent concrete check.
- **Given** an `MI-N` finding for the **overreliance / missing HITL** category, **when** the `mitigation` field is read, **then** it names `human-in-the-loop review queue on decision-critical output` and distinguishes **consumer-facing high-stakes** (HIGH or CRITICAL risk level per OWASP 3×3) from **internal low-stakes** (MEDIUM or below).
- **Given** any `MI-N` finding, **when** its `references` array is inspected, **then** at least one entry is `OWASP LLM09:2025` (primary), and `source_attribution` carries that as `relationship: primary`. Supporting references (`MITRE ATLAS AML.T0042 Verify Attack`, `NIST AI 600-1 §2.4 Hallucination`) appear in prose inside the pattern catalog's Primary Sources list; `source_attribution` carries only catalog-resolvable IDs per the F-A2 referential-integrity validator.
- **Given** the agent's output across pattern categories, **when** threat descriptions are inspected, **then** they distinguish between **factual-emission** (ungrounded output with no grounding declared), **citation-integrity** (RAG present but sources not labeled), and **decision-overreliance** (auto-action without HITL) — the three primary LLM09 sub-classes per OWASP LLM09:2025 taxonomy.

**Priority**: P0
**Effort**: M

### US-206-3: Factual-Integrity as a First-Class Distinct Threat Class

**When** an adopter runs tachi on an AI-assisted medical, legal, financial, or decision-critical application,
**I want** misinformation to be surfaced as a first-class threat class **distinct from both `prompt-injection` and `output-integrity`**,
**So I can** separate "attacker-induced wrong output" (prompt-injection), "output crosses unsanitized boundary into execution sink" (output-integrity), and "ungrounded wrong output" (misinformation) in the adopter-facing report.

**Acceptance Criteria**:

- **Given** a threat-model report that includes `LLM-{N}` (prompt-injection), `OI-{N}` (output-integrity), and `MI-{N}` (misinformation) findings on the same LLM Process, **when** the AI-category section of `threat-report.md` is read, **then** the three finding families render in the same `category: llm` section **without prose synthesis or collapsing** — each finding's ID prefix preserves its signal-class origin and each finding carries its own `source_attribution` primary (LLM01, LLM05, LLM09 respectively).
- **Given** ADR-031 at the time of F-2 merge, **when** its Decision section is read, **then** it explicitly resolves three scope boundaries: (a) why misinformation is **not** subsumed into `prompt-injection` (input-side injection is a distinct signal class — attacker-controlled input vs. architecture-level grounding absence), (b) why misinformation is **not** subsumed into `output-integrity` (F-1's scope is downstream-execution-sanitization per ADR-030 Decision 1 — machine-victim, bytes/strings/syntax primitives; F-2's scope is factual-integrity — factual-content primitives), (c) why misinformation is **not** deferred to a post-Tier-1 feature.
- **Given** a regenerated example architecture that exercises the factual-output flow, **when** `/tachi.threat-model` is run, **then** the `threats.md` AI-category rendering groups `MI-{N}` findings adjacent to (not synthesized with) `LLM-{N}` and `OI-{N}` findings — the grouping preserves the three-signal-class discipline.
- **Given** the BLP-01 Coverage Matrix post-F-2 merge, **when** LLM09:2025 row is inspected, **then** it transitions **Planned → Covered** with F-2 (Feature 206) named as the closure feature.

**Priority**: P0
**Effort**: S (the distinctness is already resolved at PRD time per ADR-030 precedent; ADR-031 records the rationale but does not re-adjudicate)

---

## ⚙️ Functional Requirements

### FR-1 — New Lean Agent File `misinformation.md`

- **File**: `.claude/agents/tachi/misinformation.md`
- **Length**: ≤150 lines (AI tier cap per ADR-023). Hard ceiling: 180 lines.
- **Shape (5-section canonical, optional 6th `Example Findings`)**:
  1. YAML frontmatter (`name`, `description`, `tools`, `model`)
  2. Metadata YAML block (`category: llm`, `threat_class: LLM`, `dfd_targets: [Process]`, `owasp_references: [OWASP LLM09:2025]`, `output_schema: ../../../schemas/finding.yaml`). **Note**: `agentic_pattern` is **not** declared in agent metadata — it is set downstream by orchestrator Phase 3.6 per ADR-026 (precedent: F-1 FR-1).
  3. `## Purpose` — describes the factual-integrity threat surface, lists the 5 pattern categories, and explicitly resolves three scope boundaries: **distinct from `prompt-injection`** (input-side attacker-induced wrong output), **distinct from `output-integrity`** (output-side execution-sink sanitization per ADR-030 Decision 1), **scoped to factual-integrity** (grounding, verification, HITL, calibration). Explicit forward-links back to `prompt-injection` and `output-integrity` as adjacent-but-distinct concerns.
  4. `## Skill References` — table with 3 rows: (a) `detection-patterns.md` (this agent's companion), (b) `severity-bands-shared.md` (OWASP 3×3 risk matrix), (c) `finding-format-shared.md` (canonical finding IR + producer-audience section)
  5. `## Detection Workflow` — exactly **one** `**MANDATORY**: Read` directive at section start pointing at the companion `detection-patterns.md`. Numbered steps (5-6 typical) walk the agent through pattern matching → indicator collection → severity computation → finding emission with `source_attribution`
  6. (Optional) `## Example Findings` — 2-3 example findings demonstrating the canonical shape with `MI-{N}` IDs, `category: llm`, `source_attribution` populated

- **Trigger keywords** (declared in metadata or discoverable from `## Detection Workflow` step 2; architect finalizes at plan time):
  - `factual output` / `factual claim` / `fact generation`
  - `citation generation` / `citation output` / `RAG citation`
  - `recommendation engine` / `advisory` / `recommendation output`
  - `decision support` / `decision-critical output` / `automated decision`
  - `RAG` / `retrieval-augmented generation` / `grounding`
  - `hallucination` / `ungrounded output`
  - `medical` / `legal` / `financial` / `clinical` (high-stakes domain signal)
- **DFD targets**: `Process` (primary; the LLM-bearing component that emits factual content). Optionally `Data Flow` for RAG-ingest boundaries when retrieval grounding is declared but retrieval strength is not documented (architect decides at plan time).
- **MAESTRO references**: **ZERO** anywhere in the file (ADR-023 Decision 2 invariant). Grep-checkable.

### FR-2 — New Companion Skill Directory `tachi-misinformation/`

- **Directory**: `.claude/skills/tachi-misinformation/`
- **Files**:
  - `README.md` — consumers + purpose header (mirror `.claude/skills/tachi-output-integrity/README.md` shape from F-1)
  - `references/detection-patterns.md` — the pattern catalog
- **`detection-patterns.md` shape** (mirror F-1's `detection-patterns.md`):
  - Frontmatter (`name`, `description`, `consumers: [tachi-misinformation]`, `last_updated: <merge date>`)
  - `## Overview` — one-paragraph description of the pattern catalog scope
  - `## Detection Scope` — `### Trigger Keywords` (case-insensitive list) + `### Applicable DFD Element Types`
  - `## Detection Patterns` — numbered list of **≥5** pattern categories. Each category specifies: name, primary OWASP/CWE source, indicators (3-6 bullet points), and at least one worked example
- **Required pattern categories (≥5; architect may propose additional categories at plan time; CWE IDs verified present in `schemas/taxonomy/cwe.yaml`)**:
  1. **Ungrounded Factual Emission** — primary `OWASP LLM09:2025`, related `CWE-345` (Insufficient Verification of Data Authenticity). Indicators: LLM Process produces factual/citation-bearing output; no declared RAG component; no declared citation-verification layer; no declared confidence-calibration mechanism; no declared source-attestation contract. Worked example: medical-summarizer LLM emits clinical claims without RAG grounding or confidence threshold. Mitigations: mandatory RAG grounding with per-claim source attribution, confidence-calibration layer, retrieval-strength metric declaration.
  2. **Citation Fabrication** — primary `OWASP LLM09:2025`, related `CWE-345` (Insufficient Verification of Data Authenticity). Indicators: RAG pipeline present but retrieved sources are not labeled in output; no output-time citation verification against retrieved URIs; decoder output not constrained to citation tokens from retrieved set. Worked example: legal-research agent emits citations that are syntactically plausible but absent from retrieved corpus. Mitigations: output-time citation verification against retrieved source URIs, strict citation-token constraint on decoder output, per-claim source-attribution requirement enforced at decoder-output-post-processing.
  3. **Overreliance / Missing HITL on Decision-Critical Output** — primary `OWASP LLM09:2025`, related `CWE-223` (Omission of Security-relevant Information — missing disclosure that decision is AI-driven). Indicators: LLM output drives approve/deny/recommend or triage/classify/content-moderation automated decision; no HITL review gate; no secondary verification path; no declared risk-threshold bypass mechanism; missing AI-provenance disclosure on decision output. Worked example: financial advisory agent auto-approves loan decisions based on LLM output without HITL review. Mitigations: HITL review queue on decision-critical output, risk-threshold-based auto-escalation, AI-provenance disclosure on all decisions, secondary-verification dual-model ensemble.
  4. **Retrieval-Grounding Gaps** — primary `OWASP LLM09:2025`, related `CWE-345`. Indicators: RAG pipeline declared but no retrieval-strength metric (hit-rate, recall@k); no staleness policy on retrieval corpus; no per-query retrieval-score threshold gating model response; retrieval corpus not versioned for audit. Worked example: clinical-decision-support RAG declared but retrieval hit-rate never measured; stale guidelines retrieved without staleness warning. Mitigations: declared retrieval-strength metric (hit-rate, recall@k), per-query retrieval-score threshold gating, versioned retrieval corpus with staleness policy, retrieval-coverage dashboard.
  5. **Confidence-Calibration Absence** — primary `OWASP LLM09:2025`, related `CWE-345`. Indicators: LLM output emits factual claims with no declared confidence score; no calibration layer (temperature scaling, Platt scaling); no ECE (Expected Calibration Error) monitor; no refusal pattern for high-uncertainty queries. Worked example: advisory agent emits recommendations with uniform confidence presentation regardless of underlying uncertainty. Mitigations: calibration layer (temperature scaling + ECE monitor), refusal pattern for queries below confidence threshold, calibrated-confidence exposure on output, uncertainty-aware decoder.

- **Primary Sources list** (pattern-catalog level; not all items need catalog resolution for `source_attribution`):
  - `OWASP LLM Top 10:2025 — LLM09 Misinformation` (primary for every pattern category; catalog-resolvable)
  - `MITRE ATLAS — AML.T0042 Verify Attack` (referenced for adversarial-grounding context in pattern catalog prose; catalog resolution verified at plan time — if absent from `mitre-atlas.yaml` curated catalog, remains prose-only per F-A2 referential-integrity validator)
  - `NIST AI 600-1 §2.4 Hallucination` (referenced for regulatory-risk-register context in pattern catalog prose; catalog resolution verified at plan time)
  - `CWE-345 Insufficient Verification of Data Authenticity` (verified present in `schemas/taxonomy/cwe.yaml` at PRD time)
  - `CWE-223 Omission of Security-relevant Information` (verified present in `schemas/taxonomy/cwe.yaml` at PRD time)

### FR-3 — Additive-Only Edit to `finding-format-shared.md`

- **File**: `.claude/skills/tachi-shared/references/finding-format-shared.md`
- **Edit**: extend the `consumers:` frontmatter list to include `misinformation`. **Insertion convention**: tier-grouping per F-1 precedent. Current list post-F-1 (verified at PRD time): `orchestrator` → STRIDE-canonical (spoofing, tampering, repudiation, info-disclosure, denial-of-service, privilege-escalation) → AI-LLM (prompt-injection, data-poisoning, model-theft) → AI-AG (agent-autonomy, tool-abuse) → new-AI-LLM (output-integrity) → infra-consumer (risk-scorer). Natural placement for `misinformation` is **after `output-integrity` and before `risk-scorer`** — appended to the AI-LLM new-agent tier. Architect adjudicates the final placement at plan time (mirrors F-1 HIGH-2 architect-fix pattern).
- **Invariant**: all existing `## ` headings remain **byte-identical** pre/post edit. Body content is unchanged. Only the frontmatter `consumers:` list changes.
- **Enforcement**: ADR-023 Decision 3 grep check verifies byte-identity on `## ` headings; manual inspection verifies the body diff is empty outside the consumer list addition.

### FR-4 — Schema Minor Bump `1.6 → 1.7`

- **File**: `schemas/finding.yaml`
- **Edit**: two-line additive change
  - `schema_version: "1.6"` → `schema_version: "1.7"`
  - `pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"` → `pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$"`
  - `examples:` list gains an `MI-1` entry for completeness
- **Rationale**: F-2 introduces the `MI` finding-ID prefix. The regex must broaden. Per ADR-026 minor-bump rule, additive regex extensions are backward-compatible (existing IDs remain valid) and warrant a minor version bump. Precedent: F-1 bumped 1.5 → 1.6 for the `OI` prefix using the identical pattern.
- **Parser round-trip**: verified via existing `schemas` pytest suite (F-A1 / F-A2 / F-1 all exercised parser round-trip on schema changes; F-2 reuses the same harness).

### FR-5 — Source Attribution on Every `MI-{N}` Finding

- Every emitted `MI-{N}` finding **MUST** include a non-empty `source_attribution` array per the F-A2 schema (Feature 189).
- Minimum: `{taxonomy: owasp, id: LLM09, relationship: primary}` on every finding.
- Per pattern category, additional CWE entries as `relationship: related` (CWE IDs verified present in `schemas/taxonomy/cwe.yaml` at PRD time):
  - Ungrounded factual emission: `{taxonomy: cwe, id: CWE-345, relationship: related}`
  - Citation fabrication: `{taxonomy: cwe, id: CWE-345, relationship: related}`
  - Overreliance / missing HITL: `{taxonomy: cwe, id: CWE-223, relationship: related}` (primary) PLUS optionally `{taxonomy: cwe, id: CWE-345, relationship: related}` when the missing HITL is over a decision output where factual authenticity was not verified
  - Retrieval-grounding gaps: `{taxonomy: cwe, id: CWE-345, relationship: related}`
  - Confidence-calibration absence: `{taxonomy: cwe, id: CWE-345, relationship: related}`
- **MITRE ATLAS `AML.T0042` is confirmed absent** from the curated `schemas/taxonomy/mitre-atlas.yaml` catalog at PRD time (architect-verified: catalog carries 12 AML techniques — `T0010, T0018, T0020, T0024, T0051, T0054, T0057, T0058, T0059, T0060, T0061, T0062`; `T0042` not present). AML.T0042 therefore remains **prose-only** in the pattern catalog; it MUST NOT appear in `source_attribution` (would fail the F-A2 referential-integrity validator). **NIST AI 600-1 `§2.4 Hallucination`** is cited in pattern-catalog prose only — catalog resolution deferred if a future feature populates `schemas/taxonomy/nist-ai-rmf.yaml` with section-level IDs.
- **F-2 is the first new producer of LLM09 citations in the codebase** — every `MI-{N}` finding anchors its `source_attribution` on LLM09. Validates the F-A2 contract on a second independent finding flow post-F-1.

### FR-6 — New ADR-031 Public Per-Feature ADR

- **File**: `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`
- **Status**: Proposed → Accepted dual-commit (ADR-027 / ADR-028 / ADR-029 / ADR-030 precedent). Initial Proposed commit at Day 1 Wave 1.1 schema-lock; transitions Accepted at PR merge with provisional merge-date; post-merge SHA fill records the squash commit.
- **Required body items**:
  1. **Decision** statement — adopt new `misinformation` agent for LLM09 closure
  2. **Heuristic A signal-class rationale** — three-way scope boundary: distinct from `prompt-injection` (input-side attacker-controlled injection), distinct from `output-integrity` (output-side execution-sink sanitization per ADR-030 Decision 1), scoped to factual-integrity (grounding, verification, HITL, calibration). Explicit reference to GUIDE-threat-coverage-research §11 Heuristic A signal-class taxonomy.
  3. **Lean-agent shape conformance** per ADR-023 — single-point load, ≤150 lines, zero MAESTRO references
  4. **Cross-references** to ADR-023 (lean shape), ADR-021 (determinism), ADR-026 (schema minor-bump rule), ADR-027 (taxonomy), ADR-028 (source_attribution contract), ADR-029 (coverage attestation), ADR-030 (F-1 precedent + its ASI09 Outcome B ruling that validates the signal-class discipline F-2 reuses; specifically ADR-030 **Decision 1** bounds F-1 scope to five downstream-execution-sink categories leaving factual-integrity unambiguously open for F-2, and ADR-030 **Decision 8** establishes the regex-alternation-prefix additive-minor-bump rule that F-2's 1.6 → 1.7 bump invokes as the second recorded application)
  5. **24-file zero-edit invariant** preserved (22 original + F-1's 2) — explicit grep-auditable enumeration of untouched files; the new `misinformation.md` + `detection-patterns.md` are additions, not edits
  6. **Commercial framing omitted** per blueprint governance — no Layer 2, no tachi Cloud, no commercial roadmap. Public ADR stands on technical merits alone.
  7. **Revision history** table tracking Proposed → Accepted transition with dates

### FR-7 — Orchestrator Dispatch Registration

- **Architect verification at PRD time** (mirrors F-1 HIGH-1): orchestrator agent discovery is **not** purely directory-walk. `.claude/agents/tachi/orchestrator.md` hardcodes the dispatch list, and `.claude/skills/tachi-orchestration/references/dispatch-rules.md` hardcodes the LLM dispatch quartet (post-F-1: `prompt-injection`, `data-poisoning`, `model-theft`, `output-integrity`). **Edit owner**: architect (mirrors F-1 HIGH-1 resolution where architect owned orchestrator-tier additive edits as part of ADR-030 Proposed-commit work). **F-1 carry-over reconciliation**: on-disk audit at PRD time surfaced three dispatch/row callsites that F-1 extended the LLM agent count to four but left prose-tier artifacts at the pre-F-1 three-agent text (`dispatch-rules.md:120` row, `orchestrator.md:296` sequential-mode text, `orchestrator.md:370` LLM Threats row). F-2 reconciles these **while extending to quintet**, so the final state is five-agent consistent across every callsite.
  1. **`.claude/agents/tachi/orchestrator.md`** — (a) add `misinformation` to the dispatch list (one-line addition at the existing LLM-tier block; preserves established ordering), (b) update sequential-mode text at line 296 from `(prompt-injection then data-poisoning then model-theft)` → `(prompt-injection then data-poisoning then model-theft then output-integrity then misinformation)` reconciling F-1 carry-over, (c) update LLM Threats row at line 370 from `prompt-injection, data-poisoning, model-theft` → `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation` reconciling F-1 carry-over.
  2. **`.claude/skills/tachi-orchestration/references/dispatch-rules.md`** — (a) extend the LLM dispatch list (current lines 71-74) to include `misinformation` as the 5th agent with FR-011-style emission activation rule (two-part gate per FR-7 emission activation rule below), (b) update the table row at line 120 (`LLM (LLM Threats) | ... | OWASP LLM Top 10 v2025`) from `prompt-injection, data-poisoning, model-theft` → `prompt-injection, data-poisoning, model-theft, output-integrity, misinformation` reconciling F-1 carry-over, (c) extend trigger-keyword rules section with `misinformation` activation logic per FR-1 trigger list.
- These edits are explicitly **out of scope** of the 24-file detection-tier zero-edit invariant (SC-9 carve-out). Orchestrator-tier files have always been editable for additive agent registration; this is the same pattern F-1 used.
- **Emission activation rule (mirrors F-1's FR-011 pattern)**: `misinformation` is dispatched on any LLM keyword match (same trigger logic as the other four LLM agents). However, unlike the pure LLM-keyword agents, `misinformation` enforces a two-part emission gate internally: the agent MUST only emit an `MI-{N}` finding when BOTH (a) the dispatched Process matches an LLM keyword AND (b) at least one factual-output indicator is structurally present in the component's description or connected Data Flows (factual-output indicators listed in FR-1). If an LLM keyword matches but no factual-output indicator is present, the agent MUST emit zero findings for that component — dispatch still happens, but the agent self-gates emission to prevent false positives on LLM components whose output is purely stylistic (copy generation, summarization without factual-claim emission).
- **Zero edits to risk-scorer, control-analyzer, threat-report, threat-infographic, or report-assembler** — those infrastructure agents read `category: llm` (existing enum value); `MI-{N}` findings flow through them without any consumer-side edit.
- Verify via: a `/tachi.threat-model` invocation against the regenerated example architecture surfaces ≥1 `MI-{N}` finding without any further pipeline-config edit.

### FR-8 — Example Regeneration

- Identify the architecture that exercises the new flow. **Candidate architectures**:
  - (a) **`examples/agentic-app/`** extended with a factual-output component (e.g., add an LLM-backed advisory sub-agent emitting medical or legal summaries). Leverages F-1 baseline already includes this example.
  - (b) **New `examples/advisory-app/`** authored specifically to exercise misinformation (healthcare-advisory example, legal-research example).
  - (c) **Extend `examples/mermaid-agentic-app/`** with a decision-support component.
  Architect adjudicates the candidate at plan time.
- The regenerated example MUST surface ≥1 `MI-{N}` finding with concrete grounding / verification mitigations, OWASP LLM09:2025 citation, and populated `source_attribution`.
- **The 5 non-factual-output example PDFs regenerate byte-identically** under `SOURCE_DATE_EPOCH=1700000000` (SC-6). **The 6th example (`agentic-app`, regenerated by F-1 with new OI findings)** is the expected mutation candidate if chosen as the F-2 regeneration target — in that case F-2 adds new MI findings on top of F-1's OI findings; baseline lift is expected and expected-diff is audited at plan time.

---

## 🚫 Non-Functional Requirements

### NFR-1 — Determinism

The new agent's output MUST be deterministic per ADR-021. Same architecture input → same finding set → same finding ordering. Pattern matching is keyword-based + structural (DFD-element-type filtering + factual-output-indicator filtering); no LLM-judgment in pattern selection. Severity computation uses the OWASP 3×3 matrix from `severity-bands-shared.md` deterministically.

### NFR-2 — Backward Compatibility

The 5 non-factual-output example PDF baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000` (SC-6). No qualifying Process in those baselines means zero new findings, which means unchanged threats.md / risk-scores.md / compensating-controls.md content, which means byte-identical PDFs. The `agentic-app` baseline is the conditional exception per SC-7 and FR-8 candidate (a).

### NFR-3 — Tier-Cap Compliance

Agent file ≤150 lines (AI tier cap per ADR-023). Hard ceiling 180 lines. Companion `detection-patterns.md` has no formal line cap but should remain in the ~150-300 line range typical of the existing 13 companion files (12 original + F-1's new companion) for readability.

### NFR-4 — Zero New Dependencies

Empty diff on `pyproject.toml`, `requirements*.txt`, `package.json` (SC-8). The new agent uses only existing tachi infrastructure (orchestrator dispatch, shared references, schema, parser).

### NFR-5 — Security & Privacy

The agent reads architecture descriptions and emits findings. No network calls, no file writes outside the standard finding-emission path, no execution of LLM-output content (the agent only **describes** the threat, never reproduces or emits hallucinated content as a test payload). The pattern catalog uses anonymized worked examples — no real-world adopter data, no real patient / client / customer information.

### NFR-6 — Content Sensitivity

Worked examples cite high-stakes domains (healthcare, legal, finance) — ensure that catalog prose does not itself emit misinformation. Examples MUST be clearly-fictional ("a hypothetical clinical-decision-support system...", "a generic legal-research tool...", "a synthetic financial-advisory component..."); no real institutional names, no real clinician / lawyer / advisor identities, no real regulatory-citation examples that could be misread as authoritative guidance.

---

## 🧱 Architecture & Design Decisions (Open for Architect)

The following decisions are **architect-owned** and adjudicated during `/aod.plan` (project-plan / spec stages) or in ADR-031 directly. PM frames the trade-off space; architect picks. Bracketed "[arch]" tags mark decisions explicitly delegated.

### Q1 — Pattern Category Count (≥5 floor, architect may propose 6th) [arch]

**Question**: Are 5 pattern categories sufficient for the LLM09 surface, or should a sixth be added?

**PM framing**:
- **5 categories** (current PRD proposal): Ungrounded factual emission, citation fabrication, overreliance / missing HITL, retrieval-grounding gaps, confidence-calibration absence. Covers the OWASP LLM09:2025 canonical three-sub-class taxonomy (hallucination, citation fabrication, overreliance) plus two architectural-grounding sub-classes (retrieval gaps, calibration absence). Matches F-1's 5-category floor.
- **6th category candidate — "Model-Specific Hallucination Patterns"**: Model-family-specific hallucination indicators (e.g., LLMs known to hallucinate legal case citations, medical drug interactions). Tradeoff: increases catalog depth but introduces model-family coupling that ages poorly as new models ship. Architect's call.
- **6th category candidate — "Feedback-Loop Overreliance"**: Agentic-application patterns where downstream agents consume LLM output as ground truth, amplifying misinformation through the agent graph. Tradeoff: closes a legitimate Tier 1 gap but overlaps with F-3 (ASI07 Inter-Agent Communication) scope. Architect adjudicates scope boundary.

**PM leaning**: **5 categories**. F-1's 5-category floor validated in production use; adding a 6th without a compelling signal-class differentiator risks scope creep and pattern-catalog dilution. The "Model-Specific" and "Feedback-Loop" candidates are legitimate but better authored as **catalog enrichments in a follow-on feature** (F-2.1 or rolled into F-3 / F-6 coverage attestation pass).

### Q2 — Trigger Keyword Count (8-12 recommended per F-1 precedent) [arch]

**Question**: How many trigger keywords should the dispatch rules declare for `misinformation`?

**PM framing**:
- **Minimum 8 keywords**: `factual output`, `citation generation`, `recommendation engine`, `decision support`, `RAG`, `grounding`, `hallucination`, `advisory` — covers the primary LLM09 vocabulary.
- **12 keywords (FR-1 proposal)**: Above 8 plus `medical`, `legal`, `financial`, `clinical` — covers high-stakes domain signals for conservative dispatch.
- **16+ keywords**: Above 12 plus `summarization`, `classification`, `triage`, `content moderation` — covers additional decision-output surfaces at the risk of false-positive dispatch on stylistic-summary components.

**PM leaning**: **12 keywords** per FR-1. High-stakes domain signals (medical/legal/financial/clinical) merit inclusion because the risk-profile delta is meaningful. F-1 adopted 12 trigger keywords and the false-positive rate was within SC compliance; F-2 should match. Architect finalizes at plan time.

### Q3 — DFD Target Scope: Process only vs. Process + Data Flow [arch]

**Question**: Should F-2 target **Process only** (mirror F-1) or **Process + Data Flow** (capture RAG-ingest boundaries)?

**PM framing**:
- **Process only** (mirror F-1): LLM Process is the primary detection surface. RAG-ingest Data Flows are captured indirectly via Process-level indicators (RAG component declared adjacent to LLM Process). Simpler dispatch; matches F-1 precedent.
- **Process + Data Flow**: Adds RAG-ingest Data Flows as secondary detection targets, enabling per-retrieval-edge findings (e.g., "retrieval-grounding gaps on Data Flow from VectorStore to LLM Process"). Richer coverage but doubles dispatch surface and complicates emission-gate logic.

**PM leaning**: **Process only** (match F-1). Data Flow targeting is best deferred to a follow-on catalog enrichment (F-2.1) if production feedback surfaces the need. Starting narrower preserves the F-1 pattern-continuity discipline and keeps PRD scope bounded.

### Q4 — Example Regeneration Target: agentic-app extension vs. new advisory-app [arch]

**Question**: Regenerate `examples/agentic-app/` (F-1 baseline) with a new factual-output sub-component, OR author a new `examples/advisory-app/`?

**PM framing**:
- **Extend `agentic-app`** (FR-8 candidate a): Leverages existing baseline. Adds one new sub-component (factual-output emitter). Post-regeneration, the `agentic-app` PDF shows findings across prompt-injection + output-integrity + misinformation — compelling demonstration of the three-signal-class discipline. **Risk**: adds LEAF complexity to a baseline that already exercises F-1 + Feature 142 agentic-pattern synthesis + MAESTRO layer classification.
- **New `advisory-app`** (FR-8 candidate b): Clean-slate architecture with explicit factual-output focus. Authored specifically to exercise misinformation patterns (healthcare-advisory, legal-research, or financial-advisory template). **Risk**: adds a new example to the fixture suite, which must pass `examples/` test harness and PDF-regeneration pipeline; requires new architecture authoring effort (~0.5 day delta).

**PM leaning**: **Extend `agentic-app`** (candidate a). Lower effort delta, demonstrates three-signal-class discipline cohesively, leverages F-1's just-merged baseline. If the architect sees scope bloat on `agentic-app`, candidate b is the fallback with the 0.5 day buffer absorbing the delta.

### Q5 — ADR-031 Sequencing: Day 1 Wave 1.1 Proposed vs. Day 2 AM Proposed [arch]

**Question**: When does ADR-031 land as Proposed?

**PM framing**:
- **Day 1 Wave 1.1 (F-1 precedent)**: ADR-031 Proposed commit at schema-lock time (Day 1 Wave 1.1 of build). Enables parallel detection-patterns authoring (Wave 1.2+) with the architectural anchor locked. Matches F-1's ADR-030 sequencing.
- **Day 2 AM**: Defer ADR-031 Proposed to Day 2 AM after pattern catalog drafts surface any scope-rethink signals. Lower risk of Proposed-commit rewrite but delays architectural anchor.

**PM leaning**: **Day 1 Wave 1.1** (mirror F-1 precedent). F-1's Day-1-Proposed approach worked; deviating introduces pattern-drift without benefit. Architect may override if a specific F-2 scope signal changes the calculus.

---

## 🔗 Dependencies & Risks

### Dependencies (all SATISFIED at PRD time)

| Dep | Feature | Status | Evidence |
|-----|---------|--------|----------|
| F-A1 (taxonomy catalogs) | Feature 180 | SATISFIED 2026-04-17 | `schemas/taxonomy/owasp.yaml` carries LLM09 entry; `cwe.yaml` carries CWE-345 + CWE-223 |
| F-A2 (source_attribution schema) | Feature 189 | SATISFIED 2026-04-17 | `schemas/finding.yaml` at v1.6 with `source_attribution` field |
| F-B (coverage attestation renderer) | Feature 194 | SATISFIED 2026-04-18 | `templates/tachi/security-report/coverage-attestation.typ` exists |
| F-1 (output-integrity precedent) | Feature 201 | SATISFIED 2026-04-19 | `.claude/agents/tachi/output-integrity.md` exists; ADR-030 Accepted; schema at 1.6 with OI prefix |

### Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| R1 | LLM09 Heuristic A resolution drifts during implementation — pattern authoring surfaces a subsume-into-output-integrity signal | LOW | HIGH | ADR-030 already resolved the signal-class distinction (LLM09 factual-integrity ≠ LLM05 output-sanitization). Re-adjudication not expected. **Day 1 Wave 1.0 gate**: if pattern authoring surfaces a subsume signal, halt and escalate to architect before Day 1 EOD. |
| R2 | Regeneration friction on `agentic-app` baseline (F-1's baseline) — new MI findings interact unexpectedly with existing OI findings | MEDIUM | MEDIUM | Day 2 buffer (2026-04-29) reserved. Fallback: switch FR-8 to candidate (b) `advisory-app` — clean-slate architecture avoids interaction. |
| R3 | MITRE ATLAS `AML.T0042` absent from curated `mitre-atlas.yaml` catalog — `source_attribution` citation drops to prose-only | CLOSED | CLOSED | **Resolved at PRD time**: architect verified `AML.T0042` confirmed absent from catalog (12 AML techniques enumerated, T0042 not present). Pattern-catalog prose retains citation; `source_attribution` anchors on LLM09 + CWE-345 + CWE-223 alone per FR-5. No residual risk. |
| R4 | Schema bump 1.6 → 1.7 collision if another feature bumps concurrently | LOW | MEDIUM | F-2 is single-threaded on schema changes — no concurrent F-3/F-4/F-5 bumps expected this week. Verify `git pull` before FR-4 edit. |
| R5 | Pattern-catalog prose quality risk — authoring faithful worked examples for healthcare/legal/finance without emitting content that could be mistaken as authoritative guidance | LOW | HIGH | NFR-6 enforcement at review time: all worked examples must be clearly-fictional with explicit "hypothetical" / "synthetic" / "generic" framing. Senior-backend-engineer + code-reviewer double-check at Day 2 PM. |
| R6 | Orchestrator dispatch-rules LLM quintet ordering drift — F-1 added output-integrity to the quartet; F-2 must append misinformation without reordering | LOW | LOW | FR-7 specifies "extend the LLM dispatch quartet to a quintet" preserving F-1's ordering. Grep-check at Day 2 AM. |
| R7 | Finding-format-shared consumer list placement drift — F-2 appends after F-1's `output-integrity` | LOW | LOW | FR-3 specifies the placement (after `output-integrity`, before `risk-scorer`). Architect adjudicates at plan time per F-1 HIGH-2 precedent. |
| R8 | F-3 / F-4 / F-5 concurrent build triggers a 4-surface additive-edit conflict on `schemas/finding.yaml` (schema bump), `dispatch-rules.md` (LLM dispatch list + rows), `finding-format-shared.md` (consumers list), `orchestrator.md` (dispatch list + sequential-mode + LLM Threats row) | LOW (currently) / MEDIUM (if scheduled concurrently) | MEDIUM | F-2 ships **solo** in the 2026-04-27 → 2026-04-29 window — verified at PRD time: no F-3/F-4/F-5 GitHub Issues filed at `stage:define` or later, no competing PRs open. Multi-feature scheduling for BLP-01 Tier 1 requires sequential discipline on the 4 additive-edit surfaces; team-lead enforces schedule serialization if/when F-3/F-5 enter build. |

---

## 📊 Success Metrics

### Quantitative

- **Coverage Matrix transitions**: LLM09:2025 Planned → Covered. Post-F-2 the BLP-01 Coverage Matrix shows 5/11 BLP-01 features delivered (F-A1, F-A2, F-B, F-1, F-2); Tier 1 at 2/5 (F-1 + F-2; F-3, F-4, F-5 remain).
- **Finding count on regenerated example**: ≥1 `MI-{N}` finding on the FR-8 target architecture, verified via SC-4.
- **Byte-identity baselines**: 5/5 non-factual-output baselines regenerate byte-identically (SC-6). The 6th (`agentic-app`) conditionally regenerates with expected-diff per FR-8 candidate (a).
- **Agent file line count**: ≤150 (SC-1). Hard ceiling 180.
- **Pattern categories**: ≥5 (SC-2).
- **Zero new dependencies**: SC-8 grep check on `pyproject.toml`, `requirements*.txt`, `package.json`.
- **Zero-edit invariant**: 24 existing detection-tier files byte-identical post-F-2 (SC-9).

### Qualitative

- **Three-signal-class discipline demonstrated on a production threat-model run**: a single LLM Process component surfaces `LLM-{N}` (prompt-injection), `OI-{N}` (output-integrity), and `MI-{N}` (misinformation) findings simultaneously on the regenerated example — the three finding families render adjacent in the `category: llm` section without prose synthesis.
- **ADR-031 cross-references ADR-030 signal-class analysis**: the Heuristic A rationale linkage is explicit, not implicit.
- **Compliance-sensitive adopter feedback**: post-merge, a healthcare / legal / finance adopter regenerates their threat model and sees LLM09 findings they would otherwise have hand-authored. (Qualitative feedback loop; monitored informally via BLP-01 Coverage Matrix tracking.)

---

## 📅 Timeline

### Calendar context (verified at PRD time via `cal 4 2026`)

- 2026-04-23 = Thursday (today; PRD authored)
- 2026-04-24 = Friday (buffer for PRD review + plan + tasks + sign-offs)
- 2026-04-25 = Saturday
- 2026-04-26 = Sunday
- 2026-04-27 = Monday (Day 1)
- 2026-04-28 = Tuesday (Day 2)
- 2026-04-29 = Wednesday (Buffer)

### Wave Structure

**Day 1 (2026-04-27 Monday)**:
- Wave 1.0 AM (30-60 min): Architect verifies Heuristic A resolution is intact (ADR-030 still governs). If no signal to re-adjudicate, proceed. If signal surfaces, escalate per R1.
- Wave 1.1 AM (parallel, ~3-4 hours):
  - senior-backend-engineer: agent file skeleton (`misinformation.md`) + ADR-031 Proposed commit
  - tester: factual-output-indicator fixture architecture authored
  - Wave 1.1 locks schema bump (FR-4 applied as single commit)
- Wave 1.2 PM (~3-4 hours): Pattern catalog authoring (`detection-patterns.md` first draft, 5 pattern categories)

**Day 2 (2026-04-28 Tuesday)**:
- Wave 2.0 AM (~2 hours): Additive edits — `finding-format-shared.md` `consumers:` list + orchestrator.md dispatch list + dispatch-rules.md quartet → quintet + trigger-keyword rules
- Wave 2.1 AM (~2 hours): Example regeneration on FR-8 target; byte-identity verification on 5 non-factual-output baselines; `MI-{N}` finding verification on regenerated example
- Wave 2.2 PM (~2 hours): Code review; ADR-031 Accepted transition; PR ready-for-merge
- Wave 2.3 PM (~1 hour): Merge; post-merge squash-SHA fill on ADR-031; BLP-01 Coverage Matrix update (LLM09 Planned → Covered)

**Buffer (2026-04-29 Wednesday)**: Reserved primarily for R2 (regeneration friction on `agentic-app`) with contingent use for R5 (prose-quality polish) and delivery-retrospective authoring.

- **Buffer-day budget model**: R5 (healthcare/legal/finance worked-example prose sensitivity per NFR-6) is polished in Wave 2.2 PM during code review with senior-backend-engineer + code-reviewer dual-check — it does **not** consume buffer capacity by default. The 2026-04-29 Wednesday buffer is reserved for R2 regeneration friction on the `agentic-app` baseline (cumulative-regen risk inherited from F-1 R7 lineage). If R2 materializes, the architect may invoke Q4 fallback candidate (b) `examples/advisory-app/` consuming ~0.5 day of buffer, leaving ~0.5 day for residual friction absorption. If R2 does **not** materialize, buffer-day capacity is redirected to delivery-retrospective authoring (DoD bullet 12) per HIGH-2 resolution (see Wave 2.3 PM note below).
- **Delivery retrospective slotting**: `specs/206-misinformation-threat-agent/delivery.md` (DoD bullet 12) is authored Wave 2.3 PM if merge completes with ≥1 hour of residual capacity; otherwise authored 2026-04-29 Wed (buffer day) as the primary buffer-day activity. F-1 precedent (`specs/201-output-integrity-threat-agent/delivery.md`) was authored same-day-as-delivery at ~1-2 hours — F-2 retrospective mirrors F-1 parity.

### Capacity Check

- Feature 201 (F-1) delivered 2026-04-19; delivery retrospective closed; no spillover.
- senior-backend-engineer load: expected 60-70% Day 1, 40-50% Day 2. No competing features in the 2026-04-27 → 2026-04-28 window per team-lead backlog audit at PRD time.
- tester load: 30-40% Day 1 (fixture authoring), 20% Day 2 (byte-identity verification).
- code-reviewer load: 20% Day 2 PM (PR review).
- architect load: 30-60 min Day 1 (Heuristic A re-verification) + 30 min Day 2 PM (ADR-031 Accepted transition).

---

## ✅ Definition of Done

All of the following must be true before F-2 is marked Delivered:

1. **SC-1 through SC-10 pass** (success criteria grep-checkable or test-verifiable).
2. `.claude/agents/tachi/misinformation.md` exists, ≤150 lines, one `**MANDATORY**: Read` under `## Detection Workflow`, zero MAESTRO references.
3. `.claude/skills/tachi-misinformation/references/detection-patterns.md` ships with ≥5 pattern categories.
4. `finding-format-shared.md` `consumers:` list extended via additive-only edit; `## ` headings byte-identical pre/post.
5. `schemas/finding.yaml` bumped 1.6 → 1.7; regex carries `MI` prefix; parser round-trip verified.
6. `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md` committed; Proposed → Accepted dual-commit; zero commercial framing; cross-references ADR-023 / ADR-021 / ADR-027 / ADR-028 / ADR-029 / ADR-030.
7. Orchestrator dispatch registration (orchestrator.md + dispatch-rules.md) edited additively per FR-7.
8. Example regeneration surfaces ≥1 `MI-{N}` finding with concrete mitigations, LLM09 citation, populated `source_attribution`.
9. 5 non-factual-output baseline PDFs regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`.
10. 24 existing detection-tier files remain byte-identical (22 original + F-1's 2).
11. BLP-01 Coverage Matrix updated: LLM09:2025 Planned → Covered.
12. Delivery retrospective filed at `specs/206-misinformation-threat-agent/delivery.md` (mirrors F-1's `specs/201-output-integrity-threat-agent/delivery.md`).
13. Post-merge: ADR-031 SHA fill with squash commit hash.

---

## 🔖 Appendix — PRD-Time Verification Evidence

Evidence collected during PRD authoring (2026-04-23) to ground the PRD in codebase reality:

- **Schema state**: `schemas/finding.yaml:13` reads `schema_version: "1.6"`; `schemas/finding.yaml:18` reads `pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"` (10 prefixes, MI absent — confirms FR-4 bump needed).
- **Category enum**: `schemas/finding.yaml:30-39` lists 8 category values: `spoofing | tampering | repudiation | info-disclosure | denial-of-service | privilege-escalation | agentic | llm`. F-2 reuses `llm` with `MI-{N}` ID prefix — no enum edit needed.
- **OWASP LLM09 catalog entry**: `schemas/taxonomy/owasp.yaml` carries `- id: LLM09 / full_id: OWASP-LLM-2025-09 / name: Misinformation / url: https://genai.owasp.org/llmrisk/llm092025-misinformation/ / cwe_refs: []`. The `cwe_refs: []` means no automatic CWE inheritance via taxonomy edges — CWE attribution is finding-level.
- **CWE catalog entries**: CWE-345 (Insufficient Verification of Data Authenticity) and CWE-223 (Omission of Security-relevant Information) both verified present in `schemas/taxonomy/cwe.yaml` with `full_id`, `name`, `url`. These are the F-2 finding-level CWE attributions per FR-5.
- **MITRE ATLAS AML.T0042 catalog entry**: **Confirmed absent** from `schemas/taxonomy/mitre-atlas.yaml` at PRD time (architect-verified: catalog carries 12 AML techniques — `T0010, T0018, T0020, T0024, T0051, T0054, T0057, T0058, T0059, T0060, T0061, T0062`; `T0042` not present). Pattern-catalog prose retains the citation; `source_attribution` MUST NOT cite AML.T0042 (would fail F-A2 referential-integrity validator). Per F-1 precedent, prose-only citations are valid for context-setting.
- **finding-format-shared.md consumers list**: 14 entries post-F-1, ordered `orchestrator` → STRIDE-canonical (6) → AI-LLM-original (3: prompt-injection, data-poisoning, model-theft) → AI-AG (2: agent-autonomy, tool-abuse) → AI-LLM-new (1: output-integrity) → infra-consumer (1: risk-scorer). F-2 inserts `misinformation` as the 2nd AI-LLM-new entry (FR-3 placement).
- **Detection-tier agents pre-F-2**: 12 agents (11 original + `output-integrity.md` from F-1). Post-F-2: 13 agents. 24 existing files preserved byte-identically per SC-9.
- **ADR-030 Accepted**: `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md` Accepted 2026-04-19. Decision 2 Outcome B (split ASI09 → F-4) validates the signal-class discipline F-2 reuses; Decision 1 scopes F-1 to downstream-execution-sanitization (machine-victim, bytes/strings/syntax primitives) — leaving factual-integrity unambiguously open for F-2.
- **GitHub Issue #206**: "F-2 — LLM09 Misinformation Detection [Tier 1]" at stage:define (moved 2026-04-23). Body content verbatim from BLP-01 §7 F-2 section. 3 user stories preserved; interface contract, deliverable, outcome, format, dependencies, DoD, governance all intact.

---

**End of PRD Draft** — ready for Architect + Team-Lead parallel review.
