# Scope

<!-- Rule file for tachi -->
<!-- This file is referenced from CLAUDE.md using @-syntax -->

## Overview

This file defines what tachi is (and isn't) to set clear expectations for adopters. tachi-the-scanner and AOD-Kit-the-methodology are kept separate here — see "Built with AOD-Kit" at the end for the relationship.

---

## What tachi Is

- A **threat modeling and AI-reasoning vulnerability detection harness for Claude Code** (STRIDE + AI + MAESTRO).
- A new scanning column alongside SAST / SCA / Secrets — same role, logic-level instead of syntax-level.
- An instrumentation harness, not a SaaS — adopters install it into their own project and run it locally; architecture descriptions never leave their machine.
- Open source under Apache 2.0.

## Key Features

- 14 specialized threat agents (6 STRIDE + 5 LLM + 3 Agentic) dispatched against your architecture description
- 6 slash commands producing 20+ artifacts: `threats.md`, SARIF, narrative report, attack trees, MAESTRO classification, risk scores, compensating controls, infographics, PDF security report
- 5 input formats (Mermaid, free-text, ASCII, PlantUML, C4)
- 50/50 OWASP coverage across LLM 2025, Agentic 2026, ML 2023, Mobile 2024, Web/API 2021/2023
- MAESTRO seven-layer classification (L1–L7) and cross-layer attack-chain detection
- Baseline delta tracking across runs

---

## What tachi Is NOT

- **NOT a SAST/SCA replacement** — complementary scanning column for logic-level risks SAST cannot reach
- **NOT application code** — adopters bring their own architecture description (`docs/security/architecture.md`)
- **NOT a CI/CD tool** — adopters integrate it into their own pipelines (SARIF outputs feed GitHub Code Scanning)
- **NOT a replacement for human oversight** — the harness surfaces findings; remediation decisions are yours
- **NOT agent-agnostic** — the scanner runs inside Claude Code (the AOD-Kit methodology backing tachi's development IS portable, but the scanner itself is not)
- **NOT a SaaS** — no telemetry, no remote inference, no data leaving your environment

---

## Built with AOD-Kit

Tachi's own development is governed by the [Agentic Oriented Development Kit (AOD-Kit)](https://github.com/davidmatousek/agentic-oriented-development-kit) — the SDLC Triad methodology (PM + Architect + Team-Lead sign-offs) and quality gates that govern how tachi is built and maintained.

AOD-Kit is a separate project; tachi adopts it as its own development discipline. **Adopters consuming tachi as a scanner do not need to use AOD-Kit themselves.** The two products serve different purposes: AOD-Kit is for building software with AI agents; tachi is for analyzing software architecture for security risks.
