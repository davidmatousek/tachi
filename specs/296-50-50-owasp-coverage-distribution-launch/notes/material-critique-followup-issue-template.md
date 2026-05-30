# FR-009 Material-Critique Follow-up — Issue Template (T036, preemptive)

**Status**: PREEMPTIVE. File a GitHub Issue from this template ONLY if the FR-009 trigger fires on an F-1 distribution surface (LinkedIn post, README, Discussion).

**FR-009 trigger** (any one): a named coverage gap, a verifiable counter-example, OR ≥5 confirming independent reactions/replies surfacing the same substantive critique.

---

**Title**: `F-1 distribution: material critique on [surface] — gap analysis`

**Labels**: `signal:material-critique`, `f-296-followup`

**Body**:

## Critique
- **Surface**: [LinkedIn post URL / README / Discussion #179 / other]
- **Raised by**: [handle, or "aggregate of N reactions/replies"]
- **Link**: [permalink to the critique]
- **Claim**: [1–2 sentence summary of the asserted gap or counter-example]

## Verification (against the canonical anchor)
- Checked against `docs/standards/OWASP_COVERAGE.md` + `schemas/taxonomy/owasp.yaml`: [accurate? which framework / item ID?]
- Reproducible? [does the counter-example reproduce under `SOURCE_DATE_EPOCH=1700000000`?]

## Disposition (FR-009 + NFR-003)
- [ ] **Valid** → remediation plan (scope a fix feature or pattern enrichment) + in-public correction (reply in-thread per NFR-003, ~24–72h).
- [ ] **Invalid** → in-public clarification with evidence (reply in-thread; cite the anchor).
- [ ] **Partial** → acknowledge + scope the valid portion.

## Notes
- Response tone: technical, evidence-led, no defensiveness (NFR-003).
- If valid and material, may seed a coverage-gap feature or a BLP-04 follow-on.
