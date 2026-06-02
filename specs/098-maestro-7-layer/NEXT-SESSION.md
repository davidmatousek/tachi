# NEXT-SESSION Handoff — Feature 098 (MAESTRO 7-Layer Coverage Matrix)

**Branch**: `098-maestro-7-layer` · **Issue**: #98 · BLP-04 Wave 4 · `feat(098)`
**Stopped at**: user request, after Wave 1 (Foundational) — implementation complete & verified
**Resume at**: **Wave 2 / T006** (run the populator over the 9 in-scope files)
**Draft PR**: #310

---

## Status: Waves 0–1 COMPLETE (T001–T005), verified. Waves 2–5 remain (T006–T017).

### Done this session (5 source edits on disk, all verified — NOT committed yet)
| Task | File | Change | Verified |
|------|------|--------|----------|
| T001 | `.claude/skills/tachi-orchestration/references/output-schemas.md` | Omission→Completeness (all 7), Ordering→canonical L1→L7, zero-finding cell schema, heading kept `#### ` | em dash **U+2014** ✓ |
| T002 | `.claude/agents/tachi/orchestrator.md` (~L718) | directive omit→always-7 + L1→L7 + annotation + Unclassified-after-L7 | U+2014 ✓, omit-rule gone ✓ |
| T003 | `scripts/extract-report-data.py` (L407) | removed zero-finding filter; **no canonical seeding added** (seeding L363–370 intact) | filter gone ✓ |
| T004 | `templates/tachi/security-report/maestro-findings.typ` (L154) | dead literal → `[Analyzed — no findings this scan.]` (trailing period = Typst prose) | U+2014 ✓ |
| T005 | `scripts/populate-maestro-coverage.py` **(NEW, untracked)** | stdlib populator: heading-agnostic discovery, h3→h4 normalize-on-write, present rows verbatim, absent→`0`+annotation, Unclassified last, `--check` | smoke-tested, idempotent, end-to-end-validated ✓ |

### Populator verification evidence (in-memory only — **no example/baseline file was modified**)
- Transforms correctly on all 3 shapes: h3+mid-Unclassified+missing-L4 (agentic-app), h4+2/7 (microservices), 7/7 reorder-only (maestro-reference).
- **Idempotent** (running twice = byte-identical).
- End-to-end through the real extractor: regenerated agentic-app parses to **7 canonical layers + Unclassified**, L4 has empty findings (→ fires the new Typst empty-layer branch), heading normalized to `#### `.
- **0 new spurious layers** introduced across all 9 in-scope files.
- `--check` exits **2** (drift) on un-regenerated files, **0** (no-op) on table-less sample-reports.

### Gates passed
- **G0** (contract frozen) ✓ · **G1** (4 prod edits landed, `--check` operational, no canonical seeding) ✓
- **G2** (h3→h4 normalization) — **NOT YET** (that is T006, next session). This is the Architect HIGH gate; must complete before T011 baseline regen.

---

## Test state (post-Wave-1 gate, sub-step 4.5)
- **No regressions introduced by Feature 098.** Verified by stashing all changes and re-running — the failures persist on the clean branch state.
- **15 PRE-EXISTING failures** on the branch, in unrelated subsystems (NOT touched by this feature): `test_coverage_attestation_audit`, `test_*_enrichment` `TestLineCountCaps`, `test_tool_abuse_enrichment` (`byte_identity_against_main`, `source_attribution`), `test_mobile_top_10_coverage_bundle_enrichment`. These are repo-/branch-level and out of scope for #98 — do **not** chase them as part of this build.
- `test_backward_compatibility.py` **VERIFIED green: 13 passed, 1 skipped** (22s) — the 6 PDF baselines are untouched by Wave 1 (T003 is a no-op on current un-regenerated markdown: `empty_seeded=[]` for all 6). The baselines change only when T011 regenerates them next session.
- Collection caveat: root `pytest tests/` errors on `tests/fixtures/init-baseline-tree/` (`init_sh_helpers` not importable). Run with `--ignore=tests/fixtures`. (F-302 fixture tree — pre-existing.)

---

## Pre-existing, OUT-OF-SCOPE observation (do not fix in #98)
`examples/agentic-app/threats.md` and `examples/agentic-app/sample-report/threats.md` carry a spurious `'MAESTRO Layer': 2` group in the **PDF** output — from 2 malformed Section 7 finding cells, **identical before and after** my changes, **not** in the distribution table the populator owns, and **not** baseline-gated. Leave it; fixing it would muddy the PR diff (PM OBS-1 says expect ONLY matrix row/order churn) and is outside this feature.

---

## Next actions (resume here)

### Wave 2 — US-1 regeneration (T006 → T007)
**T006** (senior-backend-engineer): run the populator over the **9 in-scope files** (this normalizes the 3 h3 headings → `#### ` automatically). One-shot batch:
```bash
cd /Users/david/Projects/tachi
python3 scripts/populate-maestro-coverage.py \
  examples/agentic-app/threats.md \
  examples/agentic-app/sample-report/threats.md \
  examples/mobile-banking-app/sample-report/threats.md \
  examples/web-app/threats.md \
  examples/microservices/threats.md \
  examples/ascii-web-api/threats.md \
  examples/mermaid-agentic-app/threats.md \
  examples/free-text-microservice/threats.md \
  examples/maestro-reference/threats.md
# verify idempotency / no drift:
python3 scripts/populate-maestro-coverage.py --check \
  examples/agentic-app/threats.md examples/web-app/threats.md examples/microservices/threats.md \
  examples/ascii-web-api/threats.md examples/mermaid-agentic-app/threats.md \
  examples/free-text-microservice/threats.md examples/maestro-reference/threats.md \
  examples/agentic-app/sample-report/threats.md examples/mobile-banking-app/sample-report/threats.md
```
**Do NOT** run it on `examples/predictive-ml-app/sample-report/threats.md`, `examples/consumer-agent-app/sample-report/threats.md` (table-less — would be a no-op anyway), or any `examples/**/test-output/**`.
Then **G2 gate**: confirm the 3 h3 files are now `#### `, agentic-app shows 7 canonical rows incl. L4 in L1→L7 order. **T007** (tester): US-1 acceptance.

### Wave 3 — US-2 annotation parity (T008, tester)
Confirm md cell phrase `Analyzed — no findings this scan` (no trailing period) == PDF prose phrase (trailing period OK — **assert on the phrase, NOT punctuation**; PM OBS-2). Regenerate the agentic-app PDF for the check. **US-1 + US-2 = Issue #98 close-gate.**

### Wave 4 — US-3 regression + deterministic baselines (T009, T010, T011, T012)
- **T009** (`tests/scripts/test_extract_report_data.py`): synthetic 7-layer `parsed_layers` ⇒ `maestro_findings_by_layer` len 7 + a zero-finding group has empty `findings`.
- **T010** (`tests/scripts/test_maestro_coverage_invariant.py`, NEW): every `examples/**/threats.md` (exclude `test-output/`) that has the table ⇒ all 7 L-IDs present. Discovery **heading-level-agnostic** (`^#{3,4}\s+Risk by MAESTRO Layer`), NOT `####`-anchored.
- **T011** (devops): regenerate the **6 gated PDF baselines** {web-app, microservices, ascii-web-api, mermaid-agentic-app, free-text-microservice, maestro-reference} under `SOURCE_DATE_EPOCH=1700000000` using the exact two-step pipeline at `tests/scripts/test_backward_compatibility.py:88-120` (see quickstart.md §4). **Gated behind T006's h3→h4 normalization (G2).**
- **T012** (tester): `test_backward_compatibility.py` 6 baselines byte-identical + the 2 new test files green.

### Wave 5 — Polish, gates & PR (T013, T014, T015, T016, T017)
- T013 no SARIF/schema diff · T015 CHANGELOG `feat(098)` · T016 two follow-up issues (FR-011 Model B; FR-012 maestro-stack infographic) · T014 `/aod.analyze` · T017 PR (agentic-app diff = ONLY matrix rows/order; note F-302 remedy `tests/fixtures/regenerate-baseline.sh` if init-baseline-tree drifts).

---

## Hard constraints for the executor
1. **G2 before T011** — h3→h4 normalization (T006) MUST precede baseline regen, else agentic-app PDF renders 0 layers + T010 false-greens.
2. **No canonical seeding** in `extract-report-data.py` (single source of truth; SC-003). *(Already honored in T003.)*
3. **Determinism** — every PDF (re)gen + backward-compat test under `SOURCE_DATE_EPOCH=1700000000`.
4. **Annotation parity asserts the phrase, not the punctuation** (PM OBS-2).
5. **PR title** = `feat(098): …` (release-please gate).

## Uncommitted work note
The 5 source edits + the new populator are **uncommitted** on `098-maestro-7-layer`. Re-running `/aod.build 098` will auto-checkpoint them at pre-flight (Step 0g), or commit manually first:
`git add -A && git commit -m "feat(098): MAESTRO contract + 4 production edits + populator (Waves 0-1)"`
