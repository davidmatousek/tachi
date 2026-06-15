# Research Summary: Citation-URL Link-Rot Monitoring (#183)

**Date**: 2026-06-14
**PRD**: `docs/product/02_PRD/183-citation-url-link-rot-monitoring-2026-06-14.md`
**Status feeding**: spec.md generation

This feature is unusually well-grounded — it ships with a full architect technical baseline (`.aod/results/architect-baseline-183.md`). This research confirms that baseline against the live codebase at HEAD and supplements with external best-practice and KB context.

---

## Knowledge Base Findings

- **KB Entry 14 (F-182, BLP-05 Wave 3 sibling)** — `docs/INSTITUTIONAL_KNOWLEDGE.md:539,547`. F-182 (`related`/`superseded` edges) is the *other* Wave 3 item; it explicitly names #183 (citation link-rot) as the remaining Wave 3 piece. Lesson carried forward: Wave 3 is the **crosswalk integrity track**; #183 closes it.
- **ADR-021 (determinism boundary)** — `docs/architecture/02_ADRs/ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md`. The PRD and architect baseline both cite "ADR-021 determinism" as the governing principle: the deterministic test suite must stay offline. `test_citation_shape()` was deliberately written regex-only to honor it. The new feature **must not** breach this boundary.
- **F-250 lock-step rule** (referenced in both existing CI workflows) — any new runtime dependency requires updating the manifest *and* the workflow `pip install` in the same commit. The PRD's stdlib-only choice (NFR-2) sidesteps this entirely.
- No prior link-check / scheduled-job KB entry exists — this is a **greenfield** pattern for the repo (confirmed: no `schedule:`-triggered workflow exists yet).

## Codebase Analysis

- **CI precedent — `.github/workflows/tachi-maestro-coverage.yml`**: single-concern job, `ubuntu-latest`, `actions/checkout@v4` + `actions/setup-python@v5` (Python `3.11`), direct `python3 -m pytest` invocation, `permissions: contents: read`, inline `pip install`. This is the file-for-file model for `tachi-citation-linkrot.yml`. **All existing workflows are `on: pull_request`; none use `schedule` — #183's job is the repo's first scheduled workflow.**
- **Offline guard — `tests/schemas/test_taxonomy_integrity.py:286` `test_citation_shape()`**: the parity target for FR-8.
  - URL discriminator (line 45): `URL_REGEX = re.compile(r"^https?://")`.
  - Helper (lines 52–62): `_is_url_or_existing_file(value)` → URL-shaped **or** resolves to a repo file under `REPO_ROOT`.
  - Field rule: **crosswalk edges → `citation`** field; **catalog records → `url`** field. `REQUIRED_RECORD_KEYS = {"id","full_id","name","url"}`; `REQUIRED_EDGE_KEYS = {"source","target","edge_type","confidence","citation"}`.
  - Loads all 9 YAMLs from `TAXONOMY_DIR = REPO_ROOT/"schemas"/"taxonomy"` via `yaml.safe_load`.
- **Loopback carve-out — `tests/scripts/conftest.py` `hanging_upstream()` (~line 95–172)**: binds `127.0.0.1:0` (ephemeral loopback), accepts-but-never-responds for timeout tests. **Hermetic / in-process — zero outbound fetch.** Confirms NFR-1's explicit carve-out: the "no outbound/external fetch" rule targets the *public internet*, not loopback scaffolding.
- **Scripts convention — `scripts/*.py`**: `#!/usr/bin/env python3`, module docstring with exit-code legend, `argparse`, stdlib-first, `sys.path.insert(...)` + `from tachi_parsers import ...` for shared helpers. **No reusable taxonomy-URL extractor exists** — `tachi_parsers._load_catalog_ids()` returns only ID frozensets and discards `url:`/`citation:`. A new standalone ~150–250 LOC script is the correct, lowest-coupling call (architect baseline §2 confirmed).
- **Dependency manifest — `requirements-dev.txt`**: `pytest>=8.0`, `pytest-cov>=4.1`, `pyyaml>=6.0`. `requests` is **not** present. Stdlib `urllib` path keeps it that way (NFR-2). (The Explore agent flagged "must add requests" — that is contrary to the PRD's deliberate stdlib choice and is **not** a requirement.)
- **README note — `schemas/taxonomy/README.md:224`**: current text = "Link-rot monitoring for external URLs is **out of F-A1 scope** (follow-on Issue filed on F-A1 PR merge). The integrity test (`test_citation_shape()` per FR-031) verifies URL syntax via regex only — no HTTP fetch (ADR-021 determinism)." — to be updated to reference the live monitor.

## Architecture Constraints (from architect baseline, verified at HEAD)

- **Measured surface**: `crosswalk.yaml` 645 `citation:` total → **556 URL-shaped** + 89 internal file-path (out of scope). **902 distinct URLs** across **7 hosts**. MITRE owns **835/902 (93%)** across `attack.mitre.org` (702), `cwe.mitre.org` (94), `atlas.mitre.org` (39). Then `owasp.org` (45), `genai.owasp.org` (16), `doi.org` (4), `raw.githubusercontent.com` (2). Counts drift per catalog edit → **glob at runtime, hardcode nothing**.
- **Five concerns (all resolved in the PRD, none blockers)**: A determinism invariant (NFR-1); B 403/401/429 = needs-review (FR-4); C per-host concurrency mandatory (FR-5); D single self-closing tracking issue (FR-7); E cache-miss = check-all (FR-6).
- **Resolved baseline decisions**: cron `17 9 * * 1`; stdlib `urllib` + `concurrent.futures`; cache TTL ~21 days; per-host cap 2–3 / global 10; HEAD→ranged-GET fallback; HTTP via `gh` CLI for issues; least-privilege `contents: read` + `issues: write`.

## Industry Research

- Link-rot / URL-health monitoring is conventionally a **scheduled** activity (monthly/weekly audits), not an inline gate — matches the PRD's scheduled-only design.
- **HEAD vs GET**: external guidance is thin, but the well-known failure mode (CDNs/WAFs returning 405 on HEAD while 200 on GET) is exactly what the architect baseline's HEAD→ranged-GET fallback (FR-4) mitigates. No change to the PRD design warranted.
- Cron-job monitoring tooling (Healthchecks.io et al.) is overkill here — GitHub Actions `schedule` + a self-closing tracking issue is the right-sized, zero-SaaS approach for a security-posture repo (matches NFR-7 supply-chain minimalism).
- Sources: [Link rot — Wikipedia](https://en.wikipedia.org/wiki/Link_rot); [API Health Check best practices — API7.ai](https://api7.ai/blog/tips-for-health-check-best-practices); [Healthchecks.io](https://healthchecks.io/).

## Recommendations for Spec

- **Translate the 4 PRD user stories** (weekly confirmed-rot signal; trustworthy/no-false-positives; never-blocks-merge; one self-healing issue) into prioritized, independently-testable spec user stories. US-3 (determinism / never-on-PR) is the load-bearing P1 invariant.
- **Carry NFR-1 verbatim in spirit** as the highest constraint: no outbound/external fetch in `tests/` or any PR-triggered job; checker not importable from the pytest collection path; loopback carve-out noted.
- **Make FR-8 parity guard the testability anchor**: assert set-parity (both directions) against `test_citation_shape()`'s extraction *and* encode the field rule (crosswalk→`citation`, catalogs→`url`). Fetch-free, PR-gate-eligible.
- **Pin the validation success criterion to a deterministic sentinel** (Team-Lead TL-2), never a live external 404 — the spec's SC for "exactly one issue → self-close" must be reproducible.
- Keep Success Criteria **technology-agnostic and measurable**; push tool specifics (stdlib, `gh`, cron slot) into Assumptions/Constraints, mirroring the PRD.
- No `[NEEDS CLARIFICATION]` markers needed — the architect baseline resolved every open decision.
