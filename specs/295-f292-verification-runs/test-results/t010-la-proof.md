# T010 — L-a Byte-Identity Proof (FR-014 URI Enabler)

**Feature**: #295 F-292 Post-Merge Verification Runs | **Task**: T010 (US2) | **Decision**: plan.md D-C, Architect L-a semantics
**Date**: 2026-07-03 | **Pre-change HEAD**: `bfd90a3b2bcbe0993db9d817e5db481f78a3e40f`

## Purpose

FR-014 changes `scripts/generate-threats-sarif.py::build_result` so the SARIF
`artifactLocation.uri` is derived from the generator's input path instead of a
hardcoded constant. Architect L-a semantics require proof that this is a
**behavior-preserving** change for the existing `examples/agentic-app/` fixture:
script-output-BEFORE the change must be byte-identical to script-output-AFTER
the change, on the same input, because the input path is the same path the
constant already hardcoded.

## Change Summary

- Added `REPO_ROOT = Path(__file__).resolve().parent.parent` (module level, mirrors
  the existing convention in `scripts/generate-risk-scores-sarif.py` and
  `scripts/check-catalog-drift.py`).
- Added `artifact_uri_for(input_path: Path) -> str`: resolves the input path and
  expresses it relative to `REPO_ROOT` in POSIX form (forward slashes); falls back
  to the resolved absolute POSIX path if the input lies outside the repository.
- `build_result()` gained a `source_uri: str = "examples/agentic-app/sample-report/threats.md"`
  parameter (default preserves today's constant for any caller that does not pass
  one); the hardcoded `"uri": "examples/agentic-app/sample-report/threats.md"` literal
  at the `locations[0].physicalLocation.artifactLocation.uri` field became `"uri": source_uri`.
- `build_sarif()` gained the same `source_uri` parameter (same default), threaded
  through to each `build_result()` call.
- `main()` now computes `source_uri = artifact_uri_for(args.input)` and passes it to
  `build_sarif(...)`.
- No other generator logic changed (FR-020 scope fence).

## Commands (exact, verbatim)

Run 1 — BEFORE the change (original hardcoded-constant behavior, HEAD `bfd90a3`):

```
$ python3 scripts/generate-threats-sarif.py examples/agentic-app/sample-report/threats.md /tmp/agentic-before.sarif
OK: wrote 85 findings to /tmp/agentic-before.sarif
Prefix counts: [('AG', 8), ('D', 11), ('E', 7), ('I', 9), ('LLM', 16), ('MI', 3), ('OI', 4), ('R', 9), ('S', 9), ('T', 9)]
AG-8 present: True ([UNCHANGED])
```

...apply the URI derivation change (this task)...

Run 2 — AFTER the change:

```
$ python3 scripts/generate-threats-sarif.py examples/agentic-app/sample-report/threats.md /tmp/agentic-after.sarif
OK: wrote 85 findings to /tmp/agentic-after.sarif
Prefix counts: [('AG', 8), ('D', 11), ('E', 7), ('I', 9), ('LLM', 16), ('MI', 3), ('OI', 4), ('R', 9), ('S', 9), ('T', 9)]
AG-8 present: True ([UNCHANGED])
```

Comparison:

```
$ cmp /tmp/agentic-before.sarif /tmp/agentic-after.sarif
(no output — identical)
```

SHA-256 (both files):

```
$ shasum -a 256 /tmp/agentic-before.sarif /tmp/agentic-after.sarif
988c0ed5d7404ba8cde73be5a37f646ee139f61ae2a36524c1526877ccbd78dd  /tmp/agentic-before.sarif
988c0ed5d7404ba8cde73be5a37f646ee139f61ae2a36524c1526877ccbd78dd  /tmp/agentic-after.sarif
```

## Verdict

**PASS** — `cmp` reports the two script outputs identical; SHA-256 digests match
exactly (`988c0ed5d7404ba8cde73be5a37f646ee139f61ae2a36524c1526877ccbd78dd` for
both). The FR-014 URI derivation is confirmed behavior-preserving for the
`examples/agentic-app/` fixture (Architect L-a semantics satisfied).

## Supplementary check — second FR-014 example (`examples/multi-tenant-rag-app/`)

The `examples/multi-tenant-rag-app/threats.md` fixture does not exist yet at this
point in the task sequence (it lands in T012–T014). The URI-derivation function
was exercised directly (not via full script invocation, since the input file is
absent) to confirm it satisfies the second FR-014 example ahead of T014's actual
regen check:

```
>>> artifact_uri_for(Path("examples/multi-tenant-rag-app/threats.md"))
'examples/multi-tenant-rag-app/threats.md'
```

Matches the required mapping exactly (input == output, repo-relative POSIX path,
no `REPO_ROOT`-relative divergence since the path is already given relative to the
repository root).

## Supplementary check — out-of-repository input (fallback branch)

A path outside the repository (simulating a pytest `tmp_path` fixture, which lives
under the OS temp directory) exercises the fallback branch of `artifact_uri_for`:

```
>>> artifact_uri_for(Path("/private/var/.../tmp25crtiot/threats.md"))
'/private/var/.../tmp25crtiot/threats.md'   # == input.resolve().as_posix()
```

`relative_to(REPO_ROOT)` raises `ValueError` for this input (not under the repo
root), so the function falls back to the resolved absolute POSIX path — a
deterministic, well-defined result. This is the case the T011 covering assertion
exercises (tmp_path fixture file, non-agentic-app path).
