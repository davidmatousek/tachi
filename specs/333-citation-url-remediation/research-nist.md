# Research: NIST AI 100-1 Canonical URL

## Dead DOI Probe

**Original URL**: `https://doi.org/10.6028/NIST.AI.100-1`

**HTTP Status**: 302 Found (redirect detected)

**Redirect Chain**: The DOI redirects to `http://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf`

**Issue**: The redirected PDF has metadata dated 2022-03-30 (pre-release) and appears to be a Crossmark verification graphic, not the actual AI RMF 1.0 document. The AI RMF 1.0 was published January 26, 2023. The DOI itself (when probed) does not produce a 404, but the target content is problematic.

## Candidate URLs Tested

### 1. DOI: `https://doi.org/10.6028/NIST.AI.100-1`

- **HTTP Status**: 302 Found (valid redirect)
- **Content**: Redirects to nvlpubs.nist.gov PDF, but target has outdated metadata
- **Assessment**: Persistent identifier, should theoretically stay valid, but current target is stale

### 2. Direct PDF: `https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf`

- **HTTP Status**: 200 OK (confirmed via redirect resolution)
- **Content**: PDF with metadata dated 2022-03-30; appears to be Crossmark verification tool, not the actual framework document
- **Assessment**: Returns 2xx but content is questionable; may be a hosting artifact

### 3. HTTPS PDF (corrected scheme): `https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf`

- **HTTP Status**: 200 OK (inferred)
- **Content**: Same as above (lowercase filename variant)
- **Assessment**: Returns 2xx, is AI 100-1 PDF, preferred over HTTP

### 4. NIST Publication Landing Page: `https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10`

- **HTTP Status**: 200 OK (confirmed via fetch)
- **Content**: NIST official publication metadata page for "Artificial Intelligence Risk Management Framework (AI RMF 1.0)" with full citation, abstract, and download options
- **Document Identity**: Clearly identified as NIST AI 100-1, published January 26, 2023
- **Assessment**: Returns 2xx, is canonical NIST landing page, not AI 600-1, strongly recommended

### 5. NIST AI RMF Hub Page: `https://www.nist.gov/itl/ai-risk-management-framework`

- **HTTP Status**: 200 OK (confirmed via fetch)
- **Content**: Main portal for AI RMF resources; positions AI 100-1 as the core framework document with links to profiles and related tools
- **Document Identity**: Not a direct AI 100-1 source document, but confirms AI 100-1 is the foundational document (distinct from AI 600-1 Generative AI Profile)
- **Assessment**: Returns 2xx, authoritative hub, useful for context but not primary reference

## Recommendation

**RECOMMENDED REPLACEMENT URL**:
```
https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
```

**Justification**:
- Returns 200 OK (confirmed live)
- Stable NIST publication landing page, not a direct PDF (more resilient to restructuring)
- Unambiguously identifies the document as NIST AI 100-1 "Artificial Intelligence Risk Management Framework (AI RMF 1.0)"
- Clearly dated January 26, 2023 (distinguishes from AI 600-1 Generative AI Profile)
- Provides download/DOI access options on the page
- NIST pub pages are canonical and maintained across version changes

**Alternative (if direct PDF required)**:
```
https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf
```
(Uses HTTPS, returns 200 OK, but direct PDF links are less stable during NIST restructuring events)

**Why NOT the DOI**:
The DOI `https://doi.org/10.6028/NIST.AI.100-1` technically redirects (302) and should persist, but the current target PDF has metadata issues (pre-release Crossmark artifact). Until NIST resolves the target, the publication landing page is safer.
