# ADR-014: Gemini API Optional Image Generation with Graceful Degradation

**Status**: Accepted (partially superseded by ADR-016)
**Date**: 2026-03-23
**Deciders**: Architect
**Feature**: 018 (Threat Infographic Agent)

> **Note (2026-03-28, Feature 039)**: Infographic generation was extracted from the orchestrator pipeline (Phase 6) into a standalone `/infographic` command. The Gemini API integration, spec-first architecture, and graceful degradation decisions in this ADR remain fully in effect. The Phase 6 references, opt-out flags (`--skip-infographic`, `TACHI_SKIP_INFOGRAPHIC`, `infographic: false`), and orchestrator dispatch are superseded by [ADR-016](ADR-016-infographic-pipeline-decoupling.md). The `/infographic` command now owns invocation control directly.

> **Note (2026-10-10, Feature 373)**: The image models named in Decision §2 and the Mitigation section have been shut down, and the API rejected the request body the render path sent. Feature 373 replaced both, and this note supersedes those model names. The spec-first architecture (§1) and graceful degradation (§3) stand.
>
> - **Model chain.** The chain is `gemini-3-pro-image`, then `gemini-3.1-flash-image`, both GA. They replace `gemini-3-pro-image-preview` and `gemini-3.1-flash-image-preview` (shut down 2026-06-25) and `gemini-2.5-flash-image` (shut down 2026-10-02). The retired IDs are gone from the render surface: the infographic templates, the `tachi-infographics` skill references, the infographic agent and the Claude Code adapter references. A static test fails if one returns (A6 in `tests/scripts/test_gemini_request_contract.py`, gated in CI). Its only exception is one `Retired models:` provenance line in `gemini-prompt-construction.md`.
> - **Request shape.** Requests go to `models/{model}:generateContent` with `generationConfig.responseModalities: ["TEXT","IMAGE"]` and `generationConfig.imageConfig.{aspectRatio, imageSize}`. The released body put `aspectRatio` and `imageSize` directly under `generationConfig`, and the API rejected every request with HTTP 400. Each template's own `## Gemini API Configuration` block sets its model, fallback, aspect ratio and size, so executive-architecture renders 3:4 portrait and the other five templates 16:9. `imageSize: "2K"` is kept: the slowest real-template render took 35.73 s, under the drop threshold of about 45 s (25% headroom on the 60 s single-attempt timeout).
> - **Chain walk and errors.** The next model is tried only when a model is unavailable to the calling key: HTTP 404 `NOT_FOUND` or 403 `PERMISSION_DENIED`. A 400 is not walked, because every model would reject the same body and walking would hide the cause. It is loud but non-blocking: logged at Error with the API's message and the request-body keys sent. A 429, a timeout and any other non-2xx keep a single attempt. When every chain model returns 404 or 403, the exhausted chain is logged at Error, and the summary names each model tried with its status and message. These rows extend Decision §3's six conditions; the agent's error table in `.claude/agents/tachi/threat-infographic.md` is the full list. Each keeps §3's outcome (the specification is saved and the pipeline is not blocked), but none is silent any more: silent degradation is how a request the API always rejected shipped unnoticed.
> - **Live verification** (records in `specs/373-adopter-install-output-fidelity/test-results/`). A pre-build smoke test (W0, 2026-09-28) made eight calls, both models × 16:9 and 3:4 × default size and 2K: all eight returned HTTP 200 with an image, and 2K was honored in every pair. The full render set (K14 and K15, 2026-10-06) rendered all six templates on `gemini-3-pro-image` at 2K and one template on the fallback, and executive-architecture's image compiled onto a single portrait page of the PDF report. The maintainer's visual check of the six renders passed on 2026-10-10. No live call returned a non-200, so the walk and error rows are pinned statically: A7 asserts them in the agent's error table.
> - **Key handling.** `GEMINI_API_KEY` is read from the environment and sent only in the `x-goog-api-key` header: never as a `?key=` query parameter, never echoed or logged, and never through verbose or trace output.
> - **Watching for the next shutdown.** `gemini-prompt-construction.md` keeps one dated `Verified:` line per chain model and aspect ratio, so the date each model was last proven live sits next to the chain. A chain change re-verifies and re-dates those lines, and A1–A5 pin the body and the chain in the reference, every template block and the adapter copy. At runtime, a key that loses every chain model gets the exhausted-chain Error naming each one, not a quiet spec-only result.

---

## Context

Feature 018 adds a threat infographic agent to the orchestrator pipeline as Phase 6. The agent transforms structured threat model findings (`threats.md`) into a visual risk specification (`threat-infographic-spec.md`) containing 6 sections: Metadata, Risk Distribution, Coverage Heat Map, Top Critical Findings, Architecture Threat Overlay, and Visual Design Directives.

The specification is a self-contained document that a designer can render into a visual infographic. However, for immediate value and executive presentation scenarios, the feature also supports automated image generation from the specification.

Two architectural decisions are required:

1. **External API introduction**: The tachi pipeline has been entirely self-contained (no external service dependencies) through Features 001-015. Image generation requires an external API. Which API, and how should the dependency be managed?

2. **Spec-first vs. image-first design**: Should the image be the primary deliverable (with the spec as an intermediate artifact), or should the specification be the primary deliverable (with the image as an enhancement)?

3. **Opt-out mechanism**: Phase 6 follows the default-on pattern established in Phase 5 (Feature 015) and ADR-008/ADR-011. How should opt-out work given the additional complexity of an external API dependency?

---

## Decision

### 1. Spec-First Architecture

The infographic specification (`threat-infographic-spec.md`) is the **primary deliverable**. The image (`threat-infographic.jpg`) is an **optional best-effort enhancement**. The specification is always produced when Phase 6 runs. The image is produced only when the Gemini API key is available and the API call succeeds.

This is the **spec-first pattern**: the pipeline always produces a complete, validated, human-readable specification regardless of external service availability. The image generation is a downstream enhancement that consumes the specification.

### 2. Google Gemini API for Image Generation

We will use the **Google Gemini API** (`gemini-3-pro-image-preview` model, with `gemini-3.1-flash-image-preview` as fallback) for image generation. Authentication is via the `GEMINI_API_KEY` environment variable.

### 3. Six-Condition Graceful Degradation

The infographic agent handles six specific error conditions, all with the same outcome: the specification is preserved as a standalone deliverable, and the pipeline is never blocked.

| Condition | Spec Saved | Image Generated | Pipeline Blocked |
|-----------|-----------|----------------|-----------------|
| Missing API key | Yes | No | No |
| Rate limit (429) | Yes | No | No |
| API timeout (60s) | Yes | No | No |
| Content policy rejection | Yes | No | No |
| Missing Section 6 in input | Yes (computed) | Attempted | No |
| Empty threat model | Yes (zero-count) | No | No |

### 4. Triple Opt-Out Mechanism

Phase 6 supports three independent opt-out mechanisms following the pattern established in ADR-008 and extended in ADR-011:

1. **Flag**: `--skip-infographic` -- command-line flag for per-invocation control
2. **Environment variable**: `TACHI_SKIP_INFOGRAPHIC=true` -- for CI/CD pipeline configuration
3. **Configuration**: `infographic: false` -- for persistent project-level configuration

The environment variable mechanism is new to tachi (Phase 5 used only flag and config). It was added because CI/CD pipelines that do not have Gemini API keys should be able to skip Phase 6 cleanly without modifying invocation flags.

---

## Rationale

### Why spec-first (not image-first)?

1. **Reliability**: The specification can be produced with zero external dependencies. Making the image the primary deliverable would make the pipeline's usefulness contingent on an external API -- violating tachi's local-first, dependency-free philosophy.

2. **Debuggability**: When the image does not match expectations, the specification provides a clear audit trail of exactly what data was extracted and what visual instructions were given. An image-first design would be a black box.

3. **Flexibility**: The specification is consumable by human designers, other image generation tools, and future rendering pipelines. An image-first design locks the output to a single rendering technology.

4. **Consistency**: The specification follows the same markdown-with-YAML-frontmatter pattern as every other tachi output (`threats.md`, `threat-report.md`, `threats.sarif`). The image is a rendering of the specification, not a replacement for it.

### Why Gemini API (not alternatives)?

1. **Text rendering quality**: Gemini's image generation models produce superior text rendering for data-dense infographics compared to alternatives tested during design. Data labels, severity counts, and finding summaries require legible text in the generated image.

2. **Structured prompt support**: Gemini accepts narrative scene descriptions with explicit spatial placement instructions and hex color codes, which maps directly to the specification's Visual Design Directives section.

3. **Single API call**: The entire infographic can be generated in one API call with a text prompt. No multi-step workflow, no image composition pipeline, no intermediate artifacts.

### Why graceful degradation (not hard failure)?

1. **Pipeline integrity**: Phases 1-5 represent the core threat modeling value. Phase 6 is a presentation enhancement. A failure in image generation should never invalidate the security analysis.

2. **API unreliability**: External APIs are subject to rate limits, content policy changes, model deprecation, and network failures. Designing for graceful degradation from the start prevents future reliability issues from becoming pipeline failures.

3. **Zero-config usability**: Users who do not have a Gemini API key still get the infographic specification. The feature is useful without any external service configuration.

---

## Alternatives Considered

### Alternative 1: No Image Generation (Spec Only)

**Pros**:
- Zero external dependencies
- Simpler implementation
- No API key management

**Cons**:
- Reduces immediate value for executive audiences who want a visual artifact
- Misses the opportunity to demonstrate end-to-end automated visualization

**Why Not Chosen**: The spec-first architecture provides the zero-dependency benefit while still offering image generation as an enhancement. Users who want spec-only get it by default (no API key needed).

### Alternative 2: Mermaid Diagram Instead of Image

**Pros**:
- No external API dependency
- GitHub-renderable (consistent with attack trees in Feature 015)
- Text-based, version-controllable

**Cons**:
- Mermaid cannot produce presentation-quality infographics (no custom color palettes, no spatial zone layouts, no typography control)
- Infographic requirements (donut charts, heat maps, three-zone layouts) exceed Mermaid's diagramming capabilities
- Would produce a diagram, not an infographic -- different deliverable type

**Why Not Chosen**: Mermaid is appropriate for technical diagrams (attack trees) but cannot produce the data-dense, design-controlled visual format that executive audiences expect from a risk infographic.

### Alternative 3: DALL-E or Stable Diffusion for Image Generation

**Pros**:
- DALL-E: Widely known, OpenAI ecosystem
- Stable Diffusion: Open-source, self-hostable

**Cons**:
- DALL-E: Inferior text rendering in images; data labels and counts would be illegible
- Stable Diffusion: Requires GPU infrastructure; self-hosting violates local-first simplicity
- Both: Less controllable spatial placement than Gemini for structured data visualization

**Why Not Chosen**: Text rendering quality is the primary selection criterion for data-dense infographics. Gemini's image generation produces more legible text labels and data values than alternatives tested.

### Alternative 4: Mandatory API Key (Hard Failure Without Key)

**Pros**:
- Simpler error handling
- Guarantees image output when Phase 6 runs

**Cons**:
- Blocks the pipeline for users without a Gemini account
- Violates tachi's local-first, zero-external-dependency philosophy
- Makes Phase 6 unusable in CI/CD environments without API key secrets configured

**Why Not Chosen**: The spec-first design provides value without any API key. Making the key mandatory would reduce adoption and violate the graceful degradation principle.

---

## Consequences

### Positive
- Phase 6 produces a validated specification with zero external dependencies
- Image generation is a transparent enhancement -- users see exactly what data drives the image
- Six-condition graceful degradation ensures the pipeline never fails due to an external API
- Triple opt-out (flag, env var, config) covers all skip scenarios including CI/CD
- Establishes the spec-first pattern for future features that may integrate external services

### Negative
- First external API dependency in the tachi pipeline (Gemini API)
- Image quality depends on Gemini model capabilities which may change across model versions
- `GEMINI_API_KEY` is a new environment variable that users must manage if they want image generation
- Content policy rejections from Gemini are possible despite business-oriented prompt framing

### Mitigation
- External dependency is entirely optional -- spec is always produced without it
- Fallback model (`gemini-3.1-flash-image-preview`) provides resilience against primary model deprecation
- Prompt construction uses business-oriented language (avoiding attack terminology) to minimize content policy rejections
- API key absence produces an informational log message with setup guidance, not an error

---

## Related Decisions

- [ADR-008: Opt-out Flag for Default-On Quality Gate Steps](ADR-008-opt-out-flag-for-default-quality-gates.md) -- established the `--no-X` / `--skip-X` convention that Phase 6 follows
- [ADR-011: Multi-Flag Opt-Out Pattern](ADR-011-multi-flag-opt-out-and-step-insertion-pattern.md) -- extended opt-out to multiple independent flags; Phase 6 adds `--skip-infographic`
- [ADR-013: SARIF Output Format Adoption](ADR-013-sarif-output-format-adoption.md) -- Phase 4 co-generation pattern that Phase 6 specification follows (produce validated structured output alongside primary deliverable)

---

## References

- Feature 018 spec: `specs/018-threat-infographic-agent/spec.md`
- Feature 018 plan: `specs/018-threat-infographic-agent/plan.md`
- Infographic agent: `agents/threat-infographic.md`
- Infographic schema: `schemas/infographic.yaml`
- Orchestrator (Phase 6 dispatch): `agents/orchestrator.md`
- Gemini API documentation: https://ai.google.dev/gemini-api/docs/image-generation
