---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-25
    status: APPROVED
    notes: "High-fidelity translation of approved PRD/spec. All 21 spec FRs and all 21 spec SCs explicitly wave-mapped (extends F-2's 14-SC precedent). 3 P1 user stories AC-level operationalized: US-219-1 (A2A) via Wave 2 Category 9 catalog authoring; US-219-2 (MCP-to-MCP) via Wave 2 Category 10 catalog authoring; US-219-3 (cohesive Agentic-category rendering) via Wave 3 example regen + ADR-032 Decision 1. Q2 (cosmetic dispatch annotation), Q3 (example target), Q4 (anti-indicator section) resolved with documented justifications; Q1/Q5 PRD-resolutions honored without re-litigation. Heuristic A first-execution enrichment-branch narrative preserved end-to-end. Zero scope creep — F-3 stays purely additive at 5/5 dimensions smaller than F-2 (no new agent / no new skill dir / no schema bump / no consumers list edit / no orchestrator edit). Conventional Commits PR title contract (FR-021/SC-020) and delivery retrospective (SC-021) wave-mapped to Wave 4. Buffer Day 1 retrospective slotting (HIGH-1) + Buffer Day 2 concurrency hedge (R3) preserved per PRD. 0 BLOCKING / 0 HIGH / 1 MEDIUM / 3 LOW — M1 is ADR-032 number-reconfirmation assumption already flagged at PRD time; L1/L2/L3 are stylistic tasks.md refinements. PM APPROVES for /aod.tasks. Full review: .aod/results/product-manager.md."
  architect_signoff:
    agent: architect
    date: 2026-04-25
    status: APPROVED
    notes: "10/10 review dimensions PASS. All 14 ground-truth claims independently verified against repo: tool-abuse.md=98 lines, detection-patterns.md=163 lines+8 categories, schema_version=1.7, AG prefix in regex, ADR-032 free, all 5 catalog citations (ASI07/CWE-287/CWE-345/AML.T0060/LLM03) resolve, 0 MAESTRO refs in both target files. Plan correctly: (1) honors ADR-023 lean-agent + Decision 3 additive-only edits; (2) preserves byte-identity on Categories 1-8 + Overview/DFD/Triggers (SC-006 BLOCKER); (3) reuses AG prefix without schema bump (first BLP-01 detection feature with no schema bump); (4) preserves 24-file zero-edit invariant on remaining detection tier; (5) source_attribution contract correct — ASI07/CWE-287/CWE-345/AML.T0060/LLM03 catalog-verified; (6) Heuristic A scope rationale via ADR-030 Decision 1 + ADR-031 Decision 8 cross-refs (latter as asymmetry — F-3 does NOT invoke); (7) topology gate (FR-011) does correctness + byte-identity double-duty under SOURCE_DATE_EPOCH (strongest signal); (8) Pattern Category Disambiguation Cat 6 vs Cat 10 in ADR-032 Decision 7 addresses MEDIUM-2 from PRD; (9) 5 non-multi-agent baselines byte-identical via topology gate; (10) zero new dependencies. Q2/Q3/Q4 plan-day decisions match architect leanings; Q1/Q5 PRD-resolutions preserved. 0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW (advisory only): dispatch-rules.md row wording vs Q2=YES decision phrasing; anti-indicator conjunction/disjunction prose clarity for Wave 2 — both Wave-2 implementation refinements not blocking sign-off. Architect APPROVES for /aod.tasks. Full review: .aod/results/architect.md."
  techlead_signoff: null  # Added by /aod.tasks
---

# Implementation Plan: ASI07 Tool-Abuse Enrichment (OWASP ASI07:2026)

**Branch**: `219-asi07-tool-abuse-enrichment` | **Date**: 2026-04-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/219-asi07-tool-abuse-enrichment/spec.md`
**PRD**: [docs/product/02_PRD/219-asi07-tool-abuse-enrichment-2026-04-25.md](../../docs/product/02_PRD/219-asi07-tool-abuse-enrichment-2026-04-25.md)
**BLP-01 Phase**: Tier 1 F-3 — third Tier 1 feature; first execution of the Heuristic A **enrichment** branch (vs. the new-agent branch validated by F-1 + F-2); closes ASI07:2026 on the BLP-01 Coverage Matrix

## Summary

Enrich the existing `tool-abuse` AI-tier threat agent to close OWASP ASI07:2026 detection gap via Heuristic A consolidation. **No new agent file, no new skill directory, no schema bump, no consumers-list edit, no functional orchestrator/dispatch edit.** Net change is **purely additive** to two existing files plus one new ADR-032: (1) `tool-abuse.md` metadata `owasp_references += [ASI-07]`, `## Purpose` 1-3 line extension, Detection Workflow Step 5 references += `[ASI-07, AML.T0060, CWE-287, CWE-345]`; (2) `detection-patterns.md` appends Pattern Category 9 (Insecure Inter-Agent Communication / A2A) + Pattern Category 10 (MCP-to-MCP Trust Propagation) after Category 8, plus Primary Sources extension; (3) public ADR-032 documenting the Heuristic A enrichment pattern as operational precedent (Proposed → Accepted dual-commit per ADR-027/028/029/030/031 lineage). Findings emit with existing `AG-{N}` ID prefix and `category: agentic` (existing enum value); each Category-9/10 finding carries a populated `source_attribution` array citing OWASP ASI07:2026 (primary) plus applicable CWE (CWE-287 for Category 9, CWE-345 for Category 10) and where applicable AML.T0060 (Category 9) or LLM03:2025 (Category 10) as related.

**Architectural approach**: Apply ADR-023 Decision 3 additive-only edit discipline. Existing prose in `tool-abuse.md` `## Purpose` and Categories 1-8 in `detection-patterns.md` remain **byte-identical** pre/post edit (grep-checkable). Architect MEDIUM-2 PRD-level concern resolved via Pattern Category Disambiguation paragraph in FR-2 carving Category 6 (LLM03 supply-chain — upstream ingestion at registration time) from Category 10 (runtime trust propagation between already-registered MCP servers at invocation time) — formalized in ADR-032 Decision 7. The enriched agent activates as it does today on Process components matching existing tool-abuse trigger keywords; Categories 9 and 10 fire only on multi-agent / multi-MCP topologies (the topology gate ensures byte-identity on the 5 non-multi-agent baselines).

**Touch points**: 0 new agent files, 0 new skill directories, 0 schema edits, 0 functional dispatch edits, 0 consumers-list edits, 0 new runtime dependencies. **2 additive file edits** (`tool-abuse.md`, `detection-patterns.md`) + **1 new ADR** (ADR-032) + **1 example regeneration** (multi-agent target — PM default `agentic-app`; architect may override) + **1 optional cosmetic annotation** (`dispatch-rules.md` `tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)` per PRD Q2). **F-3 is structurally the smallest BLP-01 detection delivery to date.**

## Technical Context

**Language/Version**: Markdown + YAML + Python 3.11 (existing — stdlib + `pyyaml`); agent and skill content files, not executable code
**Primary Dependencies**: `pyyaml` (runtime, already declared), `pytest` (dev-only, already declared per Feature 128 precedent); **no new runtime or dev dependencies**
**Storage**: File-based; reads `schemas/finding.yaml` (v1.7, **no edit**), `schemas/taxonomy/{owasp,cwe,mitre-atlas}.yaml` (F-A1 catalogs, read-only for `source_attribution` validation); writes only to `.claude/agents/tachi/tool-abuse.md`, `.claude/skills/tachi-tool-abuse/references/detection-patterns.md`, `docs/architecture/02_ADRs/ADR-NNN-asi07-tool-abuse-enrichment.md`, `examples/agentic-app/` (or architect-chosen multi-agent example)
**Testing**: pytest (existing harness at `tests/scripts/`) + backward-compatibility test `tests/scripts/test_backward_compatibility.py` under `SOURCE_DATE_EPOCH=1700000000` per ADR-021 — 5 non-multi-agent baselines byte-identity gate; structural-diff test on Categories 1-8 byte-identity in `detection-patterns.md`; line-count test on `tool-abuse.md` (≤150); MAESTRO grep test on both enriched files; F-A2 referential-integrity validation on Category-9/10 fixture findings
**Target Platform**: Command-line Python tooling (macOS/Linux/WSL); orchestrator + threat agents invoked via `/tachi.threat-model` Claude command; PDF rendering via Typst + Mermaid CLI (unchanged)
**Project Type**: Single project (methodology toolkit — agents + skills + schemas + templates in a unified repo); no frontend/backend split
**Performance Goals**: Agent invocation latency unchanged. Two new Pattern Categories add O(2 additional pattern matches per AG dispatch); empirical impact <1ms per architecture file. No new performance regressions.
**Constraints**: (a) SC-006 byte-identity on Categories 1-8 + `## Overview` / `## Targeted DFD Element Types` / `## Trigger Keywords` in `detection-patterns.md` is a BLOCKER; (b) SC-010 byte-identity on 5 non-multi-agent example PDFs under `SOURCE_DATE_EPOCH=1700000000` is a BLOCKER; (c) SC-002 line-count cap ≤150 on `tool-abuse.md` is a BLOCKER (PRD-time baseline 98; expected post-edit 100-106); (d) SC-013 24-file zero-edit invariant on every detection-tier file other than the host agent + companion catalog is a BLOCKER (extended count post-F-1 + F-2: 26 detection files; F-3 edits 2; the remaining 24 stay byte-identical); (e) SC-014 schema invariant — `schemas/finding.yaml` `schema_version` MUST remain `"1.7"` (BLOCKER); (f) SC-015 F-A2 referential-integrity validation MUST pass on every Category-9/10 finding (BLOCKER); (g) SC-016 zero MAESTRO references in both enriched files (grep-auditable, BLOCKER); (h) FR-011 multi-agent / multi-MCP topology gate (correctness BLOCKER) — Categories 9-10 emit zero findings on single-agent / single-MCP architectures
**Scale/Scope**: 0 new agent files; 0 new skill directories; 2 file edits (~10-15 lines additive on `tool-abuse.md`; ~120-180 lines additive on `detection-patterns.md`); 2 new Pattern Categories with ≥4 indicators each, ≥1 worked example each, named mitigations; 1 new ADR (~250-350 lines); 1 example regeneration (`agentic-app` default; architect-adjudicated). **Edit surface is 5/5 dimensions smaller than F-2** per PRD §Timeline: no new agent / no new skill dir / no schema bump / no consumers list edit / no orchestrator edit.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against `.aod/memory/constitution.md`:

| Principle | Status | Notes |
|-----------|--------|-------|
| I. General-Purpose Architecture | PASS | Pattern Categories 9 + 10 detect generic inter-agent / multi-hop-MCP signal classes; no hardcoded project-type assumptions; works on any architecture exhibiting ≥2 agents or multi-MCP topology |
| II. API-First Design | N/A | No REST/GraphQL surface; threat agents are content files consumed by the orchestrator at invocation time |
| III. Backward Compatibility (NON-NEGOTIABLE) | PASS | Multi-agent / multi-MCP topology gate (FR-011) ensures byte-identity on 5 non-multi-agent baselines. Schema unchanged; existing AG-{N} findings remain valid. Local `.aod/` workflows unaffected. **No schema bump means even the schema-version-pinning surface is byte-identical** — F-3 is the first BLP-01 detection feature with zero schema-tier impact |
| IV. Concurrency & Data Integrity | N/A | F-3 is single-invocation content authoring; no concurrent state |
| V. Privacy & Data Isolation | PASS | Worked examples use clearly-fictional scenarios (orchestrator → worker-agent over plain HTTP; agent → MCP-A → MCP-B without per-hop attestation); no PII, no adopter data, no network calls by the agent |
| VI. Testing Excellence (MANDATORY) | PASS | Structural-diff test on Categories 1-8 byte-identity; line-count test on `tool-abuse.md`; MAESTRO grep test; F-A2 referential-integrity fixtures for Category-9/10 source_attribution; backward-compat byte-identity gate on 5 non-multi-agent baselines |
| VII. Definition of Done (NON-NEGOTIABLE) | PASS | Spec-defined SCs (SC-001 through SC-021) map to grep-checkable / wc-checkable / byte-identity predicates. SC-006 + SC-010 + SC-013 + SC-014 + SC-015 + SC-016 are BLOCKER-level gates. DoD bullet 12 (delivery retrospective at SC-021) carried via Wave 4 buffer-day slot per PRD HIGH-1 + F-1/F-2 precedent |
| VIII. Product-Spec Alignment | PASS | Approved PRD 219 exists (PM APPROVED, Architect APPROVED_WITH_CONCERNS, Team-Lead APPROVED_WITH_CONCERNS — all HIGH/MEDIUM concerns resolved inline in PRD); spec.md has PM APPROVED sign-off (0 BLOCKING / 0 HIGH / 0 MEDIUM / 2 LOW stylistic only) |
| IX. Git Workflow | PASS | Feature branch `219-asi07-tool-abuse-enrichment`; draft PR #220 already opened with `feat(219):` Conventional Commits title; no main commits; ADR-032 Proposed → Accepted dual-commit pattern |
| X. Zero-Edit Invariant (ADR-023 lineage) | PASS | FR-015 / SC-013 explicit; 24-file invariant covers 12 other threat agents + 12 other companion `detection-patterns.md` files (extended count post-F-1 + F-2: 26 detection files; F-3 edits 2 host files; 24 stay byte-identical). FR-014 / SC-013 also enforce zero edit to `finding-format-shared.md` consumers list. FR-016 / SC-017 enforces zero functional edit to orchestrator dispatch tier (cosmetic annotation carve-out per Q2 architect plan-day decision is documentation-only). |

**Gate verdict**: No violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```
specs/219-asi07-tool-abuse-enrichment/
├── plan.md                  # This file (/aod.project-plan output)
├── research.md              # Phase 0 output (populated by /aod.spec)
├── data-model.md            # Phase 1 output — Pattern Category 9/10 shape + topology gate + finding shape
├── contracts/
│   └── finding-contract.md  # Finding IR contract for Category-9/10 AG-{N} findings (source_attribution + mitigation rules)
├── quickstart.md            # Phase 1 output — verification walkthrough
├── checklists/
│   └── requirements.md      # Spec quality checklist (populated by /aod.spec)
├── spec.md                  # PM-approved spec
└── tasks.md                 # Task breakdown (/aod.tasks output)
```

### Source Code (repository root)

```
tachi/
├── .claude/
│   ├── agents/
│   │   └── tachi/
│   │       ├── tool-abuse.md                         # MODIFY (additive; 3 small edits) — 98 → 100-106 lines
│   │       ├── orchestrator.md                       # UNCHANGED (zero functional edit; tool-abuse already registered)
│   │       ├── output-integrity.md                   # UNCHANGED (24-file invariant; F-1's agent)
│   │       ├── misinformation.md                     # UNCHANGED (24-file invariant; F-2's agent)
│   │       ├── prompt-injection.md / data-poisoning.md / model-theft.md / agent-autonomy.md         # UNCHANGED
│   │       ├── spoofing / tampering / repudiation / info-disclosure / denial-of-service / privilege-escalation.md  # UNCHANGED (6 STRIDE)
│   │       ├── risk-scorer.md                        # UNCHANGED (FR-017 infrastructure-tier invariant)
│   │       ├── control-analyzer.md                   # UNCHANGED
│   │       ├── threat-report.md                      # UNCHANGED
│   │       ├── threat-infographic.md                 # UNCHANGED
│   │       └── report-assembler.md                   # UNCHANGED
│   │
│   └── skills/
│       ├── tachi-tool-abuse/
│       │   └── references/
│       │       └── detection-patterns.md             # MODIFY (additive; appends Categories 9 + 10 + Primary Sources extension) — 163 → ~280-330 lines
│       │
│       ├── tachi-orchestration/
│       │   └── references/
│       │       └── dispatch-rules.md                 # UNCHANGED (Q2 cosmetic annotation contingent — architect plan-day decision; documentation-only if applied)
│       │
│       ├── tachi-shared/
│       │   └── references/
│       │       └── finding-format-shared.md          # UNCHANGED (tool-abuse already at line 18 in consumers list)
│       │
│       ├── tachi-output-integrity/                    # UNCHANGED (24-file invariant; F-1's companion)
│       ├── tachi-misinformation/                      # UNCHANGED (24-file invariant; F-2's companion)
│       └── tachi-{11 other AI + STRIDE skills}/       # UNCHANGED (24-file invariant)
│
├── schemas/
│   ├── finding.yaml                                   # UNCHANGED — schema_version stays "1.7"; id.pattern unchanged
│   └── taxonomy/                                      # UNCHANGED — read-only source for source_attribution validation
│       ├── owasp.yaml                                 # ASI07 entry present (verified PRD-time at line 308); LLM03 present
│       ├── cwe.yaml                                   # CWE-287, CWE-345 entries present (verified PRD-time)
│       └── mitre-atlas.yaml                           # AML.T0060 entry present (verified PRD-time — distinct from F-2's confirmed-absent AML.T0042)
│
├── docs/
│   └── architecture/
│       └── 02_ADRs/
│           └── ADR-032-asi07-tool-abuse-enrichment.md # NEW — Proposed → Accepted dual-commit (number reconfirmed at plan time per Assumption)
│
├── tests/
│   └── scripts/
│       ├── test_tool_abuse_enrichment.py              # NEW — structural-diff test on Categories 1-8 byte-identity + line-count test + MAESTRO grep test + F-A2 referential-integrity fixtures for Category-9/10
│       ├── test_backward_compatibility.py             # UNCHANGED — 5 non-multi-agent baselines byte-identity gate (extended scope automatic; topology gate ensures zero impact)
│       └── fixtures/
│           └── tool_abuse_enrichment/                 # NEW — fixture findings for Categories 9 + 10
│               ├── valid_category_9_a2a_finding.yaml
│               ├── valid_category_10_mcp_to_mcp_finding.yaml
│               └── invalid_attribution_finding.yaml
│
├── examples/
│   ├── web-app / microservices / ascii-web-api / mermaid-agentic-app / free-text-microservice / maestro-reference/  # UNCHANGED (SC-010 baselines; non-multi-agent or stylistic-multi-agent — zero new findings)
│   └── agentic-app/                                   # REGENERATE (PM default per Q3; architect may override at plan time with maestro-reference or new minimal multi-agent fixture)
│
└── scripts/
    └── tachi_parsers.py                               # UNCHANGED (validate_source_attribution accepts AG via existing regex; Category-9/10 source_attribution flows through unchanged validators)
```

**Structure Decision**: Single-project layout (existing tachi repo structure). **Zero new top-level directories**. All changes confined to `.claude/agents/tachi/tool-abuse.md`, `.claude/skills/tachi-tool-abuse/references/detection-patterns.md`, `docs/architecture/02_ADRs/`, `tests/scripts/`, `examples/agentic-app/`. F-3 follows Feature 082 (lean-agent refactor) + ADR-023 (additive-only shared-reference edits) + Feature 142 (multi-agent component types) + Feature 201 F-1 + Feature 206 F-2 precedents. **F-3 is the first BLP-01 feature to follow ADR-023 Decision 3 in its purest form** — additive-only edits to existing files with byte-identity preservation on existing content.

## System Design

### Components

**Modified components (additive edits only — F-3-owned)**:

1. **`tool-abuse` Threat Agent** (`.claude/agents/tachi/tool-abuse.md`)
   - **Edit 1** (one-token additive): metadata YAML `owasp_references: [ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025]` → `[ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025, ASI-07]`
   - **Edit 2** (1-3 line additive append within `## Purpose` section): name the inter-agent channel surface (A2A and MCP-to-MCP) alongside existing tool-dispatch surface — preserves existing `## Purpose` prose byte-identical (additive append only)
   - **Edit 3** (additive references-list extension on Detection Workflow Step 5): existing `(ASI-02, ASI-04, MCP-03, MCP-05, OWASP LLM06:2025, MITRE ATLAS AML.T0058/T0061/T0062, CWE-77, CWE-89)` → append `ASI-07`, `MITRE ATLAS AML.T0060`, `CWE-287`, `CWE-345`
   - Line count: ≤150 (AI tier cap per ADR-023); PRD-time baseline 98; expected post-edit 100-106
   - Five-section canonical layout, single `**MANDATORY**: Read` directive, zero MAESTRO references — all preserved

2. **Pattern Catalog** (`.claude/skills/tachi-tool-abuse/references/detection-patterns.md`)
   - **Edit 1** (additive append after Category 8): **Pattern Category 9 — Insecure Inter-Agent Communication (A2A)** with primary OWASP ASI07:2026, related CWE-287 + AML.T0060; ≥4 indicators (target 5 per architect leaning) covering ≥2 agents connected by a channel, no mutual auth, no message signing, no replay protection, agent-in-the-middle relay without taint propagation; ≥1 worked example (orchestrator → worker-agent over plain HTTP); named mitigations (mTLS, HMAC signing + nonce, replay-window, taint propagation, mutual JWT/API key fallback)
   - **Edit 2** (additive append after Category 9): **Pattern Category 10 — MCP-to-MCP Trust Propagation** with primary OWASP ASI07:2026, related CWE-345 + LLM03:2025 (inherited supply-chain vocabulary); ≥4 indicators (target 5) covering multi-hop MCP trust chain, no per-hop attestation, transitive authority assumption gaps, no trust-chain validator, undeclared cross-MCP supply-chain assumptions; ≥1 worked example (Agent → MCP-A → MCP-B without per-hop attestation); named mitigations (per-hop attestation, signed-capability handoff, MCP-trust-chain validator, supply-chain trust-chain enforcement, taint propagation across hops)
   - **Edit 3** (additive append before `## Primary Sources` section): **Pattern Category Disambiguation** subsection per PRD FR-2 carving Category 6 (LLM03 supply-chain — upstream ingestion at registration time) from Category 10 (runtime trust propagation between already-registered MCP servers) — formalizes ADR-032 Decision 7
   - **Edit 4** (additive list extension on `## Primary Sources`): append `OWASP ASI07:2026 — Insecure Inter-Agent Communication` and `MITRE ATLAS AML.T0060 — Agent-in-the-Middle`
   - **Optional anti-indicator section** per PRD Q4 architect leaning YES: each new Category 9/10 enumerates at least one anti-indicator (single-agent topology for Cat 9; single-MCP topology for Cat 10) — formalizes the topology gate for grep-auditability
   - Pre-existing Categories 1-8, `## Overview`, `## Targeted DFD Element Types`, `## Trigger Keywords` remain byte-identical pre/post edit (grep-checkable additive-only invariant per ADR-023 Decision 3)

3. **Public Per-Feature ADR** (`docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md`)
   - Proposed → Accepted dual-commit (ADR-027/028/029/030/031 precedent)
   - 6-7 numbered Decisions in body: (Decision 1) Heuristic A enrichment vs. new agent — signal-class identity rationale; (Decision 2) Additive-only edit discipline per ADR-023 Decision 3 with byte-identity proof; (Decision 3) No schema bump — reuses AG-{N} prefix; (Decision 4) No consumers-list edit — `tool-abuse` already at line 18; (Decision 5) No functional orchestrator/dispatch-rules edit — `tool-abuse` already fully registered; (Decision 6) Public ADR omits commercial framing per SDR-001 Option C; (Decision 7) Pattern Category Disambiguation — Category 6 vs. Category 10 non-overlap carve
   - Cross-references: ADR-021 (byte-identity baseline harness), ADR-023 (lean+skill-references pattern, additive-only edits Decision 3), ADR-027 (taxonomy crosswalk), ADR-028 (source_attribution schema extension), ADR-030 Decision 1 (signal-class taxonomy in LLM tier as different application of same rule), ADR-031 Decision 8 (regex-alternation minor-bump rule as the **asymmetry** F-3 does NOT invoke — Heuristic A consolidation reuses existing host's ID space)
   - Zero-MAESTRO-reference invariant: ADR-032 itself contains zero MAESTRO references in Decision sections (mirrors agent file invariant)
   - Revision History table tracking Proposed → Accepted dates; post-merge SHA fill recording squash commit

**Optional cosmetic component (Q2 architect plan-day decision)**:

4. **Dispatch Rules Annotation** (`.claude/skills/tachi-orchestration/references/dispatch-rules.md` — annotation only, contingent)
   - If architect approves Q2 at plan time (architect leaning YES per PRD): one-token annotation update extending `tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)` for Coverage Matrix traceability
   - **Documentation-only**, zero functional dispatch change — does not invalidate the SC-017 zero-functional-touch claim

### Data Flow

Given a DFD architecture description, the orchestrator dispatches the `tool-abuse` agent **as it does today** when any DFD `Process` element matches existing tool-abuse trigger keywords (orchestrator, MCP server, tool server, plugin, agent, etc.). The agent reads the companion `detection-patterns.md` via the existing single `**MANDATORY**: Read` directive, evaluates pattern categories 1-10 (1-8 existing + 9-10 new) on each dispatched Process, and emits zero or more `AG-{N}` findings. The new Pattern Categories 9 and 10 enforce the **multi-agent / multi-MCP topology gate** (FR-011): Category 9 emits findings only when ≥2 agent Process components are connected by a communication channel; Category 10 emits findings only when an architecture exhibits a multi-hop MCP trust chain. Findings flow through orchestrator Phase 3 (MAESTRO assignment, agentic_pattern assignment), Phase 4 (referential validation — F-A2 `validate_source_attribution`), and Phase 5 (deduplication) **identically** to existing Categories 1-8 `AG-{N}` findings. No consumer-tier changes required. Report-tier rendering (`threat-report.md`, `threats.md`) groups all `AG-{N}` findings (Categories 1-10) cohesively in the same `category: agentic` section — single-namespace ID space, sequential numbering across all 10 categories.

### Tech Stack

- **Agent / skill files**: Markdown + YAML (ADR-023 lean-agent + additive-only shared-reference pattern)
- **Schema**: `schemas/finding.yaml` v1.7 — **unchanged** (AG prefix already enumerated; F-3 reuses existing prefix)
- **Taxonomy catalogs**: `schemas/taxonomy/{owasp,cwe,mitre-atlas}.yaml` (F-A1, unchanged) — consumed read-only for `source_attribution` validation
- **Orchestrator dispatch**: `.claude/agents/tachi/orchestrator.md` + `.claude/skills/tachi-orchestration/references/dispatch-rules.md` — **unchanged** (`tool-abuse` already fully registered; optional Q2 cosmetic annotation is documentation-only)
- **Parser**: `scripts/tachi_parsers.py` (unchanged — `validate_source_attribution` already accepts any ID prefix matching the existing regex)
- **Test harness**: pytest + `tests/scripts/test_backward_compatibility.py` (existing — automatic scope extension via topology gate ensuring zero impact on 5 non-multi-agent baselines) + new `tests/scripts/test_tool_abuse_enrichment.py` (structural-diff + line-count + MAESTRO grep + F-A2 fixtures for Category-9/10)
- **Example regeneration pipeline**: `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report` (existing pipeline, unchanged)
- **Typst templates**: no edits — PDF renderer reads `threats.md` / `risk-scores.md` / `compensating-controls.md` and the coverage-attestation section auto-renders from `source_attribution` post-regeneration
- **ADR dual-commit**: standard Proposed → Accepted lifecycle via `gh pr` + squash merge (ADR-027/028/029/030/031 precedent)

## Phase 0: Research

**Status**: Populated by `/aod.spec` at [research.md](./research.md). Key grounding facts re-confirmed at plan time:

- `.claude/agents/tachi/tool-abuse.md` is **98 lines** (PRD-time verified; expected post-edit 100-106 lines)
- `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` is **163 lines** with **8 Pattern Categories** (PRD-time verified); `## Primary Sources` section starts at line 154
- `schemas/finding.yaml:13` `schema_version: "1.7"` (post-F-2; F-3 does NOT bump)
- `schemas/finding.yaml:18` `id.pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI)-\\d+$"` — `AG` already enumerated; F-3 reuses
- `schemas/taxonomy/owasp.yaml` contains **ASI07** record (line 308 PRD-verified) and LLM03 record
- `schemas/taxonomy/cwe.yaml` contains **CWE-287** (Improper Authentication) and **CWE-345** (Insufficient Verification of Data Authenticity)
- `schemas/taxonomy/mitre-atlas.yaml` contains **AML.T0060** (Agent-in-the-Middle) — **distinct from F-2's confirmed-absent AML.T0042**; F-3 cites AML.T0060 in `source_attribution` directly (no prose-only carve)
- `.claude/skills/tachi-shared/references/finding-format-shared.md` consumers list contains `tool-abuse` at line 18 (PRD-time verified — no edit needed)
- ADR-032 does NOT yet exist (next-available ADR number; ADR-031 is highest existing per `ls docs/architecture/02_ADRs/`)
- 0 MAESTRO references in `tool-abuse.md` and `detection-patterns.md` (PRD-time grep-verified)
- F-1 and F-2 ADRs (ADR-030, ADR-031) are Accepted; F-3 ADR-032 cross-references both as the Heuristic A scope precedents

**Open research items resolved during /aod.project-plan** (see Open Questions section):
- Q1 (Single category vs. split for "channel-without-auth" vs. "broken-auth") — RESOLVED at PRD time (single category covers both per architect 2026-04-25)
- Q2 (Cosmetic dispatch-rules annotation `tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)`) — architect plan-day decision per PRD; default YES per architect leaning
- Q3 (Example regeneration target — `agentic-app` extension vs. `maestro-reference` vs. new minimal multi-agent fixture) — architect plan-day decision; PM default `agentic-app`
- Q4 (Anti-indicator section in `detection-patterns.md` Category 9 + 10) — architect plan-day decision per PRD; default YES per architect leaning
- Q5 (Build-day sequencing — Tuesday 2026-04-28 or compressed) — RESOLVED at PRD time (Tuesday 2026-04-28 per team-lead 2026-04-25)

## Phase 1: Design & Contracts

**Prerequisites**: research.md populated (Phase 0 complete)

### Finding IR Contract (`contracts/finding-contract.md`)

**Purpose**: Document the shape of Category-9/10 `AG-{N}` findings emitted by the enriched agent, including `source_attribution` invariants and mitigation-text rules. See [contracts/finding-contract.md](./contracts/finding-contract.md) for full contract.

**Contract summary**:

```yaml
id: "AG-{N}"                          # existing prefix (no schema bump in F-3); single-namespace across Categories 1-10
category: "agentic"                   # existing enum value — unchanged
title: "{pattern_category}: {short_summary}"  # e.g., "Inter-Agent Channel Without Mutual Authentication: orchestrator dispatches to worker-agent over plain HTTP"
severity: "low" | "medium" | "high" | "critical"  # OWASP 3×3 matrix via severity-bands-shared.md
component: "{DFD Process component name | Inter-Agent Communication Channel name | MCP relay name}"
description: "{2-4 sentence threat description distinguishing A2A vs MCP-to-MCP signal-class}"
mitigation: "{inter-agent / MCP-trust mechanism}"  # e.g., "Mutual TLS on every inter-agent channel + HMAC envelope signing with per-call nonce"
references:
  - "OWASP ASI07:2026"
  - "https://cwe.mitre.org/data/definitions/{CWE_NUMBER}.html"
source_attribution:
  - {taxonomy: "owasp", id: "ASI07", relationship: "primary"}     # REQUIRED on every Category-9 AND Category-10 finding
  # Category 9: + {taxonomy: cwe, id: CWE-287, relationship: related} + (where applicable) {taxonomy: atlas, id: AML.T0060, relationship: related}
  # Category 10: + {taxonomy: cwe, id: CWE-345, relationship: related} + (where applicable) {taxonomy: owasp, id: LLM03, relationship: related}
maestro_layer: "L7"                   # assigned downstream by orchestrator Phase 1 (existing Feature 084) — agent-ecosystem layer
agentic_pattern: "communication_vulnerability" | "trust_exploitation" | "none"  # assigned downstream by orchestrator Phase 3.6 (existing Feature 142)
delta_status: null                    # assigned downstream if baseline present (existing Feature 104)
```

**Invariants**:
- Every Category-9/10 `AG-{N}` finding MUST pass `validate_source_attribution()` at orchestrator Phase 4
- The `source_attribution` array MUST contain at minimum `{taxonomy: owasp, id: ASI07, relationship: primary}`
- Category 9 findings MUST cite `{taxonomy: cwe, id: CWE-287, relationship: related}`; MAY cite `{taxonomy: atlas, id: AML.T0060, relationship: related}` for agent-in-the-middle relay topologies
- Category 10 findings MUST cite `{taxonomy: cwe, id: CWE-345, relationship: related}`; MAY cite `{taxonomy: owasp, id: LLM03, relationship: related}` for cross-MCP supply-chain trust-inheritance reasoning
- The `mitigation` field MUST name at least one specific inter-agent / MCP-trust mechanism (mTLS, HMAC signing, nonce-based replay prevention, per-hop attestation, signed-capability handoff, etc.) — NOT generic "secure the inter-agent channel"
- The `id` MUST match schema 1.7 `id.pattern` regex (existing AG prefix; no bump)
- The agent MUST enforce the multi-agent / multi-MCP topology gate (FR-011): Categories 9-10 emit zero findings on single-agent / single-MCP architectures

### Data Model (`data-model.md`)

**Purpose**: Document Pattern Category 9 + 10 entity shape, the multi-agent / multi-MCP topology gate predicates, source_attribution patterns per category, and Pattern Category Disambiguation entity (Category 6 vs. 10).

See [data-model.md](./data-model.md) for full entity definitions.

### Quickstart (`quickstart.md`)

**Purpose**: Step-by-step verification walkthrough — given a regenerated multi-agent example architecture (`agentic-app` per PM default), confirm ≥1 new `AG-{N}` finding attributable to Category 9 OR 10 with valid `source_attribution`, valid mitigation text, and passing F-A2 referential-integrity validation.

See [quickstart.md](./quickstart.md) for the verification procedure.

### Agent Context Update

Run `.aod/scripts/bash/update-agent-context.sh claude` after plan approval to refresh `CLAUDE.md` / agent-specific context with the Feature 219 entry.

## Implementation Approach (Phased Waves)

Calendar-verified against `cal 4 2026`: 2026-04-28 Tuesday (Day 1 build), 2026-04-29 Wednesday (Buffer Day 1 — primary), 2026-04-30 Thursday (Buffer Day 2 — multi-feature concurrency hedge per PRD R3).

**Single-day envelope** per PRD §Timeline: F-3 surface 5/5 dimensions smaller than F-2 (no new agent / no new skill dir / no schema bump / no consumers list edit / no orchestrator edit). Realistic envelope: **1 working day**, 0.5 days aspirational. F-3's wave structure is necessarily tighter than F-2's 6-wave / 2-day model.

### Wave 1 — Day 1 AM (Tuesday 2026-04-28, ~0.4d)

**ADR-032 Proposed + agent-file additive edits + structural validation.**

- **Wave 1.0 (15-30 min)**: Architect re-verifies (a) all 5 catalog citations still resolve in `schemas/taxonomy/{owasp,cwe,mitre-atlas}.yaml` (re-runs PRD-time grep checks); (b) Heuristic A enrichment-vs-new-agent decision intact (SDR-001 Decision 4 locked; ADR-030 Decision 1 + ADR-031 Decision 8 cross-refs valid); (c) `tool-abuse.md` line count is still 98 (no concurrent edit landed since PRD time). If any verification fails, escalate before Wave 1.1 commit.
- **Wave 1.1 (parallel)**:
  - **ADR-032 Proposed commit**: ADR body with 6-7 numbered Decisions (Heuristic A enrichment rationale, additive-only edit discipline, no schema bump, no consumers edit, no orchestrator edit, public-only governance, Pattern Category Disambiguation Cat 6 vs. Cat 10), cross-references to ADR-021/023/027/028/030/031, 24-file zero-edit invariant proof with grep-auditable enumeration, Revision History table.
  - **`tool-abuse.md` edits (Edit 1 + Edit 2 + Edit 3)**: metadata `owasp_references += [ASI-07]`; `## Purpose` 1-3 line extension; Detection Workflow Step 5 references += `[ASI-07, MITRE ATLAS AML.T0060, CWE-287, CWE-345]`. Architect adjudicates final `## Purpose` prose at Wave 1.1.
  - **Test fixture authoring**: `tests/scripts/fixtures/tool_abuse_enrichment/valid_category_9_a2a_finding.yaml`, `valid_category_10_mcp_to_mcp_finding.yaml`, `invalid_attribution_finding.yaml`.
- **Structural validation at Wave 1.1 EOD**: `wc -l .claude/agents/tachi/tool-abuse.md` returns ≤150 (expected 100-106); `grep -c '\*\*MANDATORY\*\*: Read' .claude/agents/tachi/tool-abuse.md` returns 1 (unchanged); `grep -i maestro .claude/agents/tachi/tool-abuse.md` returns empty.
- **PRD Q2 architect plan-day decision** (cosmetic dispatch-rules annotation): architect decides at Wave 1.0 whether to apply the optional one-token annotation `tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)` to `dispatch-rules.md`. If YES, the edit lands at Wave 1.1 alongside `tool-abuse.md` edits (single-token, ~30 seconds). If NO, the edit is skipped — F-3 ships with zero functional dispatch-tier touches.

### Wave 2 — Day 1 AM/PM (Tuesday 2026-04-28, ~0.4d)

**Pattern catalog authoring (Categories 9 + 10) + Pattern Category Disambiguation + Primary Sources extension.**

- `.claude/skills/tachi-tool-abuse/references/detection-patterns.md`:
  - Append **Pattern Category 9 — Insecure Inter-Agent Communication (A2A)** after existing Category 8: ≥4 indicators (target 5 per architect leaning), ≥1 worked example (clearly-fictional orchestrator → worker-agent topology), named mitigations (mTLS, HMAC + nonce, replay-window, taint propagation, mutual JWT/API key fallback). Optional anti-indicator section per Q4 architect leaning YES (single-agent topology emits zero Category-9 findings).
  - Append **Pattern Category 10 — MCP-to-MCP Trust Propagation** after Category 9: ≥4 indicators (target 5), ≥1 worked example (clearly-fictional Agent → MCP-A → MCP-B topology), named mitigations (per-hop attestation, signed-capability handoff, MCP-trust-chain validator, supply-chain trust-chain enforcement, taint propagation across hops). Optional anti-indicator section per Q4 architect leaning YES (single-MCP topology emits zero Category-10 findings).
  - Append **Pattern Category Disambiguation** subsection per PRD FR-2 / ADR-032 Decision 7: explicit non-overlap carve between Category 6 (LLM03 supply-chain — upstream ingestion at registration time) and Category 10 (runtime trust propagation between already-registered MCP servers at invocation time).
  - Extend `## Primary Sources` list with `OWASP ASI07:2026 — Insecure Inter-Agent Communication` and `MITRE ATLAS AML.T0060 — Agent-in-the-Middle`.
- **Byte-identity validation at Wave 2 EOD**: structural diff of pre/post `detection-patterns.md` returns empty for the unchanged regions (Categories 1-8 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords`). `grep -i maestro` returns empty on `detection-patterns.md`.

### Wave 3 — Day 1 PM (Tuesday 2026-04-28, ~0.3d)

**Example regeneration + backward-compat verification + tests.**

- Architect decides at Wave 2 EOD whether to extend `examples/agentic-app/` in-place (PM default per Q3) or fall back to `examples/maestro-reference/` or a new minimal multi-agent fixture (consuming Buffer Day 1 capacity per R1). Default: extend `agentic-app` if its multi-agent topology post-Feature-142 exhibits a sufficiently clean inter-agent channel signal.
- Run `/tachi.threat-model examples/{chosen-multi-agent-example}/architecture.md` to confirm dispatch emits ≥1 new Category-9/10 `AG-{N}` finding.
- Run full downstream pipeline (`/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic all`, `/tachi.security-report`).
- Commit regenerated artifacts: `threats.md`, `threats.sarif`, `risk-scores.md`, `risk-scores.sarif`, `compensating-controls.md`, `compensating-controls.sarif`, `threat-report.md`, `attack-trees/`, `attack-chains.md`, infographic JPEGs, `security-report.pdf`, `security-report.pdf.baseline`.
- Verify ≥1 new Category-9/10 `AG-{N}` finding present; verify F-A2 referential validation passes (`validate_source_attribution` returns no errors for all Category-9/10 findings); verify cohesive Agentic-category rendering (Categories 1-10 `AG-{N}` findings adjacent in `category: agentic` section without artificial fragmentation).
- Run `tests/scripts/test_backward_compatibility.py` — 5 non-multi-agent baselines (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) MUST be byte-identical under `SOURCE_DATE_EPOCH=1700000000`.
- Run `tests/scripts/test_tool_abuse_enrichment.py` — structural-diff test on Categories 1-8 byte-identity (BLOCKER per SC-006); line-count test on `tool-abuse.md` (BLOCKER per SC-002); MAESTRO grep test (BLOCKER per SC-016); F-A2 fixture validation on Category-9/10 source_attribution (BLOCKER per SC-015).

### Wave 4 — Day 1 PM / Buffer Day 1 (2026-04-28 PM or 2026-04-29 Wed)

**Code review + ADR-032 Accepted transition + PR ready + Coverage Matrix update + delivery retrospective.**

- senior-backend-engineer + code-reviewer review pattern catalog worked examples for clearly-fictional framing (no real institutional/clinician/lawyer/advisor identities); structural-diff invariants; line-count cap; MAESTRO grep — absorbs polish per HIGH-1 buffer-day budget model.
- Transition ADR-032 Proposed → Accepted with provisional merge-date.
- Mark PR #220 (draft) ready for review via `gh pr ready`.
- Triple-review + merge (squash commit with `feat(219): asi07 inter-agent communication tool-abuse enrichment` Conventional Commits title).
- **Post-merge SHA fill** on ADR-032 Revision History table.
- **BLP-01 Coverage Matrix update** (SC-018): ASI07:2026 transitions Planned → Covered with F-3 (Feature 219) named as closure feature. Post-merge documentation commit to `_internal/strategy/BLP-01-threat-coverage.md`.
- **Delivery retrospective slotting** per SC-021 / DoD bullet 12 / PRD HIGH-1: file `specs/219-asi07-tool-abuse-enrichment/delivery.md` same-day-as-delivery if Day 1 PM merge has ≥1 hour residual capacity; otherwise authored 2026-04-29 Wed (Buffer Day 1) as primary buffer-day activity. Mirrors F-1 + F-2 precedent (`specs/201-...`, `specs/206-...`). Captures: actual vs. estimated effort, **first-execution Heuristic A enrichment-pattern lessons** (precedent for F-6/F-7 Tier 2 ML+Mobile bundles which may also use enrichment), byte-identity preservation evidence (SC-006 + SC-010 grep proofs), any deviations from PRD timeline or scope.
- **Release-please post-merge verification** (SC-020 / R6): within ~30s after merge, confirm release-please PR opened. If empty, push empty `feat(219): asi07 enrichment — release marker` commit per F-212 incident recovery pattern.

### Buffer Day 2 — 2026-04-30 Thursday — Multi-Feature Concurrency Hedge

Reserved per PRD R3 for F-3 + F-4 + F-5 sequencing collisions if F-4 (ASI09) or F-5 (LLM10) enters build concurrently. Mitigation: F-3 ships first (smallest surface, no shared edits with F-4/F-5). If R3 does not materialize, Buffer Day 2 capacity redirects to additional polish or remains unused.

## Touch Points Summary

| File | Change | Lines | Scope |
|------|--------|-------|-------|
| `.claude/agents/tachi/tool-abuse.md` | MODIFY (additive; 3 small edits) | ~5-10 added | Metadata + Purpose + Step 5 references |
| `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` | MODIFY (additive; 4 sections appended) | ~120-180 added | Categories 9 + 10 + Pattern Category Disambiguation + Primary Sources extension |
| `.claude/skills/tachi-orchestration/references/dispatch-rules.md` | OPTIONAL annotation (Q2 architect plan-day decision; documentation-only if applied) | ~1 token | `tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)` — zero functional change |
| `docs/architecture/02_ADRs/ADR-032-asi07-tool-abuse-enrichment.md` | NEW | ~250-350 | Public ADR with 6-7 Decisions |
| `tests/scripts/test_tool_abuse_enrichment.py` | NEW | ~100-150 | Structural-diff + line-count + MAESTRO grep + F-A2 fixtures |
| `tests/scripts/fixtures/tool_abuse_enrichment/*.yaml` | NEW | ~20-30 each | Test fixtures (3 files) |
| `examples/agentic-app/*` (or architect-chosen multi-agent example) | REGENERATE | — | Pipeline artifacts + PDF baseline |
| `.claude/agents/tachi/{12 other detection-tier}.md` + `.claude/skills/tachi-{12 other detection-tier}/references/detection-patterns.md` | ZERO CHANGES | — | 24-file invariant (extended count post-F-1 + F-2) |
| `.claude/agents/tachi/orchestrator.md` | ZERO CHANGES | — | `tool-abuse` already registered |
| `.claude/skills/tachi-shared/references/finding-format-shared.md` | ZERO CHANGES | — | `tool-abuse` already at line 18 in consumers list |
| `.claude/agents/tachi/{risk-scorer,control-analyzer,threat-report,threat-infographic,report-assembler}.md` | ZERO CHANGES | — | Infrastructure-tier invariant |
| `schemas/finding.yaml` | ZERO CHANGES | — | No schema bump (first BLP-01 detection feature with no schema bump) |
| `scripts/*.py` | ZERO CHANGES | — | Parser + orchestrator scripts |
| `templates/tachi/*` | ZERO CHANGES | — | Typst templates |
| `requirements*.txt`, `pyproject.toml`, `package.json` | ZERO CHANGES | — | No new dependencies |

## Risks & Mitigations

See spec.md Edge Cases + PRD §Risks & Mitigations for the full list. Plan-phase active risks:

- **R1 (Example regeneration friction on `examples/agentic-app/`)** — Mitigation: Wave 1.0 architect decides example target (extend `agentic-app` per PM default, or fall back to `maestro-reference` / new minimal multi-agent fixture); Wave 3 structured pre-vs-post diff; Buffer Day 1 reserved (≤8 hours absorbs friction).
- **R2 (Heuristic A enrichment pushback at architect review)** — Mitigation: Wave 1.0 architect re-verifies SDR-001 Decision 4 + ADR-030 Decision 1 + ADR-031 Decision 8 cross-refs intact; PRD §"Three things the solution is deliberately NOT" pre-empts most likely concerns. Status: LOW likelihood per architect APPROVED_WITH_CONCERNS at PRD review (0 BLOCKING / 0 HIGH).
- **R3 (Multi-feature concurrency conflicts F-3 + F-4 + F-5)** — Mitigation: F-3 has smallest edit surface; sequencing F-3 first minimizes rebase friction. Buffer Day 2 (2026-04-30) absorbs concurrency-rebase work. team-lead checks `gh pr list` and BACKLOG.md at Wave 1.0.
- **R4 (Catalog drift between PRD time and build time)** — Mitigation: Wave 1.0 re-verification of all 5 catalog citations (ASI07, CWE-287, CWE-345, AML.T0060, LLM03). If drift detected, re-cite or remove offending citation; F-A2 referential-integrity validator catches drift programmatically.
- **R5 (BLP-01 momentum perception)** — CLOSED: F-3 closing within 1 working day demonstrates Heuristic A enrichment is faster than new-agent pattern; positive momentum, not negative.
- **R6 (Release-please skip if PR title misformatted)** — Mitigation: Plan-stage opens draft PR with `feat(219):` title from start (already done — PR #220 with title `feat(219): asi07-tool-abuse-enrichment`). Wave 4 pre-merge re-verifies title and retitles if needed; post-merge verifies release-please PR opens within ~30s; recovery via empty `feat(219): ... release marker` commit per F-212 precedent.
- **R7 (Pattern Category Disambiguation drift Category 6 vs. Category 10 confusion)** — Mitigation: Wave 2 explicit Pattern Category Disambiguation subsection per PRD FR-2; ADR-032 Decision 7 formalizes carve. Code-reviewer at Wave 4 audits worked-example prose for Category 6 vs. Category 10 boundary clarity.
- **R8 (Anti-indicator section authoring drift)** — Mitigation: PRD Q4 architect plan-day decision (default YES per architect leaning). Anti-indicator format mirrors PRD US-219-1 AC-4 / US-219-2 AC-3 structure (single-agent → zero Category-9; single-MCP → zero Category-10). Code-reviewer at Wave 4 confirms anti-indicator predicates are testable.

## Open Questions (PRD Q-set — Architect Decisions)

Architect-owned per PRD §Architecture & Design Decisions. PRD-resolved Q1 + Q5 not re-litigated; Q2/Q3/Q4 resolved during `/aod.project-plan` per architect plan-day decision authority.

| # | Question | Architect Decision | Justification | Codified In |
|---|---|---|---|---|
| Q1 | Distinguish "channel-without-auth" from "broken-auth" in Category 9? | **RESOLVED at PRD time (architect 2026-04-25)**: single category covers both | Indicator 2 ("does not declare mutual authentication") naturally encompasses both no-auth-declared and broken-auth-declared. Threat is the same (relying party accepts spoofed/tampered/replayed messages); mitigation is the same (implement strong mutual auth). Splitting would mirror F-2's pre-PRD scoping over-fragmentation | `detection-patterns.md` Pattern Category 9 single-category indicator set; ADR-032 Decision 1 supporting evidence |
| Q2 | Cosmetic dispatch-rules annotation `tool-abuse (MCP-03)` → `tool-abuse (MCP-03, ASI-07)` for parity? | **YES** (architect plan-day default per PRD architect leaning) | Adds Coverage Matrix traceability without modifying dispatch logic. Documentation-only, ~30-second edit. No functional dispatch change — F-3 zero-functional-orchestrator-touch claim preserved. | `dispatch-rules.md` line ~92 annotation update at Wave 1.1 |
| Q3 | Example regeneration target — `agentic-app` extension, `maestro-reference`, or new minimal multi-agent fixture? | **`agentic-app`** (PM default) with R1 fallback to `maestro-reference` or new fixture if Wave 3 structural inspection reveals insufficient inter-agent channel signal | Leverages existing F-1 + F-2 baseline; Feature 142 already extended `agentic-app` with `Inter-agent Communication Channel` component type — sufficient multi-agent topology by construction. Demonstrates cohesive Agentic-category rendering on a single regenerated example. | `examples/agentic-app/` extended + regenerated in Wave 3 |
| Q4 | Anti-indicator section for Categories 9 + 10? | **YES** (architect plan-day default per PRD architect leaning) | Formalizes the multi-agent / multi-MCP topology gate (FR-011) for grep-auditability. Single-agent → zero Category-9 findings; single-MCP → zero Category-10 findings — this is acceptance criteria, not aspirational. Anti-indicator section makes it testable. Mirrors F-2 MEDIUM-5 anti-indicator discipline. | `detection-patterns.md` Categories 9 + 10 each gain explicit anti-indicator subsection |
| Q5 | Build-day sequencing — Tuesday 2026-04-28 or compress to Monday 2026-04-27? | **RESOLVED at PRD time (team-lead 2026-04-25)**: Tuesday 2026-04-28 | Monday is plan day per established Tuesday-after-Monday-plan cadence (F-2 used same pattern). Compressing build into same day as plan would violate "plan complete before build starts" sequencing that F-1 and F-2 honored. | Wave structure starts 2026-04-28 Tuesday |

## Success Criteria Mapping

| Spec SC | Implementation Phase | Deliverable |
|---|---|---|
| SC-001 | Wave 1.1 | `tool-abuse.md` `owasp_references += [ASI-07]`; existing entries byte-identical (grep) |
| SC-002 | Wave 1.1 EOD | `wc -l .claude/agents/tachi/tool-abuse.md` returns ≤150 (expected 100-106) |
| SC-003 | Wave 1.1 + Wave 4 | `## Purpose` 1-3 line extension appended; pre-existing prose byte-identical (structural diff) |
| SC-004 | Wave 1.1 | Detection Workflow Step 5 references `+= [ASI-07, AML.T0060, CWE-287, CWE-345]`; existing entries byte-identical |
| SC-005 | Wave 2 | `detection-patterns.md` Categories 9 + 10 appended with ≥4 indicators each, ≥1 worked example each, named mitigations |
| SC-006 | Wave 2 EOD | Structural diff of pre/post `detection-patterns.md` returns empty for Categories 1-8 + `## Overview` + `## Targeted DFD Element Types` + `## Trigger Keywords` |
| SC-007 | Wave 2 | `## Primary Sources` extended with ASI07 + AML.T0060; existing entries byte-identical |
| SC-008 | Wave 1.1 + Wave 4 | ADR-032 Proposed at Wave 1.1; Accepted at Wave 4 with all 6-7 required Decisions and cross-references |
| SC-009 | Wave 3 | Regenerated multi-agent example emits ≥1 new Category-9/10 `AG-{N}` finding; non-qualifying baselines emit 0 (topology gate enforces FR-011) |
| SC-010 | Wave 3 | `test_backward_compatibility.py` passes on 5 non-multi-agent baselines under `SOURCE_DATE_EPOCH=1700000000` |
| SC-011 | Wave 3 | Multi-agent example regeneration produces Category-9/10 finding(s) with concrete inter-agent / MCP-trust mitigations + OWASP ASI07:2026 citation |
| SC-012 | All waves | Empty diff on dependency manifest files (verified at PR pre-merge) |
| SC-013 | All waves | Grep audit at PR pre-merge confirms zero edits to 24 detection-tier files (12 other agents + 12 other companions) |
| SC-014 | All waves | `schemas/finding.yaml` `schema_version` remains `"1.7"`; `id.pattern` regex unchanged (verified at PR pre-merge) |
| SC-015 | Wave 3 + Wave 4 | F-A2 `validate_source_attribution` returns no errors on Category-9/10 findings; fixture tests confirm |
| SC-016 | Wave 1.1 + Wave 2 | `grep -i maestro` on `tool-abuse.md` + `detection-patterns.md` returns empty |
| SC-017 | All waves | `orchestrator.md` + `dispatch-rules.md` show zero functional diff (Q2 cosmetic annotation is documentation-only if applied) |
| SC-018 | Wave 4 | BLP-01 Coverage Matrix updated: ASI07:2026 Planned → Covered with F-3 named as closure feature |
| SC-019 | Wave 3 | Cohesive Agentic-category rendering: Categories 1-10 `AG-{N}` findings adjacent in `category: agentic` section without artificial fragmentation |
| SC-020 | Wave 4 | PR title `feat(219): ...`; pre-merge re-verification at `/aod.deliver`; post-merge release-please PR opens within ~30s (or recovery via empty release-marker commit per F-212 precedent) |
| SC-021 | Wave 4 | `delivery.md` filed same-day-as-delivery (if ≥1 hour residual capacity) or on Buffer Day 1 (2026-04-29 Wed) capturing Heuristic A enrichment first-execution lessons |

## PR Pre-Merge Checklist

- [ ] All Wave 1-3 structural validations green (line count ≤150 on `tool-abuse.md`, MANDATORY count = 1, MAESTRO grep empty on both files)
- [ ] Categories 1-8 byte-identity grep audit returns empty diff for unchanged regions in `detection-patterns.md`
- [ ] 24-file zero-edit grep audit returns empty for 12 other threat-agent files + 12 other companion `detection-patterns.md` files
- [ ] Infrastructure-tier consumer files (risk-scorer, control-analyzer, threat-report, threat-infographic, report-assembler) show zero diff
- [ ] `orchestrator.md` shows zero diff; `finding-format-shared.md` shows zero diff
- [ ] `schemas/finding.yaml` shows zero diff (no schema bump)
- [ ] `dispatch-rules.md` shows zero functional diff (cosmetic annotation if applied is single-token, contingent on Q2)
- [ ] `test_backward_compatibility.py` passes on 5 non-multi-agent baselines
- [ ] `test_tool_abuse_enrichment.py` passes (structural-diff + line-count + MAESTRO grep + Category-9/10 source_attribution fixtures)
- [ ] Multi-agent example regeneration commits present including `security-report.pdf.baseline`
- [ ] At least 1 new Category-9/10 `AG-{N}` finding emitted on regenerated multi-agent example with valid `source_attribution` + grounded mitigation
- [ ] ADR-032 transitioned Proposed → Accepted with Revision History entry; cross-references to ADR-021/023/027/028/030/031 present; zero MAESTRO references in ADR Decision sections
- [ ] Pattern Category Disambiguation subsection present in `detection-patterns.md` per PRD FR-2 / ADR-032 Decision 7
- [ ] Anti-indicator subsections present in Categories 9 + 10 per Q4 architect plan-day decision
- [ ] PR title is `feat(219): ...` Conventional Commits format
- [ ] Dependency manifest diff is empty (pyproject.toml, requirements*.txt, package.json)
- [ ] Cohesive Agentic-category rendering verified on regenerated example (Categories 1-10 `AG-{N}` findings adjacent in `category: agentic` section)
- [ ] Triple sign-off in tasks.md frontmatter (PM + Architect + Team-Lead) — enforced in `/aod.tasks`

## References

- PRD: [219-asi07-tool-abuse-enrichment-2026-04-25.md](../../docs/product/02_PRD/219-asi07-tool-abuse-enrichment-2026-04-25.md)
- Spec: [spec.md](./spec.md)
- Research: [research.md](./research.md)
- Feature 082 precedent: [082-threat-agent-skill-references](../082-threat-agent-skill/)
- Feature 142 precedent (multi-agent component types: `Inter-agent Communication Channel`): [142-maestro-phase-2](../142-maestro-phase-2/)
- Feature 201 F-1 precedent (first net-new AI-tier agent under ADR-023; new-agent branch of Heuristic A): [201-output-integrity-threat-agent](../201-output-integrity-threat-agent/)
- Feature 206 F-2 precedent (second net-new AI-tier agent; new-agent branch second-execution validation): [206-misinformation-threat-agent](../206-misinformation-threat-agent/)
- ADR-021 (SOURCE_DATE_EPOCH determinism): `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`
- ADR-023 (Lean-agent + additive-only shared-reference Decision 3): `docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`
- ADR-027 (Taxonomy crosswalk schema): `docs/architecture/02_ADRs/ADR-027-taxonomy-crosswalk-schema.md`
- ADR-028 (Source attribution schema extension): `docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`
- ADR-030 (F-1 output-integrity agent, Decision 1 signal-class taxonomy in LLM tier — F-3 cross-references as different application of same rule): `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
- ADR-031 (F-2 misinformation agent, Decision 8 regex-alternation minor-bump rule — F-3 cross-references as the asymmetry; F-3 does NOT invoke this rule): `docs/architecture/02_ADRs/ADR-031-misinformation-agent.md`
