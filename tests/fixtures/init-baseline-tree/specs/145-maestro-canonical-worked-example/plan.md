---
triad:
  pm_signoff:
    agent: product-manager
    date: 2026-04-16
    status: APPROVED_WITH_CONCERNS
    notes: "Plan is product-aligned, correctly scoped to content-authoring, correctly resolves 3 Wave 0 gates per PRD guidance, fully covers 18 FRs / 6 user stories / 14 SCs, preserves all backward-compat invariants, treats all 6 PRD risks with appropriate mitigation. Phase 1 component design (18 components pre-verified against checklist conditions) is an outstanding product-side risk mitigation. 3 non-blocking concerns for /aod.tasks generation: (1) itemize 4 security-analyst review criteria in Wave 4 acceptance (Risk 145.5 rigor); (2) itemize PM Wave 4 tone-review criteria (Risk 145.4 rigor); (3) PRD FR to spec FR to wave traceability table in /aod.analyze at Wave 6. None warrant CHANGES_REQUESTED. Full details: .aod/results/product-manager.md"
  architect_signoff:
    agent: architect
    date: 2026-04-16
    status: APPROVED_WITH_CONCERNS
    notes: "Plan technically sound and well-structured. All 3 Wave 0 gates resolved with defensible reasoning. Phase 1 component architecture pre-designed to satisfy Pre-Execution Architecture Review Checklist. Backward compatibility, determinism, and zero-edit invariants all preserved. ADR cross-references complete (020/021/022/023/024/025/026). Constitution Check all 11 principles appropriately evaluated. Complexity Tracking correctly empty. Wave structure 4.5-day critical path vs 4-8d PRD budget well-calibrated with 2-round iteration cap + fallback ranking. 3 non-blocking keyword-hygiene concerns for Wave 1 authoring (now annotated in plan Components section): C1 MEDIUM 'Registry' substring L4/L5 collision on Outcomes Tracking component; C2 MEDIUM bare 'Agent' is not L3 keyword (Diagnostic Agent description must contain executor/planner/tool dispatch); C3 LOW bare 'Model' is not L1 keyword (Risk Stratification Model description must contain fine-tuned model etc). All mitigable via Wave 3 fallback (a) keyword-tune but catching in Wave 1 saves iteration round. Recommendation: flag C1/C2/C3 into tasks.md Wave 1 acceptance checklist."
  techlead_signoff: null
---

# Implementation Plan: Canonical MAESTRO Worked Example

**Branch**: `145-maestro-canonical-worked-example` | **Date**: 2026-04-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/145-maestro-canonical-worked-example/spec.md`

## Summary

Ship a purpose-built canonical MAESTRO worked example under `examples/maestro-reference/` — a multi-agent **Healthcare Clinical Decision Support System (CDSS)** reference architecture covering all seven MAESTRO layers with at least one cross-layer attack chain and at least three of the six canonical agentic patterns surfaced end-to-end by the existing tachi pipeline. Content-authoring only: zero code changes, zero schema changes, zero agent changes, zero new runtime dependencies.

**Technical approach**:
1. Hand-author `architecture.md` (Mermaid `flowchart TD`) with 14+ components organized into seven MAESTRO-layered subgraphs, with explicit inter-agent data flows, a persistent-state component (long-running learning loop), and emergent-behavior descriptions — all pre-qualified by the 4-condition FR-005 Pre-Execution Architecture Review Checklist before first pipeline invocation.
2. Run the existing pipeline (`/tachi.architecture` → `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report`) and commit all generated outputs flat under `examples/maestro-reference/`.
3. Hand-author adopter-facing `README.md` with 7 required sections (FR-003); PM reviews for neutral tone; security-analyst reviews the disclaimer prose (DoD gate per FR-017 since Option A Healthcare is selected).
4. Add `"maestro-reference"` to `BASELINE_EXAMPLES` in `tests/scripts/test_backward_compatibility.py` as the 6th baseline; update `examples/README.md` with a canonical-MAESTRO first-read callout.
5. Inject Feature 120 v1.0 frontmatter into `architecture.md` **after** architecture is frozen (Path B per FR-012) via `/tachi.architecture` in "create" mode.

## Technical Context

**Language/Version**: Markdown with Mermaid (`flowchart TD`) for architecture input; no source-language compilation. Pipeline scripts are Python 3.11 (stdlib-only) but NOT modified by this feature.
**Primary Dependencies** (all DELIVERED / PRESENT — no new dependencies added by this feature):
- **Pipeline commands**: `/tachi.architecture`, `/tachi.threat-model`, `/tachi.risk-score`, `/tachi.compensating-controls`, `/tachi.infographic`, `/tachi.security-report` (Feature 121 namespace, all DELIVERED)
- **MAESTRO capabilities**: Features 084 (Phase 1 layer tagging), 136 (canonical layer names), 141 (Phase 2 cross-layer chains), 142 (Phase 3 agentic patterns), 143/144 (Phase 4/5 compliance posture ADRs) — all DELIVERED
- **External CLI prerequisites**: `@mermaid-js/mermaid-cli` (mmdc — hard prerequisite per ADR-022 when attack trees present); Typst compiler (PDF); Gemini API (infographic JPEG generation — one-time during authoring)
- **Test harness**: pytest + `tests/scripts/test_backward_compatibility.py` (existing, developer-only; not wired to any CI workflow — see Constitution Check below)
**Storage**: Filesystem only — `examples/maestro-reference/` directory on the feature branch. No database, no cloud storage.
**Testing**:
- Local-only pytest: `pytest tests/scripts/test_backward_compatibility.py -k "maestro-reference"` verifies byte-identity of the new PDF baseline under `SOURCE_DATE_EPOCH=1700000000`
- Static review of `architecture.md` against the FR-005 Pre-Execution Architecture Review Checklist (4 conditions) before first pipeline invocation
- `/aod.analyze` cross-artifact consistency check after all artifacts committed
**Target Platform**: tachi repository (adopter-facing artifact). Artifacts are read by adopters via GitHub, so Markdown + PDF + JPEG rendering must be GitHub-compatible (already guaranteed by existing examples).
**Project Type**: Content-authoring (no source code, no backend, no frontend). Directory structure decision is Option Y (flat) — see Structure Decision below.
**Performance Goals**:
- Pipeline run against the new example completes within the time envelope of the existing `agentic-app` example run (existing production fixture)
- PDF generation time remains within the existing budget
- No ongoing runtime perf requirement (example is static content, not a service)
**Constraints**:
- **Byte-deterministic PDF baseline**: `security-report.pdf.baseline` MUST regenerate byte-identical under `SOURCE_DATE_EPOCH=1700000000` (ADR-021)
- **Backward compatibility invariant**: The 5 existing non-multi-agent baselines AND `agentic-app` MUST remain unchanged (FR-013, FR-014)
- **mmdc hard prerequisite**: Local developer environment MUST have `@mermaid-js/mermaid-cli` installed (ADR-022); CI environment does NOT need mmdc because no CI workflow runs `test_backward_compatibility.py` (confirmed — see Constitution Check)
- **Zero new runtime dependencies**: no changes to `requirements*.txt`, `pyproject.toml`, or `package.json`
- **Zero-edit invariant on the 11 detection agents**: Feature 082 / ADR-026 — this feature must not modify any detection-tier agent file
**Scale/Scope**:
- 1 new example directory with ~20 artifact files
- 1 Mermaid architecture diagram with 14+ components across 7 MAESTRO layers
- 1 hand-authored README (~1,500-2,500 words across 7 required sections)
- ~1-3 lines modified in `tests/scripts/test_backward_compatibility.py` (add to `BASELINE_EXAMPLES`)
- ~5-15 lines modified in `examples/README.md` (new row + first-read callout)
- Effort estimate: 4-8 days (per PRD team-lead review)

## Wave 0 Gate Resolutions

The PRD defers three operational decisions to `/aod.plan` Wave 0. All three are resolved here before Phase 0 research.

### WG-1: Domain Selection — **Option A (Healthcare Clinical Decision Support)** ✅ LOCKED

**Decision**: Option A — Multi-agent Healthcare Clinical Decision Support System.

**Rationale**:
1. **Strongest agentic pattern preconditions** per research.md: Supervisor↔specialist coordination satisfies R-01 (Agent Collusion); long-running outcomes-tracking + physician-override registry satisfies R-02 (Temporal Attack); cascading clinical recommendations satisfy R-03 (Emergent Behavior).
2. **Richest per-layer coverage**: Composed reference architecture (from arxiv 2504.03699 + arxiv 2506.13800 + AWS Bedrock AgentCore Healthcare) covers all 7 layers with ≥2 components each — no layer feels shoehorned.
3. **Most dramatic cross-layer chain narrative**: L2 guideline corpus poisoning → L3 Treatment Planner hijack → L5 audit log tampering → L6 policy bypass → L7 false clinical recommendation — comparable in shape to the CSA canonical financial-trading "Execution Hijack" without thematic overlap.
4. **Non-financial (FR-015)**: Avoids appearing derivative of the CSA canonical example.
5. **Regulatory surface (HIPAA, RBAC) makes L6 sharp**: Option B (research) and Option C (supply-chain) have weaker L6 compliance framing.

**Content-risk mitigation**: Per architect M2 + FR-017, security-analyst reviews the README disclaimer prose for content-risk framing. Domain naming uses abstract references ("Patient Record" not specific patient names; no medical specialty claiming clinical accuracy; disclaimer prominently in README and in `architecture.md` header comment).

**Fallback protocol**: If first-round PM or Architect review surfaces a domain-level concern, fallback ranking is A → B → C per PRD. Domain is locked after Wave 0 — changing it after architecture drafting begins is explicitly out of scope.

### WG-2: Directory Structure — **Option Y (flat at top-level)** ✅ LOCKED

**Decision**: Option Y — commit all ~20 artifacts flat under `examples/maestro-reference/`.

**Rationale**:
1. **Matches 5-of-6 existing convention** (research.md Finding 1): `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice` all use flat structure. Only `agentic-app` uses `sample-report/` subdirectory, and that is a historical variant, not a repository-wide convention.
2. **Adopter-navigation clarity**: First-read navigation from `examples/README.md` → `examples/maestro-reference/README.md` → pipeline outputs is shorter with flat layout; no mental hop through `sample-report/`.
3. **Establishes canonical structure for future rich-artifact examples**: `agentic-app` retains its `sample-report/` variant for historical compatibility (per PRD Regime B); the canonical MAESTRO example sets the forward convention.
4. **Simpler regression fixture path**: `BASELINE_EXAMPLES` entries are directory names, not nested paths — flat alignment keeps the fixture list uniform.

**Structural DoD enforcement** (team-lead L4): Pipeline output MUST land in the chosen location — no accidental mixed structure. The tasks.md acceptance checklist will verify no stray `sample-report/` subdirectory exists under `examples/maestro-reference/` at commit time.

### WG-3: mmdc CI Availability for FR-011 — **N/A (no CI runs backward-compat)** ✅ RESOLVED

**Finding**: Audit of `.github/workflows/` confirms **no CI workflow runs `tests/scripts/test_backward_compatibility.py`**. The only tachi CI workflow is `tachi-mmdc-preflight.yml`, which asserts mmdc **absence** (negative test for the Feature 130 preflight gate). `release-please.yml` is unrelated (tagging and CHANGELOG).

**Implication**: The PRD Constraint M3 ("CI environment running `test_backward_compatibility.py` MUST have mmdc available") is **vacuously satisfied** — the backward-compatibility suite is developer-local only. Local developers are already required to have mmdc installed per ADR-022 (documented in `README.md` Prerequisites section and `scripts/install.sh`).

**Decision**: FR-011 (add `"maestro-reference"` to `BASELINE_EXAMPLES`) lands in this feature without deferral. **SC-013 becomes unconditional (no longer deferred)**.

**Risk 145.3 contingency (byte-identity failure) remains live**: If the PDF baseline regeneration is non-byte-identical, baseline integration is deferred to a follow-up PR. The canonical example still ships as adopter-facing artifact without the `BASELINE_EXAMPLES` entry in that scenario. Tasks.md will sequence the baseline commit after byte-identity is proven.

**Follow-up note (out-of-scope for this feature)**: If tachi later adds a CI job that runs `test_backward_compatibility.py`, that job MUST provision mmdc because the Healthcare CDSS will produce Critical/High findings → attack trees → mmdc-invoked rendering. This is a maintainer note for the future CI evolution, tracked separately from Feature 145.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Principles from `.aod/memory/constitution.md` evaluated against this feature:

| Principle | Applicability | Evaluation |
|-----------|---------------|------------|
| I. General-Purpose Architecture | Not applicable — this feature adds content, not core API behavior. No domain-specific logic is added to any tachi component; the Healthcare domain is encoded in `architecture.md` content only, which is domain-agnostic from the pipeline's perspective. | ✅ Pass |
| II. API-First Design | Not applicable — no API changes. Example artifacts are file-based outputs of existing commands. | ✅ Pass |
| III. Backward Compatibility (NON-NEGOTIABLE) | **Strongly applicable**. FR-013 (5 existing baselines byte-identical) + FR-014 (agentic-app unchanged) + zero-edit invariant on 11 detection agents (Feature 082 / ADR-026) all enforce backward compat. | ✅ Pass |
| IV. Concurrency & Data Integrity | Not applicable — no state transitions, no locking, no database transactions. | ✅ N/A |
| V. Privacy & Data Isolation | Partially applicable — FR-016 requires a "not a real system" disclaimer in the README; FR-017 requires security-analyst review of the disclaimer since Option A Healthcare is chosen; no real PHI / patient data in any artifact (uses abstract "Patient Record" references only). | ✅ Pass (mitigations in place) |
| VI. Testing Excellence | Partially applicable — the feature adds a pytest fixture entry (`BASELINE_EXAMPLES`) but no new test framework. Byte-identity test coverage guards regressions. `/aod.analyze` cross-artifact consistency replaces integration-test coverage for a content-authoring feature. | ✅ Pass (byte-identity + /aod.analyze) |
| VII. Definition of Done (NON-NEGOTIABLE) | Applicable — spec.md FR-018 + DoD checklist (carried forward from PRD) enforce 3-step validation. Feature is documentation/content; "Pushed to Production" is interpreted as "merged to main"; "Tested" is byte-identity + `/aod.analyze`; "User Validated" is PM + Architect sign-off + deliver-stage adopter validation. | ✅ Pass |
| VIII. Observability & Root Cause Analysis | Applicable for the design loop — the Pre-Execution Architecture Review Checklist (FR-005) is a design-time observability mechanism that converts reactive iteration into static pre-flight validation (rooted in 5-whys applied to PRD Risk 145.1). | ✅ Pass |
| IX. Git Workflow & Feature Branching (NON-NEGOTIABLE) | Applicable. Feature branch `145-maestro-canonical-worked-example` in use; PR required for review; conventional commits. | ✅ Pass |
| X. Product-Spec Alignment & Architecture Review (NON-NEGOTIABLE) | Applicable. PM sign-off on spec complete (APPROVED_WITH_CONCERNS); PM + Architect dual sign-off required on this plan.md; triple sign-off on tasks.md. | ✅ Pass (dual sign-off pending this plan review) |
| XI. SDLC Triad Collaboration | Applicable. PRD carries approved Triad sign-offs; Wave 0 gates (domain, structure, mmdc CI) are the Triad-led checkpoints resolved in this plan. | ✅ Pass |

**Governance Tier**: Standard (default; constitution v1.0.0 does not override). Plan gates = spec PM sign-off + plan PM+Architect dual sign-off + tasks triple sign-off. All gates in scope.

**Constitution gate verdict**: ✅ PASS. No violations. No Complexity Tracking entries required.

## Phase 0: Research

**Research artifact**: `specs/145-maestro-canonical-worked-example/research.md` (already generated during `/aod.spec`).

**Research topics resolved** (full findings in research.md):

1. **Examples directory conventions** — flat structure is canonical (5-of-6); `agentic-app/sample-report/` is the single exception
2. **MAESTRO detection patterns** — layer classification keyword tables, multi-agent gate predicate, agentic pattern rules R-01 through R-06
3. **CSA canonical MAESTRO walkthrough shape** — 7-layer diagram + layer-populated table + single cross-layer attack narrative + per-layer threat-category mapping; Snyk Labs is the authoritative Tier-1 source
4. **Candidate domain analysis** — Option A Healthcare recommended (strongest preconditions, richest layer coverage, dramatic attack narrative, regulatory surface); Options B (Research) and C (Supply-Chain) ranked fallback
5. **Composed Healthcare CDSS reference architecture** — L1-L7 component mapping derived from arxiv 2504.03699 (6-agent decomposition) + arxiv 2506.13800 (MCP-FHIR) + AWS Bedrock AgentCore Healthcare (observability + security stack)
6. **Feature 120 workflow Path B** — hand-author body first, inject frontmatter + checksum last via `/tachi.architecture` "create" mode
7. **mmdc CI availability** — confirmed N/A (no CI runs backward-compat suite); FR-011 unblocked

**Deliverable**: [research.md](research.md) — consolidated findings with file paths, line numbers, and source citations.

## Phase 1: Design & Contracts

**Prerequisites**: Phase 0 research complete (research.md exists).

This feature does not produce conventional code contracts (no API endpoints, no data models, no service boundaries). Its "contracts" are content-format contracts anchored to existing delivered features. The design artifacts below capture those contracts explicitly.

### Components (MAESTRO 7-Layer Coverage)

The `architecture.md` will contain the following 14 components organized by MAESTRO layer. Each layer has ≥2 components (FR-004); each component carries dispatch-trigger keywords per `.claude/skills/tachi-orchestration/references/dispatch-rules.md` to guide orchestrator Phase 1 classification.

| Layer | Component | DFD Type | Dispatch Triggers | Pattern Precondition Role |
|-------|-----------|----------|-------------------|---------------------------|
| **L1 Foundation Models** | Clinical LLM | Process | LLM, model, language model | — |
| **L1 Foundation Models** | Risk Stratification Model | Process | model | — |
| **L2 Data Operations** | FHIR Resource Store | Data Store | database, FHIR, vector | — |
| **L2 Data Operations** | Clinical Guideline RAG Corpus | Data Store | vector, RAG, embedding, corpus | Chain starting-point (poisoning) |
| **L2 Data Operations** | Medical Literature Vector Index | Data Store | vector, embedding | — |
| **L3 Agent Frameworks** | Supervisor Orchestrator | Process | orchestrator, agent, supervisor | R-01 (inter-agent hub); R-03 (emergent behavior) |
| **L3 Agent Frameworks** | Diagnostic Agent | Process | agent, autonomous | R-01 (specialist #1) |
| **L3 Agent Frameworks** | Treatment Planner Agent | Process | agent, autonomous | R-01 (specialist #2); chain middle |
| **L3 Agent Frameworks** | Clinical MCP Tool Server | Process | MCP server, tool server | — |
| **L4 Deployment and Infrastructure** | Model Inference Gateway | Process | API gateway, container | — |
| **L4 Deployment and Infrastructure** | EHR Ingestion Queue | Data Store | queue | — |
| **L5 Evaluation and Observability** | Clinical Audit Log | Data Store | audit log, log, telemetry | Chain middle (tampering target) |
| **L5 Evaluation and Observability** | Outcomes Tracking & Physician Override Registry | Data Store | monitoring, tracing, long-running learning loop | **R-02 (persistent state)** — carries "learning loop" + "drift" + "re-training" keywords |
| **L6 Security and Compliance** | HIPAA RBAC + Policy Engine | Process | auth, RBAC, access control, firewall, guardrail | Chain middle (policy bypass) |
| **L6 Security and Compliance** | Consent & De-identification Guardrail | Process | encryption, guardrail, security | — |
| **L7 Agent Ecosystem** | Inter-Agent Communication Channel | Data Flow + Process | agent-to-agent, shared channel, multi-agent | **R-01 carrier** (explicit channel); R-05 (Communication Vulnerability) |
| **L7 Agent Ecosystem** | Physician Clinical Portal | External Entity + Process | user portal, frontend, web interface | Chain terminal (false clinical recommendation) |
| **L7 Agent Ecosystem** | Patient Summary Generator | Process | API endpoint | — |

Note: 18 components listed (≥14 required per FR-004). Cross-layer chain-participating components are explicitly noted — this architecture is designed to surface the intended chain without iteration.

**Keyword-hygiene items for Wave 1 authoring** (from architect review C1/C2/C3 — `tasks.md` Wave 1 acceptance checklist MUST verify):
- **C1 (L4/L5 collision on "registry")**: "Outcomes Tracking & Physician Override Registry" — the bare substring "registry" matches L4 keyword evaluated before L5. Wave 1 MUST rename to an L5-aligned noun (e.g., "Outcomes Telemetry & Physician Override Audit Store") OR structure the description so L5 keywords (`monitoring`, `tracing`, `telemetry`, `audit log`) appear prominently and the name does not bypass to L4.
- **C2 (L3 classification on bare "Agent")**: Bare "agent" is NOT an L3 keyword. "Diagnostic Agent" description MUST contain an L3 phrase keyword (`executor`, `planner`, `tool dispatch`, `orchestrator`) to land at L3. "Treatment Planner Agent" safely matches L3 via "planner" — no change needed there. Supervisor Orchestrator safely matches L3 via "orchestrator".
- **C3 (L1 classification on bare "Model")**: Bare "model" is NOT an L1 keyword. "Risk Stratification Model" description MUST contain an L1 phrase (`fine-tuned model`, `foundation model`, `base model`, `model weights`, `language model`, `inference engine`) to land at L1. Dispatch (AG/LLM) works via bare "model" keyword — this is a layer-classification concern only.

Failing to handle C1/C2/C3 in Wave 1 triggers Wave 3 fallback (a) keyword-tune on first pipeline invocation. Catching in Wave 1 saves one iteration round.

### Data Flow (Pre-Execution Checklist Evidence)

Key inter-agent data flows in `architecture.md` that satisfy FR-005 checklist conditions:

1. **Supervisor Orchestrator ↔ Diagnostic Agent** (inter-agent, both L3, both `agentic`/`llm` dispatch) — **satisfies R-01 precondition** (inter-agent data flow between two agentic components)
2. **Supervisor Orchestrator ↔ Treatment Planner Agent** (inter-agent, both L3, both `agentic`/`llm` dispatch) — reinforces R-01
3. **Diagnostic Agent ↔ Treatment Planner Agent via Inter-Agent Communication Channel** (L7 carrier) — **satisfies R-05 precondition** and enriches R-01 topology
4. **Outcomes Tracking & Physician Override Registry** (L5) has `learning loop` + `re-training` keywords in its description — **satisfies R-02 precondition** (persistent-state component)
5. **Supervisor Orchestrator description** contains `cascade` + `emergent` keywords in the context of delegating across specialist agents — **satisfies R-03 precondition** (multi-agent topology + emergent-behavior keywords)
6. **Architecture header** contains explicit `multi-agent`, `supervisor`, `delegation` keywords — **satisfies multi-agent gate predicate condition (c)**, and ≥2 `agentic`/`llm` components satisfies condition (a) independently.

**Pre-Execution Checklist static review** (FR-005 / SC-011):
- [x] Multi-agent gate predicate TRUE (conditions a + b + c all TRUE)
- [x] R-01 precondition satisfied (Supervisor↔Diagnostic flow; Supervisor↔Treatment Planner flow)
- [x] R-02 precondition satisfied (Outcomes Tracking & Physician Override Registry with "learning loop" / "re-training" / "drift" keywords)
- [x] R-03 precondition satisfied (multi-agent topology via Supervisor delegation; "cascade" / "emergent" keywords in Supervisor description)

All 4 green by design in the plan — the architecture in tasks.md Wave 1 MUST preserve these keywords or the static review fails.

### Tech Stack

No new technologies. Tech Stack is the existing pipeline:
- Mermaid (`flowchart TD`) for architecture input
- Existing `/tachi.*` commands and their underlying Python 3.11 (stdlib-only) scripts
- `@mermaid-js/mermaid-cli` (mmdc) for attack tree rendering — ADR-022 hard prerequisite
- Typst for PDF composition
- Gemini API for infographic JPEG rendering (one-time during authoring)
- pytest for byte-identity regression check (developer-local only)

### Contracts

No new API contracts, database schemas, or service interfaces. Content contracts consumed by this feature (all pre-existing):

| Contract | File | Role in this feature |
|----------|------|----------------------|
| Architecture input format (Mermaid + Component Summary) | [examples/mermaid-agentic-app/input.md](../../examples/mermaid-agentic-app/input.md), [examples/agentic-app/architecture.md](../../examples/agentic-app/architecture.md) | Template conventions the new `architecture.md` must follow |
| MAESTRO layer classification rules | [.claude/skills/tachi-shared/references/maestro-layers-shared.md](../../.claude/skills/tachi-shared/references/maestro-layers-shared.md) | Drives component naming to hit intended layer classifications |
| Agentic pattern rule table (R-01 through R-06) | [.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md](../../.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md) | Drives Pre-Execution Checklist satisfaction |
| Cross-layer chain transition table | [.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md](../../.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md) | Drives architecture design to surface ≥1 chain spanning ≥3 layers |
| Finding schema v1.4 (agentic_pattern field) | [schemas/finding.yaml](../../schemas/finding.yaml) | Pipeline consumes unchanged; feature does NOT modify |
| PDF determinism convention | [docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) | Governs baseline regeneration and byte-identity check |
| Architecture version-tracking frontmatter | [docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md) + Feature 120 PRD | Format of v1.0 frontmatter injected by `/tachi.architecture` create mode |

### Quickstart (Developer Walkthrough)

Path a developer follows to regenerate the example from scratch (captured as `quickstart.md` for this feature):

```bash
# Prerequisite: @mermaid-js/mermaid-cli installed (ADR-022)
npm install -g @mermaid-js/mermaid-cli

# 1. Generate pipeline outputs from authored architecture.md
cd examples/maestro-reference
# Commands (from tachi CLI / Claude Code):
#   /tachi.threat-model (reads architecture.md → writes threats.md, threats.sarif,
#                        threat-report.md, attack-chains.md if chains surface, attack-trees/)
#   /tachi.risk-score   (writes risk-scores.md, risk-scores.sarif)
#   /tachi.compensating-controls (writes compensating-controls.md + sarif)
#   /tachi.infographic all (writes 6 infographic JPEGs + spec files)
#   /tachi.security-report (writes security-report.pdf and baseline)

# 2. Regenerate deterministic baseline for regression fixture
cd /path/to/tachi
SOURCE_DATE_EPOCH=1700000000 \
  python scripts/extract-report-data.py \
    --target-dir examples/maestro-reference \
    --output templates/tachi/security-report/report-data.typ \
    --template-dir templates/tachi/security-report
SOURCE_DATE_EPOCH=1700000000 \
  typst compile \
    templates/tachi/security-report/main.typ \
    examples/maestro-reference/security-report.pdf.baseline \
    --root .

# 3. Verify byte-identity regression
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py \
  -k "maestro-reference"

# 4. Cross-artifact consistency check
/aod.analyze  # MUST pass with no inconsistencies
```

### Agent Context

This feature does not modify any `.claude/agents/**` file — the zero-edit invariant on the 11 detection agents (Feature 082 / ADR-026 Decision 1) is preserved. The only `.claude/` content touched by this feature is the task manifest (`specs/145-*/tasks.md`), which is spec-adjacent, not agent-adjacent.

### Design Artifacts Summary

- **research.md** (generated during `/aod.spec`): consolidated research findings with source citations.
- **quickstart.md** (generated in Phase 1 — see Quickstart section above, persisted as `specs/145-*/quickstart.md`): developer walkthrough for regenerating the example.
- **data-model.md**: Not applicable — this feature adds no new entities or schemas. Spec.md's Key Entities section describes the artifact types (all pre-existing) and serves as the equivalent reference.
- **contracts/**: Not applicable — no new API/service contracts. Content contracts table above enumerates the pre-existing contracts consumed.

## Project Structure

### Documentation (this feature)

```
specs/145-maestro-canonical-worked-example/
├── spec.md              # Feature specification (approved by PM)
├── plan.md              # This file (/aod.project-plan output)
├── research.md          # Research phase output
├── quickstart.md        # Developer walkthrough for regenerating the example
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/aod.tasks output)
```

### Repository Changes (content-authoring only)

```
# NEW directory (flat — Option Y per WG-2)
examples/maestro-reference/
├── architecture.md                    # Mermaid + Component Summary + Feature 120 v1.0 frontmatter
├── README.md                          # Adopter-facing tour (7 sections per FR-003)
├── threats.md                         # Generated — MAESTRO Pattern column populated
├── threats.sarif                      # Generated
├── threat-report.md                   # Generated — MAESTRO Findings + Cross-Layer Chains + Agentic Pattern Analysis
├── risk-scores.md                     # Generated
├── risk-scores.sarif                  # Generated
├── compensating-controls.md           # Generated
├── compensating-controls.sarif        # Generated
├── attack-chains.md                   # Generated (conditional on chain surfacing)
├── attack-trees/
│   ├── <finding-id-1>-attack-tree.md  # Generated — one per Critical/High finding
│   ├── <finding-id-2>-attack-tree.md
│   └── .manifest.json                 # Generated — sub-agent manifest
├── threat-baseball-card.jpg           # Generated (Gemini)
├── threat-baseball-card.md            # Generated (spec)
├── threat-system-architecture.jpg     # Generated (Gemini)
├── threat-system-architecture.md      # Generated (spec)
├── threat-executive-architecture.jpg  # Generated (Gemini)
├── threat-executive-architecture.md   # Generated (spec)
├── threat-risk-funnel.jpg             # Generated (Gemini)
├── threat-risk-funnel.md              # Generated (spec)
├── threat-maestro-stack.jpg           # Generated (Gemini)
├── threat-maestro-stack.md            # Generated (spec)
├── threat-maestro-heatmap.jpg         # Generated (Gemini)
├── threat-maestro-heatmap.md          # Generated (spec)
├── security-report.pdf                # Generated (Typst)
└── security-report.pdf.baseline       # Deterministic (SOURCE_DATE_EPOCH=1700000000)

# MODIFIED files (surgical edits)
examples/README.md                     # + new row in Standardized Examples; + first-read callout
tests/scripts/test_backward_compatibility.py  # + "maestro-reference" in BASELINE_EXAMPLES list

# UNCHANGED (backward-compat invariant)
examples/web-app/                      # byte-identical baseline preserved
examples/microservices/                # byte-identical baseline preserved
examples/ascii-web-api/                # byte-identical baseline preserved
examples/mermaid-agentic-app/          # byte-identical baseline preserved
examples/free-text-microservice/       # byte-identical baseline preserved
examples/agentic-app/                  # unchanged (Regime B)
.claude/agents/tachi/**.md             # zero-edit invariant (Feature 082 / ADR-026)
schemas/**.yaml                        # no changes
scripts/**.py                          # no changes
templates/tachi/**.typ                 # no changes
requirements*.txt, pyproject.toml      # no dependency changes
```

**Structure Decision**: Content-authoring only. One new directory `examples/maestro-reference/` (Option Y flat) populated with hand-authored input and pipeline-generated outputs. Two existing files modified surgically: `examples/README.md` (add row + first-read callout) and `tests/scripts/test_backward_compatibility.py` (add to `BASELINE_EXAMPLES`). Zero source-code directories modified.

## Phase 2+: Task Breakdown and Execution Plan

Detailed task breakdown will be generated by `/aod.tasks` into `tasks.md`. This plan specifies the wave structure that `/aod.tasks` will codify.

### Wave Structure (recommended to tasks.md)

Proposed wave layout matching PRD team-lead review's 4-8 day timeline with architecture-iteration contingency absorbed:

| Wave | Duration | Activities | Gate |
|------|----------|-----------|------|
| **Wave 0 — Governance** | ≤2h, EOD Day 1 hard stop | Confirm WG-1 (domain=A), WG-2 (structure=Y), WG-3 (mmdc CI=N/A) are held in plan.md; no new Wave 0 decisions surfaced | Architect + Team-Lead + PM concurrence verification (implicit — this plan's dual sign-off) |
| **Wave 1 — Architecture authoring** | ~1-1.5 days | Hand-author `architecture.md` body (Mermaid + Component Summary table + header comment w/ disclaimer); NO frontmatter yet (Path B per FR-012) | Static review against FR-005 Pre-Execution Checklist (4 conditions green) |
| **Wave 2 — Pipeline run + output commit** | ~1 day | Run full pipeline (`/tachi.architecture` validation → `/tachi.threat-model` → `/tachi.risk-score` → `/tachi.compensating-controls` → `/tachi.infographic all` → `/tachi.security-report`); review outputs against FR-007 + FR-008 | ≥1 cross-layer chain spanning ≥3 layers; ≥3 of 6 agentic patterns populated; ≥6 MAESTRO layers populated in threats.md |
| **Wave 3 — Architecture iteration (if needed)** | 0-1 day (capped at 2 iterations) | If Wave 2 output gaps surface, apply fallback ranking: (a) keyword-tune → (b) extend architecture → (c) relax FR-004 to 6/7 layers (last resort) | Re-run checklist + pipeline until Wave 2 gates pass |
| **Wave 4 — README authoring (parallel with Wave 3)** | ~1.5-2 days | PM drafts adopter-facing `README.md` sections 1/2/5/6/7 in parallel with Wave 3 architecture iteration; Sections 3 (layer coverage table) + 4 (what to look for) wait on pipeline output freeze | PM tone review (neutral factual, no marketing); security-analyst disclaimer review (FR-017 + SC-014) |
| **Wave 5 — Baseline commit + regression integration** | ~0.5 day | Regenerate PDF under `SOURCE_DATE_EPOCH=1700000000`; prove byte-identity on repeat run; commit `security-report.pdf.baseline`; add `"maestro-reference"` to `BASELINE_EXAMPLES` in `tests/scripts/test_backward_compatibility.py`; update `examples/README.md` | `pytest -k "maestro-reference"` passes byte-identity; no regression on existing 5 baselines |
| **Wave 6 — Feature 120 frontmatter injection + final validation** | ~0.5 day | Invoke `/tachi.architecture` in "create" mode on frozen architecture body to compute SHA-256 + inject v1.0 frontmatter; commit; run `/aod.analyze`; DoD walkthrough | `/aod.analyze` pass; all DoD line items checked; no mixed structure (no stray `sample-report/`) |

### Dependencies Between Waves

- Wave 1 **blocks** Wave 2 (architecture must be pre-qualified before pipeline invocation)
- Wave 2 **blocks** Wave 4 Sections 3+4 (pipeline output required for "what to look for" + layer coverage table)
- Wave 4 Sections 1/2/5/6/7 run **in parallel** with Wave 3 (team-lead M2 / L2 parallelism opportunity)
- Wave 5 **blocks** Wave 6 (frontmatter injection is last; baseline commit + regression fixture integration precede it)
- Wave 3 is **conditional** — skipped if Wave 2 gates pass on first run

### Critical Path

Wave 1 → Wave 2 → (Wave 3 iff needed) → Wave 5 → Wave 6. Wave 4 parallel to Wave 3 does not extend the critical path.

**Pessimistic critical path**: 1.5 + 1 + 1 + 0.5 + 0.5 = **4.5 days** with 2 Wave 3 iteration rounds — within the 4-8 day PRD estimate. Wave 4 parallel work fits in the 4.5-day envelope.

## Non-Functional Considerations

### Backward Compatibility Invariant

All five existing non-multi-agent baselines MUST remain byte-identical after this feature lands. Wave 5 runs `pytest tests/scripts/test_backward_compatibility.py` WITHOUT `-k` filter to prove the entire BASELINE_EXAMPLES list passes (5 existing + 1 new = 6 baselines all byte-identical). Any regression on an existing baseline is a hard stop — root-cause before proceeding.

### Determinism

Pipeline regeneration under `SOURCE_DATE_EPOCH=1700000000` is byte-identical per ADR-021. Feature 145 adds no new determinism work; it only consumes the existing convention. The Wave 5 baseline commit runs 2 consecutive regenerations and asserts byte-identity between them before committing the `.baseline` file.

### Security Considerations

- **Domain disclaimer** (FR-016) prominently placed in README Section 2 and in `architecture.md` header comment.
- **Security-analyst review** (FR-017 / SC-014) of README disclaimer prose before commit — triggered by Option A (Healthcare) selection; reviewer must confirm (a) no real patient names, (b) no clinical specialty claiming diagnostic accuracy, (c) no regulatory-advice interpretation, (d) explicit "not a real system" framing.
- **No PII in any artifact** — component names use abstract labels ("Patient Record", "Clinical Audit Log") rather than specific patient identifiers or provider names.
- **Zero-edit invariant on 11 detection agents** (Feature 082 / ADR-026 Decision 1) — preserved. Feature does not modify `.claude/agents/tachi/**.md`.

### Performance

No new performance requirements. Pipeline run time against the new example should be comparable to `agentic-app` (existing production fixture with 10+ components). No performance SLAs because the artifact is static content, not a runtime service.

### Accessibility / Readability

- README target reading level: accessible to a security engineer new to MAESTRO.
- Tachi-specific terms (STRIDE, MAESTRO, dispatch) defined inline or cross-referenced on first use.
- PDF output uses existing Typst templates — accessibility is unchanged from existing example PDFs.

## Complexity Tracking

*No Constitution violations. Table intentionally empty.*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |

## Risk Summary

Risks carried from PRD with updated mitigations post-Wave 0 resolution:

| Risk | Likelihood | Impact | Mitigation | Wave 0 update |
|------|-----------|--------|-----------|---------------|
| 145.1 Architecture draft does not surface required chains/patterns | Medium | Medium | Pre-Execution Checklist (FR-005) pre-qualifies architecture statically; fallback ranking (keyword-tune → extend → relax) capped at 2 iterations | Mitigated by Phase 1 component design (§ Components / § Data Flow) already showing all 4 checklist conditions green |
| 145.2 Domain selection disagreement | Medium | Low-Med | Domain locked as Option A Healthcare with fallback ranking A → B → C | **Closed** — WG-1 resolved in this plan |
| 145.3 PDF baseline non-byte-identical | Low | High | Follow existing ADR-021 convention; validate byte-identity twice before committing baseline; defer FR-011 if fails | Live — Wave 5 gate |
| 145.4 README reads as marketing | Medium | Medium | PM tone review before commit; neutral factual tone mandate; Non-Functional Quality Bar "Narrative substance" in spec | Live — Wave 4 PM review |
| 145.5 Domain content-risk (Healthcare PHI-adjacent framing) | Low | Med-High | Disclaimer in README + architecture header; abstract component naming; security-analyst review (FR-017 / SC-014) | Live — Wave 4 security-analyst review (triggered by Option A selection) |
| 145.6 Canonical example displaces agentic-app in adopter mental model | Low | Low | FR-010 + FR-014 + US-6 AC-3 structurally guard positioning | Closed via spec edge-case addition during /aod.spec |

## References

### Source Artifacts
- [spec.md](spec.md) — feature specification (PM APPROVED_WITH_CONCERNS)
- [research.md](research.md) — Phase 0 research findings
- [PRD 145](../../docs/product/02_PRD/145-maestro-canonical-worked-example-2026-04-16.md) — source PRD with Triad sign-offs

### Constitution
- [.aod/memory/constitution.md](../../.aod/memory/constitution.md) — Principles I-XI evaluated in Constitution Check

### Predecessor Features (All DELIVERED)
All Phase 1-5 MAESTRO features (084, 136, 141, 142, 143, 144) plus Features 024, 091, 104, 112, 120, 121, 128, 129 (enumerated in spec.md References section).

### Architecture Decisions
- [ADR-020 MAESTRO Layer Classification](../../docs/architecture/02_ADRs/ADR-020-maestro-layer-classification.md)
- [ADR-021 SOURCE_DATE_EPOCH Determinism](../../docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md)
- [ADR-022 mmdc Hard Prerequisite](../../docs/architecture/02_ADRs/ADR-022-mmdc-hard-prerequisite.md)
- [ADR-023 Threat Agent Skill References Pattern](../../docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md)
- [ADR-024 OWASP AIVSS Evaluation](../../docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md)
- [ADR-025 NIST AI RMF Evaluation](../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md)
- [ADR-026 Pattern Classification Mechanism](../../docs/architecture/02_ADRs/ADR-026-pattern-classification-mechanism.md)

### Detection Rule Tables
- [maestro-layers-shared.md](../../.claude/skills/tachi-shared/references/maestro-layers-shared.md)
- [maestro-agentic-patterns-shared.md](../../.claude/skills/tachi-shared/references/maestro-agentic-patterns-shared.md)
- [attack-chain-patterns-shared.md](../../.claude/skills/tachi-shared/references/attack-chain-patterns-shared.md)
