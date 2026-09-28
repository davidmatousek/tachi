# Architect P0 (Go/No-Go) Checkpoint: Feature 373, T033

**Reviewer**: architect · **Date**: 2026-09-28 (about 07:10–07:50Z) · **Reviewed at**: `4bea6c5`, branch `373-adopter-install-output-fidelity`, draft PR #375

## STATUS: APPROVED_WITH_CONCERNS. GO for Session 2 (W3–W4).

- **Required changes: 3.** RC-1 is MEDIUM (K3); RC-2 (K11) and RC-3 (K9) are LOW. All three are due in W3, before T036's architect checkpoint. Section 9 gives each one's owner, files and verification.
  - Together they are about **0.10–0.13 d** at tasks.md's per-task pace.
  - That is under the 0.18 d threshold of the TW-7 ruling's re-open condition 2. So TW-7 (NOT FIRED) stays final even if all three carry into Session 2.
- **None blocks the session break.** Nothing in W3's render session or T035 depends on these fixes. TW-7 did not fire, so K3 does not ship before Session 2.
- **Amended** (each edit marked "(amended at P0, 2026-09-28)"):
  - `contracts/installer-cli.md` (6 edits);
  - `data-model.md` (7);
  - `contracts/extraction-data-contract.md` (4).

  Section 12 lists them.

## 0. Rulings at a glance

| # | Item | Ruling |
|---|---|---|
| 1 | Parser semantics (K9, K10, K11, K12, K13-posture, K13.1): W1 and W2 commits | **Conforms** to data-model §3–§8 and the extraction contract. Two LOW defects (RC-2, RC-3) and 5 advisories |
| 1a | `9019528`, the T016 gap: tier-3 Status normalized at parse, with W2 edits to `tachi_parsers.py` | **RATIFIED**, as a scoped AR-3 exception |
| 1b | K11 (T020) removed the raw-score-vs-heading "misclassified" warning | **CONFIRMED** |
| 2 | Goldens by file name (SC-8, P-9.5) | **APPROVED.** 47 leaves, all authorized. The K15 golden and its full TW-6 revert set apply cleanly at HEAD |
| 3 | Oracle attribution rules for T035 | The expected movers were **confirmed at W2 by a P0 pre-look**. Section 3 adds the rules the W2 changes need |
| 4 | W0 AR-2 "other status" record | **None**, since 8/8 returned 200. The 404/403 walk set stands, unamended |
| 5 | N4 re-run | **0 new reds, 0 fixed.** The `maestro-reference` PDF went from 86 to 88 pages. That is **attributed to K13.1 (M5), and it is intended.** The `.pdf.baseline` is not regenerated (NFR-8); #364 absorbs it |
| 6a | `installer-cli.md:145` nested-unresolved variant | **AMENDED** to match data-model §2.1's precedence |
| 6b | SEC-K3-01: the 32-hop ceiling in `45bb8d6` | **RATIFIED.** But it does not close the partial-write mode on its own: P0 reproduced that mode at `4bea6c5` through two linked ancestors. **RC-1** is required |
| 6c | SEC-K3-03: the `--version` leading-dash guard | **Follow-up issue**, not in this bundle |
| 7 | N8 (T014), N11 (T009) | **Landed as decided**, as far as W1/W2 show. T036 does the full check |
| 8 | Process notes | Recorded (section 8) |

## Evidence base

- **Where things ran.** Everything that executed ran in scratch under `…/scratchpad/p0/`. The main tree was only read (git show, grep, Read); no pytest, extractor or `install.sh` ran in it.
- **Oracle.**
  - Scratch clone `p0/tachi` at `4bea6c5`. T001's own `snapshot.sh` re-run went to `p0/post/`, with 84/84 runs exiting 0.
  - It was diffed against T001's pre-snapshot (`scratchpad/oracle/pre/`, `0ce39d0`), using a path-level JSON diff (`p0/jsondiff.py`) and a type-strict golden leaf diff (`p0/goldendiff.py`).
- **PDF.** Four controlled Typst compiles of `maestro-reference` (`p0/pdf/`), with `SOURCE_DATE_EPOCH=1700000000` and Typst 0.14.2.
- **K3.** A combined-chain probe (`p0/k3probe/`) ran a copy of the W2 `install.sh` against sandbox targets. A patched copy also ran through the two K3 modules in the scratch clone; the clone was then restored.
- **Stop rule.** `tachi_parsers.py` at `0ce39d0` and `4bea6c5` was called on two micro-documents (`p0/stoprule/`).

---

## 1. Parser semantics

### 1.1 Per-commit verdicts

| Commit | K-item | Verdict | Notes |
|---|---|---|---|
| `1e30e90` | K9, K10, K12 helpers (T016) | Conforms, with RC-3 | See the list below |
| `a837ae8` | K11 parser and join (T020) | Conforms | See the list below |
| `5328b56` | K13-posture `compute_risk_posture` (T024) | Conforms | Highest non-zero band; zero findings give `low` / `LOW RISK` |
| `9019528` | K12, the T016 gap | Conforms; **ratified** (1.3) | — |
| `fddabb2` | K12 infographic wiring (T017) | Conforms | One normalized map per run. Tiers 1/2 are stamped through `apply_delta_status`; tier 3 copies the normalized parse. `warn_delta_scope` gets the tier's full ID set |
| `d989115` | K13-posture into every JSON (T025) | Conforms | Both emission sites, executive-architecture's early-exit builder included. LOW-4 separation from K15 held |
| `7a0d820` | K11 volume funnel (T021) | Conforms | See the list below |
| `3976870` | K11 S-9 and funnel warnings (T021) | Conforms, with **RC-2** | One shared funnel computation feeds the baseball card and the funnel. The comparand warns per field at a 0.1 tolerance |
| `d990f66` | K15 `allow_list` (T027) | Conforms | Follows the data-model §8 table exactly, executive-architecture via its own builder. LOW-4 separation held |
| `a94f495` | K12 report badges (T017) | Conforms | `_merge_delta_status` keeps its signature and delegates. The unconditional `warn_delta_scope` no-ops without a baseline |
| `a4ea956` | K13.1 (T017) | Conforms | Section 7 precedence on tier 1. The placeholder rule on tiers 2 and 3 is as specified. The drift warning is evaluated *before* the fallback mutates anything. Contract strings are exact |
| `1e1ed70` | K13-posture into `report-data.typ` (T025) | Conforms | Emitted right after the count block, from the same severity dict |
| `fa7fa10` | K13-posture cover and guard (T025) | Conforms | The guard sits after the `_report-data-dict` binding and before `cover-page`. The label renders verbatim and the color follows the level. The removed cover rubric equals `compute_risk_posture`, and no tracked severity count moved, so **no cover label changes on any example** |
| `5c460ba` | K11 caption (T022, B2b) | Conforms | It uses an em dash where the contract has a semicolon; equivalent (A-5) |
| `508eb83` | FR-K9.3 command alias (T018) | Conforms | — |

**`1e30e90` in detail.**
- `parse_score` catches `InvalidOperation`, `ValueError` and `TypeError`, and rejects non-finite values.
- The alias table and `is_placeholder_id` match §3.
- `match_heading` plus `start_line` means a regex match never falls back to a substring search.
- The K12 helpers match §6: N6 order, counts over the map (NM-1), and PD-16's scoping.
- K10's `^#{3,4}` pattern is on both extractors.
- **Stop rule: RC-3.**

**`a837ae8` in detail.**
- Clamp once, and a missing residual takes the inherent score.
- S-5 classifier: every tracked tier-1 label is `No Control Found` (silent) or `Partial Control`, with 0 warnings across 5 examples and 288 rows.
- Both copies of the row idiom are replaced, and both tier-1 call sites do the composites join.
- Warnings are collected before dedup (A-1).

**`7a0d820` in detail.**
- The three modes, `Decimal` clamp bounds, and quantize-then-derive are all in place.
- It is **correct on real data.** No tracked example has a `Control Found` row, so V2 = V3 on all five tier-1 examples, and widths are 100/90/80/70.
- The Tier-3 credit path is covered only by fixtures and the golden (V3 187.8 < V2 209.8).

### 1.2 Defects found

- **F-1, LOW (becomes RC-3): the stop rule loosens a level-1 match.**
  - `parse_markdown_table` stops at `level <= matched_level`. Its docstring claims that "for a level-1-or-2 match, 'same or higher level' reduces exactly to … the old, hardcoded rule". That is false for level 1: a `#` match no longer stops at `##`.
  - Reproduced by calling the function directly:

    | Case | `0ce39d0` | `4bea6c5` |
    |---|---|---|
    | `"Risk Summary"` matching a `# Threat Model Risk Summary` title | `[]` | adopts a **later `## 1. Components` table** |
    | an empty `### Critical Residual Severity` band (FR-K9.2's target) | adopts the next band's table | `[]` (fixed) |

  - Three bare-substring fallbacks can hit a document title: `"Risk Summary"`, `"Severity Distribution"` and `"Coverage Distribution"`. That breaks FR-K9.2's "existing callers MUST be unaffected".
  - No tracked example hits a level-1 line. The W0→W2 oracle has no unattributed mover, so the fix changes no oracle or golden output.
- **F-2, LOW (becomes RC-2): the row-count warning reports an unreadable table as "(0)", and the parse warning is doubled.**
  - `_funnel_4tier_mode` re-parses `risk-scores.md` just to count rows.
  - When the Scored Threat Table can't be read, it prints `controls rows (110) differ from risk-scores rows (0)`: a false comparison, since the risk-scores row count is unknown, not 0.
  - The re-parse also prints `could not find Scored Threat Table in risk-scores.md` a second time in the same run. `extract_severity`'s join already printed it.
  - Seen on `maestro-reference` (the W3 live-render example) and `consumer-agent-app/sample-report`, in every baseball-card and risk-funnel run.
  - The root input drift is pre-existing and outside the K-items (A-4).

### 1.3 `9019528` (the T016 gap): RATIFIED, as an AR-3 exception

- **The defect.** T016's own text requires tier-3 `parse_threats_findings` to normalize Status at parse. It stored the raw value, so tier-3 badges and `top_findings[].delta_status` showed `[NEW]`.
- **The fix.** Seven lines at the existing assignment. The key stays absent on an empty cell.
- **The writer.** SBE-B, the file's W1 owner, in one stand-alone commit. No other W2 lane touched the file, and no golden moved: the golden fixture resolves to tier 1.
- **Oracle effect.** At W2 it moves exactly what it should, in `agentic-app` (tier 3):
  - 81 report badges: `[NEW]`→`NEW` ×12 and `[UNCHANGED]`→`UNCHANGED` ×69;
  - `top_findings[].delta_status` in 5 JSON files.
- **Records.** data-model §6 is amended to record tier-3 normalization at parse. In W3, only SBE-W3 writes `tachi_parsers.py` (RC-3 is the one P0-ordered edit).

### 1.4 The removed "misclassified" warning: CONFIRMED

K11 removed both lines: `<ID> in '### <Band> Residual Severity' section but residual score <X> maps to <Band2>. Using score-derived band.` and the summary `<N> findings in wrong severity sections …`. The reasons:
1. **The output never depended on it.** The band was already score-derived at W0, so the warning reported a correction that was always silent in effect.
2. **After the clamp, it would be wrong.** It compared the *raw* score's band with the heading, while K11 bands the row from the *clamped* value. The fixture README shows the case: W-9 has a raw 9.5 above its inherent score. The legacy check says "maps to Critical", but the row is banded High.
3. **It was per-row and unaggregated**, which conflicts with R-P6. The normative class list (data-model §4.5) never carried it.
4. **No test, gated or ungated, pins it.** A grep of `tests/`, `scripts/`, `.claude/`, `templates/` and `docs/` finds only the fixture README's narrative.

The removal is stderr-only and needs no release note. T035 attributes it (section 3). The data model and contract now record it (section 12).

---

## 2. Goldens (SC-8, P-9.5): APPROVED

- **Only T032's three commits touch `tests/scripts/fixtures/golden/`** on the branch (`git log 0ce39d0..4bea6c5`).
- **Leaf diff from `0ce39d0` to `4bea6c5`**, independent of T032's report, type-strict:

  | Golden | K11 (`5a1810e`) | K13 (`3ffc3db`) | K15 (`982c074`) |
  |---|---|---|---|
  | risk-funnel | 24: `funnel_tiers[0..3]` ghost/severity_mix/volume/width, sources [1] and [3], `inherent_score`, `residual_score`, `risk_reduction`, `reduction_percentages[0..2].percentage` | 2 | 2 |
  | baseball-card | 3: `inherent_score`, `residual_score`, `risk_reduction` (S-9) | 2 | 2 |
  | maestro-heatmap | 0 | 2 | 2 |
  | maestro-stack | 0 | 2 | 2 |
  | system-architecture | 0 | 2 | 2 |

  - That is **47 leaves at T032's granularity**, where `severity_mix` counts as one leaf and `allow_list` as one.
  - No leaf falls outside these classes: no `top_findings`, severity, delta, heat-map or scope leaf moved.
- **SC-8 and P-9.5 hold.** K11 touches only the funnel and the baseball card, and only S-9's three fields on the card, while K11 ships. K11 is past its last trip-wire (T039). K13 adds the two posture leaves to each of the five goldens. K15 adds `allow_list` and a changed `prompt_scaffold.preamble` to all five.
- **The K15 preamble change is pure K15 text in all five.** It adds the layout-label sentence and the allow-list sentence; the `postamble` is unchanged.
  - The K11 and K13 prompt edits sit in the DATA CONTENT region, outside the scaffold.
  - So K15's golden commit is single-K-item, and a TW-6 revert of it takes no K11 or K13 text with it.
- **The revert is carve-safe.** `git revert --no-commit 982c074 7f7cd47 d990f66 f57bd37 d0eae8e` (K15's golden, T029, T027 and T028, newest first) applied **cleanly** at HEAD in the scratch clone, then was aborted. T030's rule still applies: after any carve, re-run T032 rather than relying on the revert.
- **0 tracked PNGs and 0 `.pdf.baseline` files changed** between `0ce39d0` and `4bea6c5`.

---

## 3. Oracle attribution rules for T035

**Method.** P0 re-ran T001's `snapshot.sh` at `4bea6c5` and diffed it against T001's pre-snapshot. Every changed leaf, line and warning below is attributed. T035 repeats this after W3's last change, and anything outside these rules is an unattributed mover: stop and escalate. There are 12 examples:
- **tier 1** (5): `agentic-app/sample-report`, `consumer-agent-app/sample-report`, `maestro-reference`, `mobile-banking-app/sample-report`, `predictive-ml-app/sample-report`;
- **tier 3** (7): `agentic-app`, `agentic-app/test-output/…`, `ascii-web-api`, `free-text-microservice`, `mermaid-agentic-app`, `microservices`, `web-app`;
- **tier 2**: none.

### 3.1 Infographic JSON (72 files)

| Field class | K-item (commit) | Where | Count at W2 |
|---|---|---|---|
| `metadata.risk_posture_level` / `_label` (added) | K13-posture (`d989115`) | 12 examples × 6 templates | 72 files. `critical`/`CRITICAL RISK` on all 7 tier-3 examples; `high`/`HIGH RISK` on all 5 tier-1 |
| `allow_list` (added) | K15 (`d990f66`) | 12 × 6 | 72 files. `finding_ids`: the full tier set on baseball-card and system-architecture, per-layer top findings on maestro-stack (can be `[]`), callouts on executive-architecture, and `[]` on maestro-heatmap and risk-funnel |
| `prompt_scaffold.preamble` (changed) | K15 (`d0eae8e`) | 12 × 5 scaffolded | 60 files. One identical two-sentence insertion; no K11/K13 text in the scaffold; `postamble` 0 |
| `template_data.funnel_tiers[]`, `reduction_percentages[]` (risk-funnel) | K11 (`7a0d820`) | 12 × 1 | 12 files. Every tier gains `ghost`/`volume`/`width`/`severity_mix`. **7 threats-only**: `null` tiers become ghost objects, widths 100/90/80/70, all reductions `null`, `[]` becomes 3 entries. **5 tier-1**: counts and sources from the one row set |
| `template_data.inherent_score` / `residual_score` | K11 S-9 (`3976870`) | 5 tier-1 × {baseball-card, risk-funnel} | 10 files. V2/V4: `agentic-app/sample-report` 525.4/473.5, `consumer-agent-app` 109.8/106.0, `maestro-reference` 597.9/597.9 (Section 1 said 570.6), `mobile-banking-app` 199.8/186.9, `predictive-ml-app` 281.4/281.4 (Section 1 said 269.4) |
| `template_data.risk_reduction` | K11 S-9 | 3 examples × 2 templates | 6 files: `null` becomes 9.9, 3.5 and 6.5. `maestro-reference` and `predictive-ml-app` stay 0.0 (no controls credited) |
| `delta.delta_counts` | K12 (`1e30e90` counts; `fddabb2` wiring) | 2 examples × 5 (executive-architecture carries no delta) | 10 files. `agentic-app` (tier 3): **12 NEW / 0 / 69 / 0**. `agentic-app/sample-report` (tier 1): **4 NEW / 0 UPDATED / 82 UNCHANGED / 0** (matches NM-1) |
| `top_findings[].delta_status` | K12 | `agentic-app/sample-report`: **newly present**, tier 1 (`fddabb2`). `agentic-app`: **`[NEW]`→`NEW` normalized**, tier 3 (`9019528`) | 5 + 5 files |

### 3.2 `report-data.typ` (12 files)

| Variable class | K-item (commit) | Where and count |
|---|---|---|
| `risk-posture-level` / `-label` (added) | K13-posture (`1e1ed70`) | All 12; 24 lines |
| `findings[].delta_status` | K12 | `agentic-app` (tier 3, `9019528`): 81. `agentic-app/sample-report` (tier 1, `a94f495`): 85. Both are raw `[NEW]`/`[UNCHANGED]` becoming normalized; for the report path, **"the badges change" means normalized, not newly present** |
| `delta-new-count` / `delta-unchanged-count` | K12 | The same two examples, with the figures in 3.1 |
| `recommendation` in `findings` and `remediation-actions` (2 lines per finding) | K13.1 (`a4ea956`) | M5 `Threat-model mitigation:` fallback: `maestro-reference` 79, `agentic-app/sample-report` 62, `mobile-banking-app/sample-report` 1 (`S-1`). The `No recommendation available` placeholder: `predictive-ml-app/sample-report` 33, because its `threats.md` has no Section 7 table. `consumer-agent-app`: 0. Tier 3: 0 (no empty mitigation) |

### 3.3 stderr (84 files), at W2, before RC-2

| Line class | K-item | Where |
|---|---|---|
| **+** `Section 7 status IDs differ from tier finding IDs (1 only-in-map, 0 only-in-tier)` | K12 PD-16 | `agentic-app/sample-report`, 6 files (not executive-architecture). This is the expected `T-1` |
| **+** `baseline run but threats.md Section 7 has no Status column; delta counts unavailable` | K12 PD-16. **N7, accepted** | `consumer-agent-app/sample-report`, 6 files |
| **+** `controls Section 1 {inherent,residual} score A differs from row-derived B; using rows` | K11 S-9 comparand | `maestro-reference` (570.6 vs 597.9, both fields) and `predictive-ml-app` (269.4 vs 281.4), on baseball-card and risk-funnel only |
| **+** `controls rows (N) differ from risk-scores rows (M)` | K11 (`3976870`) | `agentic-app/sample-report` 85 vs 86: genuine, and it stays. `maestro-reference` 110 vs 0 and `consumer-agent-app` 19 vs 0: **removed by RC-2**. Baseball-card and risk-funnel only |
| **+** `could not find Scored Threat Table in risk-scores.md` | K11's tier-1 join (`a837ae8`), surfacing pre-existing input drift (A-4) | `maestro-reference` and `consumer-agent-app`: 9 lines each (7 files, twice in baseball-card and risk-funnel). **After RC-2: 7 each**, once per run |
| **+** `could not find Risk Summary table in threats.md` (the baseball-card run) | K11 S-9: the baseball card now computes the shared funnel, whose Tier 1 reads Section 6 | `maestro-reference`, 1 line. Its risk-funnel line is pre-existing |
| **−** the legacy per-ID "misclassified" line, and **−** its summary line | K11 (`a837ae8`; §1.4) | `predictive-ml-app/sample-report`: 49 + 7 = **56 lines** over 7 files |
| **−** `could not find severity distribution in risk-scores.md` | K11: the 4-tier funnel no longer reads it | `consumer-agent-app` and `maestro-reference`, risk-funnel, 1 each |

**Zero-occurrence classes.** Each of these has **0** occurrences on every tracked example: unrecognized or empty status, clamp, missing residual, missing inherent, unparseable score, volumes unavailable, Section 4 drift, empty map, and unknown delta statuses. Record them as 0, so that any later occurrence is a mover to explain.

### 3.4 Rules

- **R-a: split K12 by commit.** Tier-3 status changes go to `9019528` (the T016 gap). Tier-1/2 badges go to `a94f495`, and tier-1 `top_findings` to `fddabb2`. Counts go to `1e30e90` plus the wiring.
- **R-b: nothing else moves.** No severity count, MAESTRO field, scope field or `severity_distribution`/`heat_map` leaf moves; K10 moves no tracked example, and all 9 use `####`. Executive-architecture JSON moves only in posture and `allow_list`.
- **R-c: K15 carve.** A TW-6 carve removes exactly the `allow_list` and preamble classes. Re-derive after any carve.
- **R-d: re-attribute RC-2 if it lands late.** RC-2 changes stderr only, in `maestro-reference` and `consumer-agent-app`. If it lands after T035, re-attribute those two examples' stderr (LOW-8). RC-1 and RC-3 move nothing in the oracle.
- **R-e: the PDF is outside the oracle but goes in the PR.** The `maestro-reference` PDF grows from 86 to 88 pages (K13.1, section 5). It belongs in T037's changed-examples list and in the #364 handoff.

---

## 4. W0 AR-2 "other status": none. The walk set stands

`test-results/w0-smoke.md`: all 8 calls (2 models × 2 ratios × 2 sizes) returned 200 with an image on the first attempt. There was no 400, 403, 404, 429 or 5xx. So there is nothing to escalate, and **the 404 `NOT_FOUND` / 403 `PERMISSION_DENIED` walk set stands, unamended.**

A clean smoke cannot exercise the non-200 rows. Those rows stay pinned by A7 (the static error-table test) and by the published error model. Any live non-200 in T015/T030's render session is recorded under P-10.1 and triaged against the contract's error table, not against this ruling.

---

## 5. N4 re-run (C-2, R-8): attributed; the change is intended

- **Totals are identical to W0**: 408 passed, 14 failed, 4 skipped, 8 errors. No status transitions.
- **The one changed signature.** `test_backward_compatibility.py::test_unmodified_examples_byte_identical_pdfs[maestro-reference]` was red at W0 from font-subset drift. At W2 its first divergence is `/Count 86` vs `/Count 88`.
- **Attribution by controlled compile** (scratch clone, `SOURCE_DATE_EPOCH=1700000000`, Typst 0.14.2):

  | Build | Templates | Data | Pages |
  |---|---|---|---|
  | P1 | W2 | W2 (the test's own pipeline) | **88** (reproduces the tester's result) |
  | P2 | W2 | W0 `report-data.typ`, plus the two posture lines the W2 guard requires | **86** |
  | P3 | W0 | W2 | **88** |
  | P4 | W2 | W2, with only the 158 `Threat-model mitigation: …` strings blanked back to `""` | **86** |
  | baseline | — | — | 86 |

- **What that shows.**
  - The template-side changes add **0 pages**: the K11 caption, the K13-posture cover, and the guard (P2).
  - The only data deltas in `maestro-reference`'s `report-data.typ` are the 2 posture lines and 158 recommendation lines.
  - Blanking only the M5 fallback restores 86 pages (P4). **The +2 pages are K13.1's M5 fallback** on the 79 findings with no Section 4 join, shown in both the finding cards and the remediation roadmap.
- **Why the change is intended.**
  - FR-K13.1 and PM ruling M5: "A conformant Section 4 covers only a subset of findings, so this changes conformant output too".
  - The five other PDF parametrizations are unchanged. They are tier 3, with no empty mitigation, and the cover label is unchanged.
- **Consequences:**
  - no baseline regeneration (NFR-8, NG5). #364's re-key absorbs K13.1's data changes (spec: "#364 absorbs the K13.1 fallback's … data changes");
  - T034's and T036's N4 re-runs should **expect this signature**, and must re-attribute any further change to it;
  - T037's #364 handoff lists `maestro-reference`'s PDF at +2 pages from K13.1.
- **N4's boundary does not grow.** The 4 new grep matches are `test_extraction_sibling_parity`, `test_gemini_request_contract`, `test_install_manifest_completeness` and `test_report_posture_contract`. All four are **gated** in `tachi-install-fidelity.yml`, and N4 is the ungated set.
  - Rule for later re-runs: keep the W0 23-module list, or subtract every module named in `.github/workflows/*.yml` from the grep.

---

## 6. Contract amendments

### (a) `installer-cli.md:145`: AMENDED

- The old variant was: "a nested line shows `-> '<readlink text>'` otherwise".
- It cannot be reached. Under data-model §2.1's first-match precedence, `unresolvable` comes before `nested`. So a dangling, looping or wrong-type nested link is reported on the "broken, looping or wrong-type" line (or a wrong-type line), with the same always-refused, no-flag-remedy, zero-write outcome.
- T011's review confirms no safety impact (SEC-K3-05).
- The text now says that a nested line always shows `-> <resolved>`, and why. The normative precedence is unchanged.

### (b) SEC-K3-01: 32 hops RATIFIED, and RC-1 required

**Why 32 is ratified.**
- 32 is the smaller of Darwin's `MAXSYMLINKS` (32) and Linux's limit (40). So a single chain the pre-flight accepts can be walked on both platforms, and the tests behave the same on both CI legs.
- It closes the analyst's reproduction (one 33–40-hop chain).
- The tests moved to 32/33, and the 33-hop run with the flag proves zero writes.
- Rejecting 32 would re-open a confirmed MEDIUM.

**Why that is not enough (P0 finding).** The commit says the mismatch is "closed structurally". It is not. The OS limit counts **every link met in one path lookup**, linked ancestors included, while `resolve()` counts one link's own chain. Reproduced at `4bea6c5` on macOS (`p0/k3probe/probe_combined_chain.sh`), with `.claude` and `.claude/skills` each reached through a 17-link chain:
- `resolve()` counts 17 hops for each, so both pass. With `--follow-symlinks` the pre-flight prints "Following symlinked destination(s)".
- Then `mkdir: …/.claude/skills: Too many levels of symbolic links`, with rc 1. **The plain entry listed first (`plainstuff/hello.txt`) had already been written.** That is exactly SEC-K3-01's non-atomic partial install.
- Control: two 8-link chains (16 links in all) install cleanly.

**RC-1, the fix** (validated at P0):
- It adds `[ -e "$p" ] || return 1` as `resolve()`'s first statement. `stat` fails with ELOOP when the whole path exceeds the platform's limit, so the component becomes `unresolvable`: always refused, with no flag remedy. That is D-1's own no-partial-install rule (data-model §2.1).
- On a patched copy, the 17+17 case is **refused with and without the flag, with nothing written**. The 8+8 control still installs.
- **The two K3 modules pass 58/58 on macOS** with the patch. The 32/33 boundary tests are unaffected, because tmp paths are physical.
- The D-1 help text and release-note wording already say "looping links are refused", which covers this. No product text changes.

**Amended.** `installer-cli.md`:
- the `resolve()` snippet (the guard, and 32);
- a new note on the hop ceiling and the guard;
- the plan-review verification figures, marked as superseded;
- an implementation-constraint row for SEC-K3-02's glob-safe split;
- the P0 test cases.

`data-model.md` §2: the `resolved` field and the §2.1 `unresolvable` row.

SEC-K3-02 (the glob-safe `strict_prefixes`) is also **ratified**: it splits by parameter expansion, is behavior-preserving, and has a regression test.

### (c) SEC-K3-03: follow-up issue, not in this bundle

- **Out of scope.** The `git checkout "$VERSION_TAG"` line is pre-existing, and argument validation for `--version` is outside K3's FR set (symlink safety, pre-flight, consent, ref restore). Code-economy rung 1 says a follow-up.
- **Low exploitability.** The trigger needs a real tag with that exact dash-leading name in the *source* repo, because the `rev-parse --verify refs/tags/…` gate runs first. And the operator types the value.
- **No carve-out applies.** The operator and the source are inside K3's threat model (a hostile *destination*), so the "input validation at every trust boundary" carve-out is not engaged.
- **Timing.** Keeping it out also protects TW-7's thin margin (the team-lead's stacked case).
- **The recipe for the issue**, filed at deliver's follow-up step with `export AOD_REPO=davidmatousek/tachi`:
  - at parse time, `case $VERSION_TAG in -*) die "…";; esac`;
  - plus one negative K3 case: nothing is checked out and nothing is written.
- If the PM pulls it in, it must ride the same T034 2-OS cycle as RC-1, at about 0.03 d extra.

---

## 7. N8 and N11: landed as decided (W1/W2 evidence)

- **N8 (T014):**
  - A8's `test_exactly_one_line_start_footer_after_marker` asserts exactly one line-start `FOOTER` after the marker, on all five templates.
  - The bare `^DATA CONTENT` fallback is kept and pinned with a comment (`extract-infographic-data.py:180-186`, "unreachable while the primary marker above matches").
  - The contract's scaffold note describes the PD-6 order.
- **N11 (T009):**
  - For each directory entry, `install.sh` refuses when `under "$SRC_P" "$dest"`, with the message "the tachi source clone lies inside this destination".
  - The `elif` avoids double-reporting when `dest == SRC_P`.
  - `test_n11_clone_nested_inside_directory_entry_destination_refused` pins it, and T011's security review exercised both directions dynamically.
- **The formal check stays with T036**, after W3 (including RC-1's change to the same function family).

---

## 8. Process notes (recorded; no ruling)

- **Restaging.** W1's T009 was restaged into three about-30-minute dispatches after two agent failures: one stall, and one overflow of the 64k output-token limit. Each staged dispatch landed first time. Keep this sizing for W3's writer tasks.
- **W2 dispatch pattern.** W2 used staged about-30-minute dispatches in five worktrees, plus two lock-step wiring squashes: sibling parity in `extraction-fidelity`, and the K13-only `report-posture` job.
  - Architecturally, the pattern kept per-K-item commit hygiene intact.
  - That is what the carve design needs, and it was verified here: the full K15 revert set applies cleanly at HEAD (section 2).
- **K3** converged green on both 2-OS legs at its first run (T010). RC-1 will need one more 2-OS cycle, and it rides T034's.

---

## 9. Required changes

All are due **before T036's architect checkpoint**. The preferred landing is with T034's W3 integration commit, so they ride its 2-OS cycle and come before T035. The total estimate is about 0.10–0.13 d, under the 0.18 d threshold of TW-7's re-open condition 2.

| ID | Severity | Owner | Files | What to do | Verification | Estimate |
|---|---|---|---|---|---|---|
| **RC-1** | MEDIUM (K3; the residual of SEC-K3-01) | DEVOPS-K3 (Lane A, the owner of `install.sh`) | `scripts/install.sh` (`resolve()`); `tests/scripts/test_install_sh_symlink_preflight.py` (plus a chain builder in `install_sh_helpers.py` if needed) | (1) Make `[ -e "$p" ] \|\| return 1` the first statement of `resolve()`. Keep the 32-hop ceiling, and fix the comment. (2) Add one regression test, below | The new test **fails at `4bea6c5` on both legs** and passes after. The full K3 modules stay green on both `tachi-pytest.yml` legs (58/58 already on macOS with the patch at P0). `bash -n` and shellcheck are clean. The `x-release-please-version` markers are untouched | ≈ 0.05–0.08 d |
| **RC-2** | LOW (K11) | SBE-W3 | `scripts/extract-infographic-data.py` (`extract_severity`'s tier-1 branch and `_funnel_4tier_mode`), plus one test in the K11 test module | Parse `risk-scores.md` **once** on the tier-1 path, and reuse that parse for both the composites join and the row count (for example, carry `risk_scores_row_count` on `cc_data`; `None` when absent or unreadable). Compare row counts only when the parse yields ≥ 1 row | New test: a tier-1 run whose `risk-scores.md` uses `## Section 2: Scored Threat Table` emits exactly **one** `could not find Scored Threat Table` line and **no** `differ from risk-scores rows` line. The kitchen-sink 10-vs-11 warning still fires. No golden or JSON change | ≈ 0.03 d |
| **RC-3** | LOW (K9) | SBE-W3 (the only W3 writer of `tachi_parsers.py`) | `scripts/tachi_parsers.py` (`parse_markdown_table`); `tests/scripts/test_tachi_parsers.py` | Stop at `level <= max(matched_level, 2)`, and correct the docstring's "reduces exactly" claim | One test pins a level-1 title match giving `[]` (W0 behavior), beside the existing empty-`###`-band test. No oracle or golden change, since no tracked caller hits a level-1 line | ≈ 0.02 d |

**RC-1's regression test.**
- The setup: `.claude` and `.claude/skills` are each reached through a **21-link chain**.
  - That is 42 links in one lookup, over both Darwin's 32 and Linux's 40, so the test is deterministic on both legs.
  - Each chain alone passes the 32-hop ceiling, so only the new guard can refuse it.
- The run uses `--follow-symlinks`, with a plain entry listed **first** in the manifest.
- Expected: exit 1, and the always-refused block names `.claude/skills` as a broken, looping or wrong-type link.
- Before/after snapshots show **zero writes**, so the plain entry is absent too.

**T036's code review** includes all three deltas: stage 1 (K3) for RC-1, and stage 2 (parsers and extractors) for RC-2 and RC-3.

---

## 10. Advisories (non-blocking; fold only if cheap, and at the writer's discretion)

- **A-1: the aggregated per-row warnings count rows before dedup.**
  - Covers unrecognized status, clamp, missing residual/inherent, and unparseable score.
  - A duplicate `Threat ID` row would be counted twice and could repeat an ID in "first: …".
  - This is latent: the producer no longer cross-lists (no instruction in `.claude/` or `templates/`), and no tracked example has duplicates.
  - The parser comment "control-analyzer cross-lists findings" is stale.
- **A-2: `classify_control_status` tokenizes on whitespace only.**
  - Punctuation-wrapped tokens aren't recognized.
  - `Found.` safely falls to none-with-a-warning, but `Found (partial)` would over-credit as `found`.
  - This is outside the observed labels, and S-5's literal rule holds. Revisit (for example with `re.findall(r"[a-z]+", …)` tokens) only if a producer emits punctuated labels.
- **A-3: small edges in `normalize_delta_status` and `_section4_has_content`.**
  - `normalize_delta_status` strips spaces, not all whitespace. Cells arrive stripped, so this affects only interior tabs or NBSP next to markers.
  - `_section4_has_content` treats any prose line as content, so a prose-only Section 4 with no join would warn of drift.
  - Both are acceptable as coarse signals.
- **A-4: file a follow-up issue at deliver** (PM scopes it; `export AOD_REPO=davidmatousek/tachi`) for the `## Section N: Title` heading form.
  - `maestro-reference` and `consumer-agent-app/sample-report` write `## Section 6: Risk Summary` and `## Section 2: Scored Threat Table`. The parsers match only `## 6.`/`## 2.`, and the bare `"Risk Summary"` fallback lands on the calibration matrix.
  - This is pre-existing (W0 had the same warnings) and outside K9–K13.
  - The effects: those funnels show **Threats Identified = 0**, and the K11 join cannot read composites there. Their controls tables carry an Inherent column, so volumes stay available.
- **A-5: the K11 caption** uses an em dash where the contract text has a semicolon. That is equivalent; no change.

---

## 11. Carry-forward for NEXT-SESSION.md and Session 2

- **Render session (T015/T030) judges.**
  - `maestro-reference`'s funnel will show **Threats Identified = 0** (A-4) and **0% reduction**: every row is `No Control Found`, so the widths are the 100/90/80/70 STEP cascade and the funnel shows the 0% note.
  - Both are data properties of the example, not K11/K14/K15 render defects. **Don't spend a TW-5 iteration on them.**
- **Ordering.** RC-1 to RC-3 land with T034, preferably. If RC-2 lands after T035, re-attribute its two examples' stderr (rule R-d).
- **TW-7 re-open condition 1** is the orchestrator's to close. `tachi pytest` at `4bea6c5` was Ubuntu green, with macOS still running at 07:28Z.
- **T037 and T038.** The #364 handoff lists `maestro-reference`'s PDF at +2 pages from K13.1. The D-1 notice text needs no change for RC-1.
- **Follow-up issues to file at deliver:** SEC-K3-03 (6c) and the heading-form drift (A-4).

---

## 12. Amendments made (all marked "(amended at P0, 2026-09-28)")

**`contracts/installer-cli.md`**
1. The `resolve()` snippet: the comment, the `[ -e "$p" ]` guard, and `-le 32`.
2. A new note "The hop ceiling and the whole-path guard", covering SEC-K3-01's 32 and RC-1's guard. The plan-review 40/41 figures are marked as superseded.
3. The implementation-constraints table: a new row for splitting paths with parameter expansion only (SEC-K3-02).
4. `:145` (now further down): the nested line always shows `-> <resolved>`, with the precedence explained (SEC-K3-05).
5. The test harness: "Cases added at P0" (the `45bb8d6` cases, and RC-1's required 21+21-link case).
6. The `phys_dest` comment: it fails on a dangling **or looping** link, both already refused.

**`data-model.md`**
1. §2: the `resolved` field (32 hops, and the whole-path lookup).
2. §2.1: the `unresolvable` row (32 hops, or OS ELOOP across the whole path; was "more than 40 hops").
3. §2.2: `phys_dest` fails on a dangling or looping link, and §2.1 refuses both.
4. §4.5: the row-count comparison only on a readable risk-scores table, reported once (RC-2).
5. §4.5: the missing-residual class, implemented but previously unlisted.
6. §4.5: "Removed with K11", the legacy "misclassified" warning and why.
7. §6: tier 3 normalizes Status at parse (`9019528`).

**`contracts/extraction-data-contract.md`**
1. The `parse_markdown_table` stop-rule row: `level ≤ max(L, 2)` (RC-3).
2. Warnings: the missing-residual stem, as implemented.
3. Warnings: the row-count trigger condition (RC-2).
4. Warnings: "Removed with K11", the note on the legacy lines.

## 13. Final state

- **Main tree.** `git -C /Users/david/Projects/tachi status --short` at the end of this review, with HEAD `4bea6c5`:
  - ` M` `contracts/extraction-data-contract.md`, `contracts/installer-cli.md`, `data-model.md`: this review's amendments;
  - ` M` `tasks.md`: **not this review's**. It is the orchestrator marking T040 `[X]` ("not triggered: TW-7 did not fire");
  - `??` `test-results/n4-rerun-w2.md` (tester), `test-results/w2-exit-tw7.md` (team-lead), `test-results/wave-03/` (orchestrator).

  This results file sits under the gitignored `.aod/results/`. No product code or tests were edited, and nothing is committed; the orchestrator commits.
- **Scratch.** The scratch clone `p0/tachi` is clean at `4bea6c5`, with 0 PNG drift, after the probes and the restore.
