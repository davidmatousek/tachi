# #364 Handoff Draft (T037 / R-T2)

Posted to **#364** at `/aod.deliver`, after PR #375 (`fix(373): adopter install + output
fidelity fixes`) merges. #373 ships as a patch release ahead of #364's example/baseline
re-key (spec.md §9, PM ruling M5), so #364 needs to absorb the data changes below rather
than the pre-#373 state. Source: `specs/373-adopter-install-output-fidelity/oracle-diff.md`
(100% attributed; independently re-derived at the P1 architect checkpoint,
`test-results/p1-architect-review.md` §1.4). Generic per NFR-6 — structural/count
description only, no finding content and no specific finding IDs.

Paste verbatim below this line as the #364 comment.

---

#373 (merged as `fix(373)`) changed several tracked example data surfaces while fixing
output-fidelity defects in the report and infographic pipeline. Listing them here so this
issue's example/baseline re-key starts from the right state.

**Recommendation fallback and placeholder text.** Every finding now always carries
recommendation text. Where the controls report gives no join for a finding, two sub-cases
apply:
- **Fallback** (the threat model's own mitigation text, marked `Threat-model mitigation:`):
  `maestro-reference`, `agentic-app/sample-report`, `mobile-banking-app/sample-report`.
- **Placeholder** (`No recommendation available`, no text from either source):
  `predictive-ml-app/sample-report`.

This also changes `maestro-reference`'s rendered PDF: it grows from **86 to 88 pages**,
from the added fallback text appearing in both the finding cards and the remediation
roadmap. The `.pdf.baseline` fixture was deliberately **not** regenerated for this
(NFR-8) — any PDF baseline work here should expect the new page count.

**Delta counts and badges — `agentic-app` only.**
- `agentic-app/sample-report` (tier 1): delta counts move from all-zero to **4 NEW / 0
  UPDATED / 82 UNCHANGED** (0 RESOLVED, unchanged), plus one ID-set warning (a finding ID
  appears in the threat model's status section but not in the controls report).
- `agentic-app` (tier 3): delta counts move to **12 NEW / 69 UNCHANGED**.
- In both, the infographic's `top_findings[].delta_status` values are normalized to their
  bare form (tier 3) or newly populated (tier 1), and the report's badges reflect the same
  normalized status.

**Posture and `allow_list` fields — every example.** Every infographic JSON (all 12
examples, every applicable template) and every `report-data.typ` now carries a
`risk_posture_level`/`risk_posture_label` pair and an `allow_list` subtree. These are new
fields, not corrections to existing ones — nothing prior is overwritten.

**Funnel fields — every example's risk-funnel data.** The funnel tiers and reduction
percentages are now populated (previously absent or placeholder-backed). The 5 tier-1
examples (`agentic-app/sample-report`, `consumer-agent-app/sample-report`,
`maestro-reference`, `mobile-banking-app/sample-report`, `predictive-ml-app/sample-report`)
get real row-derived counts; the 7 tier-3/threats-only examples get empty-tier objects (no
controls data to derive from, by design). The baseball card also gains matching
inherent/residual/reduction score fields for the same 5 tier-1 examples — 3 of the 5 show a
nonzero reduction figure; the other 2 stay at zero, since neither has a credited control.

**What did not change.** The MAESTRO-heading parser fix moves **zero** tracked examples —
no shipped example uses the heading form it targets, so it was verified on synthetic
fixtures only. (This corrects an earlier plan-time expectation that this issue would need
to absorb that change too; it does not.) No tracked PNG changed, and no `.pdf.baseline`
other than `maestro-reference`'s page-count note above changed.

Treat #373's merge commit as the new pre-#364 baseline for every surface above. Everything
under "what did not change" needs no extra handling here.
