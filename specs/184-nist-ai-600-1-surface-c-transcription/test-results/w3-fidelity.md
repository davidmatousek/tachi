# W3 Gate — Transcription Fidelity + Drift Guard (T010)

**Feature**: 184 — NIST AI 600-1 Surface C Transcription
**Reviewer**: code-reviewer (independent W3 gate, Risk-184.3 mitigation)
**Reviewed at**: HEAD `7d569ec` on branch `184-nist-ai-600-1-surface-c-transcription`, 2026-06-11
**Binding references**: `contracts/surface-c-transcription.contract.md` (C2/C3/C5), `quickstart.md` §1–§3, §5
**Interpreter**: `/usr/bin/python3` (Team-Lead C5 pin) for all Python invocations

---

## 1. Verdict Table

| Check | Description | Verdict |
|---|---|---|
| (a) | 15 added edges verbatim vs contract C2 | **PASS** |
| (b) | 16 removals 1:1 vs contract C3; control→rmf class untouched at 31 | **PASS** |
| (c) | Diff drift-guard — every diff line accounted for as intended change | **PASS** |
| (d) | Exempt surfaces zero-diff + `_sort_key_nist` byte-untouched | **PASS** |
| (e) | Baseline-fixture mismatch set unchanged (re-scoped per architect P0 ruling) | **PASS** |
| Suite | `test_taxonomy_integrity.py` | **PASS — 5/5** |
| §2 | Surface C = 15, drift class = 0, control→rmf = 31 | **PASS** |
| §3 | Arithmetic 541 primary / 37 related / 0 superseded = 578 total | **PASS** |

**Gate verdict: PASS** — 0 critical, 0 warning findings. 3 informational observations (§4).

---

## 2. Evidence

### 2.1 Check (a) — 15 added edges verbatim (contract C2)

Structural comparison of the parsed `tachi-stride-ai-category → nist-ai-600-1` class against the
C2 table hardcoded from the contract (multiset comparison, full edge-dict canonicalization):

```
a1 count==15: True
a2 pairs==C2 (multiset): True
a3 no dup pairs: True
a4 attrs all primary/high/citation: True      # edge_type: primary · confidence: high ·
                                              # citation: .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md
a5 target ids all str: True                   # parse-level quoted-string check
a6 extra keys per edge: []                    # exactly {source,target,edge_type,confidence,citation}
a7 source/target subkeys: ['id', 'taxonomy']
a8 no other nist-ai-600-1 edges: True         # no reverse-direction or other-class edges reference nist-ai-600-1
```

Raw-text confirmation: the diff (+5641,159 hunk) shows all 15 target ids literally double-quoted
(`id: "2.4"`, `"2.9"`, `"2.10"`, `"2.12"`), in exact C2 row order 1–15. Referential resolution of
the quoted ids against `nist-ai-600-1.yaml` is covered by `test_crosswalk_referential_integrity`
(PASSED). Direction is FR-022-correct: source taxonomy `tachi-stride-ai-category`, target taxonomy
`nist-ai-600-1` on all 15.

### 2.2 Check (b) — 16 removals 1:1 (contract C3)

Parsed `git show main:schemas/taxonomy/crosswalk.yaml` and compared classes:

```
b1 main pre-count==16: True                   # exactly the 16 C3 pairs existed on main
b2 main pairs==C3 (multiset): True
b3 branch class empty: True                   # stride-ai → nist-ai-rmf now 0
b4 control->rmf main==31: True branch==31: True
b5 control->rmf edges byte-identical: True    # 27 Surface B cells + 4 Issue #325 extras untouched, NOT flagged per C3
```

### 2.3 Check (c) — Diff drift-guard

Whole-file edge multiset delta (branch vs main, canonical JSON keying):

```
c1 removed edge total==16: True
c2 removed pairs==C3: True
c3 added edge total==15: True
c4 added pairs==C2: True
c5 removed only from stride-ai->nist-ai-rmf: True
c6 added only to stride-ai->nist-ai-600-1: True
c7 untouched remainder identical: True        # 563 non-delta edges byte-identical
totals: main 579 -> branch 578
```

Textual diff accounting — `git diff main -U0 -- schemas/taxonomy/crosswalk.yaml` = 166 insertions /
168 deletions, every hunk inspected and attributed:

| Hunk | Lines | Attribution |
|---|---|---|
| `@@ -6 +6 @@` | 1−/1+ | Header enum `taxonomy (7):` → `taxonomy (8):` incl. `nist-ai-600-1` (intended, contract C5) |
| `@@ -13 +13 @@` | 1−/1+ | Edit-lineage counts `542` → `541 primary + 37 related + 0 superseded` (intended, contract C5) |
| `@@ -19,0 +20,4 @@` | 4+ | F-184 edit-lineage entry — follows the established F-186/F-182 lineage-log convention already present on main L14–19; content accurate (15 added / 16 removed / 8-value enum / 12-record catalog). Part of the intended header update (see Observation O1) |
| `@@ -379,20 +382,0 @@` | 20− | C3 rows 2–3 (`prompt-injection→MEASURE 2.7`, `data-poisoning→MEASURE 2.7`), 2 edges × 10 lines |
| `@@ -1751,140 +1734,0 @@` | 140− | Remaining 14 C3 edges × 10 lines (rows 1, 4–16) |
| `@@ -2002,6 +1846 @@` | 6−/1+ | "Surface C DEFERRED" NOTE retirement (main L2002–2007) → one-line F-184 pointer (intended, contract C5) |
| `@@ -5801,0 +5641,159 @@` | 159+ | EOF F-184 section: 1 blank + 8-line section banner (matches the `# ───` convention used by F-182/F-A1.3/T023/Batch sections on main) + 15 C2 edges × 10 lines, in C2 table order |

Sum: deletions 1+1+20+140+6 = 168 ✓; insertions 1+1+4+1+159 = 166 ✓. **Zero unattributed diff lines.**

Removal-site hygiene: no orphaned comments. The L379 region never had its own section banner on
main (no "Slice 4" banner exists on either side); the L1751 block sat at the tail of the Batch 5
section whose banner reads `(tachi-control-category ↔ NIST)` — removing the stride-ai drift edges
makes that section *more* consistent with its banner. The T023 section banner block now ends with
the accurate one-line F-184 pointer.

### 2.4 Check (d) — Exempt surfaces (quickstart §5)

```
$ git diff main --stat -- docs/architecture/01_system_design/README.md specs/180-taxonomy-crosswalk-collection/
OK: exempt surfaces untouched                 # empty diff

$ /usr/bin/python3 <AST extraction comparison, quickstart §5 block 1>
OK: _sort_key_nist byte-untouched (code + docstring)
```

### 2.5 Check (e) — Baseline-fixture test (re-scoped gate item)

```
$ /usr/bin/python3 -m pytest tests/scripts/test_init_sh_substitution.py -q
E  AssertionError: 3 file(s) drifted from baseline. First 10:
   ['docs/devops/README.md', 'docs/devops/CI_CD_GUIDE.md', 'docs/INSTITUTIONAL_KNOWLEDGE.md']
1 failed, 1 passed in 61.81s
```

Mismatch set is EXACTLY the 3 grandfathered files (set-equal to the architect P0 ruling list; 3 < 10
so the printed list is complete). No 4th file, no change to the set → **no NEW mismatches from
F-184**. Failure remains the pre-existing fixture staleness (F-302/F-305 era), NOT an F-184
regression. Independently reproduces the committed tester run at `7d569ec`
(`test-results/wave-03/failures.txt`: same command, same 3-file set, "0 regressions, 0 new,
1 pre-existing").

### 2.6 Integrity suite (quickstart §1) and counts (§2, §3)

```
$ /usr/bin/python3 -m pytest tests/schemas/test_taxonomy_integrity.py -v
test_framework_yamls_load PASSED
test_crosswalk_loads PASSED
test_crosswalk_referential_integrity PASSED
test_citation_shape PASSED
test_records_sorted PASSED
5 passed in 1.03s

$ <quickstart §2>
Surface C edges (expect 15): 15
Drift class    (expect 0):  0
control->rmf   (expect 31): 31
pairs: [('agent-autonomy','2.9'), ('data-poisoning','2.12'), ('data-poisoning','2.9'),
 ('denial-of-service','2.9'), ('info-disclosure','2.10'), ('info-disclosure','2.4'),
 ('info-disclosure','2.9'), ('model-theft','2.10'), ('model-theft','2.9'),
 ('privilege-escalation','2.9'), ('prompt-injection','2.9'), ('tampering','2.12'),
 ('tampering','2.9'), ('tool-abuse','2.12'), ('tool-abuse','2.9')]   # == C2 sorted

$ <quickstart §3>
primary=541 related=37 superseded=0 total=578
arithmetic OK: 541/37/0 = 578                 # C3 arithmetic gate: 542−16+15=541 · 579−16+15=578 · floor ≥500 holds (headroom 41)
```

§7 combined gate equivalence: `tests/schemas/` contains only `test_taxonomy_integrity.py`
(+ `__init__.py`), so the two runs above jointly equal the §7 command (1 failed [pre-existing],
6 passed — matching wave-03/failures.txt).

---

## 3. Findings

**None.** 0 CRITICAL, 0 WARNING, 0 SUGGESTION findings against the gate rule (unintended diff
lines, contract mismatches, new fixture mismatches).

---

## 4. Informational Observations (non-gate, no action required for W3)

- **O1 — Two intentional comment blocks beyond the strictly-enumerated (c) list**: the +4-line
  F-184 edit-lineage entry (header) and the 8-line `# ─── F-184` EOF section banner. Both are
  accurate, follow the file's own established conventions (F-186/F-182 lineage entries and `# ───`
  section banners pre-exist on main), and are cross-referenced BY the intended NOTE-retirement
  pointer line ("see the `# ─── F-184` section at EOF"). Classified as constituent parts of the
  intended header-update and 15-edge-addition change-units, not drift. Documented here so the gate
  decision is auditable.
- **O2 — Uncommitted working-tree noise**: `docs/product/_backlog/BACKLOG.md` has a 1-line
  uncommitted modification (auto-generated timestamp `2026-06-11T01:58Z` → `T11:30Z`, from a
  backlog regeneration). Outside the committed F-184 delta; not crosswalk, not an exempt surface.
  Will wash out at the next `/aod.status` commit or can be discarded.
- **O3 — Committed-delta inventory sanity (23 files vs main)**: crosswalk.yaml (reviewed
  exhaustively above), nist-ai-600-1.yaml catalog + test_taxonomy_integrity.py surgery (W1-gate
  scope, previously reviewed; `_sort_key_nist` re-verified byte-identical here), and
  specs/PRD/backlog/agent-assignment workflow artifacts. No surprise files.

---

## 5. Gate Verdict

**PASS** — W3 transcription-fidelity + drift-guard gate clears. The crosswalk change-set is
contract-exact (C2 15/15 verbatim, C3 16/16 1:1, nothing else touched), exempt surfaces are
zero-diff, `_sort_key_nist` is byte-identical, the integrity suite is 5/5, count arithmetic holds
at 541/37/0 = 578, and the baseline-fixture mismatch set is unchanged at the 3 grandfathered files.
Proceed to W4.
