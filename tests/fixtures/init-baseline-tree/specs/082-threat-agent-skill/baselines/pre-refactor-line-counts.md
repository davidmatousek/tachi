# Feature 082 — Pre-Refactor Line Counts

**Capture date**: 2026-04-11
**Branch**: `082-threat-agent-skill`
**Method**: `wc -l` on each of 11 threat agent files in `.claude/agents/tachi/`
**Tier caps** (FR-10, plan.md §1.1): STRIDE ≤120, AI ≤150, hard ceiling 180

---

## STRIDE Agents

| Agent | Lines | Tier Cap | Status |
|-------|-------|----------|--------|
| `spoofing.md` | 113 | 120 | Within cap |
| `tampering.md` | 126 | 120 | Over cap (+6) |
| `repudiation.md` | 124 | 120 | Over cap (+4) |
| `info-disclosure.md` | 128 | 120 | Over cap (+8) |
| `denial-of-service.md` | 141 | 120 | Over cap (+21) |
| `privilege-escalation.md` | 136 | 120 | Over cap (+16) |
| **STRIDE subtotal** | **768** | — | 5 of 6 over cap |

## AI Agents

| Agent | Lines | Tier Cap | Status |
|-------|-------|----------|--------|
| `prompt-injection.md` | 167 | 150 | Over cap (+17) |
| `data-poisoning.md` | 171 | 150 | Over cap (+21) |
| `model-theft.md` | 188 | 150 | Over cap (+38), breaches 180 hard ceiling (+8) |
| `tool-abuse.md` | 185 | 150 | Over cap (+35), breaches 180 hard ceiling (+5) |
| `agent-autonomy.md` | 201 | 150 | Over cap (+51), breaches 180 hard ceiling (+21) |
| **AI subtotal** | **912** | — | 5 of 5 over cap, 3 breach hard ceiling |

---

## Aggregate

| Tier | Agents | Total Lines | Over Tier Cap | Over Hard Ceiling (180) |
|------|--------|-------------|---------------|-------------------------|
| STRIDE | 6 | 768 | 5 of 6 | 0 of 6 |
| AI | 5 | 912 | 5 of 5 | 3 of 5 |
| **Total** | **11** | **1680** | **10 of 11** | **3 of 11** |

**Key observations**:
- Only `spoofing.md` (113 lines) currently satisfies its tier cap — this is consistent with its selection as the STRIDE prototype in T008/T009 (Phase 3.1).
- All 5 AI agents exceed their 150 line tier cap. Three AI agents (`model-theft.md`, `tool-abuse.md`, `agent-autonomy.md`) also breach the 180 hard ceiling, which confirms the urgency of the externalization: the AI tier cannot simply trim whitespace — detection content must move to companion skill references.
- `prompt-injection.md` (167 lines) is the least-over AI agent and is selected as the AI prototype in T010/T011, leaving 17 lines of headroom to absorb into the companion skill once extraction completes.
- Aggregate line count (1680) is the pre-refactor baseline against which Phase 3 regression will measure total delta. Rough expected post-refactor target: STRIDE ≤720, AI ≤750, aggregate ≤1470 (a ~210-line net shrinkage to the agent files, with corresponding content migrating to `.claude/skills/tachi-*/references/detection-patterns.md`).
</content>
</invoke>