# CLAUDE.md - tachi

<!-- Context Budget: Target <100 lines (justified: 10-line return policy saves 9K-36K tokens/session) -->

## Core Constraints
- **Product-Led**: Start with product vision, PRDs, and user stories
- **Source of Truth**: `.aod/spec.md`
- **Validation Required**: Run `/aod.analyze` before PRs
- **Local-First**: Always supports local `.aod/` file workflows

## Git Workflow
**Always use feature branches**: `git checkout -b NNN-feature-name`
- **NNN** = GitHub Issue number, zero-padded to 3 digits
- Never commit to main directly
- Draft PR opened at plan stage, marked ready at delivery
- Branch format: `NNN-descriptive-name` (e.g., `021-feature-name` for Issue #21)

## Project Structure
```
tachi/
├── .claude/           → Agents, skills, commands, design archetypes
├── .aod/              → Active feature workspace (spec.md, plan.md, tasks.md)
├── brands/            → Brand identity assets (vision + design tokens)
├── specs/             → Archived feature artifacts (per-feature history)
├── docs/              → Product, architecture, devops docs
├── scripts/           → init.sh, check.sh
├── stacks/            → Stack packs (conventions, personas, scaffolds)
└── CLAUDE.md          → AI agent context
```

**Note**: Template provides methodology only. Users bring their own code.

## Context Discovery
- **Thinking Lenses**: `docs/core_principles/README.md` (5 Whys, Pre-Mortem, etc.)
- **Project Standards**: `docs/standards/README.md` (DoD, naming, git)
- **Product Docs**: `docs/product/README.md`
- **Architecture**: `docs/architecture/README.md`
- **Triad Guide**: `docs/AOD_TRIAD.md`
- **Constitution**: `.aod/memory/constitution.md`

## Commands
**PDL workflow** (optional, before Triad):
- `/aod.discover` → `/aod.score`

**Post-init** (recommended after `make init`):
- `/aod.foundation` — Guided workshop: product vision + design identity

**Triad workflow**:
- `/aod.define` → `/aod.plan` → `/aod.build [--no-security] [--no-design-check]`
- (`/aod.plan` chains: spec → project-plan → tasks automatically)

**Post-delivery**:
- `/aod.deliver` — Close completed feature
- `/aod.document [--autonomous]` — Quality review: simplify, docstrings, CHANGELOG, API docs (--autonomous for orchestrator-driven runs)

**Downstream Updates** (adopter-side template sync):
- `/aod.update` — Apply upstream PLSK template updates to your project. Direction: `PLSK → user`. See `docs/guides/DOWNSTREAM_UPDATE.md`.
- `/aod.sync-upstream` — Push local template improvements back to the public PLSK repo. Direction: `user → PLSK`.

**Terminology**: `sync-upstream` = `user → PLSK` (contribute back). `update` = `PLSK → user` (pull updates). These are opposite-direction commands — do not confuse them.

**Supporting commands**:
- `/aod.clarify` — Resolve spec ambiguities
- `/aod.analyze` — Cross-artifact consistency check
- `/aod.checklist` — Generate quality checklist
- `/aod.constitution` — Manage governance principles
- `/aod.kickstart` — POC kickstart: generate consumer guide with seed features
- `/aod.blueprint` — Multi-feature story generation from consumer guide
- `/aod.status` — View backlog and lifecycle stage summary
- `/aod.roadmap` — Scaffold quarterly roadmap from completed PRDs
- `/aod.okrs` — Scaffold OKR document with standard template
- `/aod.stack` — Manage stack packs (activate, remove, list, scaffold)

## SDLC Triad Governance
| Role | Defines | Authority |
|------|---------|-----------|
| PM | What & Why | Scope & requirements |
| Architect | How | Technical decisions |
| Team-Lead | When & Who | Timeline & resources |

**Sign-off Requirements**:
- `spec.md`: PM sign-off
- `plan.md`: PM + Architect sign-off
- `tasks.md`: PM + Architect + Team-Lead sign-off

## Deployment Policy
All deployments must go through the devops agent. Never deploy without verification.

## Subagent Return Policy
When invoked as a subagent (via Agent tool), return ONLY:
1. **Status** (APPROVED / CHANGES_REQUESTED / BLOCKED / pass / fail)
2. **Item count** (if applicable)
3. **File path** to `.aod/results/{agent-name}.md` with full details
- Write detailed findings to results file BEFORE returning
- Max return: 15 lines / ~200 tokens
- NEVER return code snippets, file contents, or multi-paragraph explanations
- Policy applies to subagent→main returns only, not user-facing output

## Key Principles
- **Vision First**: `/aod.define` (includes vision) → `/aod.plan` (spec → plan → tasks)
- **Triple Sign-off**: PM + Architect + Team-Lead approval on tasks.md
- **Definition of Done**: 3-step validation before marking complete

## Context Boundaries
**EXCLUDE**: `archive/`, `node_modules/`, `.git/`, `*.log`
**FOCUS**: `.aod/`, `docs/`, `.claude/`, current feature branch

## Tips
- Use `make review-spec` or `make review-plan` for manual governance checks
- Search `docs/core_principles/` for thinking methodologies
- Review `agent-assignments.md` for workload distribution

## Recent Changes
- **Feature 229** (2026-04-27): LLM10:2025 Unbounded Consumption — `denial-of-service` + `model-theft` enriched (BLP-01 Tier 1 fifth feature; second execution of Heuristic A enrichment branch; first at two-agent scope)
  - ADR-034 (Proposed → Accepted at Wave 3 T040) lineage: cross-refs ADR-030 D1 (signal-class taxonomy in LLM tier — applied at two-agent scope) + ADR-031 D8 (regex-alternation rule cross-referenced as the **asymmetry** F-5 does NOT invoke — first BLP-01 feature with zero schema bump at two-agent scope) + ADR-032 (direct precedent at single-agent scope; lines 84+182 forecast that F-5 will not need a schema bump — **fulfilled**) + ADR-033 D2 (sub-scope carve-up structural sibling — ADR-033 carved one OWASP entry across two host agents at the documentation layer; ADR-034 enriches one OWASP entry across two host agents at the pattern-catalog layer)
  - 9 Decisions: D1 enrichment-vs-new-agent at two-agent scope; D2 additive-only edits across 4 host files (`denial-of-service.md` + companion + `model-theft.md` + companion); D3 canonical 5-row LLM10 sub-pattern → owning-agent mapping table populated COMPLETE with severity-hint annotation column (audit deliverable per team-lead MEDIUM-1); D4 no schema bump (second BLP-01 detection feature reusing existing `D` and `LLM` prefixes; first at two-agent scope); D5 no consumers-list edit; D6 no functional orchestrator/dispatch edit; D7 Pattern Category Disambiguation across two companion catalogs (DoS Cat 9 vs Cat 12/13 + model-theft Cat 6 vs Cat 10/11); D8 no `source_attribution` populator wiring extension (F-A3 deferral); D9 public-only governance per SDR-001 Option C
  - BLP-01 Tier 1 5th feature delivered (after F-1..F-4); LLM10:2025 transitions Partial → Covered; **OWASP LLM Top 10:2025 framework now 10/10 fully closed** (combined with F-4's ASI09 closure: 20/20 OWASP AI top-10 entries); BLP-01 progress 8/11 features delivered
  - **Q1 SPLIT cross-agent vector decomposition**: Cat 13 (Context-Window Latency) Vector A = availability disruption → DoS host; Cat 11 (Denial-of-Wallet) Vector B = economic damage → model-theft host. First BLP-01 sub-pattern with cross-agent vector decomposition
  - **Q3 severity-floor 2-condition CRITICAL rule**: Cat 11 default = HIGH; CRITICAL only when (a) multi-tenant freemium structurally evident AND (b) BOTH per-tenant token budget AND cost alerting absent
  - **T1496 prose-only on Cat 10/11**: MITRE ATT&CK T1496 (Resource Hijacking) cited as prose context only (NOT in references array — not catalog-resolvable per ADR-034 D6); 2 prose mentions, 0 references-array entries verified across full corpus
  - Schema `finding.yaml` **unchanged at 1.8** (asymmetry to F-1 / F-2 / F-4 minor bumps; zero new schema regex-alternation entries)
  - 4 NEW findings emerged on `examples/agentic-app/` regen — D-10 (Cat 12, Critical) + D-11 (Cat 13, Critical, Q1 SPLIT Vector A) + LLM-15 (Cat 10, Critical) + LLM-16 (Cat 11, High per Q3 default — single-tenant, Q1 SPLIT Vector B); cohesive category rendering in single Section 3.5 DoS + single Section 3.8 LLM (no fragmentation); correlation group CG-8 binds all 4 in Theme 5 of regenerated `threat-report.md`
  - **22-file zero-edit invariant** preserved (12 other agents + 7 infrastructure consumers + `human-trust-exploitation.md` + `tool-abuse.md` NOT-edit); F-5 = 28 detection-tier files post-F-4 inventory + 4 file edits + 0 net-new = 28 files post-merge
  - 6/6 byte-identical baselines under `SOURCE_DATE_EPOCH=1700000000` (web-app + microservices + ascii-web-api + mermaid-agentic-app + free-text-microservice + maestro-reference); LLM-serving topology gate (FR-015) properly filters Cat 12/13/10/11 on non-LLM-serving architectures
  - Test infrastructure update at `tests/scripts/test_backward_compatibility.py`: removed F-5 hosts from `DETECTION_AGENT_PATHS` (12 → 10) and added to `DETECTION_PATTERN_REF_ENRICHMENT_HOSTS` frozenset (extending F-3's single-host pattern to multi-host enrichment branch)
  - 26 enrichment tests at `tests/scripts/test_llm10_unbounded_consumption_enrichment.py` (line caps + MAESTRO grep + MANDATORY Read directive + Pattern Categories + Disambiguation + T1496 prose-only + per-fixture references-array + Q3 severity-floor); pipeline regen 79-page security-report.pdf (Tier 1 residual risk)
  - 74/85 tasks complete (87%); zero schema-bump scope; zero new runtime dependencies; PR pending `gh pr ready` (T078) and squash-merge with `feat(229):` Conventional Commit title (R12 release-please mitigation)
- **Feature 224** (2026-04-26): `human-trust-exploitation` threat agent (OWASP ASI09:2026 communication axis)
  - ADR-033 (Proposed → Accepted at PR merge) lineage: cross-refs ADR-030 D2 Outcome B (ASI09 communication-axis carve-up reservation that **created** F-4's scope) + ADR-030 D8 third application (regex-alternation minor-bump rule) + ADR-033 D9 Naming Disambiguation (`human-trust-exploitation` agent name hyphen-cased / agent-to-human ASI09 scope vs. existing `agentic_pattern: "trust_exploitation"` schema-enum value underscore-cased / agent-to-agent multi-agent-topology scope per Feature 142) + ADR-033 D10 DFD Target Decision (`dfd_targets: [Process]` only — no External Entity declaration per BLOCKING-1; mirrors F-1 / F-2 single-target precedent)
  - BLP-01 Tier 1 4th feature delivered (after F-1 / output-integrity, F-2 / misinformation, F-3 / tool-abuse-enrichment); ASI09:2026 **communication axis** transitions Planned → Covered (autonomy axis remains attributed to `agent-autonomy`); BLP-01 Coverage Matrix at 7/11 features delivered (Foundation + F-1 + F-2 + F-3 + F-4 = 5 closure features + 2 enabler waves)
  - Schema `finding.yaml` 1.7 → 1.8 minor bump as **3rd recorded application** of D8 regex-alternation rule; `id.pattern` gains `TE` alternation: `^(S|T|R|I|D|E|AG|LLM|AGP|OI|MI|TE)-\\d+$` (12 prefixes total)
  - **Three-prefix-family discipline within agentic** demonstrated (`AG` autonomy-axis / `AGP` multi-agent-topology / `TE` communication-axis render as distinct signal classes with disjoint mitigation vocabularies); combined with the LLM three-prefix family from F-2 (`LLM` input-side / `OI` output-sanitization / `MI` factual-integrity) yields a **6-prefix-family AI threat surface** with Heuristic A signal-class boundary preservation across both AI-tier sub-categories
  - **26-file zero-edit invariant preserved INCLUDING `agent-autonomy.md` NOT-edit** despite the ASI09 sub-scope carve-up — the carve-up is documented at the ADR-033 D2 layer only; `agent-autonomy.md`'s `owasp_references` already lists ASI-09 (verified at T004) so no metadata edit was needed; F-4 = 22 original tachi files + F-1's 2 + F-2's 2 + F-3's 0 (enrichment-branch — modifies existing, no new files) + F-4's 2 = 26-file inventory + 2 net-new = 28 files post-merge
  - F-4 = **third net-new producer** of `source_attribution` (after F-1 + F-2; F-3 was first to use the enrichment-branch pattern instead of standalone), proving F-A2 referential-integrity contract against three independent populators
  - New `examples/consumer-agent-app/` baseline (Q5 lean per architect Wave 3 Step 1 decision — clean-slate baseline for F-4 trigger validation, NOT agentic-app extension); WellnessCompanionChatbot mental-health/wellness companion archetype with all 4 FR-006 emission indicators engaged (outgoing flow to End User External Entity, consumer-facing prose match on `chatbot`/`companion`/`coach`, persistent persona/multi-turn dialogue, wellness coaching authority); 5 TE findings (TE-1..TE-5, one per Pattern Category 1-5) emitted on regen; 19 total findings (1 Critical, 8 High, 7 Medium, 3 Low); pipeline regen byte-identical (40-page PDF, SHA-256 `7ac0b639...269bce5`) per ADR-021 `SOURCE_DATE_EPOCH=1700000000` invariant; 6/6 infographic JPEGs generated (baseball-card / system-architecture / executive-architecture / risk-funnel / maestro-stack / maestro-heatmap)
  - 73/73 tasks complete (100%); zero schema-bump scope beyond minor 1.7 → 1.8; zero new runtime dependencies; PR #225 prepared for squash-merge with `feat(224):` Conventional Commit title (R12 release-please mitigation per `.claude/rules/git-workflow.md` two-step Pre-merge + Post-merge enforcement)
- **Feature 219** (2026-04-25): `tool-abuse` agent enriched for OWASP ASI07:2026 (BLP-01 Tier 1 third feature; first execution of Heuristic A enrichment branch)
  - ADR-032 (Accepted) with 7 Decisions: D1 enrichment-vs-new-agent (extend `tool-abuse` rather than spawn `asi07-inter-agent-communication`); D2 additive-only edits (3 anchor points: metadata `owasp_references`, `## Purpose`, Detection Workflow Step 5); D3 no-schema-bump asymmetry to ADR-031 D8 (no new `id.pattern` prefix; reuses `AG` family); D4 zero consumer edits (24-file invariant preserved); D5 zero functional orchestrator edit (cosmetic Q2 annotation only); D6 public-only governance (no internal docs changed); D7 Pattern Category Disambiguation (explicit boundary-marking subsection vs. Categories 1-8 to prevent dispatch-mode confusion)
  - 2 net-new Pattern Categories appended to `.claude/skills/tachi-tool-abuse/references/detection-patterns.md` — Category 9 "Insecure Inter-Agent Communication (A2A)" + Category 10 "MCP-to-MCP Trust Propagation"; new Pattern Category Disambiguation subsection clarifies boundary between Categories 1-8 (single-agent tool-abuse) vs. Categories 9-10 (cross-agent trust propagation); Categories 1-8 + Overview + Targeted DFD Element Types + Trigger Keywords sections held byte-identical to baseline (SC-006 BLOCKER)
  - `.claude/agents/tachi/tool-abuse.md` — 3 additive edits only: metadata `owasp_references += ASI-07` (now `[ASI-02, ASI-04, MCP-03, MCP-05, LLM06:2025, ASI-07]`); `## Purpose` extended with 1-line A2A/MCP-to-MCP surface naming; Detection Workflow Step 5 references list extended with `ASI-07, MITRE ATLAS AML.T0060, CWE-287, CWE-345`; line count 98 → 100 (well under 150 cap)
  - Wave 3 regen on `examples/agentic-app/`: AG-8 [NEW] emerged — Insecure Inter-Agent Communication finding on Inter-Agent Communication Channel component, citing OWASP ASI07:2026 + CWE-287 + MITRE ATLAS AML.T0060; finding renders cohesively in `threat-report.md` §3.7 "Agentic Threats (AG-1 through AG-8)" — single Agentic-category section (no fragmentation)
  - Heuristic A enrichment-branch first execution — establishes precedent for F-6 + F-7 (Tier 2 ML-extraction + Mobile bundles); 24-file zero-edit invariant preserved (22 original + F-1 + F-2 additions; F-3 modifies only `tool-abuse.md` + companion `detection-patterns.md`) per ADR-032 Decision 2
  - Asymmetry to F-2 ADR-031 D8: F-3 adds zero new schema regex-alternation entries (no new `id.pattern` prefix; reuses existing `AG` family from F-Foundation); F-3 is the first BLP-01 feature with zero schema bump scope
  - 67/67 tasks complete (100%); zero schema changes; zero new runtime dependencies; 1-day envelope held; PR #220 prepared for squash-merge with `feat(219):` Conventional Commit title
- **Feature 212** (2026-04-25): Improve Executive-Architecture Infographic — OpenClaw-style flow diagram
  - Three-level upgrade: (L1) VERBATIM-locked Gemini prompt for `executive-architecture` template (`.claude/skills/tachi-infographics/references/executive-architecture.md`) — rounded-rectangle nodes, directional arrows, leader-lined callouts, dashed sub-group clusters, compact empty-layer badges
  - (L2) Callout-selection rewrite in `scripts/extract-infographic-data.py::_select_critical_high_callouts` — Largest Remainder Method picks 6–8 system-wide callouts with per-layer floor rule (≥1 per qualifying layer when total-cap ≤ 8) and 4-callout-per-layer ceiling
  - (L3) Additive payload extension in `_build_executive_architecture_payload` — new `flow_edges[]` (sourced from `parse_scope_data.data_flows[]`, sorted by `(source.lower(), destination.lower())`, capped at 50 with warning log) and `clusters[]` (sourced from `parse_scope_data.trust_boundaries[]`, sorted by `(_TRUST_LEVEL_ORDER[trust_level], name.lower())`)
  - Field-name lock to producer contract: `flow_edges[*].destination` (NOT `target`); `clusters[*].members` (NOT `components`); `clusters[*].trust_level` via hyphen→underscore rename
  - F-128 contracts preserved: output filenames, PDF position pages 2–3, skip behavior on zero Critical/High, portrait orientation, Typst bindings (`has-executive-architecture` / `executive-architecture-image-path`); ADR-017 byte-identical-payload + ADR-021 `SOURCE_DATE_EPOCH=1700000000` byte-identity invariants verified end-to-end
  - New drift-guard `tests/scripts/test_executive_architecture_payload.py` (12-case fixture matrix: field-name lock, sort stability, empty-array-when-absent, byte-identical determinism, prompt co-landing); enhanced `test_extract_infographic_data.py` per-layer floor-rule fixtures
  - 37/37 tasks complete (100%); zero new runtime dependencies; PR #213 squash-merged to main as `3df035b`
- **Feature 206** (2026-04-24): `misinformation` threat agent (OWASP LLM09:2025)
  - New AI-tier detection agent `.claude/agents/tachi/misinformation.md` + companion skill `tachi-misinformation/` — 5 factual-integrity pattern categories (Ungrounded Factual Emission / Citation Fabrication / Overreliance-Missing-HITL / Retrieval-Grounding Gap / Confidence-Calibration Absence)
  - BLP-01 Tier 1 F-2 — 2nd Tier-1 feature after F-1 (Feature 201); closes LLM09:2025 on the Coverage Matrix (Planned → Covered)
  - ADR-031 (Accepted) cross-refs ADR-030 Decision 1 (Heuristic A inheritance — factual-integrity carve-out) and ADR-030 Decision 8 (regex-alternation minor-bump rule — 2nd application)
  - Schema `finding.yaml` 1.6 → 1.7 — `MI` prefix added to `id.pattern` regex alternation (11 values now: `S|T|R|I|D|E|AG|LLM|AGP|OI|MI`) under the additive-compatibility conditions of ADR-026 extended by ADR-030 D8
  - Three-signal-class discipline: `LLM-{N}` (input-side, LLM01) / `OI-{N}` (output sanitization, LLM05) / `MI-{N}` (factual integrity, LLM09) render adjacent with distinct `source_attribution` primaries
  - 24-file zero-edit invariant preserved (22 original + F-1's 2) — F-2 is a net-new addition, not a refactor
  - F-2 is the **second net-new producer** of `source_attribution` (F-1 was first) — F-A2 referential-integrity contract proven against two independent populators
- **v2.0.0**: Anthropic Claude Code v2.1.16 Integration
  - Parallel Triad reviews, context forking, version detection
  - See `docs/devops/MIGRATION.md` for upgrade guide
- **v1.1.0**: Modular rules system
