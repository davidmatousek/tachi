# Wave 0 — Pre-change Baseline (T001 + T002)

**Captured**: build start (F-311, branch `311-maestro-matrix-model-b-clean-vs-na`)

## T001 — Toolchain

| Tool | Status |
|------|--------|
| Python | 3.9.6 (local; CI pins 3.11) — meets 3.9+ |
| pytest | 8.4.2 |
| pytest-timeout | 2.4.0 (present) |
| Typst | 0.14.2 (present — Phase D only) |
| mmdc | present (Phase D only) |
| `git tag v4.40.0` | **MISSING locally** — see gap below |

### v4.40.0 tag gap (Team-Lead R7 / Carry-Forward #7)
`git tag -l v4.40.0` returns empty locally. **Deliver-time action (T023)**: run `git fetch --tags` and confirm `v4.40.0` present before `/aod.deliver` so release-please bases the next release correctly. Non-blocking for build (no task before T023 needs the tag).

## T002 — Pre-change baseline (regression reference)

Both anchor suites GREEN at build start:

- `tests/scripts/test_maestro_coverage_invariant.py` → **9 passed, 2 skipped** (skips: `consumer-agent-app/sample-report`, `predictive-ml-app/sample-report` — intermediate-format, no MAESTRO table; documented).
- `tests/scripts/test_backward_compatibility.py` → **13 passed, 1 skipped** (skip: `mermaid-agentic-app` multi-agent gate predicate — documented T033 known-limitation). 6 byte-gated PDFs (`web-app`, `microservices`, `ascii-web-api`, `mermaid-agentic-app`, `free-text-microservice`, `maestro-reference`) byte-identical.

**G0 verdict**: repo at a clean start. Baseline is the reference for the T020 post-regen byte-gate (must remain green; `BASELINE_EXAMPLES` set unchanged).
