---
source_agent: threat-infographic.md
loaded_at: Error condition during infographic generation
extracted_from: Error Handling & Graceful Degradation lines 533-592
version: "1.0"
---

## Error Handling & Graceful Degradation

The infographic agent handles six specific error conditions. In every case, the infographic specification is preserved as a standalone deliverable. The pipeline is never blocked.

### Condition 1: Missing GEMINI_API_KEY

- **Trigger**: `GEMINI_API_KEY` environment variable is not set or is empty.
- **Action**: Log an informational message: "GEMINI_API_KEY not configured. Infographic specification saved as standalone deliverable. To generate an image, set the GEMINI_API_KEY environment variable."
- **Result**: Specification saved with `image_generated: false`. No API call attempted. Pipeline continues.

### Condition 2: API Rate Limit (HTTP 429)

- **Trigger**: Gemini API returns HTTP 429 (Too Many Requests).
- **Action**: Log a warning: "Gemini API rate limit exceeded (HTTP 429). Infographic image generation skipped. Specification saved as standalone deliverable."
- **Result**: Specification saved with `image_generated: false`. No retry attempted. Pipeline continues.
- **Rationale**: Single-attempt design per scope boundaries. Retry logic is out of scope for MVP.

### Condition 3: API Timeout

- **Trigger**: Gemini API call does not return within 60 seconds.
- **Action**: Log an error: "Gemini API request timed out after 60 seconds. Infographic image generation skipped. Specification saved as standalone deliverable."
- **Result**: Specification saved with `image_generated: false`. Pipeline continues.

### Condition 4: Content Policy Rejection

- **Trigger**: Gemini API returns a response indicating content policy violation (typically a `SAFETY` finish reason or blocked prompt).
- **Action**: Log a warning with the specific rejection reason: "Gemini API content policy rejection: {reason}. Infographic image generation skipped. Specification saved as standalone deliverable."
- **Result**: Specification saved with `image_generated: false`. Pipeline continues.
- **Mitigation**: The prompt construction section is designed to use business-oriented language specifically to minimize this condition. If rejections occur frequently, review the prompt for inadvertent attack-specific terminology.

### Condition 5: Missing Section 6 in threats.md

- **Trigger**: `threats.md` does not contain a Section 6 (Risk Summary) with aggregate severity counts.
- **Action**: Compute severity counts directly from individual findings in Sections 3, 4, and 4a using the fallback methodology defined in Data Extraction Methodology (Step 2). Log an informational message: "Section 6 (Risk Summary) not found in threats.md. Severity counts computed from individual findings."
- **Result**: Specification generated with computed counts. Data accuracy is maintained through direct finding enumeration. Add a note to the specification Metadata: "Risk counts derived from individual findings (Section 6 absent in source)."
- **Cross-reference**: See Data Extraction Methodology, Step 2, "Fallback" for the deduplication procedure that prevents double-counting findings appearing in both individual tables and correlation groups (Section 4a).

### Condition 6: Empty Threat Model (Zero Findings)

- **Trigger**: `threats.md` contains no findings in Sections 3, 4, or 4a (all tables empty or absent).
- **Action**: Produce a complete specification with zero-count values across all sections.
- **Result**: Specification contains:
  - Metadata: `Total Findings: 0`, Risk Posture: "No threats identified in this threat model."
  - Risk Distribution: All severity counts = 0, all percentages = 0%.
  - Coverage Heat Map: Empty table with column headers only.
  - Top Critical Findings: "No findings to display."
  - Architecture Threat Overlay: Components listed with `Low` risk weight and annotation "No findings identified."
  - Visual Design Directives: Standard directives (unchanged — layout is data-independent).
  - `image_generated: false` — no Gemini API call attempted for empty threat models.

### Degradation Summary

| Condition | Spec Saved | Image Generated | Pipeline Blocked | Log Level |
|-----------|-----------|----------------|-----------------|-----------|
| Missing API key | Yes | No | No | Info |
| Rate limit (429) | Yes | No | No | Warning |
| API timeout | Yes | No | No | Error |
| Content policy rejection | Yes | No | No | Warning |
| Missing Section 6 | Yes (computed) | Attempted | No | Info |
| Empty threat model | Yes (zero-count) | No | No | Info |
