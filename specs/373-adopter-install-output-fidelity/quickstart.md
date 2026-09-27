# Quickstart: verifying Feature 373

A runbook for build agents and reviewers. The commands are illustrative, and paths are relative to the repo root unless they are marked scratch.

**Revision 1 (2026-09-27).** This revision folds in the plan reviews:
- PM: RC-P1, RC-P2, RC-P3, RC-P6 and RC-P8; P-10.1 to P-10.3; R-P1 and R-P8;
- architect: M2, M6, M7 and L3.

Changed sections are marked **(rev. 1)**.

## 1. Safety rules (read first)

- **Never run the extraction modules, the extractors or `install.sh` in the main working tree** unless you are prepared to restore what they write.
  - The existing report tests and the report extractor render attack-tree PNGs into `examples/` (#365).
  - Use a **scratch clone** (`git clone --no-hardlinks . "$SCRATCH/tachi"`), where `$SCRATCH` is the session scratchpad.
  - From wiring commit A-2 on, PD-8 moves the one example-writing fixture to a temporary copy. The PR describes that change as #365-adjacent hygiene, not a #365 fix.
- **Commit before running the gated suites.** `tachi-pytest.yml`'s harness clones the committed HEAD.
- **Stage explicit paths only** (never `git add -A`). Before each commit, run `git status --short`. Restore only the `examples/**/*.png` changes **this session produced**, using the zsh-safe pipe:
  ```bash
  git status --short | awk '$1=="M" && $2 ~ /^examples\/.*\.png$/ {print $2}' | xargs git checkout --
  ```
- **New tests never write into `examples/`.** They use `tmp_path` copies, or run in-process.

## 2. Running the tests **(rev. 1)**

**The fast workflow's three jobs** (`tachi-install-fidelity.yml`, ubuntu, seconds each):
```bash
# manifest-completeness: the cut line's only job (A-1)
python3 -m pytest tests/scripts/test_install_manifest_completeness.py -v

# extraction-fidelity: pre-existing modules from A-2, then contract (A-3) and parity (W2)
python3 -m pytest \
  tests/scripts/test_tachi_parsers.py \
  tests/scripts/test_extract_infographic_data.py \
  tests/scripts/test_extract_report_data.py \
  tests/scripts/test_extractor_contract_fixes.py \
  tests/scripts/test_gemini_request_contract.py \
  tests/scripts/test_extraction_sibling_parity.py -v

# report-posture: W2, only if K13-posture ships; CI sets TACHI_REQUIRE_TYPST=1
TACHI_REQUIRE_TYPST=1 python3 -m pytest tests/scripts/test_report_posture_contract.py -v
```

- Run them **in a scratch clone**. The report module writes PNGs into `examples/` until A-2 lands.
- Without mmdc, the five `test_existing_image_flags_unchanged` cases skip (PD-8).
- A missing Typst fails the posture test rather than skipping it when `TACHI_REQUIRE_TYPST=1` is set.

**The installer tests** (`tachi-pytest.yml` 2-OS matrix). Locally, they run on macOS's strict shell:
```bash
LC_ALL=C python3 -m pytest tests/scripts/test_install_sh_symlink_preflight.py tests/scripts/test_install_sh_ref_restore.py -v
```

The helper invokes `/bin/bash` (3.2.57) explicitly, so a Homebrew bash first on `PATH` doesn't mask the strict leg.

**The manual-install loop under bash 3.2 and zsh** is recorded once in `test-results/`:
```bash
LC_ALL=C python3 -m pytest tests/scripts/test_install_manifest_completeness.py -k manual_install_loop -v
```

The zsh variant feeds the block on stdin to `zsh -f -i`, which models a paste into a stock interactive shell. It skips when zsh is absent.

## 3. W0 pre-state and the Group B oracle (in a scratch clone at the W0 commit) **(rev. 1)**

**Pre-state** (`specs/373-*/test-results-prestate.md`). Record the literal pass, fail, skip and error totals for every module in §2 and for `tachi-pytest.yml`'s current invocation list. Note any red that exists before this bundle's code lands. The out-of-gate set predates F-362, so re-record it rather than assuming it.

**Oracle pre-snapshot.** Cover every **tracked** `examples/**` directory that holds a `threats.md` (12 at HEAD; untracked `test-output` runs are out of scope, and the scratch clone doesn't see them), plus risk scores or controls where present:
```bash
for t in baseball-card system-architecture risk-funnel maestro-stack maestro-heatmap executive-architecture; do
  python3 scripts/extract-infographic-data.py --target-dir "$D" --template "$t" --output "$OUT/$(basename "$D")/$t.json" \
    || echo "$D $t exit=$?" >> "$OUT/nonzero-exits.txt"     # e.g. executive-architecture without scope data exits 2
done
python3 scripts/extract-report-data.py --target-dir "$D" --template-dir templates/tachi/security-report \
  --output "$OUT/$(basename "$D")/report-data.typ"
```

- **Normalize** run-specific fields before diffing: `generation_timestamp`, absolute paths such as `source_file`, and image paths.
- **After W2**, repeat into `$OUT_POST` and diff.
- **Attribution (rev. 1, PM §9 item 4).** Group `specs/373-*/oracle-diff.md` **by field class × K-item, with per-example counts**; one row per example × file × field would swamp W3. The expected movers are:
  - K10: none among the tracked examples (every `###` MAESTRO run is an untracked local `test-output` directory);
  - the K13.1 M5 fallback examples;
  - `agentic-app`'s delta counts and badges (K12 bracket normalization);
  - the posture and `allow_list` fields (every JSON);
  - the funnel fields.
- **Snapshots** stay in the scratchpad. Only `oracle-diff.md` is committed.

## 4. Live renders (W0 smoke, K14, K15): `[MANUAL-ONLY]` **(rev. 1)**

**Secret handling (NFR-5).**
- Load the key into the environment **per command** (shell calls don't share environment), or run the whole session under the secret store's runner.
- Never echo it, never use `curl -v` or `--trace*`, never send it as `?key=`. Send it only as a header, read from stdin.
- The inner `sh -c` sees only **exported** variables, so export `BODY`, `MODEL` and `RESP`.

```bash
export BODY="$SCRATCH/w0/body-3x4-2k.json" MODEL="gemini-3.1-flash-image" RESP="$SCRATCH/w0/resp.json"
GEMINI_API_KEY="$(op read 'op://<vault>/Gemini API Key/credential')" sh -c '
  printf "x-goog-api-key: %s\n" "$GEMINI_API_KEY" |
  curl -sS -H @- -H "Content-Type: application/json" -d @"$BODY" \
    -w "%{http_code} %{time_total}\n" \
    "https://generativelanguage.googleapis.com/v1beta/models/$MODEL:generateContent" -o "$RESP"'
```

A scratch-only Python helper reads `$RESP`. It finds the part with `inlineData` (or `inline_data`) and records which key casing came back. It decodes the image and reads the pixel dimensions from the PNG IHDR or the JPEG SOF marker. It never writes into the repo.

**W0 smoke (PD-3, P-10.3, RC-P3).**
- **The calls.** Eight calls, each with a trivial prompt: `MODEL` ∈ {`gemini-3-pro-image`, `gemini-3.1-flash-image`} × `aspectRatio` ∈ {`16:9`, `3:4`} × {no `imageSize`, `imageSize: "2K"`}. Both keys go inside `imageConfig`.
- **Record for each call:**
  - the HTTP status;
  - whether an image part came back;
  - the pixel dimensions;
  - the response time;
  - the response key casing.
- **Retry.** A transient 429 or 5xx gets one retry, and the second result stands.
- **Decisions:**
  1. **Restore `image_size: "2K"` only if all four 2K calls return an image whose long edge exceeds its default variant's.** Otherwise the default size ships.
  2. **3:4 at the default size must succeed on both models.** If it does not, stop and take it to the architect before K14 commits.
  3. **A refusal with any status other than 404 or 403** (for example a 429 with a zero quota, or a 400 `FAILED_PRECONDITION`): record it and bring the chain-walk semantics back to the architect before K14 commits (R-P2, PD-14).
- **If a model is unreachable (rev. 1, RC-P8, P-10.1).** Record it, diagnose it (key scope, model entitlement, quota) and retry within TW-6's budget.
  - **W1 proceeds regardless**, because K14's deterministic parts need no render.
  - P-9.2's full path applies only after TW-6's half day plus one retry session, and only if **both** models stay blocked.
  - If one model is blocked, both stay in the chain. The blocked one is recorded as statically verified only (in the reference provenance, the PR record and the release notes), with a follow-up issue, and 2K stays dropped.

**K14 render set (W3; P-10.2, RC-P2).** It runs **through the agent end to end**: `/tachi.infographic` in a scratch clone, on a scratch copy of the MAESTRO reference example, never a bare `curl` of the body.
- (a) **K15 ships:** its first-iteration renders double as K14's per-template renders.
- (b) **K15 is carved:** each of the six templates renders once, with no leakage check and no iteration.
- (c) **Either way:** at least one render uses the **fallback** model (set that template block's `model` to `gemini-3.1-flash-image` in the scratch clone only). Executive-architecture (3:4) is assembled into a scratch PDF and must land on **one** portrait page.
- (d) **A blocked model** is recorded as statically verified only.
- **Latency (P-10.3 (d)).** If 2K was restored and any 2K render takes more than about 45 s, drop 2K before merge in one commit: the six blocks, the reference, the adapter copy and `IMAGE_SIZE_RESTORED`. Record why.

**K15 (W3, only if K15 ships).** One image per template, all six, with executive-architecture at 3:4. Check each image for any layout-label text and for any ID outside the JSON `allow_list`. Allow at most two prompt iterations (TW-5), and record any residual leakage as a follow-up.

**Each record** (in the PR body):
- template, model, endpoint, date, HTTP status and response time;
- the pixel dimensions;
- the visual-check verdict;
- that the saved extension matches the image's magic bytes (`\x89PNG` → `.png`; `\xFF\xD8\xFF` → `.jpg`);
- the response key casing;
- for executive-architecture, that the portrait image lands on **one** page of the scratch PDF.

Images are never committed.

## 5. Golden regeneration (W2 wave-final, authorized files only) **(rev. 1)**

The tester regenerates only the goldens SC-8 authorizes, from the fixture the test uses, as the last W2 commit. The architect checkpoint at the end of W2 reviews it.
```bash
python3 scripts/extract-infographic-data.py --target-dir tests/scripts/fixtures/exec_arch/agentic_app \
  --template <t> --output tests/scripts/fixtures/golden/<t>.json
```

The authorizations:
- risk-funnel and baseball-card: for K11 (the baseball card only while K11 ships);
- every golden that gains posture fields: for K13;
- all five: for K15.

Review the diff hunk by hunk, and attribute each hunk to one K-item in the PR. In W3, regenerate again only if a K15 prompt iteration changes template text.

## 6. Installer smoke (sandbox, scratch only) **(rev. 1)**

```bash
S="$SCRATCH/inst"; mkdir -p "$S/p/.agents/skills" "$S/p/.claude" && ln -s ../.agents/skills "$S/p/.claude/skills"
(cd "$S/p" && /bin/bash "$SCRATCH/tachi/scripts/install.sh")                      # expect: refusal, "Nothing was written.", exit 1
(cd "$S/p" && /bin/bash "$SCRATCH/tachi/scripts/install.sh" --follow-symlinks)    # expect: resolved destination named; installs
```

These are refused **with or without** the flag:
- a dangling or looping link;
- a link to the wrong type (a file where a folder is needed);
- a nested link;
- any destination whose physical location is inside the tachi clone, including through a link to the clone's **parent** (for example `templates → ..` next to the clone).

A dangling deprecated-command file link is refused without the flag and skipped with it. Always use a scratch clone as the source, never the live checkout.

## 7. Release notes (deliver; PD-7) **(rev. 1)**

**The notices** (`upgrading.md`, the PM's W4 text, generic per NFR-6):

| # | Notice | Include when |
|---|---|---|
| 1 | Update the clone first, then re-run `install.sh`; names the three skills and the Affected Assets populator | always |
| 2 | The D-1 behavior note | always |
| 3 | M5: `Threat-model mitigation:` marks mitigations shown where the controls report gives no recommendation | always |
| 4 | The funnel narrows by risk volume; the Risk Reduction figure on the funnel and the baseball card is computed from the controls rows and can differ from the controls summary | K11 ships |
| 5 | A `report-data.typ` compiled outside `/tachi.security-report` now stops with a regenerate instruction | K13-posture ships |
| 6 | The render path is statically verified only, for the named model(s) | P-9.2 or P-10.1 fired |
| 7 | Replace a symlinked destination before re-running | TW-7 shipped Lane A without K3 |

**Step 1: before merging the release-please PR** (R-P1).
- Insert the notices **inside the PR body's notes region**: after the `## [x.y.z](…) (date)` line and before the first `###` section.
- Leave the `:robot:` header, both `---` separators and the footer intact.
- Make this the **last action before the merge**, because release-please regenerates the body on every push to `main`.
- *Why this works:* release-please builds the GitHub release from the merged PR's body. At plan review, v4.48.0's published body matched PR #371's notes region byte for byte, apart from one trailing blank line. So the notices reach the publish notification.

**Step 2: after publish** (the durable backstop):
```bash
gh release view vX.Y.Z --json body -q .body > "$SCRATCH/generated.md"
# if scripts/polish-release-notes.sh is used at all, run it BEFORE this step, never after
grep -qF "$(head -1 "$SCRATCH/upgrading.md")" "$SCRATCH/generated.md" \
  || { cat "$SCRATCH/upgrading.md" "$SCRATCH/generated.md" > "$SCRATCH/notes.md"; gh release edit vX.Y.Z --notes-file "$SCRATCH/notes.md"; }
```

**Step 3: verify SC-6.** `gh release view vX.Y.Z --json body -q .body` must contain the Upgrading section **verbatim**.

If the release PR merges after `/aod.deliver`, these steps are the deliver follow-through item. Post the #364 handoff comment listing the example data surfaces that changed (from `oracle-diff.md`).
