# Quickstart: F-362 Verification Battery

Runbook for the gates in plan.md §Verification & Gates. Run from repo root. **The gated harness clones committed HEAD — commit before running suites** (F-248/F-256 lesson).

## 0. Pre-state capture (W0, before any edit)

```bash
python -m pytest tests/scripts/test_backward_compatibility.py -q 2>&1 | tail -3
python -m pytest tests/schemas/test_taxonomy_integrity.py -q 2>&1 | tail -3
# Record LITERAL totals (incl. the ~19 known out-of-gate failures elsewhere) in:
#   specs/362-remap-owasp-llm-top10-2026/test-results-prestate.md
```

## 1. Taxonomy integrity (after W1, again at W5)

```bash
python -m pytest tests/schemas/test_taxonomy_integrity.py -q
# Expect: all green · 645 edges · 74 LLM-keyed · 0 duplicate dedupe keys · primary floor ≥500
```

## 2. Byte-identity / no-churn proof (pre-merge, committed HEAD)

```bash
git status --short   # must be clean
python -m pytest tests/scripts/test_backward_compatibility.py -q
# Expect green with ZERO baseline bytes changed. The #329 drift guard's green is
# UNINFORMATIVE for this change class — do not cite it as evidence.
```

## 3. Sweep gate (W5) — tooling must see gitignored-but-tracked files

```bash
# NOTE (PM plan-review CRITICAL, fixed 2026-08-06): git grep's -E has no \b and -P/-E do
# not combine — the forms below are the EMPIRICALLY VERIFIED ones. -P (PCRE2) is confirmed
# available in this environment; for the bare-census lookahead -P is REQUIRED (no ERE
# equivalent). ERE fallback for the suffixed form only: '(^|[^[:alnum:]_])LLM(0[1-9]|10):2025'

# Suffixed 2025 forms outside the FR-008 exclusion set (all hits must be ledger-dispositioned):
git grep -nP '\bLLM(0[1-9]|10):2025' -- \
  ':!specs' ':!docs/product/02_PRD' ':!docs/guides/CONSUMER_GUIDE_TACHI.md' \
  ':!docs/architecture/02_ADRs' ':!docs/INSTITUTIONAL_KNOWLEDGE.md' \
  ':!tests/fixtures/init-baseline-tree' ':!examples' ':!CHANGELOG.md'
# Prose forms (no \b needed — plain ERE is safe here):
git grep -niE 'LLM Top 10 (for LLM Applications )?2025|llm top 10.*2025' -- <same exclusions>
# Bare census reconciliation vs bare-code-ledger.md — count OCCURRENCES, not lines
# (git grep -c counts matching LINES; the ledger accounts occurrences):
git grep -oP '\bLLM(0[1-9]|10)\b(?!:)' -- <in-scope paths> | wc -l                      # total
git grep -oP '\bLLM(0[1-9]|10)\b(?!:)' -- <in-scope paths> | cut -d: -f1 | sort | uniq -c  # per-file
# Sanity: each command MUST produce hits on the pre-remap tree (a zero before the remap
# means the command is broken, not that the repo is clean).
```

## 4. Gated pytest subset (pre-merge, committed HEAD)

```bash
# The real gate is the 15-module subset invoked by .github/workflows/tachi-pytest.yml —
# run its exact invocation (read it from the workflow file; paths: filter and invocation
# move in lockstep if any test file was added/renamed).
```

## 5. CA-PDF baselines (F-362b ONLY — not this feature)

```bash
# Runs only in the loop that re-keys example findings' source_attribution (plan FR-007b binding):
scripts/regenerate-ca-baselines.sh   # local-only; requires typst + PyYAML; SOURCE_DATE_EPOCH pinned;
                                     # re-emits examples/ca-baseline-fingerprints.json as final step
```

## 6. Deliver stage

```bash
gh workflow run tachi-citation-linkrot.yml -f no_cache=true   # live URL validation of re-anchored set
gh pr list --state open --search "release-please" --limit 3   # verify release fires post-merge
# KB 18 hygiene: branch current; main == origin/main (full-tree diff) before merge/doc-push.
```
