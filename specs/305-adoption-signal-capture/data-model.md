# Data Model: Adoption Signal Capture (F-3, BLP-04 Wave 3)

**Feature**: 305 | **Date**: 2026-06-01 | **Plan**: [plan.md](./plan.md)

There is no database and no application code. These "entities" are the **document shapes** for the markdown artifacts the feature produces. They define the field set, required/optional status, validation rules, and where each lives.

---

## 1. Adopter Case Study (submission)

**Location**: authored from `docs/adopters/case-study-template.md`; an accepted instance is listed in `docs/adopters/README.md` **only after an explicit consent grant**.

| Field | Required? | Notes |
|-------|-----------|-------|
| Adopter org / identifier | Required | May be an anonymized identifier if the consent grant says "anonymized". |
| Scale of use | Required | e.g., team size, repos/architectures scanned, frequency. |
| Integration point | Required | Where tachi runs in their workflow (local, CI, pre-merge, etc.). |
| Capabilities used | Required | Which tachi commands/agents/outputs (threat-model, SARIF, risk-score, etc.). |
| Outcomes | Required | What value/result they observed (qualitative is fine). |
| Logo | Optional | Used only if the consent grant permits. |
| Pull-quote | Optional | Short attributable quote. |
| Public-reference link | Optional | Blog/slides/video/talk — the credibility anchor (CNCF/Microcks convention). |
| **Consent grant** | **Required** | See entity 2. Captured at submission. |

**Validation rules**:
- All five required content fields present before an entry is listed in the index.
- **Consent-default-deny**: absent an explicit "yes" grant, the org name/logo are NOT published; the entry may still be recorded anonymized if the grant says so.
- Required vs optional must be visually marked in the template.

---

## 2. Consent Grant (embedded in the case study)

**Location**: a required block within `docs/adopters/case-study-template.md`.

| Prompt | Allowed values | Default if unanswered |
|--------|----------------|-----------------------|
| Publish your org name? | `yes` / `anonymized` / `no` | treated as `no` (do not publish name) |
| Use your logo? | `yes` / `no` | treated as `no` |
| Preferred attribution + contact | free text | none — no attribution applied |

**Validation rules**:
- The block is **required** in the template (FR-002).
- Publication of any identifying field requires the corresponding explicit `yes`.
- This makes consent self-enforcing at submission rather than a manual maintainer gate applied after the fact (PRD PM M-2).

---

## 3. Signal-Log Entry (internal, gitignored)

**Location**: a new append-only subsection in `_internal/strategy/BLP-03-signed-updates.md`. **Never committed** (`.gitignore:198`). Distinct from the existing 2-condition "Re-evaluation log" table in the same file (D4 — no schema overload).

| Field | Required? | Notes |
|-------|-----------|-------|
| date | Required | ISO 8601 (YYYY-MM-DD). |
| source | Required | Where the signal came from (e.g., Discussion #NNN, email, citation URL, traffic dashboard). |
| signal-type | Required | **Closed vocabulary**: `inquiry \| citation \| procurement-mention \| traffic \| adopter-story`. |
| decision | Required | The maintainer's disposition/next action (free text; neutral, no commercial framing). |

**Validation rules**:
- Canonical four-field shape, in order, every entry (NFR-6 format consistency).
- `signal-type` MUST be one of the closed vocabulary values; a novel type is recorded only after the vocabulary is deliberately extended (Edge: enum drift).
- Append-only — existing entries are not edited.
- Content stays positioning-neutral even though the file is private (no pricing/competitor framing — keeps the file safe even if ever surfaced).

---

## 4. Outreach Recipient (private)

**Location**: logged privately in **Issue #305** (never in a public file).

| Field | Required? | Notes |
|-------|-----------|-------|
| Identifier | Required | Handle/name of the contact. |
| Previously-engaged basis | Required | The enumerable qualifying interaction: prior Discussion comment / prior issue or PR / direct reply to a tachi post / prior logged inbound. No cold or first-degree-network contacts. |
| Sent? | Required | Whether the warm message was sent. |

**Validation rules**:
- Each recipient satisfies the enumerable previously-engaged rule (D5).
- The list stays private to Issue #305; never published without consent (FR-008).
- Pre-send tone-review gate passed before any send (R2).

---

## 5. AIVSS Watch Record (platform state)

**Location**: a comment + pin on **Issue #168**.

| Field | Required? | Notes |
|-------|-----------|-------|
| Scope statement | Required | F-3 covers the **watch** only; technical evaluation is a separate future initiative. |
| Pin | Required | Issue pin (issue-pin pool 0/3 → 1/3). |

**Validation rules**:
- The comment explicitly scopes F-3 to the watch (not the evaluation) — prevents scope creep into AIVSS evaluation work.
- References the prior AIVSS-evaluation record (Feature 143 / ADR-024) for continuity.

---

## Index State (empty vs populated)

`docs/adopters/README.md` has two valid states:
- **Empty** (launch): an explicit, non-broken empty state ("No case studies captured yet — here's how to submit"). This is a valid, decidable state (R1) — not a failure.
- **Populated**: a list of accepted case studies, each respecting its consent grant (name or anonymized; logo only if granted).
