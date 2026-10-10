# T035 — Oracle Post-Snapshot and Attribution

**Feature**: 373-adopter-install-output-fidelity
**Task**: T035 (W3, `/aod.build`)
**Agent**: `senior-backend-engineer` instance SBE-B
**Commits compared**: W0 `0ce39d0` (`0ce39d033357f6315221bb70f2db8c1f1effe86e`, 2026-09-27) → current HEAD `748d634` (`748d6341dd8bb616ebc4a791ab744d940cba975d`, 2026-10-10)
**Code state**: identical to W3 commit `91e4542` (`91e454274ec150cc1c62607c8d70ae9b5eb0ef45`, 2026-10-06). Verified `git diff --stat 91e4542 748d634` touches only `tasks.md` (status checkboxes) and four files under `specs/373-adopter-install-output-fidelity/test-results/` — no `scripts/`, `templates/` or `examples/` change. So this snapshot's "post" state is W3's code exactly.
**Executed**: all pytest/extractor runs below ran in scratch clones (`/private/tmp/.../scratchpad/t035/clone-w0/tachi`, `clone-post/tachi`), never the main tree (#365 / standing rule). Only this document was written directly into the main tree.

---

## 1. Method

1. **Pre-snapshot regeneration.** T001's own scratchpad (session 1) no longer exists. Re-cloned `/Users/david/Projects/tachi` at `0ce39d0` into a scratch path *ending in `/tachi`* (`clone-w0/tachi`) — this matters: the Appendix `snapshot.sh`'s N2 normalization rule only rewrites absolute paths that contain a literal `/tachi/` segment, so a scratch clone directory not named `tachi` would silently skip normalizing `metadata.source_file` (caught and fixed during this run; see §6).
2. Extracted `snapshot.sh` **verbatim** from the prestate doc's appendix via `sed -n '261,464p'` (byte-exact, no retyping), `bash -n`-checked, then ran it unmodified: `snapshot.sh clone-w0/tachi SC/pre`.
3. **Fidelity check** of the regenerated pre-snapshot against `test-results-prestate.md` §S4, before trusting it as a baseline:
   - 84/84 runs exit 0 (`nonzero-exits.txt` empty) — matches.
   - Total stderr: **18,753 bytes across 84 files** — **exact match** to §S4's "18,753 bytes across 84 files."
   - All 5 warning classes and counts (14 / 7×7 / 7 / 2 / 1) — **exact match**, including the specific scores (S-1 8.4→High, R-1/I-4 4.5→Medium, D-5/D-3 4.3→Medium, D-4/D-2 4.7→Medium).
   - **Verdict: faithful.** Proceeded.
4. **Post-snapshot.** Cloned HEAD (`748d634`) into `clone-post/tachi`, ran the same unmodified `snapshot.sh` → `SC/post`. 84/84 exit 0.
5. **Diff.** Wrote a type-strict recursive JSON leaf differ (dict/list/scalar, additions/removals/type-mismatches all counted), a `difflib.SequenceMatcher`-based `.typ` line-pair differ with regex field extraction (`key: "value"` pairs) for the `findings`/`remediation-actions` tuple arrays, and a full stderr multiset line differ attributed by `(example-slug, template)`. Script: `SC/analyze.py`. Classification rules map every leaf/line to a field class; anything that doesn't match a rule is recorded as `UNCLASSIFIED` — the mechanism that would catch an unattributed mover.
6. **Checks.** `git diff --stat 0ce39d0 HEAD -- 'examples/**/*.png' 'examples/**/*.pdf.baseline'` → empty. Main-tree `git status --short` → clean except this file.

---

## 2. Verdict

**100% ATTRIBUTED.** 0 unclassified JSON leaves (of 552 changed), 0 unclassified `.typ` field/line changes (of 544), 0 unattributed stderr line classes (of 18 changed, 95 instances). No PDF baseline or tracked PNG changed on the branch. No `examples/**` change in the main tree (nothing ran against it).

RC-1 (`60f3714`) and RC-3 (`7b8a93f`) move **nothing** in the oracle, confirmed empirically (no tracked example hits a level-1 heading or the 32-hop symlink path). RC-2 (`7cf98f0`) moves **stderr only**, exactly as predicted in §3 below.

---

## 3. JSON leaf diff — 72 files, 552 leaves changed, 0 unclassified

| Field class | K-item (commit) | Files touched | Leaves | Per-example detail |
|---|---|---|---|---|
| `metadata.risk_posture_level` (added) | K13-posture (`d989115`) | 72/72 | 72 | 1 per file, all 12 examples × 6 templates |
| `metadata.risk_posture_label` (added) | K13-posture (`d989115`) | 72/72 | 72 | 1 per file, same scope |
| `allow_list` (added, whole-subtree) | K15 (`d990f66`) | 72/72 | 72 | 1 per file (subtree counted as one leaf, per P0's own convention) |
| `prompt_scaffold.preamble` (changed) | K15 (`d0eae8e`) | 60/60 | 60 | All 12 examples × 5 scaffolded templates (not `executive-architecture`) |
| `template_data.funnel_tiers[]` | K11 (`7a0d820`) | 12/12 (risk-funnel.json only) | 144 | **7 tier-3/threats-only** examples (`agentic-app`, `…test-output…`, `ascii-web-api`, `free-text-microservice`, `mermaid-agentic-app`, `microservices`, `web-app`): 7 leaves each (49) — `null` tiers become ghost objects. **5 tier-1** examples (`agentic-app/sample-report`, `consumer-agent-app/sample-report`, `maestro-reference`, `mobile-banking-app/sample-report`, `predictive-ml-app/sample-report`): 19 leaves each (95) — counts/sources from the row set |
| `template_data.reduction_percentages[]` | K11 (`7a0d820`) | 12/12 | 36 | 3 leaves per file, uniform across all 12 |
| `template_data.inherent_score` | K11 S-9 (`3976870`) | 10 (5 tier-1 × {baseball-card, risk-funnel}) | 10 | 1 each |
| `template_data.residual_score` | K11 S-9 (`3976870`) | 10 | 10 | 1 each |
| `template_data.risk_reduction` | K11 S-9 (`3976870`) | 6 (3 of the 5 tier-1 examples × 2 templates) | 6 | `agentic-app/sample-report`, `consumer-agent-app/sample-report`, `mobile-banking-app/sample-report` only — `maestro-reference` and `predictive-ml-app/sample-report` stay `0.0→0.0` (no controls credited), confirmed unchanged |
| `delta.delta_counts.new` / `.unchanged` | K12 (`1e30e90` + `fddabb2` wiring) | 10 (2 examples × 5 templates, no executive-architecture) | 20 | **`agentic-app/sample-report`** (tier 1): `0→4` new, `0→82` unchanged, per file. **`agentic-app`** (tier 3): `0→12` new, `0→69` unchanged, per file. `.updated`/`.resolved` stay `0→0` (not in diff) |
| `top_findings[].delta_status` | K12 (R-a: tier-1 `fddabb2` — newly present; tier-3 `9019528` — normalized) | 10 (same 2 examples × 5) | 50 | `agentic-app/sample-report`: 5 entries/file, **newly present** (`None→`), 1×`NEW` + 4×`UNCHANGED` per file. `agentic-app`: 5 entries/file, **normalized** (`'[UNCHANGED]'→'UNCHANGED'`, all 5 in every file — this top-5 subset happens to contain none of the 12 NEW rows) |

**Verified independently**: `delta.delta_counts` (4 NEW/82 UNCHANGED for tier 1; 12 NEW/69 UNCHANGED for tier 3) cross-checked against the `report-data.typ` `findings[].delta_status` NEW/UNCHANGED split below — both methods agree exactly.

No `severity_distribution`, `heat_map`, MAESTRO, scope, or any severity-count leaf moved (rule R-b) — confirmed by the 0-unclassified result. `metadata.project_name` is byte-identical pre→post on every one of the 72 files, including `maestro-reference`'s `"Unknown Project"` (pre-existing, not a mover) — checked explicitly, not just by omission.

---

## 4. `report-data.typ` diff — 12 files, 544 field/line changes, 0 unclassified

| Variable class | K-item (commit) | Files | Count | Detail |
|---|---|---|---|---|
| `risk-posture-level` (added `#let` line) | K13-posture (`1e1ed70`) | 12/12 | 12 | 1 line each |
| `risk-posture-label` (added `#let` line) | K13-posture (`1e1ed70`) | 12/12 | 12 | 1 line each |
| `delta-new-count` | K12 (`1e30e90`+wiring) | 2 | 2 | `agentic-app` 0→12, `agentic-app/sample-report` 0→4 |
| `delta-unchanged-count` | K12 | 2 | 2 | `agentic-app` 0→69, `agentic-app/sample-report` 0→82 |
| `findings[].delta_status` | K12 (R-a: tier-3 `9019528`, tier-1 `a94f495`) | 2 | 166 | `agentic-app` (tier 3): 81 lines, split **12× `[NEW]→NEW` / 69× `[UNCHANGED]→UNCHANGED`** (verified by independent regex pass, matches the JSON `delta_counts` exactly). `agentic-app/sample-report` (tier 1): 85 lines, **4× `[NEW]→NEW` / 81× `[UNCHANGED]→UNCHANGED`** |
| `recommendation` (in `findings` **and** `remediation-actions`, 2 lines/finding) | K13.1 (`a4ea956`) | 4 | 350 | **M5 fallback** (`"Threat-model mitigation: …"`): `maestro-reference` 79 findings ×2 = 158; `agentic-app/sample-report` 62×2 = 124; `mobile-banking-app/sample-report` 1 (`S-1`) ×2 = 2. **Placeholder** (`"No recommendation available"`): `predictive-ml-app/sample-report` 33×2 = 66 (no Section 7 table). `consumer-agent-app/sample-report`: 0. All 7 tier-3 examples: 0 (no empty mitigation there) |

284 FALLBACK + 66 PLACEHOLDER = 350, matching 124+158+2 = 284 and 66 exactly. `allow_list` and `prompt_scaffold` do not appear in `.typ` (JSON-only fields) — confirmed absent from every diff.

---

## 5. stderr diff — 84 files, 18 distinct line-classes changed (95 instances: 37 added, 58 removed), 0 unattributed

| Direction | Line | K-item (commit) | Where (post) |
|---|---|---|---|
| **−56** (7 lines × 7 occ. + summary) | the 7 per-ID `"<ID> in '### <Band> Residual Severity' section but residual score <X> maps to <Band2>"` lines (S-1, R-1, I-4, D-5, D-4, D-3, D-2) + `"7 findings in wrong severity sections…"` | K11 removes the legacy "misclassified" check (`a837ae8`; P0 §1.4) | was `predictive-ml-app/sample-report`, all 7 runs; now **0** everywhere |
| **−2** | `could not find severity distribution in risk-scores.md` | K11: 4-tier funnel no longer reads it | was `consumer-agent-app/sample-report` + `maestro-reference` (risk-funnel, 1 each); now **0** |
| **+1** (net; 1→2) | `could not find Risk Summary table in threats.md` | K11 S-9: baseball-card now computes the shared funnel too | `maestro-reference`: risk-funnel's line is pre-existing (1); baseball-card adds 1 more → 2 |
| **+14** | `could not find Scored Threat Table in risk-scores.md` | K11 tier-1 join (`a837ae8`), surfacing pre-existing input drift (A-4); **post-RC-2** | `maestro-reference` + `consumer-agent-app/sample-report`, **7 each — one per template run** (all 7 runs incl. `report-data`, not duplicated within baseball-card/risk-funnel). Pre-RC-2 this was 9 each (18 total) with a duplicate print inside baseball-card and risk-funnel; **RC-2 (`7cf98f0`) removed the duplicate**, landing at 14 total as this task's instructions specified |
| **+2** | `controls rows (85) differ from risk-scores rows (86)` | K11 S-9 comparand (`3976870`) | `agentic-app/sample-report` only — baseball-card + risk-funnel. **Genuine and stays** (85 vs 86 is a real row-count mismatch in the fixture) |
| **(removed by RC-2)** | `controls rows (110) differ from risk-scores rows (0)` / `controls rows (19) differ from risk-scores rows (0)` | RC-2 (`7cf98f0`): row-count compared only when the risk-scores parse actually yields ≥1 row | **Confirmed absent from post** at `maestro-reference` and `consumer-agent-app/sample-report` — these false "(0)" comparisons do not appear anywhere in the 84-file post set |
| **+8** (4 lines × 2 occ.) | `controls Section 1 {inherent,residual} score A differs from row-derived B; using rows` | K11 S-9 comparand (`3976870`) | `maestro-reference` (570.6 vs 597.9, inherent+residual) and `predictive-ml-app/sample-report` (269.4 vs 281.4, inherent+residual), baseball-card + risk-funnel only — 2×2×2=8 |
| **+6** | `Section 7 status IDs differ from tier finding IDs (1 only-in-map, 0 only-in-tier)` | K12 PD-16 (`1e30e90`+wiring) | `agentic-app/sample-report`, 6 of 7 runs (not `executive-architecture`). This is the expected **T-1** ID-set warning named in tasks.md |
| **+6** | `baseline run but threats.md Section 7 has no Status column; delta counts unavailable` | K12 PD-16; **N7, accepted** | `consumer-agent-app/sample-report`, 6 of 7 runs (not `executive-architecture`) |

**RC-2 verification (this task's step-4 instruction, confirmed against real output, not assumed)**: the `maestro-reference`/`consumer-agent-app` "(0)" false row-count lines are gone; `could not find Scored Threat Table` prints exactly 7 times per example (once per run), not 9; `agentic-app/sample-report`'s genuine 85-vs-86 warning is unchanged and stays. All exactly as specified.

**Unchanged (not movers, listed for completeness)**: `could not find Recommended Actions table in threats.md` — flat at 14 (7 `consumer-agent-app/sample-report` + 7 `predictive-ml-app/sample-report`) in both pre and post; not in P0's mover list and confirmed not to have moved. All 107 distinct non-`Warning:` informational lines (tier/count/coverage reporting) are byte-identical pre→post — confirmed via full multiset diff, not spot-checked.

### Zero-occurrence classes (recorded as 0, per P0 §3.3)

Confirmed **0 occurrences** in both pre and post, by keyword search across all 168 stderr files (84+84): unrecognized/empty status, clamp, missing residual, missing inherent, unparseable score, volumes unavailable, Section 4 drift, empty map, unknown delta statuses.

---

## 6. Methodological note: the `/tachi/` clone-path requirement

The normalization script's N2 rule (`PATH_RE = re.compile(r'/[^"\s]*/tachi/')`) only rewrites an absolute path if it contains a literal `/tachi/` segment. My first pass cloned into directories named `repo-w0` / `repo-post`, which produced a real but spurious diff on `metadata.source_file` (12 leaves, `UNCLASSIFIED`) purely because the clone path had no `/tachi/` segment to match. Caught by the 0-unclassified check, not assumed benign: re-cloned into `clone-w0/tachi` and `clone-post/tachi` (matching the convention T001 and P0 used — `.../w0-t001/tachi`, `.../p0/tachi`) and re-ran both snapshots end to end. Re-verified the pre-snapshot fidelity check still passes exactly after the re-clone (18,753 bytes, same 5 classes) before trusting the new baseline. Recorded here so a future re-run (T036/T037, or the orchestrator's final re-snapshot) doesn't repeat it.

---

## 7. PDF note (outside the oracle; rule R-e)

The PDF is explicitly out of scope for this oracle (JSON/`.typ`/stderr only). Per P0 §5 and tasks.md: `maestro-reference`'s rendered PDF grows from 86 to 88 pages, attributed to K13.1's M5 fallback text on findings with no Section 4 join (shown in both finding cards and the remediation roadmap). The `.pdf.baseline` fixture is **not** regenerated (NFR-8) — confirmed via `git diff --stat 0ce39d0 HEAD -- 'examples/**/*.pdf.baseline'` returning empty. This belongs in T037's #364 handoff, not here.

---

## 8. Expected-mover checklist (tasks.md T035, L8)

- [x] K10: none among the tracked examples — confirmed, 0 occurrences anywhere (no leaf, line or warning classifies to K10)
- [x] The M5 fallback examples (K13.1) — `maestro-reference`, `agentic-app/sample-report`, `mobile-banking-app/sample-report` (fallback) + `predictive-ml-app/sample-report` (placeholder); 350 `.typ` occurrences, exact split confirmed
- [x] K12 (NM-1): `agentic-app/sample-report` → **4 NEW / 0 UPDATED / 82 UNCHANGED**, one ID-set warning (`T-1`) — confirmed exactly, both JSON and `.typ`
- [x] K12: `agentic-app` (tier 3) → **12 NEW / 69 UNCHANGED** — confirmed exactly, both JSON and `.typ`
- [x] K12: badges change (tier-1 `a94f495`, tier-3 `9019528`) — confirmed, 166 `.typ` lines
- [x] K12: `top_findings[].delta_status` normalized at tier 3, newly present at tier 1 — confirmed, 50 JSON leaves
- [x] K11's funnel fields and S-9's baseball-card fields — confirmed, 144+36 funnel leaves, 10+10+6 S-9 leaves
- [x] Posture fields and `allow_list` everywhere, `prompt_scaffold` text (K11, K13, K15) — confirmed, 72+72+72 JSON leaves, 24 `.typ` lines, 60 preamble files
- [x] Warnings: new aggregated classes, and `has_baseline`'s stateless false positive (N7), attributed from stderr — confirmed, all 9 changed stderr classes attributed
- [x] 100% attributed — **yes**
- [x] No PDF baseline or tracked PNG changes — confirmed empty diff

---

## 9. Final checks

```
$ git -C /Users/david/Projects/tachi status --short
(clean until this file is added)
$ git -C /Users/david/Projects/tachi diff --stat 0ce39d0 HEAD -- 'examples/**/*.png' 'examples/**/*.pdf.baseline'
(empty)
```

Scratch artifacts (raw/norm snapshots, `analyze.py`, reports) live under `/private/tmp/claude-501/-Users-david-Projects-tachi/2ad26401-b1da-4436-8824-d43d5ff80457/scratchpad/t035/` — `pre/` and `post/` are kept (both raw and norm) for the orchestrator's later final re-snapshot-and-diff against `post/`.

---

## 10. Final-commit confirmation (`729fa1b`)

**Commit**: `729fa1b` (`729fa1b6859a9344f15488bff9d9beb58a8969b9`, 2026-10-10), branch tip, pushed. 12 commits landed after this oracle's `post` snapshot (code `91e4542`): `117b2a3`, `b03b834` (T036 H-1/M-1; L-2 comments), `f106c9e` (L-1), `383140e`, `0fc2ebe` (L-8, CI path widening), `2ef4cec`, `91fbe7a`, `e12318b` (L-3), `819830e` (L-4), `3dcaf84` (L-5), `da7a196` (L-6), `dfccde5` (L-7), plus `729fa1b` itself (this doc's own T035 commit).

**Method**: fresh scratch clone of `729fa1b` at `clone-final/tachi` (path ends in `/tachi`, satisfying N2 normalization per §6 above). Ran the same unmodified `snapshot.sh` → `SC/final`. 84/84 runs exit 0. Diffed normalized `SC/post` (W3, code `91e4542`) against normalized `SC/final` (`729fa1b`) two ways: (1) the same type-strict JSON / `difflib`-based `.typ` / stderr-multiset classifier used throughout this document, and (2) an independent raw `diff -rq SC/post/norm SC/final/norm` over all 168 files (72 JSON + 12 `.typ` + 84 stderr).

**Result**: **0 JSON leaves changed, 0 `.typ` lines changed, 0 stderr lines changed.** Both methods agree: the classifier found no classes to report in any of the three categories, and the raw `diff -rq` returned exit 0 with zero output — `SC/post/norm` and `SC/final/norm` are byte-identical across all 168 files. No mover to attribute. Matches the coordinator's expectation (0/0/0) exactly:

- **L-3** (`e12318b`, tier-2 risk-scores parsed once): stderr-only change, and none of the 12 tracked examples is tier-2 — confirmed no effect.
- **L-4** (`819830e`, exact `Decimal` 0.1 tolerance for the S-9 comparand warning): no tracked example sits exactly on the boundary this tightens — confirmed no effect.
- **L-5** (`3dcaf84`, `parse_score` None-input guard): latent on all tracked fixtures (none passes `None` to the parser) — confirmed no effect.
- **L-6** (`da7a196`, `cover.typ` fail-closed guard): guards an input shape (missing posture data) that doesn't occur in any tracked example's `report-data.typ`, and the PDF is outside this oracle's scope regardless — confirmed no effect.
- H-1/M-1/L-1/L-2 (`b03b834`, `f106c9e`) touch `install.sh` only — no extractor/Typst output path, confirmed no effect by construction (not exercised by `snapshot.sh` at all).
- The test and CI-workflow commits (`117b2a3`, `383140e`, `2ef4cec`, `91fbe7a`, `dfccde5`, `0fc2ebe`) add test/workflow files only — confirmed no effect by construction.

**Checks**: `git diff --stat 0ce39d0 729fa1b -- 'examples/**/*.png' 'examples/**/*.pdf.baseline'` → empty. Main-tree `git status --short` → clean before this section was appended.
