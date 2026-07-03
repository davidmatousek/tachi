# SC-015 Verification Record — F-292 T026 / Cat 6 Evidence Baseline

**Feature**: #295 | **User Story**: US2 (Phase 4, T012–T016) | **Date**: 2026-07-03
**Owner**: security-analyst | **Attempt cap**: 2 live runs — **both consumed** (attempt 1: tooling-orphaned, not usable; attempt 2: fully executed to a gate-evaluable artifact set)

**Verdict: FAIL** — gate executed honestly; disposition is defect-filed stop, not silent pass, per spec FR-018/FR-020 and tasks.md T013.

---

## 1. Run provenance

### Attempt 1 — tooling failure, orphaned, unused

**Command / dispatch**: `tachi-orchestrator` dispatched against `examples/multi-tenant-rag-app/architecture.md` with its 11 threat agents launched under background execution; the orchestrator instance ended its turn before the children completed.

**Result**: the parent orchestrator instance could never collect the dispatched agents' results — a tooling failure, not a detection or compilation failure. The child agents kept running after the parent's turn ended and their results were later delivered directly to the orchestrating session, **not** to the (already-concluded) parent orchestrator instance. Because no parent instance existed to receive and compile them, attempt 1 produced no usable compiled artifact and was **not** counted as a gate outcome — only as a consumed attempt (per FR-021's 2-attempt cap) and as a tooling-failure data point.

**Preserved evidence**: the attempt-1 `tachi-output-integrity` agent's verbatim, uncompiled return is committed at `specs/295-f292-verification-runs/test-results/t026-attempt1-orphan-oi-return.md` — used in this record purely as **corroborating counter-evidence** (§4) that the sub-agent itself reliably emits the `OI-` prefix and CWE-943 citation for this exact architecture. Its late-arriving output was **not** mixed into, spliced with, or otherwise used to construct attempt 2's compiled artifacts — attempt 2 (below) is a fresh, fully independent, fully synchronous run.

### Attempt 2 — fully executed, gate-evaluable, FAIL

**Command** (per tasks.md T012):
```bash
SOURCE_DATE_EPOCH=1700000000  # exported; convention-uniformity only — the SARIF generators
                                # are timestamp-free, so regen byte-identity is structural
                                # and needs no env pin (spec.md Assumptions)
/tachi.threat-model examples/multi-tenant-rag-app/architecture.md \
  --output-dir examples/multi-tenant-rag-app/test-output/
```

This resolved to the timestamped run directory:
```
examples/multi-tenant-rag-app/test-output/2026-07-03T13-28-42/   (gitignored — examples/*/test-output/ is excluded)
```

**Provenance**: all 5 pipeline phases completed (Phase 5 — narrative/report — was ON, per US-2 scenario 1, since `threat-report.md` is a required artifact for the eventual baseline). 51 raw findings → 43 deduplicated findings (4 correlation groups absorbing 12 raw findings into 4 unique threats); 17 Critical / 17 High / 8 Medium / 1 Low. Populator step ran: every finding's Affected Assets row is `[]` (confirmed — the architecture carries no `[asset:...]` tags, an all-`[]` block is valid per FR-010/data-model.md entity 4).

**Files produced**:
```
examples/multi-tenant-rag-app/test-output/2026-07-03T13-28-42/
├── architecture.md
├── threats.md          (67,453 bytes)
├── threats.sarif        (88,551 bytes)
├── threat-report.md    (130,312 bytes)
├── attack-chains.md     (18,518 bytes)
└── attack-trees/        (42 files + manifest)
```

No overflow occurred; the known Phase-5 overflow risk (spec.md Edge Cases) did not manifest on this run.

---

## 2. T013 — Cat 6 gate evaluation

Per tasks.md T013 / spec FR-009: run-output `threats.md` MUST contain ≥1 `OI-*` finding on the Cat 6 surface (CWE-943 primary; Pinecone `tenant_id`-omission shape per `examples/multi-tenant-rag-app/architecture.md:92`). On zero, the gate is a fail-closed ERROR-stop, never a pass.

**Commands run against the attempt-2 output** (re-verified for this record):
```bash
$ grep -c "| OI-" examples/multi-tenant-rag-app/test-output/2026-07-03T13-28-42/threats.md
0

$ grep -c "CWE-943" examples/multi-tenant-rag-app/test-output/2026-07-03T13-28-42/threats.md
0

$ jq '[.runs[0].results[] | select(.partialFingerprints["findingId/v1"] // "" | startswith("OI-"))] | length' \
    examples/multi-tenant-rag-app/test-output/2026-07-03T13-28-42/threats.sarif
0
```

**GATE VERDICT: FAIL.** All three independent checks (markdown ID-prefix, markdown CWE citation, SARIF findingId-prefix) return zero. FR-009 requires ≥1 on each axis.

---

## 3. The pattern surface WAS detected — present but misprefixed as `LLM-10`/`LLM-11`

This is a **compilation-tier** defect, not a **detection-tier** defect. `threats.md` (Section 4, LLM Threat Table) contains two rows that fully describe the Cat 6 mechanism and explicitly self-label it as such:

| ID | Component | Risk | OWASP refs | Threat text (verbatim) |
|---|---|---|---|---|
| `LLM-10` | LLM Query Synthesizer | Critical | LLM05:2025, LLM08:2025 | "The synthesizer's output is executed by Pinecone's metadata-filter DSL — a search-DSL query-execution engine analogous to a SQL WHERE clause — against the entire Pool-model shared index with no server-side validation that the tenant clause is present. **This is Cat 6 Vector/Search-DSL Injection.**" |
| `LLM-11` | RAG Retriever | Critical | LLM05:2025, LLM08:2025 | "RAG Retriever receives the LLM-emitted filter and forwards it byte-for-byte into Pinecone's query-execution engine without inspecting, validating, or supplementing it — the last control point before **Cat 6 Vector/Search-DSL Injection** reaches execution against the shared index." |

Both rows: Critical severity, correct OWASP pair (LLM05:2025 primary output-handling + LLM08:2025 vector/embedding weaknesses), explicit "Cat 6 Vector/Search-DSL Injection" self-label, base-filter-pinning + namespace-per-tenant mitigations matching the architecture's own design intent (`architecture.md:92`). **Neither row carries an `OI-` id or a CWE-943 citation.**

They are structurally indistinguishable from `LLM-1`..`LLM-9` (prompt injection LLM01, data poisoning LLM04/LLM03, model theft LLM10, quota theft LLM10) and `LLM-12`/`LLM-13` (misinformation LLM09) — all 13 findings sit in one contiguous, undifferentiated `LLM-N` id sequence with no sub-heading or id-family boundary marking which findings originated from the `tachi-output-integrity` agent specifically. The Coverage Matrix (`threats.md` Section 5) reinforces this: there is no distinct "OI" column, only a combined "LLM" column. A full ID-prefix inventory of the compiled `threats.md`/`threats.sarif` confirms **zero** `OI-` prefixed findings anywhere in the run output — the entire output-integrity contribution landed inside the `LLM-N` sequence.

`scripts/sarif_common.py::PREFIX_TO_RULE` maps both `"OI"` and `"LLM"` prefixes to the identical ruleId (`tachi/ai/llm`) — a plausible mechanism for how a compilation step keyed on ruleId/category-family rather than source-agent identity could conflate the two prefixes.

---

## 4. Counter-evidence: run-specific compilation nondeterminism, not a systematic regression

| # | Evidence | Result |
|---|---|---|
| 1 | Same-day T017 fallback run (same orchestrator persona, same session), `specs/295-f292-verification-runs/test-results/t017-fallback-native-threats.sarif` | `jq` OI-prefix count = **4** (`OI-1..OI-4`) — compiled correctly |
| 2 | Attempt-1 orphaned `tachi-output-integrity` agent return, `specs/295-f292-verification-runs/test-results/t026-attempt1-orphan-oi-return.md`, for this exact architecture | Native, uncompiled agent output uses `id: "OI-1"` and cites `CWE-943` (relationship: related, alongside CWE-89) directly — before any Phase-3 compilation touched it |
| 3 | Committed `examples/agentic-app/sample-report/threats.sarif` at HEAD | `jq` OI-prefix count = **4** (`OI-1..OI-4`) — compiled correctly |

The sub-agent itself reliably emits the `OI-` id and CWE-943 citation (row 2), and the orchestrator has correctly compiled that shape into final SARIF output in two independent instances (rows 1 and 3 — one same-day, one at HEAD). The defect is specific to the Phase-3 compilation path taken on this attempt-2 run of `multi-tenant-rag-app` — the `OI-`-prefix carve-out applies inconsistently, not never. Filed as a defect (§6) rather than diagnosed further here, per FR-020 (no detection-tier or compilation-tier code changes in scope for this feature).

---

## 5. FR-013 README accuracy check (read-only; no artifacts landing)

Per tasks.md T015 (adapted, record-only): `examples/README.md:15`'s `multi-tenant-rag-app` row was checked for continued accuracy, **without any edit**, since no artifacts are landing in this disposition.

**Row content** (verbatim, unchanged):
> "Multi-tenant RAG application backed by Pinecone \| 7 (Tenant User, Auth Gateway, LLM Query Synthesizer, RAG Retriever, Pinecone Vector Index, LLM Answer Generator, Audit Logger) \| Triggers F-292 Cat 6 (Vector / Search-DSL Injection) — LLM-synthesized Pinecone metadata filter omits `tenant_id` clause; CWE-943 primary, OWASP LLM08:2025 primary; exercises pre-retrieval filtering / base-filter pinning / namespace-per-tenant mitigations"

**Result: row remains accurate as a description of architectural intent** — component count (7, matching the README's own "8th `###` entry is the external Anthropic LLM API" convention per spec.md Assumptions) is unchanged, and the Cat 6 trigger description matches `architecture.md:92`'s own stated design intent ("The `output-integrity` agent **should** emit at least one `OI-{N}` finding under Cat 6 ... on this baseline") word-for-word in substance. The row describes what the fixture is *designed to exercise*, not a claim that committed evidence exists — no artifacts are committed as part of this disposition, so the row is not contradicted by (nor validated against) any newly-committed baseline. **No edit made** (nothing changed; T015's edit-only-if-evidence-contradicts condition does not trigger).

---

## 6. Disposition (fix-vs-file, no inline fix — FR-020 scope fence)

Per spec FR-018 and tasks.md T013:

- **NO baseline commit.** The 5-artifact exactness rule (data-model.md entity 4: `threats.md`, `threat-report.md`, `risk-scores.md`, `risk-scores.sarif`, `threats.sarif`) is not satisfiable — the run output does not carry the required `OI-*`/CWE-943 shape FR-009 demands, and per FR-020 no inline fix to detection-tier files, compilation logic, or the run output itself is in scope for this feature. Landing the artifacts as-is would silently misrepresent the flagship Cat 6 fixture's own evidence baseline.
- **T014 NOT EXECUTED** — nothing to copy/regenerate; the copy-to-root-and-regenerate step is moot without a passing T013 gate. (Reflected in tasks.md T014's line — see §8.)
- **US-3 (durable SARIF-regen byte-identity check) DEFERRED** to the defect Issue filed below, per the FR-018 structural gate: US-3 proceeds only on US-2 regen success (T014), which was never reached because T013 stopped Phase 4 first. This deferral does **not** count as a US-3 failure (FR-018 explicit carve-out; tasks.md Phase 5 owner note).
- **FR-014 URI-derivation enabler stays landed** (commit `995359f`, `scripts/generate-threats-sarif.py::build_result` input-path-derived `artifactLocation.uri` + covering assertion + `tachi-pytest.yml` hardening-paths anchor). This is unaffected by the T013 gate outcome — it is an enabler, not a verification-tier fix (tasks.md Story Dependency note: "T010/T011 land regardless of T013's gate outcome").
- The defect Issue filed below **inherits the US-3 re-run**: once the compilation defect is fixed, re-run the T026 pipeline over `examples/multi-tenant-rag-app/architecture.md`, confirm the Cat 6 gate now passes, commit the 5-artifact baseline, then land the deferred SARIF-regen byte-identity test + workflow per `specs/295-f292-verification-runs/contracts/regen-byte-identity-contract.md`.

### What T026 DID durably produce, despite the gate FAIL

- The FR-014 URI-derivation enabler + covering assertion + CI hardening-paths anchor (commit `995359f`) — landed, unaffected by this gate's outcome.
- This verification record — an honest, evidenced FAIL disposition (KB Entry 17 pattern: a discovered defect fails a *gate*, not the *feature*; the feature closes on the honest record).
- Two filed Issues (§7) carrying the defect forward with full reproduction evidence and an inherited US-3 re-run obligation.

---

## 7. Filings

| Issue | Title | Trigger | Status |
|---|---|---|---|
| [#356](https://github.com/davidmatousek/tachi/issues/356) | `defect(tachi-orchestrator): Phase-3 compilation can absorb output-integrity findings into the LLM-N sequence, dropping the OI- prefix carve-out and CWE citations (F-295 T026 gate FAIL)` | Conditional (FR-007/US-2 scenario 7 — T013 gate FAIL) | Filed |
| [#357](https://github.com/davidmatousek/tachi/issues/357) | `enhancement: parameterize generate-risk-scores-sarif.py (CLI args, configurable paths, findings-count gate) to support additional example baselines` | ALWAYS (FR-011, T016) | Filed |

Both cross-reference the related, same-session Issues [#354](https://github.com/davidmatousek/tachi/issues/354) (contract §3 dual-defect) and [#355](https://github.com/davidmatousek/tachi/issues/355) (agentic-app OI/LLM duplicate-ID defect) filed during this feature's US-1 phase — #356, #354, and #355 together describe three different failure modes (absorption/non-emission; contract-verification breakage; additive duplication) of the same underlying mechanism: the `OI-`-vs-`LLM-` id-prefix assignment is not a stable, deterministic step of Phase-3 compilation.

---

## 8. tasks.md marks applied

- T013: `[X]` — gate executed to a verdict (FAIL); disposition honestly recorded and filed, not silently absorbed.
- T015: `[X]` — this record committed (adapted scope: record-only, no baseline commit, no artifact landing — nothing existed to co-update or edit).
- T016: `[X]` — enhancement Issue #357 filed (ALWAYS task, independent of T013's outcome).
- T014: left `[ ]`, annotated " — NOT EXECUTED: T013 gate FAIL stopped Phase 4 before the copy/regen step (see sc-015-verification-record.md)".

---

## 9. Issue #295 linkage

- Comment posted on #295 linking this record's path, the disposition summary, the commit SHA, and both new Issue numbers (#356, #357).
- The F-292 T026 checkbox on #295 flipped `- [ ]` → `- [x]` — the run-and-disposition is complete (gate executed honestly to a FAIL verdict, evidence committed, defect filed) even though the gate itself did not pass. Per KB Entry 17 / spec Success Criteria preamble: "a discovered defect fails a *gate* but not the *feature*, which closes on the honest record."
