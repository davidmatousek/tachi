# Research Summary: Citation-URL Remediation (F-333, BLP-06 Wave 1)

**Created**: 2026-06-29
**Feature**: F-333 — close the 41 dead citation URLs the #183 monitor surfaced (#332 tracker)
**Inputs**: PRD `docs/product/02_PRD/333-citation-url-remediation-2026-06-29.md` (Approved); feasibility-check.md (Team-Lead).

This research grounds the spec in verified codebase reality. Every load-bearing claim below was confirmed in-tree (file:line) or against authoritative external sources.

---

## Knowledge Base Findings

- **KB Entry 17 (F-183 — the predecessor monitor)**: The link-rot monitor (`scripts/check-citation-urls.py` + `tachi-citation-linkrot.yml`) classifies HEALTHY / LINK_ROT (404·410) / NEEDS_REVIEW (401·403·429) / TRANSIENT (5xx·timeout). Its first live sweep (2026-06-15) found **41 real dead URLs** — "verified real, not bot-blocks: checker UA and browser UA both 404, redirects followed": ~38 MITRE ATLAS technique pages (#186), the NIST AI RMF DOI target (#184, ~73 records), 4 OWASP GenAI LLM URLs. Fixing was **out of scope** for #183 → filed as **#333** (this feature); live state held by self-healing tracker **#332**. Corollary captured in the entry: *"citation URLs added in rapid expansion were never validated against live endpoints — 41 were dead on arrival; authoring-time URL reachability checks would shift that left."*
- **KB Entry 15/16 (F-185 — the `ORDERED_FRAMEWORKS` lesson)**: Catalog **record** growth for frameworks in `ORDERED_FRAMEWORKS` (`scripts/extract-report-data.py:1077`) pulls in a CA-page PDF baseline-regen lane + coverage-percentage test pins. `mitre-atlas` and `nist-ai-rmf` **are** members. **But** the predicate is *record* add/remove, and the render path reads record **IDs/counts**, never `url:`/`citation:` strings — so a pure **string** edit to a citation does **not** trigger the regen lane. F-333's FR-7 exists to *verify* this (cheaply), not assume it.
- **KB Entry 13 (F-186)**: Source of the ATLAS citations; 36 ATLAS technique records dispositioned against `mitre-atlas/atlas-data` (ATLAS-2026.05) — establishes `atlas-data` as the authoritative existence oracle for technique IDs, the exact source FR-1 must re-query.

## Codebase Analysis (all verified in-tree)

### `scripts/check-citation-urls.py` — the classifier (FR-2 re-classify surface)
- **`_HARD_ROT_STATUSES = frozenset({400, 404, 410, 451})`** (`:288`) and **`_NEEDS_REVIEW_STATUSES = frozenset({401, 403, 429})`** (`:290`) — **flat global frozensets, NOT host-scoped**. A **404 is hard-rot**, so an anti-bot 404 (as opposed to a 403) sails past the needs-review guard and is reported as confirmed rot. This is the exact mechanism behind the ATLAS false positive.
- Verdict mapping lives in **`_verdict_for_status(url, status, final_url, detail)` (`:447`)** — crucially, **the function already receives `url`**, so a bounded host-keyed override is feasible *inside* it without a `classify_one()` control-flow refactor. This is the "stay" side of the Team-Lead's pre-authorized split valve.
- TTL ledger: **`should_skip(url, ttl_days, *, no_cache=False)` (`:568`)**, default **`--ttl-days 21`** (`:925`). **`--no-cache` (`:923`) forces `return False`** (full sweep). **`--inject-sentinel-rot` (`:937`)** appends a pre-classified synthetic finding with **no network** — the offline precedent for testing the verdict path.

### Taxonomy catalogs (the data edit surfaces)
- **`schemas/taxonomy/mitre-atlas.yaml`** — R7 TRIPWIRE note at **`:18–26`**: *"atlas.mitre.org individual technique pages return HTTP 404 via WebFetch — confirmed as client-side anti-bot gating … This is a WebFetch-client limitation, NOT a URL stability issue. URL pattern verified stable via the authoritative MITRE-owned atlas-data repo."* **36 distinct `AML.Txxxx` IDs**, **37 `atlas.mitre.org/techniques/` url: refs**.
- **`schemas/taxonomy/nist-ai-rmf.yaml`** — `url: https://doi.org/10.6028/NIST.AI.100-1` appears in **73 records** (`grep -c` = 73; first at `:49`). All NIST AI RMF 1.0 subcategories share the one DOI → a single corrected URL cascades to all 73.
- **`schemas/taxonomy/crosswalk.yaml`** — **16 distinct `genai.owasp.org` URLs**. `llm01-prompt-injection/` is **present and live** (`:39`, 7 citations) — the regression guard. The dead-candidate set is messier than "4": non-year `llm02/03/04/05`, **9 year-suffixed `llm0X2025` variants** (`llm022025`…`llm102025`), and **2 Agentic resource pages** (`agentic-ai-top-10-vulnerabilities/`, `owasp-top-10-for-agentic-applications-for-2026/`). FR-1 must adjudicate which are actually dead.

### Render / CI surfaces
- **`scripts/extract-report-data.py:1077`** — `ORDERED_FRAMEWORKS = ("owasp", "mitre-attack", "mitre-atlas", "nist-ai-rmf", "cwe")`. Render path (`:1140–1193`) reads `record.get("id")` and counts, **never citation strings** → string edits are not byte-baseline-exposed (FR-7 expected: no exposure).
- **`.github/workflows/tachi-citation-linkrot.yml`** — triggers **`schedule` (Mon 09:17 UTC) + `workflow_dispatch` only** (`:40–48`), `runs-on: ubuntu-latest` (`:59`). The **only** dispatch input is `inject_sentinel_rot` (boolean) — **there is no `--no-cache` dispatch input today**, so FR-6's full-sweep acceptance must add one or clear the ledger.
- **`tests/schemas/test_taxonomy_integrity.py:286` — `test_citation_shape()`**: regex/file-only (`URL_REGEX = ^https?://`, `:45`), **no HTTP**. **Notable correction to the PRD's INFO note**: this test is **NOT wired into any GitHub Actions workflow** (`tachi-pytest.yml` runs only the F-248/F-256 hardening suites; `tachi-citation-linkrot.yml` is the monitor, not a gate). It runs locally / pre-commit / manual only. → *Where the new synthetic-404 unit test runs (local-only vs. added to a CI job) is a plan/tasks decision, not a spec scope question; the determinism boundary permits it as a PR gate because it is network-free.*

## Architecture Constraints

- **ADR-021 (Accepted)** — `SOURCE_DATE_EPOCH=1700000000` byte-determinism for PDF baselines; **production unchanged, test-path only**. F-333 inherits this as the determinism boundary: no network may enter `pytest`/`pull_request`/`push` jobs. The re-classify verdict logic must be unit-tested over a **synthetic 404**, never a live fetch.
- **Source-of-truth positioning** (`project_tachi_source_of_truth`): tachi is the upstream machine-readable contract downstream AI-security tools consume — a 404 citation erodes the evidentiary value of every crosswalk edge that cites it. This is *why* the feature is P0.
- **`ORDERED_FRAMEWORKS` consequence-scope (#185 lesson)**: verify rendering exposure before assuming — FR-7.

## Industry Research (link-rot remediation best practices)

- **404 ≠ always-dead**: 404/410 are *usually* genuine (95%+), **but some anti-bot systems return 404** — so a headless 404 on a page that renders in a browser must be adjudicated, not auto-trusted. The correct method is **dual-channel**: machine UA + cross-check the **authoritative source repo** (here, MITRE's `atlas-data`). This is precisely FR-1.
- **Re-point vs. re-classify**: best practice (W3C DCAT, scholarly DOI/persistent-identifier guidance) strongly favors **preserving the human-canonical URL and re-classifying** the checker over re-pointing to a machine-convenient mirror. Re-pointing to an un-anchored raw blob is a "wrong-but-2xx" outcome that silently misleads (an analyst clicking a technique ID lands in a 1.5MB dump with no fragment) — validates the PRD naming the flat-`atlas-data`-blob re-point an **anti-pattern**.
- **Verify landing accuracy**: after following redirects, confirm the final page actually contains the **cited content**, not just any 2xx — validates FR-6's **landing-content spot-check** (a green #332 is necessary but not sufficient).
- **Citation integrity cadence**: persistent identifiers (DOI) + scheduled monitoring (already shipped in #183) + content-drift awareness are the established pattern; F-333 is the remediation half of that loop.
- Sources: arXiv cs/0511077 (link-rot), arXiv 1602.09102 (persistent URIs), PLOS ONE / PMC5135130 (content drift, "3 of 4 URIs lead to changed content"), W3C DCAT v2, RFC 9264 (linksets), DataCite link-checker, reproducible-builds.org (SOURCE_DATE_EPOCH).

## Recommendations for Spec

1. **Four user stories** map cleanly to the PRD: ATLAS adjudication+resolution (P1, the headline fork), NIST DOI cascade (P1), OWASP dead-set re-point (P2), and the #332 self-close end-to-end gate (P1, the real DoD).
2. **Frame ATLAS as research-first with a non-co-equal fork**: re-classify (preferred, host-scoped) vs. flat-blob re-point (anti-pattern) vs. same-host re-point (non-starter, fails the runner-egress test) vs. per-ID real rot. The acceptance is *runner-egress 2xx*, not local-client 2xx.
3. **Make the acceptance gate the monitor**, not local edits: `--no-cache` full sweep self-closing #332 + a landing-content spot-check. Mark these ACs `[MANUAL-ONLY]` (live network + side-effecting `gh` lifecycle, gated out of CI by the determinism boundary — deliver-adjacent).
4. **Preserve determinism**: keep `test_citation_shape()` green; any classifier change is synthetic-404 unit-tested, stays in the scheduled-only surface, host-scoped + reversible (NFR-5). Flag that the new test's CI placement is a plan decision (the offline shape test is not currently in any CI gate).
5. **FR-7 is a verify-not-assume step**: grep the baselined PDF/coverage artifacts for the corrected citation strings; expected zero hits (render path reads IDs/counts).
6. **#325 is explicitly OUT** (deferred standalone — cites a local file, not the dead DOI).
7. **Zero new runtime dependency**; the true re-point edit surface is ~133 occurrences / 36 distinct (only on the unlikely re-point path); re-classify path = zero data edits.
