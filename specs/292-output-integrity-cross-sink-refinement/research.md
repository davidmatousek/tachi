# Research Summary: F-292 Output-Integrity Cross-Sink Refinement

**Feature**: F-292 — Output-Integrity Cross-Sink Refinement
**PRD**: [docs/product/02_PRD/292-output-integrity-cross-sink-refinement-2026-05-14.md](../../docs/product/02_PRD/292-output-integrity-cross-sink-refinement-2026-05-14.md)
**Date**: 2026-05-14
**Sources**: 4 parallel research streams (KB, codebase, architecture, web)

---

## Knowledge Base Findings

**Direct architectural precedents**:
- ADR-030 (F-1 baseline) — Decision 2 establishes encoding/sanitization signal-class fence; F-292 must respect it
- ADR-032 (F-3 tool-abuse enrichment) — closest structural sibling: single-agent scope, no schema bump, additive-only, authored ADR
- ADR-035 (F-6 ML Top 10 bundle) — multi-host enrichment precedent; D4 two-facet disjoint-tells pattern applicable to Gap 3 framing
- BLP-01 strategy doc — F-292 is the **eighth Heuristic A enrichment execution** at single-agent scope

**Community-merge precedent (F-260)**:
- @north-echo PR #262 merged 2026-05-06 within ~4 days of discussion
- Authorship preservation: native GitHub PR authorship + Constitution IX `Co-Authored-By:` trailer + CHANGELOG attribution line
- F-260 contributor declined follow-on offer → F-292 Q5 default-to-(b) fallback empirically supported
- Comment-first-give-choice policy is canonical (path A default)

**Key lessons that should inform the spec**:
1. Heuristic A enrichment branch delivers cheapest (5/5-dimension reduction validated 7+ times)
2. Signal-class fence MUST be operationalized as a testable invariant (FR-7 + SC-5 are the operational tests)
3. ADR authorship is the BLP-01 lineage default — no Heuristic A enrichment skips an ADR
4. Memory-Promotion Rules is novel surface (no prior tachi pattern) — treat as institutional-knowledge seed
5. Over-scoped byte-comparison is a known F-248-style trap — restrict no-emission tests to `output-integrity`-tagged findings
6. CWE-943 (not CWE-89) is the canonical primary anchor for non-SQL query-language injection

**Patterns to follow** (validated 7+ times): additive-only edit discipline, Pattern Category Disambiguation subsection, Proposed → Accepted dual-commit ADR governance, F-A2 source_attribution referential integrity, community-merge attribution chain.

**Patterns to avoid**: over-scoped byte-comparison, schema bump for prefix segmentation, modifying cross-link target agents, per-output master-content modification, eager context loading from cross-link prose.

---

## Codebase Analysis

**Target files (audit-ready)**:
- `.claude/skills/tachi-output-integrity/references/detection-patterns.md` — 151 lines, 5 pattern categories (Cat 1-5). Insertion point for Cat 6 / Gap 3 prose: after line 151.
- `.claude/agents/tachi/output-integrity.md` — 120 lines (under ≤180 hard ceiling). Cross-link injection point: Purpose section line 27, before F-4 forward-reference.
- `.claude/agents/tachi/tool-abuse.md` — 152 lines, EXISTS ✓. Cross-link target anchor: "Insecure Inter-Agent Communication" phrase at Purpose line 27.
- `.claude/agents/tachi/data-poisoning.md` — 143 lines, EXISTS ✓. Cross-link target anchor: "poisoned RAG knowledge bases" phrase at Purpose line 35-36.
- `schemas/finding.yaml` — Current version 1.8 post-F-4. OI prefix confirmed at line 18 regex (no bump needed).
- `schemas/taxonomy/cwe.yaml` — CWE-943 confirmed at line 238 (alphabetical, post-F-2 expansion).

**ADR slot availability**: ADR-043 RESERVED for BLP-03 cosign-vs-minisign; ADR-044 used by Dual-Frame Public Positioning. **ADR-045 is the next available slot for F-292**.

**CHANGELOG F-260 attribution format** (verbatim):
```markdown
* **260:** asset-sensitivity tag prototype ([#262](https://github.com/davidmatousek/tachi/issues/262)) ([3dfe6a7](https://github.com/davidmatousek/tachi/commit/3dfe6a7...))
```

**Multi-agent baselines available for SC-5 cross-link no-emission verification**:
- `agentic-app/` (7 agents, 7 MCP) — **IDEAL** for SC-5; already F-1 mutation target
- `maestro-reference/` (12 agents, 13 MCP) — secondary; comprehensive multi-agent topology

**Non-qualifying baselines (must remain byte-identical)**: `web-app/`, `microservices/`, `ascii-web-api/`, `mermaid-agentic-app/`, `free-text-microservice/` — 5 baselines per NFR-1.

---

## Architecture Constraints

**Constitution Principle X (verbatim quote)** — line 394 of `.aod/memory/constitution.md`:
> **Architect documents all architectural decisions in docs/architecture/02_ADRs/**

This mandates ADR authorship for architectural decisions. The PRD's Q3 lean (author ADR-045 per BLP-01 lineage) is constitutionally mandated, not optional.

**ADR-030 Decision 2 (signal-class scope)**: F-292 must stay within the **encoding/sanitization signal class** (machine-victim output handling per LLM05:2025). MUST NOT spill into psychology/linguistics (F-4 / ADR-033 scope).

**ADR-030 Decision 8 (OI-{N} prefix)**: schema 1.6 added `OI` to regex alternation. Current schema is 1.8 post-F-4. F-292 reuses prefix — **no schema bump required**.

**ADR-032 7-decision structure** (closest sibling, F-292 ADR should mirror):
- D1: Heuristic A enrichment vs new agent — signal-class identity rationale
- D2: Additive-only edit discipline per ADR-023 D3
- D3: No schema bump — operational signal of signal-class identity preservation
- D4: No consumers-list edit
- D5: No functional orchestrator/dispatch edit
- D6: Public ADR omits commercial framing per SDR-001 Option C
- D7: Pattern Category Disambiguation

**ADR-021 byte-identity discipline**: `SOURCE_DATE_EPOCH=1700000000` for all baseline regeneration and backward-compatibility test runs. 5 non-qualifying baselines must regenerate byte-identical.

**ADR-035 D4 two-facet disjoint-tells pattern**: applicable to Gap 3 framing — same architecture surfaces output-integrity finding AND tool-abuse/data-poisoning findings with disjoint mitigation taxonomies, not duplicates.

**Hard constraints (non-negotiable)**:
1. ADR authorship is MANDATORY (Constitution Principle X)
2. Heuristic A signal-class discipline (no F-4 spillover)
3. No schema bump (operational signal of signal-class identity)
4. 22-file zero-edit invariant (frozen STRIDE/AI tier + frozen companions + non-target hosts)
5. Byte-identity on non-qualifying baselines (`SOURCE_DATE_EPOCH=1700000000`)
6. F-1 `source_attribution` populator-wiring contract preserved

---

## Industry Research

**Gap 1 (Vector-Filter Injection)**:
- **OWASP LLM08:2025 Vector and Embedding Weaknesses** is the canonical industry anchor; OWASP explicitly enumerates "missing tenant isolation in multi-tenant RAG systems" as a vulnerability
- **CWE-943** (PRD FR-3) is correctly the primary anchor (canonical parent for non-SQL query-language injection)
- Industry-named mitigations align with PRD: **pre-retrieval filtering** (Microsoft Azure, AWS Bedrock+OpenSearch), **base filter that cannot be overridden** (Mavik Labs, Authzed), **permission-aware vector database** (OWASP LLM08 mitigation language)
- Strongest control per OWASP: **separate collections/namespaces per tenant** (Silo model); metadata-filtering is secondary (Pool model). Worked example should make Silo-vs-Pool trade-off visible.

**Gap 2 (Package-Manager / CI-Workflow Sinks)**:
- 2026 incident record: **SANDWORM_MODE npm worm** (Sep 2025 → Apr 2026) injecting prompt-injection into AI assistant tool descriptions; **LiteLLM PyPI compromise** (Mar 2026) exfiltrating creds via `.pth` payload
- Academic anchor: arXiv 2605.07135 "Demystifying and Detecting Agentic Workflow Injection in GitHub Actions" formalizes **AWI (Agentic Workflow Injection)** attack pattern
- Industry-named mitigations: **allowlist of registries and scopes** (NVIDIA/Nesbitt), **microVM isolation / gVisor / hardened container** (canonical 2026 isolation trio), **Sigstore-backed package signing** (npm + PyPI rolled to production 2025)
- Recommendation: loosen FR-5 OR-phrasing to "at minimum one of {allowlist, sandbox, signature gate} with defense-in-depth note recommending all three"

**Gap 3 (Memory-Promotion Rules)**:
- **OWASP ASI06 Memory & Context Poisoning** (NOT LLM04 which is training-time) is the canonical anchor; OWASP has dedicated **Agent Memory Guard** project
- Academic anchors: **A-MEMGUARD** (arXiv 2510.02373) — "staging buffer with validation rather than direct write to live store"; **MemoryGraft** (arXiv 2512.16962); **MINJA Memory Injection Attack** (arXiv 2601.05504, >95% success rate without schema validation)
- Industry implementations: **AWS Bedrock AgentCore Memory** (scope/namespace dicts), **Vertex AI Memory Bank** (IAM conditions), **Scalekit access-control patterns**
- Additive recommendation: surface **human approval gate** as optional layered control beyond schema validation alone

**Community-Merge Precedent (F-260)**:
- Aligns with Google Open Source Casebook: "commit log is the most accurate record of contributors' work"
- `Co-Authored-By:` trailer is GitHub-recognized standard for shared credit
- AUTHORS file / CHANGELOG attribution is industry-standard supplementary recognition

**Source quality**: 25+ Tier 1-2 sources gathered; ≥85% are 2025-2026 publications. No PRD approach contradicted.

---

## Recommendations for Spec

1. **Adopt OWASP framework language verbatim**:
   - Gap 1 → "OWASP LLM08:2025 Vector and Embedding Weaknesses" + "missing tenant isolation in multi-tenant RAG systems"
   - Gap 2 → "OWASP LLM05:2025 Improper Output Handling" + "agentic workflow injection (AWI)"
   - Gap 3 → "OWASP ASI06 Memory & Context Poisoning" + "OWASP Agent Memory Guard" (NOT LLM04)

2. **Promote layered controls over single-control framing** in FR-5 and Gap 1 worked-example acceptance.

3. **Surface the Silo-vs-Pool trade-off** in Gap 1 worked example: namespace-per-tenant (Silo) is strongest; metadata-filter pinning (Pool) is secondary.

4. **Add A-MEMGUARD "staging buffer" framing** to Gap 3 Memory-Promotion Rules as optional layered control.

5. **Cite 2026 supply-chain incident record** (SANDWORM_MODE, LiteLLM) in Gap 2 worked example for real-world urgency.

6. **Respect signal-class fence**: Gap 3 cross-links are navigational only; `output-integrity` does NOT emit findings on tool-arg or memory-write flows.

7. **Use industry-recognized mitigation terms**: pre-retrieval filtering, base filter that cannot be overridden, microVM isolation, Sigstore-backed signing, staging buffer with validation, namespace-scoped memory.

8. **Anchor ADR-045 in spec references** (next available slot, ADR-043 reserved for BLP-03).

9. **Restrict regression-test scope to OI-tagged findings** (avoid F-248 over-scoped byte-comparison trap).

10. **Preserve F-260 community-merge playbook**: comment-first-give-choice (path A default), 7-day SLA, `Co-Authored-By:` trailer if (b) maintainer-authored, CHANGELOG attribution either way.

---

## Detail Files

Full research detail is preserved in `.aod/results/`:
- `spec-research-kb.md` — Knowledge Base findings
- `spec-research-codebase.md` — Codebase analysis
- `spec-research-architecture.md` — Architecture constraints
- `spec-research-web.md` — Industry / OWASP / academic references
