---
source_agent: risk-scorer
extracted_from: .claude/agents/tachi/risk-scorer.md
version: 1.0.0
---

# Reachability Analysis Reference

Assess how exposed each finding's target component is based on its position within the architecture's trust boundaries. Reachability captures the architecture-aware attack surface that other dimensions do not address -- a vulnerability in an internet-facing component poses a fundamentally different risk than the same vulnerability behind multiple authentication layers and network segmentation.

### Input Dependencies

This section consumes two data sources:

1. **`component_zone_map`** (required): The component-to-zone mapping dictionary produced by Trust Zone Extraction (Section 2). Maps each component name to its `zone` and `trust_level` (`Untrusted`, `Semi-Trusted`, or `Trusted`).
2. **`architecture.md`** (optional): When an `architecture.md` file exists in the same directory as the input `threats.md`, parse it for supplementary architecture context (authentication barriers and network segmentation) that adjusts the baseline zone-derived score.

### Zone-to-Reachability Baseline Mapping

Map each finding's target component to a baseline reachability score using the component's trust level from `component_zone_map`. The baseline reflects the inherent exposure of the trust zone.

| Trust Level | Zone Name Examples | Baseline Score Range | Default Baseline | Rationale |
|-------------|-------------------|---------------------|-----------------|-----------|
| `Untrusted` | External Zone, Public Internet, External Services, User Zone | 8.0 - 10.0 | 9.0 | Directly exposed to untrusted actors; minimal barriers to reach |
| `Semi-Trusted` | DMZ, Partner Zone, Internal Services Zone | 4.0 - 7.0 | 5.5 | Behind at least one trust boundary; some access controls in place |
| `Trusted` | Internal Zone, Internal Network, Internal Services | 1.0 - 4.0 | 2.5 | Deep within the architecture; multiple barriers to reach |

**Default baseline selection**: Use the midpoint of the range as the default baseline for each trust level (9.0 for Untrusted, 5.5 for Semi-Trusted, 2.5 for Trusted). Refinements in Steps 6b and 6c adjust this baseline up or down within the range.

### Per-Finding Baseline Refinement

For each finding, determine its baseline reachability score:

**Step 1 -- Look up component trust level**: Query `component_zone_map` using the finding's `component` field. Perform a **case-insensitive** lookup (as specified in Section 2e).

**Step 2 -- Apply zone name refinement within the baseline range**: Analyze the zone name itself (not just the trust level) to position the score within the baseline range. Apply these zone name keyword adjustments:

| Zone Name Keyword (case-insensitive) | Adjustment | Rationale |
|--------------------------------------|------------|-----------|
| "internet", "public", "external" | +0.5 from default baseline | Directly internet-facing increases exposure |
| "user", "client" | +0.5 from default baseline | User-facing endpoints are primary attack targets |
| "dmz", "perimeter", "gateway" | +0.5 from default baseline | DMZ components are designed to be reachable |
| "internal", "backend", "core" | -0.5 from default baseline | Internal positioning reduces exposure |
| "database", "storage", "data store" | -0.5 from default baseline | Data stores are typically not directly addressable |

**Keyword matching**: Scan the zone name for each keyword using case-insensitive substring matching. If multiple keywords match, apply the **net sum** of all matching adjustments. The result must remain within the trust level's baseline range (clamp to range boundaries).

**Example**: A component in zone "Public Internet" with trust level `Untrusted`:
- Default baseline: 9.0
- Keyword "public": +0.5, keyword "internet": +0.5
- Net adjustment: +1.0
- Pre-clamp score: 10.0
- Clamped to Untrusted range [8.0, 10.0]: **10.0**

**Example**: A component in zone "Internal Services Zone" with trust level `Trusted`:
- Default baseline: 2.5
- Keyword "internal": -0.5
- Net adjustment: -0.5
- Pre-clamp score: 2.0
- Clamped to Trusted range [1.0, 4.0]: **2.0**

### Architecture Adjustments

When an `architecture.md` file is available, parse it for supplementary context that adjusts the baseline score downward. Architecture adjustments represent protective barriers that reduce reachability.

**Locating architecture.md**: Search for `architecture.md` in the same directory as the input `threats.md`. If not found, skip architecture adjustments entirely (the zone-derived baseline stands as the final score, subject to clamping in Step 6d).

**Parsing rules**: Scan `architecture.md` for the following patterns. These patterns may appear in headings, bullet lists, tables, or prose paragraphs. Match case-insensitively.

#### Authentication Barrier Adjustment: -1.5 per layer

For each authentication barrier between an attacker and the finding's target component, subtract 1.5 from the baseline score. Authentication barriers include:

| Pattern to Match (case-insensitive) | Counts As |
|--------------------------------------|-----------|
| "authentication", "auth layer", "auth required" | 1 authentication barrier |
| "multi-factor", "MFA", "2FA", "two-factor" | 1 additional barrier (stacks with base auth) |
| "mutual TLS", "mTLS", "client certificate" | 1 authentication barrier |
| "API key", "API token", "bearer token" | 1 authentication barrier |
| "OAuth", "OIDC", "OpenID Connect" | 1 authentication barrier |

**Counting rules**:
- Count barriers that are **explicitly associated** with the finding's target component or its zone. A barrier mentioned for "all API endpoints" applies to API-facing components; a barrier mentioned for "admin panel" applies only to admin components.
- If `architecture.md` describes barriers at a general/system level without component specificity, apply them to all `Semi-Trusted` and `Trusted` zone components (not to `Untrusted` -- external components are outside the authentication perimeter by definition).
- Maximum authentication barrier count per finding: **3** (cap at -4.5 total adjustment). Additional layers beyond 3 do not further reduce the score.

#### Network Segmentation Adjustment: -1.0 per boundary

For each network segmentation boundary between the external attack surface and the finding's target component, subtract 1.0 from the baseline score. Network boundaries include:

| Pattern to Match (case-insensitive) | Counts As |
|--------------------------------------|-----------|
| "network segment", "network segmentation", "VLAN" | 1 network boundary |
| "firewall", "firewall rule", "security group" | 1 network boundary |
| "private subnet", "private network" | 1 network boundary |
| "air gap", "air-gapped" | 2 network boundaries (strong isolation) |
| "VPN", "VPN required" | 1 network boundary |

**Counting rules**:
- Count boundaries that **separate** the finding's target component from the untrusted zone. A component in a private subnet behind a firewall has 2 network boundaries.
- If `architecture.md` describes segmentation at a general/system level, apply boundaries based on zone depth: `Semi-Trusted` components get 1 boundary (one hop from external); `Trusted` components get 2 boundaries (two hops from external). `Untrusted` components get 0 boundaries.
- Maximum network segmentation count per finding: **3** (cap at -3.0 total adjustment).

#### Combined Architecture Adjustment

The total architecture adjustment is the sum of authentication barrier and network segmentation adjustments:

```
architecture_adjustment = (auth_barrier_count x -1.5) + (network_boundary_count x -1.0)
```

**Maximum total architecture adjustment**: -7.5 (3 auth barriers at -4.5 + 3 network boundaries at -3.0). This cap prevents over-adjustment that could push all scores to floor values.

**Example**: A `Semi-Trusted` component (baseline 5.5) with 1 auth barrier and 1 network boundary:
- Auth adjustment: 1 x -1.5 = -1.5
- Network adjustment: 1 x -1.0 = -1.0
- Total adjustment: -2.5
- Adjusted score: 5.5 - 2.5 = 3.0
- Clamped to Semi-Trusted range [4.0, 7.0]: **4.0** (zone floor enforced)

**Example**: An `Untrusted` component (baseline 9.0) with 0 auth barriers (external) and 0 network boundaries:
- Total adjustment: 0.0
- Adjusted score: 9.0
- Clamped to Untrusted range [8.0, 10.0]: **9.0**

**Example**: A `Trusted` component (baseline 2.5) with 2 auth barriers, MFA, and 2 network boundaries:
- Auth barriers: 2 (base auth + MFA) x -1.5 = -3.0
- Network boundaries: 2 x -1.0 = -2.0
- Total adjustment: -5.0
- Adjusted score: 2.5 - 5.0 = -2.5
- Clamped to Trusted range [1.0, 4.0]: **1.0** (zone floor enforced)

### Final Score Clamping

After all adjustments (zone baseline + zone name refinement + architecture adjustments), clamp the final reachability score to the **per-zone range** for the component's trust level. This ensures scores cannot fall below the zone floor — even the most protected component in a zone retains the minimum reachability inherent to that trust level.

| Trust Level | Clamp Range |
|-------------|------------|
| `Untrusted` | [8.0, 10.0] |
| `Semi-Trusted` | [4.0, 7.0] |
| `Trusted` | [1.0, 4.0] |
| Default (no zone data) | [0.0, 10.0] |

```
reachability = max(zone_floor, min(zone_ceiling, adjusted_score))
```

The final score must be rounded to one decimal place. The per-zone clamp prevents architecture adjustments from producing scores that contradict the trust level classification — a Trusted component cannot score below 1.0 regardless of how many barriers exist, because it is still reachable within its zone.

### Default Behavior When Trust Zone Data Is Unavailable

When `component_zone_map` is empty (any of the fallback cases defined in Section 2g), apply a flat default reachability score to all findings:

- **Default reachability score**: 5.0 (medium exposure)
- **Warning**: Emit a warning with each finding: `"Reachability defaulted to 5.0 -- no trust zone data available for component '{component_name}'"`
- **architecture.md still applies**: Even when `component_zone_map` is empty, if `architecture.md` is present, parse it for general system-level authentication and segmentation data. Apply architecture adjustments to the 5.0 default baseline for all findings. This allows architecture context to improve scoring even without trust zone assignments.
- **Neither source available**: When both `component_zone_map` is empty AND no `architecture.md` exists, use flat 5.0 for all findings. Emit the warning: `"Reachability scores default to 5.0 -- no trust zone or architecture data available"`

### Component Name Fuzzy Matching

Finding components may not exactly match `component_zone_map` keys due to naming variations between the threat model tables and the trust zone table. Apply fuzzy matching when an exact case-insensitive lookup fails:

**Step 1 -- Exact case-insensitive match**: Query `component_zone_map` using the finding's `component` field with case-insensitive comparison. If found, use the matched entry.

**Step 2 -- Substring containment match**: If Step 1 fails, check whether the finding's component name is contained within any `component_zone_map` key, or vice versa (case-insensitive). Use the longest matching key.

Examples:
- Finding component `"LLM Agent"` matches map key `"LLM Agent Orchestrator"` (finding name contained in key)
- Finding component `"External API Gateway"` matches map key `"External API"` (key contained in finding name)

**Step 3 -- Word overlap match**: If Steps 1 and 2 fail, tokenize both the finding component name and each `component_zone_map` key into words (split on spaces, hyphens, underscores). Select the map key with the highest word overlap ratio (matching words / total unique words). Require a minimum overlap of 50% to accept the match.

Example:
- Finding component `"Knowledge Base Store"` vs map key `"Knowledge Base"`: overlap words = {"knowledge", "base"}, total unique = {"knowledge", "base", "store"}, ratio = 2/3 = 67% -- match accepted

**Step 4 -- No match found**: If all fuzzy matching steps fail, treat the component as having no trust zone data. Apply the default reachability score of 5.0 with a warning: `"Component '{component_name}' could not be matched to any trust zone; reachability defaulted to 5.0"`

### Reachability Scoring Summary

The complete reachability calculation for a single finding follows this sequence:

1. **Look up component** in `component_zone_map` (case-insensitive, then fuzzy match per Section 6f)
2. **Determine baseline** from trust level (9.0 / 5.5 / 2.5) or default 5.0 if no match
3. **Apply zone name refinement** using keyword adjustments (Section 6b Step 2); clamp to trust level range
4. **Apply architecture adjustments** if `architecture.md` is available (Section 6c); auth barriers at -1.5 each (max 3), network boundaries at -1.0 each (max 3)
5. **Clamp final score** to the per-zone range (Untrusted [8.0, 10.0], Semi-Trusted [4.0, 7.0], Trusted [1.0, 4.0], Default [0.0, 10.0]) and round to one decimal place
6. **Record output**: Store `reachability` score (0.0-10.0) for the finding
