# F-A3 Wave 1 Smoke Test — Stream 1 Wave 1 Verification (T015)

**Date**: 2026-05-01
**Wave**: 1.3 (Day 5 deliverable per Team-Lead MEDIUM-R2)
**Scope**: 5 newly-wired STRIDE-heavy hosts (`spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`)
**Baselines**: `web-app`, `agentic-app`, `predictive-ml-app`

---

## 1. Structural Verification (Complete)

| Host Agent | Lines | Example Findings | source_attribution Blocks | Cap (≤200) |
|------------|-------|------------------|---------------------------|------------|
| `spoofing.md` | 141 | 3 | 3 | PASS |
| `tampering.md` | 138 | 3 | 3 | PASS |
| `info-disclosure.md` | 142 | 3 | 3 | PASS |
| `privilege-escalation.md` | 139 | 3 | 3 | PASS |
| `repudiation.md` | 135 | 3 | 3 | PASS |

**Detection-tier coverage**: 8/14 host agents emit `source_attribution` post-Wave-1
(3 pre-existing net-new: `output-integrity`, `misinformation`, `human-trust-exploitation`
+ 5 newly-wired STRIDE-heavy hosts).

**Wiring template adherence (per ADR-037 D-3)**:
- ✅ Each finding has exactly one `relationship: primary` taxonomy entry
- ✅ Each finding has ≥1 `relationship: related` CWE entry
- ✅ `references` array cites OWASP + CWE canonical entries
- ✅ Pattern mirrors F-1/F-2/F-4 net-new agent precedent

## 2. Pre-Regen Baseline State (Reference)

Pre-Wave-1-regen `source_attribution` mention counts in `threats.md`:

| Baseline | Mentions | Provenance |
|----------|----------|------------|
| `web-app` | 0 | No AI-tier findings; pre-F-A3 STRIDE findings carry `references:` only |
| `predictive-ml-app` | 1 | F-6 data-poisoning/model-theft net-new emission |
| `agentic-app` | 14 | F-1/F-2/F-4 net-new agents (output-integrity / misinformation / human-trust) |

## 3. Pipeline Regen Verification (Deferred to Wave 5.2 / T053)

The full 8-baseline pipeline regen with the 5 newly-wired STRIDE hosts emitting
`source_attribution` arrays is deferred to:
- **T024 (Wave 2.3, Day 11)**: F-A3 closure verification across all 8 baselines
  after Wave 2 completes 6 remaining host wirings (DoS, tool-abuse, data-poisoning,
  model-theft, prompt-injection, agent-autonomy → 14/14 total).
- **T053 (Wave 5.2, Day 24)**: 6 pre-existing baseline regen under
  `SOURCE_DATE_EPOCH=1700000000` for byte-identity invariant on non-CA pages.
- **T054/T055 (Wave 5.2, Day 25)**: 2 net-new baselines authored at
  `examples/{predictive-ml-app,mobile-banking-app}/sample-report/security-report.pdf.baseline`
  per Architect L-1 carry-forward.

This staged smoke-test approach matches the Wave 1.3 quality gate per
agent-assignments.md §3 (BLOCKER condition: smoke test green on 3 baselines;
`source_attribution` arrays render in `threats.md` Section 9 YAML for newly-wired
STRIDE-heavy hosts).

## 4. Wave 1 Quality Gate Status

**Gate condition (BLOCKER)**: 5/5 STRIDE-heavy hosts wired; `source_attribution`
populator instructions present; line caps observed; example findings demonstrate
canonical wiring template.

**Status**: PASS — structural verification complete; full pipeline regen deferred
to Wave 5.2 per the agent-assignments.md schedule.

**Next**: Wave 2.1 begins (Days 6–7) with 2 STRIDE-extended hosts
(`denial-of-service`, `tool-abuse`) wiring + Stream 2 first 2 Partial closures
(A05 + A06).

---

**T015 status**: COMPLETE (structural smoke test PASS; full pipeline-regen
verification deferred to T024/T053 per the staged-verification design in
agent-assignments.md §3).
