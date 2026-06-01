# NEXT-SESSION — Feature 302 (Asset-Tag Output Wiring, F-260b)

**Branch**: `302-asset-tag-output-wiring` | **Draft PR**: #303
**Handoff written**: 2026-05-31 | **Reason**: standalone 3-wave ceiling reached (build Step 4 sub-step 7) — Waves 6, 7, 8 executed this session.
**Progress**: 21 / 23 tasks complete (T001–T020 + T023). **P0 + P1 + P2 checkpoints all APPROVED.**

---

## Next Actions (resume here)

Run `/aod.build 302` in a fresh conversation. It auto-resumes at the first unchecked task.
The next wave is **Wave 9** (the final gates), then build **Steps 5–8**:

- **T021** [Polish] — **SC-011 frozen-constraint binary diff gate**: verify `git diff main -- schemas/risk-scoring.yaml scripts/tachi_parsers.py` shows NO change to `VALID_ASSET_TAGS`, `modifier_ceiling: 9.2`, the modifier-after-clamp ordering, or `risk-scoring.yaml` `schema_version` (stays `1.1`). Agent: **tester**. (Independent — run first.)
- **T022** [Polish] — **full `quickstart.md` acceptance** (SC-001…SC-012): confirm the 26-case suite + `test_affected_assets_wiring.py` are green in CI; NFR-2 score-equivalence vs the v4.31.0 worked example holds. Agent: **tester**. Depends on everything incl. T020's CI wiring. **Closing acceptance gate.**

T021 → T022 are serial (T022 is the closing gate). After Wave 9: run build **Steps 5–8** (final Architect + Code + Security reviews; **Design Gate is N/A** — no UI; **Security Scan Step 7 applies** to the populator/extractor; completion report) → `/aod.deliver` → `/aod.document`.

> **R9 note for T022**: the live-pipeline R9 gate (T018) is **already done + PASS** this session (see below) — T022 should cite it, not re-run the expensive live pipeline. The full agentic-app threat-model overflows the orchestrator's context (~17–18 min, "Prompt is too long"); a scoped run (skip Phase 5) is the workaround if a re-run is ever needed.

---

## What's done this session (Waves 6–8) — all committed + pushed to PR #303

| Task | Wave | What | Commit |
|------|------|------|--------|
| T016 | 6 | SC-002 baseline regen — `examples/agentic-app/sample-report/{threats.md,threats.sarif,risk-scores.sarif}` under `SOURCE_DATE_EPOCH=1700000000`; additive-only (0 deletions ×3), all `[]`, 3-way snake_case equality vs wave-00 snapshot | 4f6c8fd |
| T017 | 6 | SC-007 + SC-004 tests (+9, 3rd/final append to `test_affected_assets_wiring.py`; file total 35 green) | 4f6c8fd |
| T018 | 7 | **R9 live-pipeline gate** — found a real production defect; **PASS after T023 fix** (live re-verify: 0 mismatches, 3-way equality) | 2af05a5 |
| T023 | 7 | **Remediation (Option B, user-chosen)** — orchestrator **Phase 3.7** runs the populator before Phase 4 SARIF authoring | 2af05a5 |
| T019 | 8 | CHANGELOG `feat(302):` entry + @north-echo (Christopher Lusk) PROTOTYPE-AUTHOR credit (PR #262, Discussion #246) | d555292 |
| T020 | 8 | CI lock-step wiring — both asset-tag suites + source surfaces into `tachi-pytest.yml` paths + invocation | d555292 |

**Post-wave tests**: wave-06 full suite 865P/16F/2S — failure set BYTE-IDENTICAL to wave-05 (0 regressions; +9 = T017's new tests). 16 failures are the documented F-302-independent cluster. Waves 7–8 were `.md`/`.yml`-only (no source change → Step 4.5 skipped; targeted content tests green).

---

## ⚠️ The T018 finding + T023 fix (read before T022 / delivery)

**T018's R9 live gate caught a real defect SC-006 was structurally blind to** (exactly architect L-2). On a live `tachi.threat-model` run, the orchestrator **self-authored** the `## Affected Assets` block (LLM) instead of the deterministic populator, mis-assigned **S-7** (`[]` vs deterministic `[safety]` — S-7's component was the safety-tagged Learning Loop), and copied that into `threats.sarif` → a 1/69 cross-format (NFR-3) disagreement. Root cause: the command ran the populator (Step 2.5) **after** the orchestrator authored the SARIF.

**T023 fix (Option B, in-scope — markdown/authoring-contract only, frozen files untouched)**:
- `.claude/agents/tachi/orchestrator.md`: new **Phase 3.7** "Populate Affected Assets Block (deterministic, pre-SARIF)" at the Phase 3→4 boundary; populator is the value authority, self-authoring forbidden; **both** Phase 3.6 exit paths (incl. the `result == false` early-exit) route through it.
- `.claude/commands/tachi.threat-model.md`: Step 2 prompt imperative + ordered; Step 2.5 reframed as idempotent re-assert.
- `.claude/commands/tachi.risk-score.md`: verified ALREADY correct (Step 1.5 populator precedes risk-scorer SARIF authoring) — unchanged.
- `.claude/skills/tachi-orchestration/references/sarif-specification.md`: one clarifying clause.

**Live re-verification PASS** (run2): orchestrator-written block == deterministic authority (0 mismatches → it ran Phase 3.7); threats.sarif == block over 67 IDs (0 mismatches → NFR-3 holds live). Full evidence: `.aod/results/tester-t018.md` + `.aod/results/sbe-t018-fix.md`. Architect **P2 APPROVED** (0 BLOCKING/HIGH/MEDIUM, 3 LOW; L-2 discharged): `.aod/results/architect.md` → "## P2 Checkpoint Review".

---

## Gate status (verified, not assumed)

- **P0 (Waves 0–2)**: APPROVED_WITH_CONCERNS / GO — both MEDIUMs closed.
- **P1 (Waves 3–5)**: APPROVED / GO — 0 BLOCKING/HIGH/MEDIUM, 2 LOW (discharged).
- **P2 (Waves 6–7)**: **APPROVED** — 0 BLOCKING/HIGH/MEDIUM, 3 LOW. T023 fix architecturally sound; risk-scores.sarif disposition adequate (live run not required, carried as L-3); L-2 discharged + vindicated.
- **SC-011 frozen gate** (T021, NOT YET RUN): `risk-scoring.yaml` + `tachi_parsers.py` + `populate-affected-assets.py` confirmed untouched by the T023 fix (`git diff` clean) — T021 is the formal binary-diff gate.

---

## Delivery-time tails (NOT build waves — execute at `/aod.deliver`)

- **FR-011c**: Discussion #246 acknowledgment comment + offered `Co-Authored-By` (trailer already on the Wave 8 commit d555292).
- **FR-012**: close Issue #302 (cite PR + release + credit URL) and parent #260 (link F-260b PR + credit @north-echo) — completing the #246 → #262 → #260 → #302 chain.
- **FR-010 / SC-009**: PR title MUST be `feat(302): …`; after squash-merge verify a release-please PR opens within ~30s (`gh pr list --state open --search "release-please"`); if absent, push a `feat(302):` release marker (per `feedback_aod_deliver_release_gate.md`).
- **P0 carry**: before deliver, grep for any remaining `== "1.8"` `finding.yaml` schema pins (bump was 1.8→1.9; only `test_output_integrity` pinned it — fixtures legitimately retain 1.8 as authored-version data).

---

## Resume prompt

```
Resume F-260b asset-tag output wiring (branch: 302-asset-tag-output-wiring).
Waves 0–8 complete (T001–T020 + T023), P0+P1+P2 APPROVED. Run /aod.build 302 to continue with Wave 9 (T021 SC-011 frozen diff → T022 full quickstart acceptance), then build Steps 5–8.
T018 R9 live gate is DONE + PASS (T023 fixed the orchestrator Phase 3.7 sequencing) — T022 cites it, do NOT re-run the live pipeline (it overflows orchestrator context).
```
