# NEXT-SESSION Handoff — F-241 Web/API Coverage Attestation + Populator Wiring

**Generated**: 2026-05-01
**Branch**: `241-web-api-coverage-attestation`
**Draft PR**: #242 (`feat(241):` Conventional Commit title verified)
**Wave ceiling reached**: 3/3 (non-orchestrated mode hard stop after Waves 2.1, 2.2, 2.3)

---

## Progress Snapshot

**Tasks complete**: 28/84 (33.3%)
**Waves complete**: 1.1 + 1.2 + 1.3 + 2.1 + 2.2 + 2.3 (Phase 3 / US4 / Stream 1 substantively complete)
**Calendar elapsed**: Days 1–11 (per agent-assignments.md plan)

### Done This Session

**Wave 2.1 — Cross-stream parallel start (T016, T017, T025, T026)**:
- T016 — `denial-of-service.md` populator wired; 143 lines; LLM10:2025 primary on D-3 LLM inference flooding finding (F-5 ADR-034 lineage)
- T017 — `tool-abuse.md` populator wired; 152 lines; ASI-02/04/07 + MCP-05 primaries across AG-1/2/3/4 (added AG-4 inter-agent comm finding citing ASI-07 per F-3 ADR-032)
- T025 — A05 closure on `tachi-privilege-escalation` Cat 11; renamed to "Mobile (M8:2024) and Server-Side (A05:2021)"; 6 server-side indicators + Primary Source block + A05 mitigation bullets
- T026 — A06 closure on `tachi-tampering` Cat 8; renamed to "(OWASP A08:2021 + A06:2021)"; 3 A06-specific indicators (SCA tooling absent, EOL deps, no upgrade cadence) + Primary Source + 3 A06 mitigation bullets

**Wave 2.2 — ML hosts + API8 + Wave 1 fixtures (T018, T019, T027, T029)**:
- T018 — `data-poisoning.md` populator wired; 143 lines; LLM03:2025 + ML06:2023 corpus-side primaries; added LLM-3 finding for predictive-ML public dataset supply chain
- T019 — `model-theft.md` populator wired; 162 lines; LLM03:2025 + ML03:2023 + ML06:2023 artifact-side primaries; added LLM-4 finding for unsigned weight promotion (F-6 ADR-035 D-4 artifact-side lineage)
- T027 — A05/A06 fixtures authored under `stream_2_partial_closures/` (.md format following Wave 1 precedent)
- T029 — API8 closure on Cat 11 (extending T025); 8 API-specific indicators + Primary Source + API8 mitigation bullets

**Wave 2.3 — AI-tier hosts + tests + closure verification (T020, T021, T022, T023, T024)**:
- T020 — `prompt-injection.md` populator wired; 127 lines; LLM01:2025 primary on LLM-1/2/3 with CWE-77 + CWE-94 related (HIGH-A)
- T021 — `agent-autonomy.md` populator wired; 158 lines; ASI-01/06/08/10 primaries distributed across AG-1/2/3/4; ASI-09 retained as related on AG-4 (autonomy axis per F-4 ADR-033 D-2)
- T022 — 6 Wave 2 fixtures authored under `stream_1_f_a3_wiring/` (.md format)
- T023 — `tests/scripts/test_f_a3_populator_wiring.py` authored; 68 tests across 4 test classes; ALL GREEN
- T024 — Structural closure verification artifact at `specs/241-web-api-coverage-attestation/closure-verification-wave-2.md`; full PDF-regen deferred to T053 (Wave 5.2) per staged-verification design

**CHECKPOINT 2 (BLOCKER per SC-001)**: ✅ APPROVED (0 BLOCKING / 0 HIGH / 0 MEDIUM / 0 LOW)
- Architect review at `.aod/results/architect-checkpoint2-241.md`
- SC-001 BLOCKER cleared: 14/14 detection-tier hosts emit `source_attribution`
- SC-003 line cap preserved: largest is `model-theft.md` at 162 lines (under 200 cap)
- All 8 architect criteria pass

### Detection-tier coverage progress

**14/14 host agents** now emit `source_attribution`:
- Pre-existing F-1/F-2/F-4 net-new (3): `output-integrity`, `misinformation`, `human-trust-exploitation`
- F-241 newly-wired Wave 1 (5): `spoofing`, `tampering`, `info-disclosure`, `privilege-escalation`, `repudiation`
- F-241 newly-wired Wave 2 (6): `denial-of-service`, `tool-abuse`, `data-poisoning`, `model-theft`, `prompt-injection`, `agent-autonomy`

### Test status

- `test_f_a3_populator_wiring.py` — 68/68 passing
- `test_backward_compatibility.py` — 13/13 passing + 1 pre-existing skip
- Full project test suite: 81 passed, 1 skipped

---

## Next Actions (Resume Here)

### Wave 3.1 (Days 12–13) — Stream 2 Wave 2 closures

**Parallel tasks (Stream 2 closures)**:
- T028 [P] [US2] Close API6 Unrestricted Access to Sensitive Business Flows → `tachi-tool-abuse` (NEW Indicator category per Q-Plan-1)
- T030 [P] [US2] Close API9 Improper Inventory Management → `tachi-info-disclosure` (NEW Indicator category per Q-Plan-2)
- T031 [P] [US2] Close API10 Unsafe Consumption of APIs (Primary Source on `tachi-tampering` Cat 9 + cross-ref `tachi-info-disclosure` Cat 7)

**Sequential after closures**:
- T032 [US2] Author Wave 2 fixtures (4 YAMLs under `stream_2_partial_closures/`)
- T033 [US2] Verify Stream 2 byte-identity invariant (`tachi-repudiation` + `tachi-spoofing` companion catalogs unchanged)
- T034 [US2] FR-008 deferral path (CONTINGENT — fires if any closure fails)
- T035 [US2] Author `tests/scripts/test_coverage_attestation_audit.py`

**Phase 4 Checkpoint** (end Wave 3.1, Day 13): 6/6 Partial items closed (or surface deferral ADR rationale + follow-on Issue). US2 independently testable via `pytest test_coverage_attestation_audit.py`.

### Wave 3.2 (Days 14–16) — Phase 5 / US1 / Stream 3 OWASP + ATLAS audit

- T036–T039 [P] [US1] OWASP audit + ATLAS expansion + record-shape +2-field extension
- (ATT&CK expansion deferred to Wave 4.1+4.2 Days 17–19)

---

## Prerequisites for Next Session

- ✅ Branch `241-web-api-coverage-attestation` is current
- ✅ Draft PR #242 open with `feat(241):` Conventional Commit title
- ✅ Wave 2 work committed (commit `3e10019`)
- ✅ Wave 1 work committed (commit `7ba5447`)
- ✅ ADR-037 stub at status: Proposed (full narrative deferred to T059 / Wave 5.3)
- ✅ All 11 newly-wired Wave 1+2 STRIDE+AI hosts under 200-line cap
- ✅ `test_f_a3_populator_wiring.py` 68/68 passing
- ✅ `test_backward_compatibility.py` 13/13 passing
- ✅ CHECKPOINT 2 architect sign-off APPROVED (0/0/0/0)

**Suggested resume command**:
```
claude "Resume F-241 Web/API Coverage Attestation. Branch: 241-web-api-coverage-attestation. Waves 1.1-1.3 + 2.1-2.3 complete (28/84 tasks); CHECKPOINT 2 APPROVED. Run /aod.build to continue with Wave 3.1 (T028, T030, T031, T032, T033, T035)."
```

---

## Architect Carry-Forwards (still pending)

- **M-1**: ADR-027 forward-pointer addendum cross-linking ADR-037 D-7 (T060 + T083, Wave 5.3)
- **M-2**: Aggregator filter at line 1073/1101 not 1144 (T044 + T045 + T084, Wave 4.3)
  - Already documented in ADR-037 stub D-8 narrative
- **L-1**: Canonical baseline paths for predictive-ml-app + mobile-banking-app (T054 + T055 + T081)
  - Already verified at T006

---

## Out-of-Session Risks

1. **Pre-existing baseline byte-identity** — non-CA pages on 6 pre-existing baselines must remain byte-identical under `SOURCE_DATE_EPOCH=1700000000`. The Wave 1+2 wiring is pure addition to agent definitions; should not affect determinism. Verified at Wave 5.2 T058.
2. **F-7 28-file zero-edit invariant** — F-241 has now modified 11 host agents + 2 Stream 2 companion catalogs (within scope). T075 will verify final compliance with the 11+up-to-5 modification budget.
3. **schema unchanged at v1.8** — confirmed at T008; no `id.pattern` regex extension needed (F-241 reuses S/T/I/E/R + LLM/AG/AGP prefixes).
4. **Deferred PDF-regen verification** — T024's structural-only closure verification deferred the PDF-rendered Coverage Attestation section validation to T053 (Wave 5.2, Days 24–25). The 8-baseline regen under `SOURCE_DATE_EPOCH=1700000000` will be the final SC-007 / SC-009 / SC-015 BLOCKER verification.

---

**End of NEXT-SESSION handoff** — 28/84 tasks complete (33.3%); resuming at Wave 3.1.
