# Research: Feature 224 — `human-trust-exploitation` Threat Agent (OWASP ASI09:2026)

**Phase**: 0 (preceding plan.md design)
**Date**: 2026-04-26
**Status**: Complete — all key decisions resolved at PRD time per architect Q1-Q6 binding sign-off; verified at plan time by research agent

## Research Questions Resolved

### Q1 — Pattern category count

**Resolution**: 5 categories (architect APPROVE per Q1 binding).

**Reasoning**: F-1 / F-2 5-category floor validated in production use; vulnerable-population fits in category 5 sub-axis (Synthetic-Relationship Exploitation with vulnerable-population safeguards layer); cross-channel persona-bridge attacks deferred to F-7 Mobile bundle. Adding a 6th category without a compelling signal-class differentiator risks scope creep and catalog dilution.

**Final 5 categories**:
1. Undisclosed AI Authorship (CWE-223)
2. Authority-Claim Emission Without Confidence/Source Attestation (CWE-345)
3. Persuasive-Tone Manipulation / Missing Uncertainty Disclosure (CWE-345 + optional CWE-223)
4. Persona-Boundary Violations on Long-Running Dialogues (CWE-287 + CWE-290)
5. Synthetic-Relationship Exploitation (CWE-223 + CWE-290 + vulnerable-population safeguards layer)

### Q2 — Trigger keyword count + persona anti-indicator

**Resolution**: ~22 keywords with `persona` anti-indicator subsection (architect APPROVE 12 baseline; spec FR-005 captures verbatim Q2 enumeration; final count tightened or expanded at architect Wave 1.0 review per architect MEDIUM-A residual concern).

**Reasoning**: Covers consumer-facing AI vocabulary (`chatbot`, `assistant`, `advisor`, `customer-facing`, `companion`, `coach`, `tutor`) plus high-stakes domain signals (`mental health`, `eldercare`, `clinical decision support`, `legal advisor`, `financial advisor`) plus dual-use keywords (`persona`, `personality`, `character agent`) with explicit anti-indicator subsection (when these dual-use keywords appear in prompt-engineering context with no human-user-facing emission, agent emits zero findings).

### Q3 — Category enum

**Resolution**: `category: agentic` (architect APPROVE).

**Reasoning**: OWASP framework attribution decisive — ASI09 is in OWASP Agentic Top 10 (2026). Aligns with `agent-autonomy` and `tool-abuse` precedent. Findings render in `## Agentic Threats` section adjacent to existing AG-{N} and AGP-{N} families (SC-014 three-prefix-family discipline within agentic).

### Q4 — DFD target set (REVERSED per BLOCKING-1)

**Resolution**: Process only with indicator-level human-user filtering (architect REVERSED to BLOCKING-1 fix from PM original lean Process+ExternalEntity).

**Reasoning**: Verification at PRD time showed no AI-tier or agentic-category agent declares External Entity (only STRIDE-only precedents `repudiation`, `spoofing` exist). F-4 would be the first AI-tier agent with this declaration. Defer first-application until justified by a second use case; mirror F-1 / F-2 single-DFD-target pattern. Capture human-user trust boundary at indicator level within `detection-patterns.md` via the 4-category Human-User-Facing Emission Indicators subsection (FR-006).

### Q5 — Example regeneration target (CONDITIONAL per MEDIUM-4)

**Resolution**: New `examples/consumer-agent-app/` (Q5 lean) with conditional fallback to `examples/agentic-app/` extension at Wave 3 Step 1 AM gate (architect MEDIUM-4).

**Reasoning**: New `consumer-agent-app` baseline (chatbot / mental-health-companion / eldercare-coach archetype) demonstrates communication-axis surface cleanly without entangling with F-1 + F-2 + F-3's existing findings on `agentic-app`. Cumulative-complexity argument is sound; 0.5-1 day delta absorbed by buffer; explicit fallback gate documented at Wave 3 Step 1 AM (FR-015). Q5 fallback triggers if (a) architecture-authoring on `consumer-agent-app` exceeds 1 day OR (b) test-harness friction surfaces during fixture authoring.

### Q6 — ADR-033 sequencing

**Resolution**: Day 1 Wave 1.1 Proposed (architect APPROVE).

**Reasoning**: F-1 / F-2 precedent. Proposed → Accepted dual-commit unblocks parallel pattern-catalog authoring downstream of Heuristic A signal-class verification. Day 2 Wave 6 Accepted transition mirrors ADR-030 / ADR-031 / ADR-032 provisional-merge-date pattern; post-merge SHA fill records squash commit (deferred to buffer day per team-lead LOW-2).

## Repo State Verification (verified at plan time by research agent)

### Schema state (`schemas/finding.yaml`)

| Field | Value | Line |
|-------|-------|------|
| `schema_version` | `"1.7"` | 13 |
| `id.pattern` | `"^(S\|T\|R\|I\|D\|E\|AG\|LLM\|AGP\|OI\|MI)-\\d+$"` | 18 |
| `examples:` | 6 entries (S-1, T-3, AG-2, LLM-1, AGP-1, MI-1) | 22-28 |
| `agentic_pattern` enum | includes `trust_exploitation` value (Feature 142) | 162 |

### Catalog state

| Catalog | Entry | Status | Line |
|---------|-------|--------|------|
| `owasp.yaml` | ASI09 with `name: Human-Agent Trust Exploitation`, `cwe_refs: []` | Present | 318-322 |
| `cwe.yaml` | CWE-223 (Omission of Security-relevant Information) | Present | 82 |
| `cwe.yaml` | CWE-287 (Improper Authentication) | Present | 106 |
| `cwe.yaml` | CWE-290 (Authentication Bypass by Spoofing) | Present | 110 |
| `cwe.yaml` | CWE-345 (Insufficient Verification of Data Authenticity) | Present | 118 |
| `cwe.yaml` | CWE-451 (UI Misrepresentation of Critical Information) | **ABSENT** | — |
| `mitre-atlas.yaml` | AML.T0060 (Publish Hallucinated Entities) | Present (offensive use-case; prose-only) | 83-87 |

### Dispatch state

| Surface | Current state | F-4 edit |
|---------|---------------|----------|
| `dispatch-rules.md` Agentic dispatch DUO | `agent-autonomy`, `tool-abuse` (post-F-3) | Extend to TRIO with `human-trust-exploitation` |
| `finding-format-shared.md` `consumers:` | post-F-2 ordering at lines 6-21 | Insert `human-trust-exploitation` between `tool-abuse` (line 18) and `output-integrity` (line 19) |
| `agent-autonomy.md:17` `owasp_references` | includes ASI-09 | NOT EDITED — sub-scope carve-up at ADR-033 layer only |
| `maestro-agentic-patterns-shared.md:220-231` R-04 | `pattern: trust_exploitation`, multi_agent gate | NOT EDITED — Naming Disambiguation contrasts at ADR-033 §"Naming Disambiguation" |

### NFR-006 safe-language framing precedent (existing in F-2 detection-patterns.md)

F-2 worked examples already use "A hypothetical..." / "(fictional scenario; no real institution)" framing at lines 70, 98, 127, 155 of `.claude/skills/tachi-misinformation/references/detection-patterns.md`. F-4 inherits this precedent and extends with the 4 explicit safe-language patterns per architect Pre-Mortem fix R7:
1. Hypothetical: prefix on all worked examples
2. Regulatory framing as "see, e.g., [regulation] — for context, not legal interpretation"
3. Non-clinical distress framing ("user expresses high emotional distress" not "suicidal ideation")
4. No real institutional/clinician/lawyer/advisor/product names

## Open Questions (deferred to plan-time architect review)

- **architect MEDIUM-A**: FR-005 final keyword count alignment between Q2 12-keyword baseline and PRD FR-1 8-bullet enumeration. Spec retains verbatim Q2 enumeration as a starting point with architect license to tighten or expand at Wave 1.0 review. Plan-time tightening expected.

## Out-of-Scope (deferred to follow-on features)

See spec.md §Out of Scope for the full list (16 items including External Entity DFD targets, sixth pattern category, CWE-451 catalog population, ATLAS catalog growth, NIST section IDs, F-5 LLM10, F-6/7/8, cross-channel persona-bridge, adversarial fine-tuning detection, live runtime detection, compliance certification mappings, quantitative trust-exploitation risk-scoring beyond OWASP 3×3, multi-language detection, vulnerable-population pre-deployment review).

## References

- PRD: `docs/product/02_PRD/224-trust-exploitation-threat-agent-2026-04-26.md`
- Spec: `.aod/spec.md`
- Plan: `.aod/plan.md`
- F-1 precedent: `specs/201-output-integrity-threat-agent/`
- F-2 precedent: `specs/206-misinformation-threat-agent/`
- F-3 precedent: `specs/219-asi07-tool-abuse-enrichment/`
- ADR-030 Decision 2 Outcome B (creates F-4's scope): `docs/architecture/02_ADRs/ADR-030-output-integrity-agent.md`
