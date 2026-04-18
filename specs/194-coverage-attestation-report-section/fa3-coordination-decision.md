# T039 — F-A3 Merge-Order Coordination Decision

**Wave**: 2.3 (Day 2 EOD checkpoint)
**Owner**: team-lead
**Date**: 2026-04-18

## GitHub Issue Search

Queries executed via `gh issue list`:

1. `--search "F-A3 in:title"` → 0 results
2. `--search "populator source_attribution in:title,body"` → 0 results
3. `--search "threat agent source_attribution"` → 0 net-new results
   (only Issues #194 [this feature, OPEN] and #189 [F-A2, CLOSED] surface, neither is F-A3)

## Decision

**Advance F-B independently. No F-A3 serialization hold.**

Rationale:

- No F-A3 Issue is currently filed. F-A3 (populator wiring — threat agents emitting `source_attribution` values during detection across the 22-file scope deliberately preserved by F-A2) is enumerated in BLP-01's 9-remaining feature list but has not entered the backlog as a tracked Issue.
- F-B's contract surface (Typst declarations + aggregator) is fully decoupled from F-A3's runtime emission surface (per-finding population in detection agents). They share only the `schemas/finding.yaml` v1.5 `source_attribution` field shape — already frozen and shipped at F-A2 merge (2026-04-17).
- All 6 baseline examples currently have `source_attribution` absent on every finding (since F-A3 hasn't shipped). This means F-B's `has-source-attribution: false` gate evaluates false on all baselines, the section is omitted, and PDFs are byte-identical (SC-002 holds).
- When F-A3 lands in a future PR, baselines will need to be re-baselined under the new populated state. That re-baseline work is owned by F-A3, not F-B. F-A3 will see a single coordinated re-generation across all 6 examples. PRD A7 fallback was pre-approved for ~0.5-1 day re-baseline if needed.

## Consequence for PR Description (T046)

T046 PR-prep should cite this decision under the F-A3 coordination outcome line:

> "F-A3 coordination outcome: No F-A3 Issue filed at Day 2 EOD checkpoint. F-B advances independently. Baseline re-generation if/when F-A3 ships will be owned by the F-A3 PR (PRD A7 fallback)."
