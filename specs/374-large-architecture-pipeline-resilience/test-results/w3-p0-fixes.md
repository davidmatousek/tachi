# W3: the P0 checkpoint's findings as landed, and the W3 rulings (for T070)

**Session:** build session S2, PR 1's W3, 2026-11-23. **Branch:** `374-large-architecture-pipeline-resilience`. The P0 checkpoint (T061, at W2's end) was APPROVED_WITH_CONCERNS, with 1 HIGH, 5 MEDIUM and 6 LOW. W3 ran its fixes as a fix lane, FX0, beside W3's planned tasks. Each ruling below was made by the architect or the PM in W3, and recorded in ADR-050 and `contracts/` before or with the code that implements it.

## The P0 findings

| Finding | Disposition | Commits | Tests |
|---|---|---|---|
| **P0-1 (HIGH)** A prose line that starts with `~~~` opened a fence, and the next run lost §4 and §6 | Fixed. A line-start `~` or `#` is written as its reference after any whitespace but a newline, and the reference set has 9 entries. The baseline reader strips only spaces and tabs. The staged file is read back through the next run's reader before any move (KB 22). | `da8097f`, `4d3a103`, `0322bf2` | `test_tachi_parts.py`, `test_tachi_scoring_rules.py` and `test_render_risk_scores.py`'s two-run carries, including an NBSP-led `~~~` |
| **P0-2 (MEDIUM)** A legacy-carried finding lost its tags, date and rationales on the next read | Fixed. §6's tags and scored-on date are read whatever the row's form, D10's step 3a tests the recorded tags, and 1.1's three dimension paragraphs read as legacy prose. | `d727485` | A three-run case: legacy, then `{pii}`, then `{}` |
| **P0-3 (MEDIUM)** The `threats.sarif` fallback crashed on unnamed groups, and blanked the legacy form | Fixed. One reader, `parse_sarif_member_set(with_details=True)`, gives each member's details from its own result. Unnamed groups route their peers, with a `correlation-group-unnamed` warning. The planner's unit rows carry the same details. | `6b9ed96`, `e3e0ae8`, `4b0c16b` | Render- and plan-level cases on copies of three shipped shapes, and a planner-renderer label agreement test |
| **P0-4 (MEDIUM)** Control characters from inputs other than parts reached output | Fixed. `tachi_parts.forbidden_character` is the one predicate; it also catches lone surrogates. Values are refused at intake (exit 2), with a whole-file backstop in the staged checks (exit 4). | `da8097f`, `4d3a103`, `cd79abf` | Each input source, the backstop, and the controls renderer's intake |
| **P0-5 (MEDIUM)** §3 dropped D2's weighted values and the MAESTRO line | Fixed. §3 writes each finding's weighted table (exact `Decimal`, two decimals) and a MAESTRO Layer field. The 1.1 template and `output-formatting.md` say so. | `b0bd04f`, `ef11343` | Goldens, including an x.x5 product, and the fixture's renderer-form baseline |
| **P0-6 (MEDIUM)** A copied peer took its primary's asset tags | Fixed, after the PM's ruling 1 (approved, with an amendment). A NEW or UPDATED peer takes its primary's assessment, and is scored with its own tags. With equal tags it copies its primary exactly. When its own tags move its composite it is flagged `divergent` on the run that scores it. | `6abccc2`, `b0bd04f`, `2d1db5f`, `a82b63d` | Acceptance cases C1–C6 |
| **P0-7 (LOW)** A dead fallback read `refs` from a batch input | Fixed. | `e3e0ae8` | |
| **P0-8 (LOW)** An empty mitigation omitted `message.markdown` | Fixed. `markdown` is always written in both files, the empty string included. | `e3e0ae8`, `03b6810` | |
| **P0-9 (LOW)** The NEW-finding ±1.0 bound needed a defined reading | Ruled and pinned. The bound applies only when a usable baseline `risk-scores.md` was read. The PM added a fifth oracle class for it (ruling 2b). | `7dc8000`, `2d1db5f` | A pin test |
| **P0-10 (LOW)** The RESOLVED-ID self-check flagged third-party text | Fixed in W3, not left to T080 (ruling Q9). The scan covers only what the emitter composes. | `a41baeb` | Copied text naming a RESOLVED ID renders, and composed identity naming one still fails |
| **P0-11 (LOW)** A missing helper read as a missing Python | Lane D's controls command names the five helpers in its presence check. The scorer command's matching follow-up stays with T080. | `1635ec6` | |
| **P0-12 (LOW)** Nits | `module-signatures.md`'s list of additions is complete (`file_reasons` and the W3 names). `fail`'s `counts.open` stays with T080. | `7dc8000`, `ecc41f2` | |

## The W3 rulings that changed code

- **The residual of P0-1:** both fixes, (a) the sink guard and (b) the reader's strip.
- **The heading capture:** the checks and the carry readers find a heading as an exact line outside fences (`match_heading(..., outside_fences=True)`). The extractors' older lookups go to a T080 follow-up, ranked above P0-10.
- **The controls default architecture source,** ruled (B): with no flag, neither plan carries `refs.architecture`, and the controls agent reads the run's snapshot, as the scorer's does.
- **The PM's ruling 2 (the oracle's field scope),** with 2b and 2c. NFR-1 has six value classes. Uncontracted keys are dropped and listed. Gap A: the rules carry name-only `relationships`, from `sarif_common`'s one shared table. Gap B: every controls result carries `maestro-layer`. Gap C: both drivers write `version` beside `semanticVersion`, which is tachi's release version.
- **The controls render's counts, flags, caps and evidence:**
  - §2 overwrites are counted as `cell_overwrites`;
  - the four row checks raise `input:<field>:sources-disagree`;
  - every finding-ID list names at most 10 IDs;
  - a missing evidence file is flagged `input:evidence.file:unresolved`, with a warning, not refused. This also answers T064's SA-2.
- **The controls part's structure** (the 11-cell `matrix_row`, opening with its own ID, and the §4 body's keys and Effort) is rejected at `read_part`, so `reconcile` re-dispatches its batch.

## What T070 re-checks

P0-1 to P0-5, P0-7 and P0-8 as landed. The step-3a tie-break, the architect's reading. The security advisory's PR 1 fix set (T064, `test-results/security-advisory-pr1.md`, section 4), which W4's fix lane (T146) carries with T065–T068's findings.
