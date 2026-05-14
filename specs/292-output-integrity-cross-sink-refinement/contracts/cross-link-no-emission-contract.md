# Contract: Cross-Link No-Emission Invariant

**Feature**: F-292
**Phase**: 1 (Design)
**Date**: 2026-05-14

This contract codifies the **FR-007 testable invariant** that the Gap 3 Cross-Agent Handoff Sinks subsection MUST be **navigational only** — it does NOT cause the `output-integrity` agent to emit findings on tool-call-argument or durable-memory-write flows.

---

## 1. The Invariant

**Statement**: Adding the Cross-Agent Handoff Sinks subsection to `detection-patterns.md` MUST NOT change the count or content of `output-integrity`-tagged findings on any existing baseline.

**Domain**: All existing tachi example baselines, with particular focus on multi-agent architectures where tool-call-argument and durable-memory-write flows are present.

**Operational definition**:
- Before F-292 merge: baseline `B` produces `N` `OI-{N}`-tagged findings
- After F-292 merge: baseline `B` produces exactly the same `N` `OI-{N}`-tagged findings
- The `OI-{N}`-tagged finding subset is byte-identical under `SOURCE_DATE_EPOCH=1700000000`

---

## 2. Why the Cross-Link Prose Cannot Trigger Emissions

**Mechanism (per Assumption A-6 in spec)**: The `output-integrity` agent's existing detection workflow enforces the both-signal requirement:
1. **Trigger keyword** must be present in the architecture description
2. **Downstream sink indicator** must also be present (the indicator naming an actual encoding/sanitization sink — XSS DOM, server-side execution, SSRF URL, template engine, path traversal, OR the new Cat 6 vector-DB filter)

The Cross-Agent Handoff Sinks subsection introduces **no new trigger keywords** and **no new downstream sink indicators**. It is purely navigational prose pointing to adjacent agents. The agent's existing workflow §6 enforcement (return zero findings if both-signal requirement not satisfied) carries through unchanged.

**No `**MANDATORY**: Read` directive added** (per Avoid pattern #5 from KB): the cross-link subsection does NOT instruct the agent to read `tool-abuse.md` or `data-poisoning.md` at runtime. The pointer is for human-reader navigation, not for runtime context loading.

---

## 3. Verification Test (SC-003)

**Test fixture**: `examples/agentic-app/` baseline (7 agents, 7 MCP — per spec research codebase analysis, this is the IDEAL multi-agent test fixture).

**Test procedure**:

```bash
# Step 1: Baseline OI-tagged finding subset BEFORE F-292
SOURCE_DATE_EPOCH=1700000000 tachi.threat-model examples/agentic-app/architecture.md > /tmp/oi-pre-292.json
jq '.runs[0].results[] | select(.ruleId | startswith("OI-"))' /tmp/oi-pre-292.json > /tmp/oi-pre-292-scoped.json

# Step 2: Apply F-292 refinement (Cat 6 + Cat 2 keyword extension + Cross-Agent Handoff Sinks subsection + agent file cross-link prose)
# (Done by the implementation tasks per tasks.md)

# Step 3: Baseline OI-tagged finding subset AFTER F-292
SOURCE_DATE_EPOCH=1700000000 tachi.threat-model examples/agentic-app/architecture.md > /tmp/oi-post-292.json
jq '.runs[0].results[] | select(.ruleId | startswith("OI-"))' /tmp/oi-post-292.json > /tmp/oi-post-292-scoped.json

# Step 4: Byte-identical comparison (SC-003 expected: zero diff)
diff /tmp/oi-pre-292-scoped.json /tmp/oi-post-292-scoped.json
# Expected: empty output (byte-identical)
```

**Scope restriction (per PM L-2 resolution + KB Entry 1 / F-248 lesson)**: The byte-identical comparison is restricted to the `OI-{N}`-tagged finding subset, NOT the whole pipeline output. Whole-pipeline byte-identity is owned by SC-004 on the 5 non-qualifying baselines (where output-integrity emits zero today and zero after).

**Rationale for scoped comparison**: F-248 institutional lesson — whole-tree byte-comparison fixtures drift when unrelated content additions occur. Restricting to `OI-{N}`-tagged subset anchors the test to the actual invariant being protected (cross-link prose does not cause OI emissions). Other agents' findings on the same baseline (e.g., `tool-abuse`, `data-poisoning`) may legitimately change for unrelated reasons; those changes are not in scope for the F-292 cross-link no-emission invariant.

---

## 4. Distinguishing-Prose Requirement (PM M-2 Resolution)

**Issue**: The Gap 1 vector-filter signal (output-handling — filter SYNTHESIS goes wrong) is conceptually adjacent to `data-poisoning` corpus signals (corpus CONTENT goes wrong). Readers may conflate the two and miss why both findings may co-emit on the same multi-tenant RAG architecture.

**Resolution**: The Cat 6 worked example in `detection-patterns.md` MUST include a **distinguishing-prose block** (≥1 sentence, ≤2 sentences) that:
1. States the boundary explicitly: "This is an output-handling signal — the LLM's *filter SYNTHESIS* goes wrong. It is distinct from `data-poisoning` corpus-side signals where the *corpus CONTENT* goes wrong."
2. Acknowledges co-emission: "Both findings can co-emit on the same multi-tenant RAG architecture without contradiction."
3. Provides navigational pointer: "See `.claude/agents/tachi/data-poisoning.md` for the corpus-content surface."

**Verification**: grep-auditable check on `detection-patterns.md` post-merge:
```bash
grep -c "filter SYNTHESIS goes wrong" .claude/skills/tachi-output-integrity/references/detection-patterns.md
# Expected: >= 1
```

---

## 5. Agent File Diff Cap

**Cap (FR-009 / SC-005)**: Total diff of `.claude/agents/tachi/output-integrity.md` ≤10 lines.

**Verification**:
```bash
git diff main -- .claude/agents/tachi/output-integrity.md | grep -E "^[+-]" | grep -vE "^[+-]{3}" | wc -l
# Expected: <= 10
```

**Approved cross-link prose** (per data-model.md §4): 6 lines of prose. Well under the cap; 4 lines of headroom for paragraph break or formatting tweaks.

---

## 6. No-Emission Counter-Tests

To strengthen confidence in the invariant, also verify on **multiple multi-agent baselines** (per data-model.md §6 if Q2=Add, the new `multi-tenant-rag-app/` baseline becomes an additional fixture):

```bash
# `agentic-app/` (7 agents, 7 MCP)
diff <(jq '.runs[0].results[] | select(.ruleId | startswith("OI-"))' /tmp/agentic-pre.json) \
     <(jq '.runs[0].results[] | select(.ruleId | startswith("OI-"))' /tmp/agentic-post.json)

# `maestro-reference/` (12 agents, 13 MCP — secondary fixture per spec research)
diff <(jq '.runs[0].results[] | select(.ruleId | startswith("OI-"))' /tmp/maestro-pre.json) \
     <(jq '.runs[0].results[] | select(.ruleId | startswith("OI-"))' /tmp/maestro-post.json)
```

**Expected on both**: byte-identical OI-scoped finding subsets.

---

## 7. Acceptance Tests

| Contract Invariant | Acceptance Test | Spec Anchor |
|---|---|---|
| Cross-link prose does not add trigger keywords | grep `detection-patterns.md` Gap 3 subsection for known Cat 1–6 keywords — match count unchanged from pre-F-292 | FR-007 |
| Cross-link prose does not add sink indicators | Manual review of Gap 3 subsection content — confirm no XSS/DOM/SQL/SSRF/template/path-traversal/vector-filter sink indicator introduced | FR-007 |
| Agent file diff ≤10 lines | `git diff main` line-count check | FR-009 + SC-005 |
| `agentic-app/` OI-scoped byte-identical | diff of jq-filtered SARIF output | SC-003 |
| Distinguishing-prose block present | grep for "filter SYNTHESIS goes wrong" | PM M-2 resolution |
| No `**MANDATORY**: Read` directive added | grep `detection-patterns.md` Gap 3 subsection for "MANDATORY" — must be absent | KB Avoid pattern #5 |
