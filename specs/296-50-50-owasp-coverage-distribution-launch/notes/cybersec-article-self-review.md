# Cybersec Article — NFR-008 Self-Review (T014)

**Date**: 2026-05-28 (Day 1 PM, build-resume session)
**Author**: maintainer
**Article draft**: `specs/296-50-50-owasp-coverage-distribution-launch/notes/cybersec-article-draft.md`
**Feature**: F-1 (Issue #296) — 50/50 OWASP Coverage Distribution Launch (BLP-04 Wave 1)

## Purpose

Evidence that the Cybersec article draft satisfies the NFR-008 6-item
self-review checklist. Per plan.md §Wave 2 + tasks.md T014, this checklist
MUST pass before T015 (PR open) fires.

## Checklist Results

### (a) Framework citation accuracy — PASS

- **OWASP URL HTTP-status re-verify** (run at build-resume time, 2026-05-28):
  | Framework | URL | Status |
  |---|---|---|
  | LLM 2025 | <https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/> | 200 OK |
  | Agentic 2026 | <https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/> | 200 OK |
  | ML 2023 | <https://owasp.org/www-project-machine-learning-security-top-10/> | 200 OK |
  | Mobile 2024 | <https://owasp.org/www-project-mobile-top-10/> | 200 OK |
  | Web 2021 | <https://owasp.org/Top10/> | 200 OK |
  | API 2023 | <https://owasp.org/API-Security/> | 200 OK |
- **Per-framework count**: every framework cites 10/10 (LLM01–LLM10, ASI01–ASI10, ML01–ML10, M1–M10, A01–A10, API1–API10). PASS.

### (b) Coverage matrix accuracy — PASS

Article §c matrix table reproduced byte-faithful from `docs/standards/OWASP_COVERAGE.md`. Side-by-side `diff`-equivalent inspection confirms:
- 6 rows present
- Per-bucket counts identical: 10/10 × 6 = 60/60
- Per-framework ADR lineage identical (LLM 2025: ADR-030/031/034/045; Agentic 2026: ADR-032/033 + pre-BLP-01; ML 2023: ADR-035; Mobile 2024: ADR-036; Web 2021 + API 2023: ADR-037)
- Headline framing identical: 5 slots × 10 items = 50/50 (Web + API combined per ADR-037 D-2)
- Only difference: article uses `[LLM 2025](url)` markdown link form; canonical anchor uses bare `https://…` URLs. Both render to the same anchor at consumer time.

### (c) Verification walkthrough reproducibility — PASS

`SOURCE_DATE_EPOCH=1700000000` cited in 5 locations:
- Article §b intro paragraph (env-var explanation)
- 4 example recipes: `agentic-app`, `web-app`, `predictive-ml-app`, `mobile-banking-app`
- §b troubleshooting paragraph (`If the diff isn't empty` — cause #1 is missing env-var)

Each recipe is a complete, copy-pasteable two-command block:
```bash
SOURCE_DATE_EPOCH=1700000000 /tachi.security-report examples/<name>/
diff examples/<name>/<layout-specific-path>.pdf{,.baseline}
```

Both baseline layouts documented (Architect M-1):
- Nested layout (`agentic-app`, `predictive-ml-app`, `mobile-banking-app`): `examples/{name}/sample-report/security-report.pdf.baseline`
- Top-level layout (`web-app`): `examples/{name}/security-report.pdf.baseline`

ADR anchors cited for byte-determinism contract: ADR-021 + ADR-029 + ADR-037 D-11. PASS.

### (d) Link validity — PASS

**Tachi repo URLs** (all well-formed; resolve in production):
- <https://github.com/pratik-saptarshi/tachi-rust>
- <https://github.com/pratik-saptarshi/tachi-rust/blob/main/docs/standards/OWASP_COVERAGE.md>
- <https://github.com/pratik-saptarshi/tachi-rust/blob/main/docs/guides/DEVELOPER_GUIDE_TACHI.md>
- <https://github.com/pratik-saptarshi/tachi-rust/discussions>
- <https://github.com/pratik-saptarshi/tachi-rust/discussions/categories/in-the-wild>
- <https://github.com/pratik-saptarshi/tachi-rust/issues>

**ADR file existence check** (12 references; all PASS):
- ADR-021, ADR-028, ADR-029, ADR-030, ADR-031, ADR-032, ADR-033, ADR-034, ADR-035, ADR-036, ADR-037, ADR-045 — all exist under `docs/architecture/02_ADRs/`.

**Sub-decision anchors** (D-2, D-11): documented within ADR-037 (Web/API combined-slot narrative compression + byte-determinism contract).

### (e) Word count 2400–3600 — PASS

- Body word count (excludes YAML frontmatter + heading lines): **2470 words**
- Total word count (frontmatter included): **2754 words**
- Method: `awk '/^---$/{f=!f; next} f{next} /^#/{next} {print}' draft.md | wc -w`
- Target band: 2400–3600 (~3000 ±20% per PRD FR-3 / plan §Wave 2 word budget)
- Result: 2470 ∈ [2400, 3600]. PASS.

### (f) Asset-tag mention NOT present — PASS

Per Team-Lead L-2 + FR-007 sequencing guard: the F-2 (F-260b @north-echo asset-tag SARIF/affected_assets[]/populator wiring) work has NOT shipped. The article must not promise or describe asset-tag implementation; only the merged community-prototype precedent (F-260, PR #262, v4.31.0) is in scope, and even then only as a community-merge example, not as a wiring claim.

**Grep check** (case-insensitive, multi-pattern):
```bash
grep -inE "asset.tag|asset_tag|assetTag|affected_assets|sensitivity.*tag|tag.*sensitivity|F-2 |F-260b|@north-echo.*asset|north-echo.*wiring" draft.md
```

**Result**: zero matches. PASS.

**Cross-check** (intentional F-260/F-292 contributor references in §f):
- Line ~134: "F-260 (`@north-echo`, PR #262, v4.31.0) and F-292 (`@armorer-labs`, PR #293, v4.36.0) are recent examples of community contributions that closed real gaps in the catalogue"
- This is the community-merge precedent reference required by §f per plan.md §Wave 2 (US-8 / PM L-1 fold). Reference names the contributors and PRs but does NOT describe asset-tag wiring. Allowed.

## Verdict

**6/6 PASS** — article draft satisfies NFR-008 and is ready for T015 (PR open against `davidmatousek/Cybersecurity-Content`).

## What T015 + T016 require (carry-over for maintainer)

T015 + T016 are `[MANUAL-ONLY]` and cannot be completed in the build agent's session:

- **T015**: open a PR against `davidmatousek/Cybersecurity-Content` with the article body from `cybersec-article-draft.md`. Suggested filename per repo convention (PascalCase folders observed: `SecurityManifesto/`, `Speaking/`): `Articles/2026-XX-XX-50-50-OWASP-Coverage-tachi.md` or similar; final filename at maintainer discretion. Title format: `feat: 50/50 OWASP coverage in tachi — what it means and how to verify it`. Record the PR URL in `notes/cybersec-article-pr-url.txt`. Hold ≥24 hours before self-merge.
- **T016**: after ≥24h hold, re-read with fresh eyes, re-run this checklist, self-merge, and update the URL file with the merged-state URL.

**Article location**: `specs/296-50-50-owasp-coverage-distribution-launch/notes/cybersec-article-draft.md` (paste body to new PR; frontmatter format may need adjustment to match Cybersec Content repo's convention if it has one).
