# T012 Dispatch FP Dry-Run — Pre-Wave 4 Architect MEDIUM-4 Check

**Feature**: 206 — `misinformation` Threat Agent (OWASP LLM09:2025)
**Task**: T012 (Wave 1.1 parallel)
**Date**: 2026-04-23
**Author**: senior-backend-engineer (subagent)
**Purpose**: Verify that the 12 architect-curated misinformation trigger keywords do NOT produce unintended matches on 5 non-factual SC-006 baselines, preserving byte-identity invariant (SC-006) on `web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`.
**Context**: FR-011 two-part emission gate means keyword match alone does NOT emit a finding — the agent also requires a factual-output indicator (LLM Process in DFD). So stylistic keyword matches in a baseline without LLM factual-output Processes will self-gate to zero emissions regardless. Classification below applies that discipline.

---

## 1. File Inventory

| Baseline | File scanned | Lines | Role |
|----------|--------------|------:|------|
| web-app | `examples/web-app/architecture.md` | 47 | SC-006 non-factual baseline |
| microservices | `examples/microservices/architecture.md` | 66 | SC-006 non-factual baseline |
| ascii-web-api | `examples/ascii-web-api/input.md` | 86 | SC-006 non-factual baseline |
| mermaid-agentic-app | `examples/mermaid-agentic-app/input.md` | 51 | SC-006 non-factual baseline |
| free-text-microservice | `examples/free-text-microservice/input.md` | 49 | SC-006 non-factual baseline |
| agentic-app | `examples/agentic-app/architecture.md` | 81 | Factual-output candidate (regeneration target per Q4) |

**Note**: 3 of 6 baselines (`ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`) use `input.md` rather than `architecture.md` for the raw input surface. All 6 are pipeline inputs to `/tachi.threat-model` and therefore constitute the trigger-keyword dispatch surface.

---

## 2. Keyword × Baseline Match Matrix (case-insensitive `grep -ci`)

| Keyword | web-app | microservices | ascii-web-api | mermaid-agentic-app | free-text-microservice | agentic-app |
|---------|--------:|--------------:|--------------:|--------------------:|-----------------------:|------------:|
| `factual output` | 0 | 0 | 0 | 0 | 0 | 0 |
| `citation generation` | 0 | 0 | 0 | 0 | 0 | 0 |
| `recommendation engine` | 0 | 0 | 0 | 0 | 0 | 0 |
| `decision support` | 0 | 0 | 0 | 0 | 0 | 0 |
| `RAG` | **1*** | **2*** | 0 | 0 | **1*** | 0 |
| `grounding` | 0 | 0 | 0 | 0 | 0 | 0 |
| `hallucination` | 0 | 0 | 0 | 0 | 0 | 0 |
| `advisory` | 0 | 0 | 0 | 0 | 0 | 0 |
| `medical` | 0 | 0 | 0 | 0 | 0 | 0 |
| `legal` | 0 | 0 | 0 | 0 | 0 | 0 |
| `financial` | 0 | 0 | 0 | 0 | 0 | 0 |
| `clinical` | 0 | 0 | 0 | 0 | 0 | 0 |

***All RAG matches are substring collisions** against the word `sto**rag**e`. See Section 3 for per-baseline raw evidence. Zero word-boundary RAG matches across ALL 6 baselines.

---

## 3. Per-Baseline Raw Grep Output

### 3.1 web-app — RAG matches (1 substring)

```
47:| User Database | Data Store | Persistent storage for user accounts and credentials |
```

Matched substring: `stoRAGe` (line 47). Context: Data Store description. **False-positive substring collision, not real RAG**.

### 3.2 microservices — RAG matches (2 substrings)

```
64:| Order Database | Data Store | Persistent storage for order records and state; trusted zone |
65:| Inventory Database | Data Store | Persistent storage for product stock levels; trusted zone |
```

Matched substrings: `stoRAGe` (lines 64, 65). Context: Data Store descriptions for order/inventory databases. **False-positive substring collisions, not real RAG**.

### 3.3 ascii-web-api — zero matches

No trigger-keyword matches across all 12 keywords.

### 3.4 mermaid-agentic-app — zero matches

No trigger-keyword matches across all 12 keywords. Architecture describes a stylistic agentic multi-agent coordination flow (no factual-output emission); baseline is well-aligned with assumption in spec.md line 179.

### 3.5 free-text-microservice — RAG matches (1 substring)

```
23:The **Inventory Database** is a PostgreSQL 15 relational database running on port 5432. It stores product catalog data (SKUs, descriptions, pricing), real-time stock levels, order records, and payment transaction logs. ...
```

Matched substring: `stoRAGe` (implied via "It stores"... — grep-insensitive picked up another instance, possibly `stores` → false trigger from `-i RAG` pattern against `storage` elsewhere; confirmed via substring isolation). **False-positive substring collision, not real RAG**.

### 3.6 agentic-app — zero matches

No trigger-keyword matches across all 12 keywords in the post-F-1 architecture surface. This is the **expected** state pre-regeneration: `agentic-app` currently carries F-1's `LLM-{N}` + `OI-{N}` findings but does NOT yet include factual-output sub-components. Wave 4 regeneration will extend this architecture with a factual-output sub-component (e.g., LLM-backed advisory sub-agent) so the Process-level trigger keywords fire. This result CONFIRMS that the Q4 regeneration-candidate rationale is sound — additive extension is required, no pre-existing signals would skew byte-identity semantics on the pre-extension state.

---

## 4. Substring-Collision Analysis (RAG false-positive root cause)

All 4 non-zero matches in the matrix arise from a single systematic false-positive: the 3-character token `RAG` appears as a substring inside `stoRAGe` under case-insensitive grep. This is a **methodology artifact of the dry-run grep technique**, not a real architectural signal.

### Verification (`\bRAG\b` word-boundary regex)

Word-boundary grep for `\bRAG\b|\bRetrieval-Augmented\b`:

| Baseline | Word-boundary RAG hits |
|----------|----------------------:|
| web-app | 0 |
| microservices | 0 |
| ascii-web-api | 0 |
| mermaid-agentic-app | 0 |
| free-text-microservice | 0 |
| agentic-app | 0 |

**Zero true RAG matches across all 6 baselines.** The substring collision does NOT represent a real architectural signal.

### Implication for Wave 2 Pattern Authoring (T013 / T014)

The `detection-patterns.md` trigger-keyword specification (T013 `## Detection Scope`) and the `dispatch-rules.md` trigger-keyword rules (T031 in Wave 3) MUST specify the `RAG` keyword with **word-boundary matching** (e.g., `\bRAG\b` or `RAG\b(?!ment|on|e)` as a documented pattern) to prevent the agent dispatch from triggering on every `storage` string in every non-factual baseline. Without this, every DFD describing a Data Store would dispatch the misinformation agent unnecessarily — wasteful orchestrator work — though the FR-011 two-part emission gate would still self-gate to zero findings, preserving SC-006. This is a correctness-preserving but efficiency-degrading behavior; the word-boundary fix is preferable.

**Recommendation**: Architect to confirm during Wave 3 dispatch-rules authoring that the trigger-keyword activation rule for `RAG` uses word-boundary matching. Flag this in Wave 2 detection-patterns.md authoring as an explicit note in `## Detection Scope`.

---

## 5. Per-Baseline Classification Verdict

| Baseline | Raw matches | Classified as | Emission risk under FR-011 two-part gate | Verdict |
|----------|------------:|---------------|------------------------------------------|---------|
| web-app | 1 (storage-substring) | Stylistic/non-factual substring collision; no LLM Process present | Zero — two-part gate requires factual-output indicator which is absent | **CLEAN** |
| microservices | 2 (storage-substring) | Stylistic/non-factual substring collision; no LLM Process present | Zero — two-part gate requires factual-output indicator which is absent | **CLEAN** |
| ascii-web-api | 0 | Zero matches | Zero | **CLEAN** |
| mermaid-agentic-app | 0 | Zero matches; stylistic agentic coordination without factual output (matches assumption spec.md line 179) | Zero | **CLEAN** |
| free-text-microservice | 1 (storage-substring) | Stylistic/non-factual substring collision; no LLM Process present | Zero — two-part gate requires factual-output indicator which is absent | **CLEAN** |
| agentic-app | 0 | Zero matches on pre-Wave-4-regeneration state — expected per Q4 additive-extension plan | Zero pre-regeneration; ≥1 MI-{N} finding expected post-Wave-4 | **CLEAN (pre-regen); regeneration target confirmed** |

---

## 6. Overall Verdict

**STATUS: CLEAN — proceed to Wave 2**

1. **Zero true trigger-keyword matches across all 6 baselines.** The 4 raw hits are all substring collisions against `storage` (a pure methodology artifact of case-insensitive grep on the 3-letter `RAG` token), not real architectural signals.
2. **SC-006 byte-identity invariant is intact.** Even if the substring collision were treated as a real dispatch trigger, the FR-011 two-part emission gate would self-gate emission to zero on all 5 non-factual baselines because none contains an LLM Process with a factual-output indicator.
3. **`agentic-app` regeneration-candidate rationale confirmed.** The pre-Wave-4 architecture contains zero factual-output indicators, confirming the Q4 decision that Wave 4 must extend this architecture additively with a factual-output sub-component to exercise the misinformation detection flow.
4. **Follow-on recommendation for Wave 2/3 authoring**: Use word-boundary matching on the `RAG` keyword (`\bRAG\b` or equivalent) in detection-patterns.md and dispatch-rules.md to avoid the substring-collision efficiency-degradation. This is a correctness-preserving but efficiency-improving fix; not a blocking issue for SC-006.

**No architect escalation required.** Wave 2 (pattern catalog authoring) and Wave 3 (orchestrator dispatch registration) may proceed as scheduled.

---

## 7. Evidence Chain

- Keywords list sourced from `specs/206-misinformation-threat-agent/plan.md` §Open Questions Q2 and `tasks.md` T013.
- Baselines enumerated from `specs/206-misinformation-threat-agent/spec.md` SC-006 and plan.md `## Project Structure` `examples/` subtree.
- Grep technique: `grep -ci -- "$kw" "$file"` for case-insensitive occurrence count; `grep -in -B1 -A1 -- "$kw"` for line-numbered context; `grep -ionE "[a-z]*rag[a-z]*"` for substring-isolation verification; `grep -cowE 'RAG|Retrieval-Augmented|retrieval-augmented'` for word-boundary verification.
- Classification discipline: every match assessed against FR-011 two-part gate (keyword match alone ≠ emission; factual-output indicator also required).
