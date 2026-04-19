# ADR-030: `output-integrity` Threat Agent (OWASP LLM05:2025)

**Status**: Accepted
**Date**: 2026-04-18 (Proposed); 2026-04-18 (Accepted — provisional; confirmed at post-merge SHA fill)
**Accepted-commit-SHA**: `<pending-post-merge-fill>`
**Deciders**: Architect, Product Manager, Team-Lead
**Feature**: 201 (F-1 `output-integrity` Threat Agent — first BLP-01 Tier 1 feature)
**Related ADRs**: [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO classification — F-1 inherits L5 layer from orchestrator Phase 1), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism — Wave 4 regeneration gate), [ADR-022](ADR-022-mmdc-hard-prerequisite.md) (mmdc hard prerequisite — Wave 4 regenerated PDF depends on this), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (lean-agent detection variant — extended here with regex-prefix additive rule per Decision 8), [ADR-026](ADR-026-pattern-classification-mechanism.md) (minor-bump rule — extended here via regex-alternation Complex-Shape Clarifier), [ADR-027](ADR-027-taxonomy-crosswalk-schema.md) (F-A1 taxonomy enum source for `source_attribution`), [ADR-028](ADR-028-source-attribution-schema-extension.md) (F-A2 `source_attribution` contract — F-1 is the first net-new producer), [ADR-029](ADR-029-coverage-attestation-report-section.md) (F-B downstream consumer — `has-source-attribution` fires true on agentic-app regen)

---

## Context

Tachi's agentic-AI threat-modeling pipeline currently ships 5 AI-tier detection agents (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`) governed by ADR-023's lean-agent pattern. The 5 agents cover the **input** side of the LLM threat surface (prompt injection, training-data poisoning, model extraction, agent misalignment, MCP/tool abuse) comprehensively, but the **output** side — where LLM-generated content flows unsanitized into downstream execution sinks (browsers, SQL clients, shells, template engines, outbound HTTP clients, file writes) — is silent. This asymmetry is observable in threat-model output: an architecture with a single LLM Process plus a rendered-HTML downstream gets `prompt-injection` findings but zero findings on the XSS / CSP-bypass surface, even though OWASP LLM05:2025 (Improper Output Handling) names this as one of the top 10 LLM application risks for 2025.

BLP-01 (Better LLM Protection initiative, documented in `_internal/strategy/BLP-01.md`) identifies this gap as Tier 1 priority F-1, with three Foundation features (F-A1 / F-A2 / F-B) shipped in Features 180 / 189 / 194 as the prerequisite machine-readable taxonomy + source-attribution + coverage-attestation plumbing. F-1 is the first downstream consumer of the Foundation tier — the first net-new agent that populates `source_attribution` on every emitted finding, the first agent whose `OI-{N}` findings are counted in the F-B coverage-attestation section, and the first test of whether the Foundation tier's machine-readable contract holds up end-to-end against a real detection-tier populator.

The feature introduces one new AI-tier agent `output-integrity` plus a companion skill directory `tachi-output-integrity/` with a pattern catalog covering five output-handling sink categories (XSS/DOM, server-side execution, SSRF, template injection, path traversal). Agent shape mirrors `prompt-injection.md` verbatim per ADR-023's lean-agent detection variant. The schema `schemas/finding.yaml` receives a **regex-alternation prefix addition** — `id.pattern` gains `OI` as a 10th alternation value — which is the first such addition in tachi's schema evolution and requires the ADR-026 minor-bump rule to extend from enum-typed scalar and list-of-RECORD fields to regex-alternation additions. The ADR-030 Proposed commit at Wave 1.1 is the schema-lock point that unblocks parallel Wave 2 authoring of the pattern catalog and the agent file.

PRD 201 was approved 2026-04-18 with full Triad sign-off (all three APPROVED_WITH_CONCERNS). The spec was PM-approved same day with 1:1 PRD-to-spec FR mapping preserved. The architect-authority question **Q1 — Heuristic A** (whether to subsume ASI09 human-victim signal class into F-1's pattern catalog or forward-reference F-4 `trust-exploitation` as the future owner) is resolved in Decision 2 below via Outcome B (split), with the Outcome A counter-argument absorbed per PM M2.

### Constraints

- **22-file zero-edit invariant** (spec SC-009, FR-013 — ADR-023 lineage): F-1 MUST NOT edit any file under `.claude/agents/tachi/stride/` (6 files), `.claude/agents/tachi/ai/` (5 files), or `.claude/skills/tachi-{spoofing,tampering,repudiation,info-disclosure,denial-of-service,privilege-escalation,prompt-injection,data-poisoning,model-theft,tool-abuse,agent-autonomy}/references/detection-patterns.md` (11 files). ADR-023 Decision 2 stabilized this 22-file scope; F-1 adds one new agent (the 12th AI-tier file by authorship, the 6th AI-tier file in scope) and one new companion skill directory without reopening any of the 22 frozen files.
- **Byte-identity backward compatibility** (spec SC-006, FR-009 — ADR-021 lineage): the 5 non-agentic example PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) MUST regenerate byte-identically under `SOURCE_DATE_EPOCH=1700000000`. The `has-source-attribution` conditional section 9 (F-A2 Q1-E) is already authored per ADR-028 Decision 2 to return `false` on all 5 baselines today; F-1's zero-finding-on-non-qualifying-architecture discipline (US1 Acceptance Scenario 4) preserves this gate.
- **Zero new runtime or developer dependencies** (spec SC-008): empty diffs on `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`, `package.json`. `pyyaml` and `pytest` remain developer-only per Feature 128 precedent.
- **F-A2 referential-integrity contract** (spec SC-010 — ADR-028 Decision 5 lineage): every emitted `OI-{N}` finding's `source_attribution` array MUST resolve every `(taxonomy, id)` pair against `schemas/taxonomy/{taxonomy}.yaml`. The `validate_source_attribution` helper at `scripts/tachi_parsers.py:826` (authored in F-A2 / Feature 189) is the enforcement point; F-1 is the first net-new producer it validates.
- **Zero MAESTRO references** in agent file and companion skill (spec FR-010): grep-auditable invariant. MAESTRO layer assignment happens at orchestrator Phase 1 (Feature 084 / ADR-020) — F-1 agent does not author its own layer; `output-integrity` findings inherit L5 Evaluation and Observability layer by orchestrator classification.
- **Heuristic A signal-class discipline** (research.md §11, plan.md Open Questions Q1): F-1 owns the encoding/sanitization signal class (bytes/strings/syntax primitives); F-4 `trust-exploitation` owns the psychology/linguistics signal class (tone/authority/uncertainty primitives). Decision 2 below records Outcome B as the architect ruling.

---

## Decision

We adopt the new `output-integrity` AI-tier threat agent per the 8 numbered decisions below. The agent ships with a companion skill directory, a regex-alternation schema bump from 1.5 to 1.6, one public per-feature ADR (this ADR), and one regenerated example (`agentic-app`). The 22-file zero-edit invariant and the 5-baseline byte-identity gate are preserved by construction. Seven of the eight decisions resolve architectural questions raised in the PRD + spec + plan; Decision 8 extends the ADR-023 + ADR-026 governance rules to cover the new kind of additive surface F-1 introduces.

### Decision 1 — Adopt new `output-integrity` AI-tier agent for LLM05:2025 closure

We introduce `output-integrity` as the 6th AI-tier threat agent under `.claude/agents/tachi/output-integrity.md`, governed by the ADR-023 lean-agent detection variant. The agent's canonical shape is 5 sections (YAML frontmatter → metadata YAML block → `## Purpose` → `## Skill References` table → `## Detection Workflow`) with an optional `## Example Findings` section, a ≤150-line soft target / ≤180-line hard ceiling, and exactly one `**MANDATORY**: Read` directive loading the companion pattern catalog at detection start.

The agent emits findings with `OI-{N}` ID prefix (per schema 1.6 regex extension, Decision 8 below) and `category: llm` (no new category enum value — LLM05 + ML09 bundle cleanly under the existing `llm` category per Decision 4 below). Every finding carries a populated `source_attribution` array citing OWASP LLM05:2025 as `relationship: primary` plus one or more relevant CWEs (CWE-22/78/79/89/94/918) as `relationship: related`. Mitigation text names a specific encoding/library/pattern matched to the sink category — no generic "sanitize output" prose.

The 5 existing AI-tier agents (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`) are NOT modified. `output-integrity` is a sibling, not a refactor target. ADR-023's 22-file zero-edit invariant holds — the 11 frozen detection-tier files plus the 11 companion skill-reference files remain byte-identical at F-1 merge.

### Decision 2 — Heuristic A resolution: Outcome B (split) with Outcome A counter-argument recorded

We select **Outcome B** (split) as the Heuristic A resolution for ASI09 human-victim signal class scope per the architect ruling at `.aod/results/heuristic-a-decision.md`. The `output-integrity` agent owns the **encoding/sanitization signal class** (machine-victim output handling, LLM05:2025) covering five pattern categories: Client-Side Execution Sinks (XSS/DOM), Server-Side Execution Sinks (SQLi/Command/Code), SSRF from LLM-Synthesized URLs, Template/Expression Injection, and Path Traversal + Unsafe File Writes. F-4 `trust-exploitation` (future agent under BLP-01 §8) is forward-referenced as the owner of the **psychology/linguistics signal class** (human-victim output handling, ASI09:2026) covering authority claims, urgency framing, false reassurance, and mimicry of trusted roles.

**Rationale**: per GUIDE-threat-coverage-research §11 signal-class distinction, an agent owns a specific detection vocabulary, trigger-keyword set, and DFD-element-type focus. Encoding/sanitization detection interrogates architectural signals (renderer-without-escape, SQL-without-parameterization, URL-without-allowlist, path-without-canonicalization) and is amenable to deterministic pattern matching. Psychology/linguistics detection has no DFD-element-type signature — "overconfident tone" and "absence of uncertainty disclaimers" are text-semantic primitives that would force `output-integrity`'s trigger-keyword set to span two disjoint semantic spaces, degrade the quality of both halves, and set a precedent that erodes Heuristic A's discipline on subsequent BLP-01 features (notably F-2 misinformation, which §11 Worked Example 4 already distinguishes from F-1 on the same grounds). The agent's `## Purpose` section forward-references F-4 explicitly and lists ASI09:2026 as out-of-scope.

**Outcome A counter-argument (recorded per PM M2)**: subsuming ASI09 into F-1 as a sixth pattern category carries a legitimate BLP-01 Tier 1 simplification benefit — one agent rather than two means one fewer citation target for ecosystem consumers, one less bureaucratic surface, and a cleaner Coverage Matrix transition (ASI09 → Covered immediately on F-1 merge rather than Planned-with-clear-owner). §11 Worked Example 6 itself frames the Option A reasoning fairly — "the human is the downstream system; the integrity gate is deceptive-pattern classifier before presentation to human." If F-4 slips or is deprioritized post-F-1, ASI09 remains Planned until F-4 actually ships. The Outcome A path is recorded here so future readers see Outcome B as a deliberate non-selection rather than an unconsidered alternative.

### Decision 3 — Lean-agent shape conformance per ADR-023 detection variant

The `output-integrity` agent file strictly conforms to the ADR-023 lean-agent detection variant established in Feature 082 for the 11 existing detection-tier agents. Specifically:

- **Single-point load**: exactly one `**MANDATORY**: Read` directive under `## Detection Workflow` section start. No phase-gated loads (unlike the ADR-023 methodology variant used by control-analyzer).
- **Line count discipline**: ≤150 lines soft target (AI tier cap per ADR-023), ≤180 lines hard ceiling. The target applies to the agent file only; companion skill files are not bound by the cap.
- **Zero MAESTRO references**: grep-auditable invariant per spec FR-010. MAESTRO layer classification is orchestrator-owned per Feature 084 / ADR-020; `output-integrity` does not author its own layer field.
- **No `agentic_pattern` in metadata**: pattern classification is orchestrator Phase 3.6-owned per Feature 142 / ADR-026. Per spec FR-016, `output-integrity` does NOT assign `agentic_pattern` on emitted findings — the orchestrator assigns `none` via default (pattern classification applies to multi-agent architectures; output-handling signals are not one of the 6 canonical patterns).
- **Canonical 5-section shape**: YAML frontmatter (name, description, tools, model) → metadata YAML block (category, threat_class, dfd_targets, owasp_references, output_schema) → `## Purpose` → `## Skill References` table → `## Detection Workflow`. Optional `## Example Findings` section permitted (agent files typically include 2-3 worked examples).

ADR-023 Decision 3's `## `-heading byte-identity enforcement on shared-reference edits applies at Wave 3 T029: the `finding-format-shared.md` `consumers:` frontmatter list extension is additive-only; zero edits to any body `## ` heading.

### Decision 4 — LLM05:2025 + ML09:2023 bundling documentation-only per BLP-01 §4

We document LLM05:2025 ("Improper Output Handling" — the 2025 OWASP LLM Top 10 entry) and ML09:2023 ("Output Integrity Attack" — the 2023 OWASP ML Top 10 entry) as a **semantic bundle** in the agent's metadata `owasp_references` list and in the companion `detection-patterns.md` `## Overview` section. Both frameworks describe the same underlying threat class (LLM output flowing unsanitized into downstream sinks); the two framework IDs are cited together in the agent's documentation.

**However, `source_attribution` carries LLM05 ONLY** — the F-A1 catalog at `schemas/taxonomy/owasp.yaml` contains LLM05 as a first-class record; ML09 is an OWASP ML Top 10 2023 entry, which is not presently in the F-A1 catalog (F-A1 transcribed OWASP Top 10 2021 Web + OWASP LLM Top 10 2025 as scope-bounded per ADR-027 Decision 3). Citing ML09 in `source_attribution` would fail the F-A2 referential-integrity validation at `validate_source_attribution` (spec SC-010 BLOCKER). We resolve this by:

1. **Documentation-layer citation**: both LLM05 and ML09 are named in the agent's `owasp_references` metadata field and the companion skill's `## Overview` paragraph. Adopters reading the agent file see both references.
2. **`source_attribution`-layer citation**: only LLM05 (plus applicable CWEs) populates `source_attribution`. F-A1 is the authoritative catalog; future expansion of F-A1 to cover OWASP ML Top 10 MAY enable ML09 inclusion in a future feature, governed by a new ADR amending this one.

This bundling preserves documentation completeness (both framework identifiers are visible to readers) without violating the F-A2 referential-integrity contract. Per BLP-01 §4, the documentation-only bundling pattern is how tachi handles framework references that are semantically relevant but not presently in the F-A1 catalog.

### Decision 5 — 22-file zero-edit invariant preserved with grep-auditable enumeration

F-1 preserves the ADR-023 22-file zero-edit invariant. The 22 frozen files, enumerated for grep audit per spec SC-009 and quickstart.md Step 5:

**6 STRIDE agent files**:

```
.claude/agents/tachi/stride/spoofing.md
.claude/agents/tachi/stride/tampering.md
.claude/agents/tachi/stride/repudiation.md
.claude/agents/tachi/stride/info-disclosure.md
.claude/agents/tachi/stride/denial-of-service.md
.claude/agents/tachi/stride/privilege-escalation.md
```

**5 AI agent files**:

```
.claude/agents/tachi/ai/prompt-injection.md
.claude/agents/tachi/ai/data-poisoning.md
.claude/agents/tachi/ai/model-theft.md
.claude/agents/tachi/ai/agent-autonomy.md
.claude/agents/tachi/ai/tool-abuse.md
```

**11 companion `detection-patterns.md` files**:

```
.claude/skills/tachi-spoofing/references/detection-patterns.md
.claude/skills/tachi-tampering/references/detection-patterns.md
.claude/skills/tachi-repudiation/references/detection-patterns.md
.claude/skills/tachi-info-disclosure/references/detection-patterns.md
.claude/skills/tachi-denial-of-service/references/detection-patterns.md
.claude/skills/tachi-privilege-escalation/references/detection-patterns.md
.claude/skills/tachi-prompt-injection/references/detection-patterns.md
.claude/skills/tachi-data-poisoning/references/detection-patterns.md
.claude/skills/tachi-model-theft/references/detection-patterns.md
.claude/skills/tachi-tool-abuse/references/detection-patterns.md
.claude/skills/tachi-agent-autonomy/references/detection-patterns.md
```

The T048 pre-merge grep audit (`git diff main --stat` on these 22 paths) MUST return zero lines. Orchestrator-tier edits (`.claude/agents/tachi/orchestrator.md`, `.claude/skills/tachi-orchestration/references/dispatch-rules.md`) and shared-reference edits (`.claude/skills/tachi-shared/references/finding-format-shared.md`) are carved out as additive-only per HIGH-1 / HIGH-2 / ADR-023 Decision 3 and are NOT part of the 22-file invariant scope.

### Decision 6 — Proposed → Accepted dual-commit governance protocol

ADR-030 follows the Proposed → Accepted dual-commit pattern established in ADR-027 Decision 8, ADR-028 Decision 7, and ADR-029 Decision 8. Lifecycle:

1. **Day 1 Wave 1.1 (Proposed commit)**: This ADR commits with `Status: Proposed` after the architect Heuristic A ruling at T004 and the schema lock at T006. The Proposed commit is the schema-lock signal that unblocks parallel Wave 2 authoring of the pattern catalog, the agent file, and the mitigation text. All 8 decisions land at Proposed time — no decision is deferred to Accepted.
2. **Day 3 Wave 5 (Accepted transition, pre-PR)**: At T022, this ADR transitions from `Status: Proposed` to `Status: Accepted` with a provisional Accepted-date recorded in Revision History and a `<pending-post-merge-fill>` placeholder on the `Accepted-commit-SHA` field. Wave 4 regeneration completion (T036) plus Wave 5 SC sweep (T040-T051) are the pre-conditions; the ADR Accepted commit is atomic with the provisional PR row in Revision History.
3. **Post-merge (SHA fill)**: At T025, after PR squash-merge to `main`, the `Accepted-commit-SHA` placeholder is replaced with the actual squash-merge commit SHA, and a new Revision History row records "Accepted with post-merge SHA fill | squash commit {SHORT_SHA} | confirmed". The provisional Accepted-date is preserved (not retconned to the UTC merge date) per ADR-027 T039 / ADR-028 post-merge-fill guidance.

Rationale: the dual-commit pattern lets architectural decisions reach Proposed status early (unblocking parallel work) without committing to an Accepted seal before the feature's implementation waves verify the decisions hold. The SHA fill is the last post-merge bookkeeping step and serves as the ADR's provenance anchor.

### Decision 7 — `category: llm` enum reuse (no new category value)

`OI-{N}` findings use the existing `category: llm` enum value — already defined in `schemas/finding.yaml` and already consumed by all 5 pre-existing AI-tier agents (`prompt-injection`, `data-poisoning`, `model-theft`, `agent-autonomy`, `tool-abuse`). We do NOT introduce a new category enum value (`oi`, `output-integrity`, or `llm-output`).

**Rationale**: the downstream infrastructure tier (`risk-scorer`, `control-analyzer`, `threat-report`, `threat-infographic`, `report-assembler`) processes `category: llm` findings through existing code paths. Adding a new category value would require touching the infrastructure tier to handle the new value — violating spec FR-014 (infrastructure-tier invariant). Reusing `llm` keeps F-1 strictly additive at the agent layer and schema layer; zero edits propagate below the agent boundary.

The ID prefix distinction (`LLM-{N}` for existing AI-tier findings vs `OI-{N}` for output-integrity findings) carries the sub-category discrimination needed by future consumers. Downstream aggregators that want to separate output-integrity from other LLM-tier findings can filter on the `id` prefix or on `source_attribution.id = LLM05` — both are machine-readable without category-enum expansion.

### Decision 8 — ADR-026 Complex-Shape Clarifier extended to regex-alternation prefix additions

We extend the ADR-026 minor-bump rule (originally for NEW enum-typed scalar field additions; extended in ADR-028 Decision 1 to NEW list-of-RECORD field additions under the Complex-Shape Addition Clarifier) to cover **regex-alternation prefix additions on existing string fields**. This is the first such extension in tachi's schema evolution.

`schemas/finding.yaml` bumps from `schema_version: "1.5"` to `schema_version: "1.6"` — a **minor bump** — with the following surface change:

```yaml
# Pre-1.6
id:
  pattern: "^(S|T|R|I|D|E|AG|LLM|AGP)-\\d+$"

# Post-1.6
id:
  pattern: "^(S|T|R|I|D|E|AG|LLM|AGP|OI)-\\d+$"
```

The three additive-compatibility conditions from ADR-026 hold for regex-alternation prefix additions:

| ADR-026 Condition | How Decision 8 Satisfies It |
|-------------------|------------------------------|
| (a) Additive | All 9 pre-existing regex alternation values (`S`, `T`, `R`, `I`, `D`, `E`, `AG`, `LLM`, `AGP`) remain valid. `OI` is appended as the 10th alternation value. No removal, rename, or re-typing of any existing prefix. |
| (b) Has default (regex-field equivalent) | The `id` field is a REQUIRED string field (no default) but its acceptance domain EXPANDS rather than narrowing. A parser reading a post-1.6 finding against a pre-1.6 regex would fail on `OI-{N}` IDs but still succeed on the 9 pre-existing prefixes. The FIELD default is not meaningful here (the field is required); the ACCEPTANCE DOMAIN expansion is the analog. All pre-1.6 valid IDs remain valid in 1.6. |
| (c) Schema shape unchanged | Top-level `finding:` mapping remains a single-key document. No new field is added, removed, or re-typed. The `id` field's shape (string with pattern) is unchanged; only the pattern's internal acceptance domain expands. |

**The Complex-Shape Addition Clarifier is extended**: the ADR-026 rule applies uniformly to regex-alternation prefix additions when the three conditions hold — additive alternation values, monotonic acceptance-domain expansion (pre-change IDs remain valid), and unchanged top-level schema shape. Future regex-alternation additions MAY cite this ADR to invoke the same clarifier; other regex modifications (pattern rewrites, alternation removals, character-class narrowing) require explicit future-ADR extension before invoking the minor-bump rule.

**Scope boundary**: Decision 8 does NOT authorize regex-pattern rewrites that REMOVE or RENAME existing alternation values, or that narrow the acceptance domain in any way. Those remain major-bump changes. Decision 8 is a generalization of the existing additive-compatibility rule to a new typing surface (regex alternation), not a relaxation of the additive constraint.

---

## Alternatives Considered

### Alternative 1 — Outcome A (subsume ASI09 into F-1 as sixth pattern category)

Add a 6th pattern category "Human-Trust Exploitation via LLM Output" to F-1's companion skill covering authority claims, urgency framing, false reassurance, and mimicry of trusted roles. Forgo the F-4 `trust-exploitation` agent entirely.

**Why Not Chosen**: detailed in Decision 2 rationale and counter-argument. Signal-class discipline per GUIDE-threat-coverage-research §11 favors separating encoding/sanitization primitives (machine-victim) from psychology/linguistics primitives (human-victim). Outcome A's BLP-01 Tier 1 simplification benefit is real but outweighed by the scope-creep risk to subsequent BLP-01 features and the trigger-keyword-set coherence problem within F-1 itself.

### Alternative 2 — Extend `prompt-injection` agent to cover LLM05 output-handling surfaces

Reopen the existing `prompt-injection.md` agent (frozen per ADR-023 Decision 2 / 22-file invariant) to add output-handling pattern categories.

**Why Not Chosen**: violates the 22-file zero-edit invariant directly. Also violates the signal-class discipline — `prompt-injection` owns the input-side LLM threat surface (LLM01:2025 Prompt Injection), which is a different framework category than LLM05:2025 Improper Output Handling. Merging the two agents would force a wider trigger-keyword set, degrade both halves' detection precision, and set a dangerous precedent that any new LLM-related threat class can be bolted onto the nearest existing LLM agent rather than getting its own focused agent.

### Alternative 3 — New category enum value `output-integrity` or `llm-output`

Introduce a new top-level category value distinct from `llm` for `OI-{N}` findings, enabling downstream aggregators to discriminate purely on category.

**Why Not Chosen**: detailed in Decision 7 rationale. Adding a new category value forces edits to the downstream infrastructure tier (`risk-scorer`, `control-analyzer`, `threat-report`, `threat-infographic`, `report-assembler`) to handle the new value — violating spec FR-014. The ID-prefix distinction + `source_attribution` semantic filter accomplishes the same discrimination without touching the infrastructure tier.

### Alternative 4 — Inline pattern catalog in agent file (no companion skill)

Author the 5 pattern categories directly inside `output-integrity.md` rather than externalizing them to a companion `detection-patterns.md`.

**Why Not Chosen**: violates the ADR-023 lean-agent shape. Pre-refactor agents (before Feature 082) had 113-201 lines with inline content; post-refactor all 11 agents use the lean + skill-references pattern, with companion skill directories holding the pattern catalog content. Inlining would push `output-integrity.md` above the 150-line soft target (5 pattern categories each with 3-6 indicators and ≥1 worked example would consume 200+ lines). The lean + skill-references pattern is the tachi standard; F-1 conforms.

### Alternative 5 — Major schema bump (1.5 → 2.0) rather than minor (1.5 → 1.6)

Treat the regex-alternation prefix addition as a breaking schema change requiring a major-bump and a full ADR-026 rule rewrite.

**Why Not Chosen**: the three ADR-026 additive-compatibility conditions hold (see Decision 8 table). Major-bumping for an additive alternation value would violate the established discipline of minor-bumping for additive schema changes (Features 084, 091, 104, 112, 142, 189 all minor-bumped for additive schema changes). Decision 8 extends the Clarifier surface rather than breaking the additive discipline — this is consistent with the ADR-028 list-of-RECORD extension precedent.

---

## Consequences

### Positive

- **LLM output-handling threat surface closed**. F-1 ships the first detection-tier coverage of OWASP LLM05:2025, eliminating the asymmetric LLM threat-surface gap (input-side comprehensive via 5 existing agents, output-side silent). The 5 pattern categories cover the bulk of the LLM05 threat class.
- **F-A2 contract proven end-to-end against a real producer**. F-1 is the first net-new agent that populates `source_attribution` on every emitted finding. If the F-A2 referential-integrity validator works correctly on `OI-{N}` findings, the F-A2 contract is proven against a real detection-tier populator (not just parser fixtures). Evidence for all 4 Foundation features shipping as a coherent capability unit.
- **F-B coverage-attestation surface gains its first TRUE trigger**. Pre-F-1, all 6 baselines have `has-source-attribution: false` — the conditional Section 9 never renders. Post-F-1 regen on `agentic-app`, `has-source-attribution: true` fires and the F-B coverage-attestation section renders for the first time. F-B's conditional logic is proven against a real populator. The 5 non-agentic baselines still emit `has-source-attribution: false` (byte-identity preserved).
- **ADR-023 lean-agent pattern scales to 6 AI-tier agents**. F-1 is the first net-new addition to the AI tier since Feature 082 stabilized the 5 existing agents under ADR-023. Conformance to the detection variant (single-point load, ≤150 lines, zero MAESTRO) is grep-auditable; the template scales cleanly to a 6th member.
- **ADR-026 Complex-Shape Clarifier extended to regex-alternation prefix additions**. Decision 8 is a durable precedent for future regex-alternation additions. Any future threat-agent family introduction (F-2, F-3, F-4, F-5 under BLP-01) that needs its own ID prefix can cite ADR-030 Decision 8 to invoke the minor-bump rule. The rule is additive — it extends the ADR-026 surface without breaking the additive-compatibility discipline.
- **Heuristic A discipline preserved across BLP-01 Tier 1**. Outcome B keeps F-1 focused on encoding/sanitization primitives and explicitly reserves the psychology/linguistics signal class for F-4. This sets the precedent for how subsequent BLP-01 features handle signal-class overlap: follow §11 Worked Examples rather than subsume adjacent scopes.
- **Zero regression on the 22-file detection tier**. ADR-023 stabilization holds. The 11 frozen detection-tier agent files and the 11 frozen companion skill-reference files are byte-identical at F-1 merge. F-1 is a net-new addition, not a refactor.
- **SC-006 byte-identity preserved by construction**. The 5 non-agentic baselines do not qualify for the `output-integrity` trigger (no LLM-output-to-downstream-sink flows in their DFDs, verified by T012 pre-check for `mermaid-agentic-app`). Agent emits zero findings on non-qualifying architectures. The 5 baselines regenerate byte-identically.
- **Zero new runtime or developer dependencies**. Empty diffs on all dependency manifests. `pyyaml` and `pytest` remain developer-only. Consistent with Features 128 / 180 / 189 / 194.
- **Determinism preserved**. No new orchestrator phase, no new LLM-judgment step, no new HTTP fetch. The agent's pattern matching is a pure function of the architecture input + the companion `detection-patterns.md` rules. ADR-021 byte-identity harness consumes no new knobs.

### Negative

- **Pattern-catalog curation burden**. F-1 requires 5 detection-pattern categories each with 3-6 indicators, ≥1 worked example, and primary/related citations. Authoring 5 categories at pattern-match-quality standard (not generic LLM prose) requires deliberate research. Mitigated by reusing OWASP LLM05:2025 primary source + CWE-22/78/79/89/94/918 secondary sources; categories are well-documented in OWASP and CWE corpora.
- **Trigger-keyword false-positive risk on non-LLM baselines**. The 10 trigger keywords in `detection-patterns.md` could match on non-LLM components if the agent's structural-indicator check (FR-011) is bypassed. Mitigated by the both-keyword-AND-sink-indicator rule in `dispatch-rules.md` Wave 3 edit + T030 FP check on `web-app` and `agentic-app` baselines before Wave 4 regen.
- **F-4 `trust-exploitation` is unscheduled until F-1 merges**. Outcome B forward-references F-4 but does not schedule it. Until F-4 ships, ASI09:2026 remains Planned-with-clear-owner (not Covered). Mitigated by the BLP-01 §8 commitment that F-4 enters `/aod.discover` on F-1 merge.
- **ML09:2023 not in `source_attribution`**. Decision 4 documents ML09 in `owasp_references` metadata and the companion `## Overview` but does not populate it in `source_attribution`. Adopters who filter on `source_attribution.id` see LLM05 only, not ML09. Mitigated by the Overview-prose documentation layer and the forward-compatibility for future F-A1 expansion.
- **Schema 1.6 regex-alternation rule extension is novel**. Decision 8 is the first regex-alternation-specific minor-bump rule. If future regex modifications creep outside the additive-alternation scope (e.g., narrowing a character class, removing an alternation value), a new ADR amending Decision 8 is required. Mitigated by the explicit Scope Boundary paragraph in Decision 8.
- **Example regeneration risk on `mermaid-agentic-app` baseline**. If T012 pre-check or T038 byte-identity fails on `mermaid-agentic-app`, TL-H1 re-baseline escalation fires. T012 ran with zero matches; risk is low but non-zero. Mitigated by the Wave 4 T031 decision-gate review.

### Neutral

- **One new ADR (ADR-030) + one new agent file + one new companion skill**. The feature's surface is well-bounded and comparable to prior net-new agents (Features 141, 142 added orchestrator phases with much larger surface). The ADR body is longer than some (e.g., ADR-022) but comparable to ADR-028 / ADR-029 which similarly carry 7-8 numbered decisions.
- **`category: llm` enum reused** per Decision 7. No new category value; the ID-prefix distinction carries the sub-category discrimination.
- **Forward-compatibility for F-4 `trust-exploitation`**. F-4 will be a separate AI-tier agent with its own `TE-{N}` or similarly-prefixed ID (requiring another Decision-8-style regex extension) and its own companion skill. F-1 does not pre-design F-4 beyond the `## Purpose` forward-reference.
- **MAESTRO Layer 5 inheritance** per ADR-020 lineage. `OI-{N}` findings will inherit L5 Evaluation and Observability layer via orchestrator Phase 1 keyword classification. The agent does not author its own layer field; this is correct per ADR-020 Decision and ADR-023 Decision 4.

---

## Related Decisions

- [ADR-020](ADR-020-maestro-layer-classification.md): MAESTRO layer classification — orchestrator Phase 1 assigns MAESTRO layers based on component type + keyword matching. `OI-{N}` findings inherit L5 layer automatically via orchestrator classification — the agent does not author its own layer field. ADR-020's orchestrator-owned-classification rule is the reason `output-integrity.md` is MAESTRO-free (spec FR-010 invariant).
- [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md): SOURCE_DATE_EPOCH determinism. F-1's Wave 4 regeneration gate (T038) uses `SOURCE_DATE_EPOCH=1700000000` to verify 5-baseline byte-identity. The agent's pattern matching is deterministic (pure function of architecture input + pattern catalog); no new determinism knobs introduced.
- [ADR-022](ADR-022-mmdc-hard-prerequisite.md): mmdc hard prerequisite. Wave 4 T036 `/tachi.security-report` regeneration on `agentic-app` depends on the mmdc Mermaid CLI being installed. The existing preflight gate in `scripts/extract-report-data.py::render_mermaid_to_png()` applies unchanged. F-1 does not introduce new CLI prerequisites.
- [ADR-023](ADR-023-threat-agent-skill-references-pattern.md): lean-agent detection variant + 22-file zero-edit invariant. F-1 is the first net-new AI-tier agent since Feature 082 stabilized the pattern. Decision 3 of this ADR confirms conformance; Decision 5 confirms the 22-file invariant preservation. ADR-023 Decision 3's `## `-heading byte-identity enforcement applies at Wave 3 T029 on the `finding-format-shared.md` additive edit.
- [ADR-026](ADR-026-pattern-classification-mechanism.md): minor-bump rule for NEW enum-typed scalar field additions under three additive-compatibility conditions. This ADR's Decision 8 **extends** ADR-026's rule to regex-alternation prefix additions, following the same three-condition framework. The rule is a durable precedent for future regex-alternation additions; other regex modifications (pattern rewrites, alternation removals, character-class narrowing) require explicit future-ADR extension.
- [ADR-027](ADR-027-taxonomy-crosswalk-schema.md): F-A1 taxonomy schema. F-1's `source_attribution` citations resolve against `schemas/taxonomy/owasp.yaml` (for LLM05) and `schemas/taxonomy/cwe.yaml` (for CWE-22/78/79/89/94/918). F-1 is read-only against the F-A1 catalog; no edits to `schemas/taxonomy/`. ADR-027 Decision 3's 7-value `taxonomy` enum and Decision 5's closed-domain constraint both apply to F-1's attribution emissions.
- [ADR-028](ADR-028-source-attribution-schema-extension.md): F-A2 `source_attribution` contract. F-1 is the first net-new producer of `source_attribution` data. Every `OI-{N}` finding carries `{taxonomy: owasp, id: LLM05, relationship: primary}` plus ≥1 `{taxonomy: cwe, id: CWE-XX, relationship: related}` entry. F-A2's referential-integrity validator at `scripts/tachi_parsers.py:826` enforces the contract on every emission.
- [ADR-029](ADR-029-coverage-attestation-report-section.md): F-B coverage-attestation report section. F-1 is the first net-new feature that causes `has-source-attribution: true` to fire on regeneration — specifically, on `examples/agentic-app/` post-F-1 regen. The F-B conditional Section 9 renders for the first time. F-1 does not edit F-B's renderer logic; the trigger flip is a downstream consequence of F-1's detection-tier emission.

---

## References

- Spec: [`specs/201-output-integrity-threat-agent/spec.md`](../../../specs/201-output-integrity-threat-agent/spec.md) — 3 user stories, 19 FRs, 12 SCs
- Plan: [`specs/201-output-integrity-threat-agent/plan.md`](../../../specs/201-output-integrity-threat-agent/plan.md) — C1..Cn components, Data Flow, R1..R5 risks, wave structure
- Research: [`specs/201-output-integrity-threat-agent/research.md`](../../../specs/201-output-integrity-threat-agent/research.md) — Heuristic A §11 framing, `prompt-injection.md` template baseline, F-A1 catalog verification
- Heuristic A ruling memo: [`.aod/results/heuristic-a-decision.md`](../../../.aod/results/heuristic-a-decision.md) — architect ruling at T004 for Outcome B (split) with counter-argument
- Tasks: [`specs/201-output-integrity-threat-agent/tasks.md`](../../../specs/201-output-integrity-threat-agent/tasks.md) — 55 tasks across 9 phases
- PRD: [`docs/product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md`](../../product/02_PRD/201-output-integrity-threat-agent-2026-04-18.md)
- Schema: [`schemas/finding.yaml`](../../../schemas/finding.yaml) — 1.5 → 1.6 bump per Decision 8
- F-A1 catalog YAMLs: [`schemas/taxonomy/owasp.yaml`](../../../schemas/taxonomy/owasp.yaml), [`schemas/taxonomy/cwe.yaml`](../../../schemas/taxonomy/cwe.yaml) — read-only source for `source_attribution` resolution
- F-A2 parser + validator: [`scripts/tachi_parsers.py`](../../../scripts/tachi_parsers.py) — `parse_threats_findings` + `validate_source_attribution` (unchanged)
- Feature 082 (ADR-023 lean-agent stabilization): [`docs/architecture/02_ADRs/ADR-023-threat-agent-skill-references-pattern.md`](ADR-023-threat-agent-skill-references-pattern.md)
- Feature 189 (F-A2 direct precedent): [`docs/architecture/02_ADRs/ADR-028-source-attribution-schema-extension.md`](ADR-028-source-attribution-schema-extension.md)
- Feature 194 (F-B direct precedent): [`docs/architecture/02_ADRs/ADR-029-coverage-attestation-report-section.md`](ADR-029-coverage-attestation-report-section.md)
- BLP-01 Tier 1 F-1 framing: `_internal/strategy/BLP-01.md` §8 (F-4 forward-reference contract), §4 (documentation-only framework bundling)
- GUIDE-threat-coverage-research §11 — Heuristic A signal-class distinction (encoding/sanitization vs psychology/linguistics primitives)

---

## Revision History

**2026-04-18 (Proposed — Feature 201, Day 1 Wave 1.1 schema-lock commit)**: Records the F-1 `output-integrity` Threat Agent decisions. Documents 8 numbered decisions covering the new AI-tier agent adoption (Decision 1), the Heuristic A Outcome B scope resolution with Outcome A counter-argument per PM M2 (Decision 2), lean-agent shape conformance per ADR-023 detection variant (Decision 3), LLM05 + ML09 documentation-only bundling per BLP-01 §4 (Decision 4), the 22-file zero-edit invariant preservation with grep-auditable enumeration (Decision 5), the Proposed → Accepted dual-commit governance protocol per ADR-027/028/029 precedent (Decision 6), `category: llm` enum reuse without new category value (Decision 7), and the ADR-026 Complex-Shape Clarifier extension to regex-alternation prefix additions under the three additive-compatibility conditions per architect M1 (Decision 8). Heuristic A resolution and D8 regex-extension rule are both recorded at Proposed time; no Decision is deferred to Accepted. Authored at Day 1 Wave 1.1 after T004 Heuristic A ruling and T006 schema bump; serves as the schema-lock signal that unblocks parallel Wave 2 authoring of the pattern catalog, agent file, and mitigation text. Status transitions to Accepted at Wave 5 T022 per Decision 6; `<pending-post-merge-fill>` placeholder on the `Accepted-commit-SHA` field replaced at post-merge T025 with the squash-merge commit SHA.

**2026-04-18 (Proposed → Accepted — Feature 201, Wave 5 T022 transition, PR #NNN pending merge)**: Status transitions from Proposed to Accepted with a provisional Accepted-date. Preconditions verified: Wave 3 orchestrator-tier registration landed (T026-T028 additive-only per HIGH-2 tier grouping and ADR-023 Decision 3 byte-identity); Wave 4 test coverage green (27/27 pass on `tests/scripts/test_output_integrity.py` including F-A2 referential-integrity validation fixture-driven checks; 13/13 pass + 1 skipped on backward-compat suite under `SOURCE_DATE_EPOCH=1700000000` per ADR-021); structural checks green (T029 `## ` heading byte-identity on `finding-format-shared.md`; T030 zero keyword false-positives on `web-app` baseline). The `Accepted-commit-SHA` field carries the `<pending-post-merge-fill>` placeholder until post-merge T025 records the squash-merge commit short SHA per ADR-027/028/029 lineage. All 8 decisions remain as committed at Proposed time — no reinterpretation, no scope change at the Accepted transition.
