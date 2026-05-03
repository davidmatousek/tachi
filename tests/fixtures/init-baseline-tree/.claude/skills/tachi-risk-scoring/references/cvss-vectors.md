---
source_agent: risk-scorer
extracted_from: .claude/agents/tachi/risk-scorer.md
version: 1.0.0
---

# CVSS 3.1 Base Scoring Reference

CVSS 3.1 base vector mappings, metric assessment guidance, AI-specific refinements, and category default vectors for the risk scoring pipeline.

---

## Scoring Methodology

Assign a CVSS 3.1 base score and full vector string to each parsed finding. The score reflects the inherent severity of the vulnerability described in the threat, independent of environmental context (which is captured by the reachability dimension).

**Step 1 -- Load category default vector**: Look up the finding's `category` in the `category_defaults` section of `schemas/risk-scoring.yaml`. This provides a baseline CVSS 3.1 vector string for the threat category.

**Step 2 -- Refine per-threat**: Analyze the finding's `threat` description to adjust individual CVSS metrics from the category default. Each metric is assessed independently:

| CVSS Metric | Abbreviation | Values | Assessment Guidance |
|-------------|-------------|--------|---------------------|
| Attack Vector | AV | N (Network), A (Adjacent), L (Local), P (Physical) | Where must the attacker be? Network attacks are remote; local requires authenticated shell access |
| Attack Complexity | AC | L (Low), H (High) | Does the attack require special conditions? Race conditions, specific configurations = High |
| Privileges Required | PR | N (None), L (Low), H (High) | What access level does the attacker need before exploiting? Unauthenticated = None |
| User Interaction | UI | N (None), R (Required) | Must a user take action (click, open, approve) for exploitation? |
| Scope | S | U (Unchanged), C (Changed) | Does exploitation affect resources beyond the vulnerable component? Cross-component impact = Changed |
| Confidentiality | C | N (None), L (Low), H (High) | How much data can the attacker access? Full DB dump = High; metadata only = Low |
| Integrity | I | N (None), L (Low), H (High) | How much data can the attacker modify? Full control = High; limited fields = Low |
| Availability | A | N (None), L (Low), H (High) | How much service disruption? Complete outage = High; degraded performance = Low |

**Step 3 -- Compute CVSS 3.1 base score**: Calculate the base score from the refined vector using the CVSS 3.1 specification formulas. The score must be a value between 0.0 and 10.0, rounded to one decimal place.

**Step 4 -- Record outputs**: For each finding, store:
- `cvss_base`: The numeric base score (0.0-10.0)
- `cvss_vector`: The full vector string (e.g., `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`)

---

## AI-Specific CVSS Guidance

Standard CVSS 3.1 metrics do not natively cover AI/ML threat characteristics. Apply these refinements for AI threat categories:

**Agentic threats (`agentic`)**:
- Default vector: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L`
- **PR:L** (not PR:N): Agent misuse typically requires authenticated access to the agent system; setting PR:N would create a ceiling effect where all agentic threats score at maximum
- **S:C**: Agent actions typically cross component boundaries (tool servers, external APIs, data stores)
- Refine **A** based on whether the threat involves resource exhaustion (A:H) or data manipulation only (A:N)
- Refine **PR** upward to H if the threat requires admin-level agent access

**LLM threats (`llm`)**:
- Default vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N`
- **UI:R**: Most LLM attacks require the model to process attacker-crafted input (user interaction in the CVSS sense)
- **S:C**: Prompt injection typically causes the model to affect other system components
- Refine **UI** to N for indirect prompt injection (attacker content is already in the knowledge base -- no real-time interaction needed)
- Refine **AC** to H for attacks requiring precise prompt engineering or specific model behavior
- Refine **PR** based on whether the attacker needs an account (PR:L) or can exploit public-facing endpoints (PR:N)

---

## Category Default Vector Reference

These defaults from `schemas/risk-scoring.yaml` serve as baselines. Per-threat refinement adjusts individual metrics based on the specific threat description:

| Category | Default Vector | Base Score | Rationale |
|----------|---------------|------------|-----------|
| spoofing | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N` | 8.2 | Auth bypass: remote, no privileges, high confidentiality impact |
| tampering | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L` | 7.1 | Data modification: requires some access, high integrity impact |
| repudiation | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N` | 4.3 | Audit evasion: lower direct impact, enables other attacks |
| info-disclosure | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` | 6.5 | Data exposure: high confidentiality, no integrity/availability |
| denial-of-service | `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H` | 7.5 | Resource exhaustion: remote, no auth needed, high availability impact |
| privilege-escalation | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H` | 9.9 | Privilege gain: scope change, full CIA impact |
| agentic | `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L` | 9.1 | Agent misuse: scope change, high CI, lower A |
| llm | `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N` | 9.3 | Prompt injection: no auth but requires input processing |

---

## Bounded Scoring for NEW Findings (Baseline Mode)

When a finding has `delta_status: NEW` (discovered in Phase 2 of a baseline-aware run), its CVSS base score must fall within ±1.0 of the category default CVSS base score defined in `schemas/risk-scoring.yaml` → `category_defaults`.

**Bounding formula**:
- `min_score = max(0.0, category_default - 1.0)`
- `max_score = min(10.0, category_default + 1.0)`
- If the assessed `cvss_base` falls outside `[min_score, max_score]`, clamp it to the nearest bound.

**Category defaults with bounded ranges**:

| Category | ID Prefix | Default CVSS | Bounded Range |
|----------|-----------|-------------|---------------|
| spoofing | S | 8.2 | 7.2 – 9.2 |
| tampering | T | 7.1 | 6.1 – 8.1 |
| repudiation | R | 4.3 | 3.3 – 5.3 |
| info-disclosure | I | 6.5 | 5.5 – 7.5 |
| denial-of-service | D | 7.5 | 6.5 – 8.5 |
| privilege-escalation | E | 9.9 | 8.9 – 10.0 |
| agentic | AG | 9.0 | 8.0 – 10.0 |
| llm | LLM | 9.3 | 8.3 – 10.0 |

**Category resolution**: Determine the category from the finding's ID prefix (S→spoofing, T→tampering, R→repudiation, I→info-disclosure, D→denial-of-service, E→privilege-escalation, AG→agentic, LLM→llm). The default CVSS base score is computed from the corresponding default vector in `schemas/risk-scoring.yaml`.

**When bounding applies**: Only to `NEW` findings from Phase 2 isolated discovery. `UPDATED` findings are re-scored fresh without bounding (they have established context). `UNCHANGED` and `RESOLVED` findings inherit scores verbatim.

**When no baseline is present**: Bounding does not apply. All findings are scored using the standard CVSS assessment without constraints.

**Edge cases at extremes**: If a category default is 9.5, the bounded range is 8.5–10.0 (capped at CVSS maximum). If a category default is 1.0, the bounded range is 0.0–2.0 (floored at CVSS minimum).
