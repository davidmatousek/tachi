# Quickstart: NIST AI RMF Integration Evaluation ADR (Feature 144)

**For**: Implementer (web-researcher Wave 1, architect Wave 2)
**Estimated effort**: ~1 working day (Wave 1 ≤3h + Wave 2 4-6h) + half-day PR cycle

## Prerequisites

- Branch checked out: `144-nist-ai-rmf-evaluation-adr` (already created)
- Spec read: [spec.md](spec.md) (PM-approved 2026-04-15)
- Plan read: [plan.md](plan.md) (PM + Architect dual sign-off)
- PRD context: [docs/product/02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md](../../docs/product/02_PRD/144-nist-ai-rmf-evaluation-adr-2026-04-15.md)

## Wave 1: Research (web-researcher, 3-hour timebox)

1. Open NIST canonical landing page: https://www.nist.gov/itl/ai-risk-management-framework
2. Read AI RMF 1.0 (NIST AI 100-1): https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf
3. Read NIST AI 600-1 Generative AI Profile: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf (DOI: https://doi.org/10.6028/NIST.AI.600-1)
4. Capture in `research.md` under new heading `## Wave 1 — NIST AI RMF Spec Notes`:
   - Confirmed canonical URLs + version numbers + publication dates
   - 4 Functions (Govern, Map, Measure, Manage) + Categories + representative Subcategory sample (5-10 per Function)
   - Complete list of NIST AI 600-1 §2 GAI risk categories (validate exactly 12 vs PRD's 12-13 estimate)
   - Notes on revision status (any newer NIST AI RMF revision since this PRD filing? See spec Edge Case 2 for handling)
5. **If 3-hour budget exceeded**: pause and choose ONE of:
   - (a) Descope spec FR-002 Surface B sample from "5-10 representative subcategories" to "3 subcategories"
   - (b) Defer FR-007 tachi-shared artifact creation to follow-on Issue (ship only ADR-025 + SKILL.md update)
   - (c) Escalate to PM with timebox-overrun flag

## Wave 2: ADR Authorship (architect, sequential)

Sequence is critical — SKILL.md and tachi-shared artifact reference the **final** ADR Decision text, not draft text.

### Step 2.1 — Draft ADR-025 skeleton

Create `docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md` with:
- Header block: `**Status**: Accepted` | `**Date**: <merge-date>` | `**Deciders**: Architect, Product Manager, Team-Lead` | `**Feature**: 144 (MAESTRO Companion: NIST AI RMF)` | `**Related ADRs**: [ADR-024](ADR-024-owasp-aivss-evaluation.md) (companion AIVSS), [ADR-020](ADR-020-maestro-layer-classification.md) (MAESTRO classification), [ADR-019](ADR-019-shared-definitions-and-model-field-governance.md) (shared definitions), [ADR-018](ADR-018-baseline-aware-pipeline-correlation.md) (baseline lineage), [ADR-021](ADR-021-source-date-epoch-for-deterministic-pdf-comparison.md) (SOURCE_DATE_EPOCH determinism), [ADR-023](ADR-023-threat-agent-skill-references-pattern.md) (skill-references pattern)`
- All section headings (Context, Decision, Rationale, Alternatives Considered, Consequences, When to Re-Evaluate, References)

### Step 2.2 — Fill three Surface tables

Each Surface gets explicit anchor: `<a id="surface-a"></a>` / `<a id="surface-b"></a>` / `<a id="surface-c"></a>` (SC-003 verifier requires exactly 3 matches).

- Surface A: NIST AI RMF Functions (4 rows) × tachi pipeline phases (6 columns: Phase 1 Scope, Phase 2 Threat Detection, Phase 3 Compensating Controls, Phase 3.5 Cross-Layer Chains, Phase 4 Assessment, Phase 5 Reporting)
- Surface B: 5-10 representative NIST AI RMF Subcategories × 8 tachi compensating-control categories (authentication, input-validation, rate-limiting, encryption, logging-audit, csrf-protection, csp-security-headers, access-control)
- Surface C: 12 NIST AI 600-1 GAI risks × 11 tachi STRIDE+AI categories (S, T, R, I, D, E + Prompt Injection, Data Poisoning, Model Theft, Agent Autonomy, Tool Abuse)

Every row uses one of: **Overlap** | **Gap** | **Conflict** | **No equivalent** (SC-004; no TBD/unclear/empty allowed). If Surface C is structurally intractable, abbreviate to summary paragraph + 3-4 exemplar rows per Edge Case 3 (architect scope-reduction authority).

### Step 2.3 — Draft Decision section

First paragraph contains canonical decision-noun: choose ONE of `documentation-only mapping` / `shallow wired integration` / `deep wired integration` / `hybrid B+C`. This phrase MUST be byte-identical (case-insensitive) to the SKILL.md NIST AI RMF Relationship section noun (SC-007 verifier).

### Step 2.4 — Fill Rationale, Alternatives, Consequences, Re-Evaluation Triggers, References

- Rationale: 5-criteria justification (maturity, adoption, compatibility, effort, compliance value); explicit comparison to ADR-024 reasoning; sector mentions (SOC 2, FedRAMP, HIPAA, FFIEC, EU AI Act)
- Alternatives Considered: 3 options (A docs-only / B shallow / C deep), each with Pros / Cons / Effort (S/M/L + day estimate) / Compliance Value / Determinism Impact / Why-Chosen|Not
- Consequences: Positive / Negative / Mitigation / Follow-on (link to follow-on Issue if Option B/C; name artifact location + maintenance commitment if Option A)
- When to Re-Evaluate: concrete trigger
- References: internal (PRDs, ADRs, files) + external (NIST canonical URLs)

### Step 2.5 — Create `nist-ai-rmf-mapping.md`

Path: `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md`

- **If Option A**: complete mapping table (8 control categories → NIST Subcategories) + Surface C crosswalk + back-link to ADR-025
- **If Option B/C**: one-paragraph stub naming wired-integration site + forward link to follow-on Issue + back-link to ADR-025

### Step 2.6 — Append SKILL.md section

Path: `.claude/skills/tachi-control-analysis/SKILL.md`

Insert new `## NIST AI RMF Relationship` section AFTER existing `## Domain Overview` section, BEFORE existing `## Baseline-Aware Control Analysis Rules` section.

Constraints:
- 80-200 words (verify with `awk '/^## NIST AI RMF Relationship/{flag=1; next} /^## /{flag=0} flag' .claude/skills/tachi-control-analysis/SKILL.md | wc -w`)
- Decision-noun byte-identical to ADR-025 Decision section first paragraph (case-insensitive)
- Relative link to ADR-025: `../../../docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md`

### Step 2.7 — Append ADR-024 back-reference

Path: `docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md`

Append `[ADR-025](ADR-025-nist-ai-rmf-evaluation.md) (companion NIST AI RMF evaluation)` to the existing Related ADRs line. Single-line edit; ADR-024 Status field unchanged.

### Step 2.8 — File follow-on Issue (conditional)

If Option A chosen → SKIP this step (FR-008 N/A).

If Option B or C chosen → product-manager runs `bash .aod/scripts/bash/create-issue.sh` to file Issue with:
- `stage:discover` label
- Concrete title (e.g., "Implement NIST AI RMF compensating-control tagging (per ADR-025)" or "Implement NIST AI RMF coverage analyzer agent (per ADR-025)")
- Body: links to ADR-025, names surfaces that would change, includes effort estimate verbatim from ADR-025 Alternatives, names "non-disruptive"/"opt-in" constraint

## Verification (Before Opening PR)

Run all 13 SCs locally:

```bash
# SC-001: ADR-025 file exists
[ -f docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md ] && echo "SC-001 PASS"

# SC-002: Status is Accepted
grep -E '^\*\*Status\*\*: Accepted$' docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md && echo "SC-002 PASS"

# SC-003: Three Surface anchors
[ "$(grep -c '<a id="surface-[abc]"></a>' docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md)" = "3" ] && echo "SC-003 PASS"

# SC-004: Manual reviewer inspection — no TBD/unclear/empty rows in Surface tables

# SC-005: SKILL.md word count in [80, 200]
WC=$(awk '/^## NIST AI RMF Relationship/{flag=1; next} /^## /{flag=0} flag' .claude/skills/tachi-control-analysis/SKILL.md | wc -w)
[ "$WC" -ge 80 ] && [ "$WC" -le 200 ] && echo "SC-005 PASS ($WC words)"

# SC-006: Zero git diff drift on schemas/scripts/agents/examples
[ -z "$(git diff main..144-nist-ai-rmf-evaluation-adr -- schemas/ scripts/ .claude/agents/ examples/)" ] && echo "SC-006 PASS"

# SC-007: Decision-noun byte-equality (case-insensitive)
ADR_NOUN=$(grep -oE -i '(documentation-only mapping|shallow wired integration|deep wired integration|hybrid [BC])' docs/architecture/02_ADRs/ADR-025-nist-ai-rmf-evaluation.md | head -1 | tr '[:upper:]' '[:lower:]')
SKILL_NOUN=$(grep -oE -i '(documentation-only mapping|shallow wired integration|deep wired integration|hybrid [BC])' .claude/skills/tachi-control-analysis/SKILL.md | head -1 | tr '[:upper:]' '[:lower:]')
[ "$ADR_NOUN" = "$SKILL_NOUN" ] && [ -n "$ADR_NOUN" ] && echo "SC-007 PASS ($ADR_NOUN)"

# SC-008: Mapping reference exists
[ -f .claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md ] && echo "SC-008 PASS"

# SC-009: Follow-on Issue (only if Option B/C)
# gh issue list --label stage:discover --search "ADR-025" — manual check

# SC-010: Backward-compatibility test
SOURCE_DATE_EPOCH=1700000000 pytest tests/scripts/test_backward_compatibility.py && echo "SC-010 PASS"

# SC-011: ADR-024 back-reference
grep -E 'ADR-025' docs/architecture/02_ADRs/ADR-024-owasp-aivss-evaluation.md && echo "SC-011 PASS"

# SC-012: docs: conventional commit prefix
[ -z "$(git log main..144-nist-ai-rmf-evaluation-adr --pretty=%s | grep -vE '^docs(\(.+\))?:')" ] && echo "SC-012 PASS"

# SC-013: 3-hour Wave 1 timebox — captured in delivery retrospective
```

## Open PR

```bash
git push -u origin 144-nist-ai-rmf-evaluation-adr
gh pr create --title "docs(144): MAESTRO Companion — NIST AI RMF evaluation ADR" --body "$(cat <<'EOF'
## Summary

Closes the regulated-adopter half of the MAESTRO companion-framework decision space (the AIVSS half closed in PR #167 / Feature 143).

- New ADR-025 evaluating NIST AI RMF against tachi compensating controls analyzer
- New `.claude/skills/tachi-shared/references/nist-ai-rmf-mapping.md` (content shape per chosen option)
- New `## NIST AI RMF Relationship` section in `.claude/skills/tachi-control-analysis/SKILL.md`
- One-line back-reference appended to ADR-024 Related ADRs

## Test plan

- [x] All 13 SCs verified locally (see quickstart.md)
- [x] `pytest tests/scripts/test_backward_compatibility.py` 5/5 byte-identical under `SOURCE_DATE_EPOCH=1700000000`
- [x] Decision-noun byte-equality between ADR-025 and SKILL.md (SC-007)
- [x] `git diff` zero-drift on schemas/scripts/agents/examples (SC-006)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
