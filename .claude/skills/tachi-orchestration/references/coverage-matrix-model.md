---
source_agent: orchestrator
extracted_from: .claude/agents/tachi/orchestrator.md
version: 1.0.0
---

# Coverage Matrix Model Reference

The coverage matrix (Section 5 of the output) cross-references components (rows) against threat categories (columns) with finding counts per cell. This reference defines the three-state cell model, deduplication rules for correlated findings, the Total column and Total row computations, and footnote rules.

---

## Matrix Structure

| Component | S | T | R | I | D | E | AG | LLM | Total |
|-----------|---|---|---|---|---|---|----|-----|-------|

- **Rows**: One row per component from the Phase 1 inventory, listed in the same order as the Phase 1 component inventory.
- **Columns**: 8 threat category columns (S, T, R, I, D, E, AG, LLM) plus a Total column.

---

## Three-State Cell Model

Each cell in the matrix contains exactly one of three values:

### 1. Deduplicated Finding Count (integer)

The number of unique threats identified for that component-category pair.

**Deduplication rule**: When computing the count, apply correlation-group deduplication. If any findings in the cell belong to a correlation group (from the Correlation Detection phase), those findings contribute **1** to the cell count collectively rather than individually. Uncorrelated findings each contribute **1** as normal.

**Example**: A cell contains findings T-1, T-2, and T-3. Findings T-1 and T-2 belong to correlation group CG-1. The cell count is **2** (1 for the correlation group + 1 for uncorrelated T-3).

**Example**: A cell contains findings S-1 and S-2, neither of which belongs to a correlation group. The cell count is **2** (1 + 1, each counted individually).

**Example**: A cell contains findings I-1, I-2, and I-3, all belonging to correlation group CG-2. The cell count is **1** (the entire group counts as 1).

### 2. Analyzed, Zero Findings (em dash: `---`)

The component was dispatched to that category's agent, and the agent returned zero findings. The component was analyzed for that threat category, and no threats were identified.

**Display**: An em dash (`---`).

**Meaning**: "We looked and found nothing" -- the absence of findings is an affirmative result of completed analysis.

### 3. Not Applicable (`n/a`)

The category does not apply to this component. The component was not dispatched to that category because its DFD element type does not include that STRIDE category (per the STRIDE-per-Element normalization table), and no AI keywords matched for AI categories.

**Display**: `n/a`.

**Meaning**: "We did not look" -- the absence of findings is expected because the analysis was not applicable.

### Distinction Importance

This distinction is critical for threat model consumers:

- A `---` cell means analysis was performed with no findings. This confirms coverage.
- A `n/a` cell means analysis was not applicable. This is expected and does not indicate a gap.
- A numeric cell means threats were identified. The count reflects unique threats after correlation deduplication.

All three states must be visually distinguishable in the matrix.

---

## Total Column

For each component row, sum all deduplicated finding counts in that row. Cells with `---` or `n/a` contribute **0** to the sum.

**Example**: A component row with cells `2`, `---`, `n/a`, `1`, `---`, `n/a`, `n/a`, `n/a` has a Total of **3** (2 + 0 + 0 + 1 + 0 + 0 + 0 + 0).

## Total Row

Include a final row labeled **Total** that sums each category column. The Total-Total cell (bottom-right) contains the grand total of all findings across all components and categories.

**Computation**: For each category column, sum all deduplicated finding counts across all component rows. Cells with `---` or `n/a` contribute **0**.

---

## Footnote Rules

After producing the coverage matrix table, check whether any correlation groups were created during the Correlation Detection phase:

### Correlation Groups Exist (count > 0)

Append a footnote below the matrix table:

```
Counts reflect deduplicated findings. N correlation groups merged M individual findings.
```

Where:
- **N** is the number of correlation groups
- **M** is the total number of individual findings absorbed into those groups

**Example**: If 3 correlation groups exist, containing 2, 3, and 2 findings respectively (total 7 individual findings), the footnote reads: `"Counts reflect deduplicated findings. 3 correlation groups merged 7 individual findings."`

### No Correlation Groups Exist

Do **not** include a footnote. The matrix counts are already raw counts with no deduplication applied.

---

## Self-Check

After producing the coverage matrix, verify:

- Every component from the Phase 1 inventory appears as a row.
- Cell values with finding counts reflect deduplicated counts: for each cell, count uncorrelated findings individually and count each correlation group's findings as 1, then verify the cell value matches this deduplicated total.
- Cells marked `---` (em dash) correspond to component-category pairs where the agent was dispatched but returned zero findings.
- Cells marked `n/a` correspond to component-category pairs where the component's DFD type excludes that STRIDE category and no AI keywords matched.
- The Total column for each row equals the sum of that row's deduplicated finding counts.
- The Total row for each column equals the sum of that column's deduplicated finding counts.

If any self-check fails, correct the matrix before proceeding.
