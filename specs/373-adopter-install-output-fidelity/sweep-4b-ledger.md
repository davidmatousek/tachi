# FR-K12.5 Sweep — "Section 4b" Disposition Ledger

**Task**: tasks.md T017, "the sweep" (Lane B2b, W2, stage 2).

**Rule applied at every occurrence**: The current schema's resolved-findings section
is `## 4c. Resolved Findings` (`templates/tachi/output-schemas/threats.md:480`). The
resolved-findings parser (`tachi_parsers.py::parse_resolved_findings`, via
`_RESOLVED_FINDINGS_HEADING = r"^##\s+4[bc]\.\s+Resolved Findings\s*$"`) accepts the
legacy `## 4b.` spelling as a backward-compatible alias (FR-K12.4). Schema 1.4
(Feature 142) separately gave the `## 4b.` heading to a *different* section, "Findings
by Agentic Pattern" (`threats.md:392`), which is unrelated to Resolved Findings and
was **never** renumbered. A reference is:
- **changed** when it describes the current/canonical format and said "Section 4b"
  meaning Resolved Findings (now stale — the canonical heading is 4c);
- **kept** when "Section 4b" in that reference means Findings by Agentic Pattern (a
  different, correct, still-current usage); or when the site is outside the
  maintained, distributed surface (see "Found outside the sweep" below).

Source of the site list: spec.md FR-K12.5 (the PM's 16-site/7-file count, of which
`scripts/tachi_parsers.py` — the resolved-findings docstring and code — was already
brought into compliance by FR-K12.4/T016 in W1, prior to this sweep; verified
unchanged/correct below). This task's assignment ("the remaining 4b→4c sites") is the
other 6 files / 13 occurrences enumerated below.

---

## Changed (13 occurrences, 6 files)

| # | File:Line | Old text | New text | Rule |
|---|-----------|----------|----------|------|
| 1 | `.claude/skills/tachi-orchestration/references/output-schemas.md:173` | "...When the threats.md template uses Section 4b for a different artifact (Resolved Findings, baseline-aware mode), this pattern-grouping section may render under a renumbered heading chosen at code time per plan.md Component 4..." | "...This pattern-grouping section owns the `## 4b.` heading permanently. The baseline-aware Resolved Findings artifact...is `## 4c.` — renumbered specifically to avoid colliding with this section (FR-K12.5); the resolved-findings parser also accepts the legacy `## 4b.` spelling for backward compatibility (FR-K12.4). The two 'Section 4b' meanings are never the same section." | Stale collision note that hedged on an already-settled fact (spec.md: "the stale collision note that hedges on it"). Rewritten to state the settled disposition plainly, since the ambiguity it was hedging about is resolved. |
| 2 | `.claude/skills/tachi-orchestration/references/output-schemas.md:275` | "Section 4b (Resolved Findings) is present when a baseline was used...." | "Section 4c (Resolved Findings) is present when a baseline was used...." | The orchestrator's own producer/validation checklist — the site spec.md identifies as "the likely source of legacy `## 4b.` outputs." Describes current format; corrected to 4c. |
| 3 | `.claude/agents/tachi/report-assembler.md:242` | "...parse all sections including Section 4b (Resolved Findings) and Section 8..." | "...parse all sections including Section 4c (Resolved Findings) and Section 8..." | Describes current format (what a v1.2-schema threats.md contains). Plain fix to 4c. |
| 4 | `templates/tachi/output-schemas/threat-report.md:57` | "...Count of findings with delta_status RESOLVED (from Section 4b)." | "...Count of findings with delta_status RESOLVED (from Section 4c)." | Input-contract description of the source threats.md, which is always template-conformant (4c). Plain fix. |
| 5 | `templates/tachi/output-schemas/threat-report.md:207` | "...They appear only in Section 4b of the input threats.md." | "...They appear only in Section 4c of the input threats.md." | Same as #4 — attack-tree delta dispatch guidance. Plain fix. |
| 6 | `templates/tachi/output-schemas/threat-report.md:298` | "...Baseline findings no longer applicable (from Section 4b)" | "...Baseline findings no longer applicable (from Section 4c)" | Same as #4 — Delta Summary table guidance. Plain fix. |
| 7 | `templates/tachi/output-schemas/threat-report.md:303` | "...Reference RESOLVED findings from Section 4b by ID..." | "...Reference RESOLVED findings from Section 4c by ID..." | Same as #4 — remediation progress narrative guidance. Plain fix. |
| 8 | `templates/tachi/output-schemas/threat-report.md:314` | "...plus RESOLVED findings from Section 4b. The sum..." | "...plus RESOLVED findings from Section 4c. The sum..." | Same as #4 — generation guidance for delta counts. Plain fix. |
| 9 | `scripts/extract-report-data.py:2287` (line shifted from the `63438d7` `:2202` baseline due to this stage's earlier K12/K13.1 commits; located fresh) | `# Parse resolved findings from Section 4b (empty when no baseline)` | `# Parse resolved findings from Section 4c (legacy `4b` heading also accepted, FR-K12.5); empty when no baseline` | Code comment on the call to the shared `parse_resolved_findings()`. The call itself was already correct (imports the shared, dual-accepting parser) — only the comment was stale. Comment updated to name both the canonical heading and the accepted legacy alias, since it sits directly at the call site. No behavior change. |
| 10 | `docs/architecture/01_system_design/README.md:2077` | "Parse Section 4b Resolved Findings table.... Returns empty list when Section 4b is absent..." | "Parse the `## 4c.` Resolved Findings table (the legacy `## 4b.` heading is also accepted, FR-K12.5).... Returns empty list when neither heading is present..." | Dedicated function-reference row for `parse_resolved_findings()`. Chosen as one of the two sites (with #13) that names the legacy-alias behavior explicitly, since this row's whole purpose is to document that function's actual behavior. |
| 11 | `docs/architecture/00_Tech_Stack/README.md:130` | "8 sections + Section 4a/4b: ...**Correlated Findings (4a)**, **Resolved Findings (4b)** (Feature 074)..." | "8 sections + Section 4a/4c: ...**Correlated Findings (4a)**, **Resolved Findings (4c)** (Feature 074; heading changed from `4b`, FR-K12.5)..." | Schema structure enumeration; "4b" appeared twice in this one line (the summary-prefix shorthand and the bolded label) — both changed together to avoid a self-contradictory line. Plain fix, with a short pointer to why the heading moved. |
| 12 | `docs/architecture/00_Tech_Stack/README.md:200` | "...canonical 8-section + Section 4a/4b threat model template.... RESOLVED findings section (Section 4b)...." | "...canonical 8-section + Section 4a/4b/4c threat model template.... RESOLVED findings section (Section 4c)...." + one added closing sentence noting the 4b→4c renumbering and the parser's legacy acceptance | This entry already correctly discusses Feature 142's *separate* "new conditional Section 4b 'Findings by Agentic Pattern'" later in the same paragraph (untouched) — so the line genuinely has two different "4b" meanings ("two of them mixed" per spec.md). The Feature-074 "Resolved findings section (Section 4b)" mention was the stale one; fixed to 4c. The leading "4a/4b" shorthand became "4a/4b/4c" so the count matches the three lettered subsections the paragraph actually describes (4a, 4b, and now 4c). |
| 13 | `docs/architecture/00_Tech_Stack/README.md:234` | "...`parse_resolved_findings()` parses Section 4b Resolved Findings table..." | "...`parse_resolved_findings()` parses the Section 4c Resolved Findings table (the legacy `4b` heading is also accepted, FR-K12.5)..." | `scripts/tachi_parsers.py` module-reference row, describing the same function as #10. The second of the two sites chosen to name the legacy-alias behavior explicitly. |

All 13 are prose/comment-only; no parsing logic changed (the parser already accepted
both spellings, per T016 in W1). Verified via `git diff --stat` that only these 6
files changed in this commit.

---

## Kept — means Findings by Agentic Pattern, untouched (same 6 files + 1 adjacent)

These "Section 4b" occurrences were left exactly as they were: they correctly refer to
the *other* Section 4b (Findings by Agentic Pattern, Feature 142), which was never
renumbered and is not part of this sweep.

| File:Line(s) | Disposition |
|---|---|
| `.claude/skills/tachi-orchestration/references/output-schemas.md:35,169,183,184,189,199,365,368` | The section's own heading, schema-version note, and field/rendering rules. All correctly mean Findings by Agentic Pattern. |
| `docs/architecture/01_system_design/README.md:3033,3099` | Feature 142 changelog entries describing the new conditional Section 4b. Correct as-is. |
| `docs/architecture/00_Tech_Stack/README.md:200` (the Feature 142 sentence), `:218` | "new conditional Section 4b 'Findings by Agentic Pattern'" / "conditional Section 4b" in the Phase 3.6 pipeline description. Correct as-is. |
| `.claude/agents/tachi/orchestrator.md:670` | "threats.md Section 4b (Findings by Agentic Pattern): gates the conditional Section 4b..." Found via the repo-wide grep (not in T017's assigned list); correct as-is, part of the maintained/distributed surface, confirmed untouched. |

---

## Found outside the sweep (repo-wide grep, not changed)

A repo-wide grep for `4b` (excluding `examples/`) turned up many more matches. None of
these are part of "the maintained, distributed surface" (agents, skills, templates,
scripts and architecture docs) that FR-K12.5 / spec.md AC US-3a#11 scopes the sweep to;
each category below is exactly one of the categories spec.md explicitly places out of
the sweep:

1. **The non-distributed legacy `agents/` tree** (spec.md: "Out of the sweep: the
   non-distributed legacy `agents/` tree..."). This is a pre-rename copy, not
   installed by `install.sh` / not in `INSTALL_MANIFEST.md`. Real "Section
   4b = Resolved Findings" text still present, not changed:
   - `agents/threat-report.md:55,696,856,859,863,880`
   - `agents/threat-infographic.md:72,84`
2. **The frozen `init-baseline-tree` fixture** (spec.md: "...the frozen
   init-baseline-tree fixture..."): `tests/fixtures/init-baseline-tree/docs/architecture/01_system_design/README.md:2077`
   — a frozen byte-for-byte copy used as a golden/diff baseline by the installer
   tests; it is deliberately *not* kept in sync with the live docs tree.
3. **Historical specs/ and PRD artifacts** (spec.md: "...historical PRDs and
   CHANGELOG entries..."; `specs/` is "Archived feature artifacts (per-feature
   history)" per the project's CLAUDE.md). ~30 occurrences across point-in-time
   planning/validation/review docs for already-delivered features, e.g.
   `specs/104-downstream-baseline-propagation/{plan,tasks,agent-assignments,
   final-review-*,validation-t01[67],checkpoints/p0-review,NEXT-SESSION}.md`,
   `specs/074-baseline-aware-pipeline/{validation-report,validation-t036-quickstart,
   checkpoint-p1,NEXT-SESSION}.md`, `specs/142-maestro-agentic-pattern-expansion/*`,
   `specs/189-source-attribution-schema-extension/research.md`, and this feature's
   own `specs/373-.../{spec,research,plan,tasks,NEXT-SESSION,agent-assignments,
   checklists/requirements}.md` (which *describe* the bug/fix and correctly use "4b"
   when discussing the legacy heading or the bug's history). Also two captured
   run-artifacts under `specs/302-asset-tag-output-wiring/test-results/` and
   `specs/248-substitution-surface-hardening/tasks-runlog.txt` (point-in-time test
   output, not living docs). None of these are edited — they are historical records
   of what was true (or was being planned/reviewed) at the time, exactly like
   CHANGELOG.md history.
   `docs/product/02_PRD/373-adopter-install-output-fidelity-2026-09-27.md` and other
   `docs/product/02_PRD/*.md` files fall in this same "historical PRDs" category and
   were likewise left untouched.
4. **AOD step/wave numbers** (spec.md: "...and AOD step numbers."): e.g.
   `.claude/skills/~aod-define/skill.md:737,874,876,886` ("Step 4b: Persist Governance
   Artifacts"), `.claude/commands/aod.document.md:170,267` ("4b: Compare and Report"),
   `.claude/skills/security/SKILL.md:309` ("4b: SCA Finding Format"),
   `.claude/skills/~aod-deliver/SKILL.md:816` ("Wave 4b"),
   `.claude/skills/~aod-build/USAGE.md:64` ("4b. Key Achievements"),
   `docs/guides/prompts/developer-guide-prompt.md:758` ("Section 4b — Post-Pipeline
   Enrichment Workflow"). These are AOD's own orchestration step/section numbering
   (unrelated documents' internal structure) — the string "4b" coincides but the
   meaning has nothing to do with threats.md's Resolved Findings section.
5. **Test code and test fixtures** (the test lane's ownership, T019 — not touched by
   this docs-only sweep, and explicitly out of scope for a lane that owns prose/comment
   files): `tests/scripts/test_tachi_parsers.py`, `tests/scripts/fixtures/fidelity_373/
   {README.md,baseline_resolved_4b_legacy/threats.md}`, `tests/scripts/
   test_pattern_extraction.py`. These already correctly test *both* the `4c` and
   legacy-`4b` spellings (T016's dual-acceptance behavior) — nothing here describes
   current format incorrectly; it's test infrastructure exercising the alias.
6. **`scripts/tachi_parsers.py`** (the 7th file in spec.md's 16-site/7-file count —
   "the resolved-findings docstring and code, FR-K12.4"): already correct, verified
   this session. `:1006` — `_RESOLVED_FINDINGS_HEADING = r"^##\s+4[bc]\.\s+Resolved
   Findings\s*$"`; `:1010-1011` — docstring: "Parse the Resolved Findings table: the
   template's ``## 4c.`` heading, or the legacy ``## 4b.`` spelling (FR-K12.4)."; `:214`
   — a `K12` doc-comment citing the same regex; `:673` — a Findings-by-Agentic-Pattern
   mention (correct, different section). This file was implemented by FR-K12.4/T016 in
   W1 (prior to this stage), is not in B2b's W2 ownership, and needed no further change.
7. **Hex-hash / commit-SHA false positives**: substrings like `c4b8dc6`,
   `4b659b935fa4`, `0e1ef0b8-20aa-4be7-...` in security-scan reports, delivery SHAs and
   ADR revision-history rows. Not "4b" as a section reference at all — noise from the
   grep, not a disposition.

---

## Verification

- `git diff --stat` for this commit touches exactly the 6 files listed in "Changed"
  above (plus this ledger).
- No test pins the swept strings: `grep -rn "Section 4b" tests/` finds only sites in
  category 5 above (which intentionally test the legacy alias, not the swept prose).
- Gated suite (`test_extract_report_data.py`, `test_extractor_contract_fixes.py`,
  `test_catalog_drift_guard.py`, `test_mmdc_preflight.py`) run green after this commit
  — see `.aod/results/sbe-b2b-373-s2.md`.
