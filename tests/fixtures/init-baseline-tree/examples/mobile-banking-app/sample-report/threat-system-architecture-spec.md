---
schema_version: "1.4"
template: "system-architecture"
date: "2026-04-29"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 31
image_generated: false
---

# Threat Infographic Specification — System Architecture

**Project**: WellnessBank Mobile Banking Application
**Template**: System Architecture
**Data Source**: compensating-controls.md (residual risk tier)
**Generated**: 2026-04-29

---

## 1. Metadata

| Field | Value |
|-------|-------|
| Project Name | WellnessBank Mobile Banking Application |
| Scan Date | 2026-04-29 |
| Analysis Agents | 8 |
| Total Findings | 31 |
| Risk Posture | Residual risk — 0 Critical and 9 High findings across 12 components |

---

## 2. Risk Distribution

**Chart Title**: Residual Risk Distribution

| Severity | Count | Percentage | Color |
|----------|-------|------------|-------|
| Critical | 0 | 0% | #DC2626 |
| High | 9 | 29% | #EA580C |
| Medium | 20 | 65% | #CA8A04 |
| Low | 2 | 6% | #2563EB |
| **Total** | **31** | **100%** | — |

---

## 3. Coverage Heat Map

| Component | Critical | High | Medium | Low | Total |
|-----------|----------|------|--------|-----|-------|
| WellnessBank Android Client | 0 | 3 | 7 | 0 | 10 |
| WellnessBank Backend API | 0 | 0 | 4 | 1 | 5 |
| WellnessBankCredentialCache | 0 | 1 | 2 | 0 | 3 |
| WellnessBankLocalDB | 0 | 0 | 3 | 0 | 3 |
| Mobile Banking Customer | 0 | 2 | 0 | 0 | 2 |
| MoneyTransferActivity | 0 | 2 | 0 | 0 | 2 |
| WellnessAnalyticsSDK | 0 | 0 | 1 | 1 | 2 |
| Other | 0 | 1 | 3 | 0 | 4 |

> "Other" aggregates WellnessBankDebugActivity (1H+1M), WellnessPaySDK (0H+2M) — 4 findings total.

### Cell-Level Grid

| Component | S | T | R | I | D | E |
|-----------|---|---|---|---|---|---|
| WellnessBank Android Client | Medium | High | Medium | High | Medium | --- |
| WellnessBank Backend API | Low | --- | Medium | Low | High | Medium |
| WellnessBankCredentialCache | n/a | Medium | n/a | High | Medium | n/a |
| WellnessBankLocalDB | n/a | Medium | n/a | Medium | Medium | n/a |
| Mobile Banking Customer | High | n/a | Medium | n/a | n/a | n/a |
| MoneyTransferActivity | --- | High | --- | --- | --- | High |
| WellnessAnalyticsSDK | --- | Medium | --- | Low | --- | --- |
| WellnessBankDebugActivity | --- | --- | Medium | --- | --- | High |
| WellnessPaySDK | --- | Medium | --- | Medium | --- | --- |

> AG and LLM columns omitted — no AI/agentic components in this architecture.

---

## 4. Top Critical Findings

> No Critical residual findings. Listing top 5 High findings by residual score descending.

| # | Finding ID | Component | Threat | Residual Risk |
|---|-----------|-----------|--------|---------------|
| 1 | E-1 | WellnessBankDebugActivity | Debug Activity in production release allows any ADB user to bypass authentication and execute privileged banking operations | High (8.5) |
| 2 | E-2 | MoneyTransferActivity | Exported money-transfer screen accepts external app commands to initiate fund transfers without any login requirement | High (8.3) |
| 3 | T-3 | MoneyTransferActivity | Android inter-process messages from any installed app can hijack the money-movement flow without authentication | High (8.1) |
| 4 | T-4 | WellnessBank Android Client | App ships without code obfuscation or tampering detection, enabling reverse engineering and runtime hook injection | High (7.7) |
| 5 | I-4 | WellnessBank Android Client | 4-digit PIN key derivation uses only 1,000 iterations with no salt — entire PIN space exhausted in under one second | High (7.5) |

---

## 5. Architecture Threat Overlay

### Trust Zones

| Zone | Trust Level | Components |
|------|-------------|------------|
| User Zone | Untrusted | Mobile Banking Customer |
| Device Zone | Semi-Trusted | WellnessBank Android Client, WellnessBankDebugActivity, MoneyTransferActivity, WellnessAnalyticsSDK, WellnessPaySDK, WellnessBankLocalDB, WellnessBankCredentialCache |
| Backend Zone | Trusted | WellnessBank Backend API, BackendUserAccountStore |
| External Services | Untrusted | Third-Party Analytics Provider, Third-Party Payment Provider |

### Component Risk Weights (Residual)

| Component | Risk Weight | Score | Annotation |
|-----------|-------------|-------|------------|
| Mobile Banking Customer | High | 3.0 | 2 High findings — session replay, non-repudiation |
| MoneyTransferActivity | High | 3.0 | 2 High findings — intent hijacking, privilege escalation |
| WellnessBank Android Client | Medium | 2.3 | 3 High + 7 Medium — binary protection, cryptography, privacy gaps |
| WellnessBankCredentialCache | Medium | 2.3 | 1 High + 2 Medium — plaintext credential storage |
| Other | Medium | 2.2 | 1 High + 3 Medium — debug bypass, supply chain |
| WellnessBankLocalDB | Medium | 2.0 | 3 Medium — unencrypted SQLite, backup exposure |
| WellnessBank Backend API | Low | 1.8 | 4 Medium + 1 Low — rate limiting, audit, authorization |
| WellnessAnalyticsSDK | Low | 1.5 | 1 Medium + 1 Low — supply chain, communication |

### Data Flows (Severity-Colored by Residual Risk)

| Source | Destination | Data Label | Severity Color |
|--------|-------------|------------|----------------|
| Mobile Banking Customer | MoneyTransferActivity | Intent Extras (External App or Shell) | High (orange) |
| Mobile Banking Customer | WellnessBank Android Client | Login Credentials (UI Input) | High (orange) |
| Mobile Banking Customer | WellnessBankDebugActivity | adb shell am start (Debug Activity Bypass) | Gray (neutral) |
| MoneyTransferActivity | WellnessBank Android Client | Money-Movement Request | High (orange) |
| WellnessBank Android Client | WellnessAnalyticsSDK | Analytics Event | Medium (yellow) |
| WellnessBank Android Client | WellnessBank Backend API | Transaction Request | Medium (yellow) |
| WellnessBank Android Client | WellnessBankCredentialCache | Username + Auth Token | High (orange) |
| WellnessBank Android Client | WellnessBankLocalDB | Account Snapshot + Recent Transactions | Medium (yellow) |
| WellnessBank Android Client | WellnessPaySDK | Payment Initiation | Gray (neutral) |
| WellnessBank Backend API | BackendUserAccountStore | Account Read / Write | Gray (neutral) |
| WellnessBank Backend API | WellnessBank Android Client | Transaction Response | High (orange) |
| WellnessBankCredentialCache | WellnessBank Android Client | Restored Credentials on App Launch | High (orange) |
| WellnessBankDebugActivity | WellnessBank Android Client | Privileged Action without Auth Boundary | High (orange) |
| WellnessBankLocalDB | WellnessBank Android Client | Cached Account Data | High (orange) |
| BackendUserAccountStore | WellnessBank Backend API | Account Record | Medium (yellow) |
| WellnessAnalyticsSDK | Third-Party Analytics Provider | Telemetry Payload | Gray (neutral) |
| WellnessPaySDK | Third-Party Payment Provider | Payment Authorization Request | Gray (neutral) |
| Third-Party Payment Provider | WellnessPaySDK | Payment Confirmation | Gray (neutral) |
| WellnessPaySDK | WellnessBank Android Client | Payment Result | High (orange) |

### Trust Boundary Crossings

| Crossing Point | From Zone | To Zone | Finding Count |
|----------------|-----------|---------|---------------|
| Mobile Banking Customer → WellnessBank Android Client | User Zone | Device Zone | 0 (flows carry High findings in components, not boundary) |
| Mobile Banking Customer → WellnessBankDebugActivity | User Zone | Device Zone | 0 |
| Mobile Banking Customer → MoneyTransferActivity | User Zone | Device Zone | 0 |
| WellnessBank Android Client → WellnessBank Backend API | Device Zone | Backend Zone | 0 |
| WellnessBank Backend API → WellnessBank Android Client | Backend Zone | Device Zone | 0 |
| WellnessAnalyticsSDK → Third-Party Analytics Provider | Device Zone | External Services | 0 |
| WellnessPaySDK → Third-Party Payment Provider | Device Zone | External Services | 0 |
| Third-Party Payment Provider → WellnessPaySDK | External Services | Device Zone | 0 |

---

## 6. Visual Design Directives

### Color Palette (Tailwind CSS)

| Severity | Hex Code | Usage |
|----------|----------|-------|
| Critical | #DC2626 | Red-600: component box borders, finding badge pills |
| High | #EA580C | Orange-600: component box borders, finding badge pills, data flow arrows |
| Medium | #CA8A04 | Yellow-600: component box borders, finding badge pills, data flow arrows |
| Low | #2563EB | Blue-600: component box borders, finding badge pills |
| Note | #6B7280 | Gray-500: neutral data flow arrows, clean component borders |
| Clean cell | #F3F4F6 | Gray-100: component boxes with no findings |
| Card bg | #F9FAFB | Gray-50: component fill |
| Border | #E5E7EB | Gray-200: panel and zone borders |

### Layout Structure

- Background: clean white (#FFFFFF)
- Aspect Ratio: 16:9 landscape
- Style: professional architecture poster, Figma / Miro design artifact quality
- 4 trust zones rendered as labeled color-tinted regions:
  - User Zone (warm red tint, top-left): Mobile Banking Customer
  - Device Zone (neutral slate tint, center): 7 components with severity-colored borders
  - Backend Zone (cool green tint, right): WellnessBank Backend API, BackendUserAccountStore
  - External Services (warm red tint, top-right): Third-Party Analytics Provider, Third-Party Payment Provider
- Data flow arrows: curved, colored by highest residual severity on that path; labeled with data description
- Finding ID badges: severity-colored pill badges on component boxes
- Legend panel: bottom strip with severity color swatches and finding counts

### Typography

- Title: Bold, 28-32pt equivalent
- Section Headers: Semi-bold, 18-22pt equivalent
- Data Labels: Regular, 12-14pt equivalent
- Data Values: Bold, 14-16pt equivalent

### Background

Clean white (#FFFFFF). Dark text throughout. Component boxes: white fill with rounded corners, subtle drop shadow, full colored border matching highest residual severity.

### Gemini Prompt

**PREAMBLE** (verbatim from scaffold):

Create a premium, professionally designed system architecture diagram showing security threat analysis findings. This should look like an architecture poster from a top-tier security consultancy — clean, authoritative, and visually sophisticated. The feel should be modern and polished, like a Figma or Miro design artifact.

IMPORTANT: The styling directives below are for your interpretation only. Do NOT render any hex color codes, pixel values, font sizes, or technical CSS specifications as visible text in the image. Only render the data labels, component names, finding IDs, and natural-language text specified in the DATA CONTENT sections.

STYLING DIRECTIVES (interpret these, do not display them):
- Background: clean white
- Severity color mapping: Critical = red, High = orange, Medium = amber/yellow, Low = blue, Clean = emerald green
- Trust zone tints: untrusted = soft warm red tint, application = neutral slate tint, trusted = cool green tint
- Component boxes: rounded corners, subtle drop shadow, white fill, full colored border matching highest severity
- Finding IDs: rendered as individual pill badges with severity-colored background and white text
- Data flow arrows: smooth curved arrows, colored by highest severity on that path
- Layout: 16:9 landscape, professional spacing between components

DATA CONTENT (render this as visible text):

TITLE: "WellnessBank Mobile Banking Application — Residual Risk Architecture (2026-04-29)"
SUBTITLE: "31 Residual Findings | 9 High | 20 Medium | 2 Low | OWASP Mobile Top 10:2024"

TRUST ZONES (4 zones, render as labeled colored regions):
- User Zone (untrusted): Mobile Banking Customer [High border — S-5, R-3]
- Device Zone (semi-trusted): WellnessBank Android Client [High border — T-4, I-4, I-2], WellnessBankDebugActivity [High border — E-1], MoneyTransferActivity [High border — E-2, T-3], WellnessAnalyticsSDK [Medium border — T-1], WellnessPaySDK [Medium border — T-2, I-6], WellnessBankLocalDB [Medium border — T-5, I-3, D-3], WellnessBankCredentialCache [High border — I-7, T-6]
- Backend Zone (trusted): WellnessBank Backend API [High border — D-2], BackendUserAccountStore [clean border]
- External Services (untrusted): Third-Party Analytics Provider [clean border], Third-Party Payment Provider [clean border]

DATA FLOWS (colored arrows):
- Mobile Banking Customer → MoneyTransferActivity: "Intent Extras" — orange (High)
- Mobile Banking Customer → WellnessBank Android Client: "Login Credentials" — orange (High)
- Mobile Banking Customer → WellnessBankDebugActivity: "adb debug bypass" — gray
- MoneyTransferActivity → WellnessBank Android Client: "Money-Movement Request" — orange (High)
- WellnessBank Android Client → WellnessBankCredentialCache: "Auth Token" — orange (High)
- WellnessBankCredentialCache → WellnessBank Android Client: "Restored Credentials" — orange (High)
- WellnessBankDebugActivity → WellnessBank Android Client: "Privileged Action" — orange (High)
- WellnessBankLocalDB → WellnessBank Android Client: "Cached Account Data" — orange (High)
- WellnessBank Android Client → WellnessBankLocalDB: "Account Snapshot" — yellow (Medium)
- WellnessBank Android Client → WellnessBank Backend API: "Transaction Request" — yellow (Medium)
- WellnessBank Backend API → WellnessBank Android Client: "Transaction Response" — orange (High)
- WellnessBank Android Client → WellnessAnalyticsSDK: "Analytics Event" — yellow (Medium)
- WellnessAnalyticsSDK → Third-Party Analytics Provider: "Telemetry Payload" — gray
- WellnessBank Android Client → WellnessPaySDK: "Payment Initiation" — gray
- WellnessPaySDK → Third-Party Payment Provider: "Payment Auth Request" — gray
- Third-Party Payment Provider → WellnessPaySDK: "Payment Confirmation" — gray
- WellnessPaySDK → WellnessBank Android Client: "Payment Result" — orange (High)
- WellnessBank Backend API → BackendUserAccountStore: "Account Read/Write" — gray
- BackendUserAccountStore → WellnessBank Backend API: "Account Record" — yellow (Medium)

FINDING LEGEND: Top 5 High findings as badge entries:
"E-1" (High) — WellnessBankDebugActivity — Debug Activity bypasses authentication
"E-2" (High) — MoneyTransferActivity — External app commands can initiate fund transfers
"T-3" (High) — MoneyTransferActivity — Intent hijacking into money-movement flow
"T-4" (High) — WellnessBank Android Client — No code obfuscation or tampering detection
"I-4" (High) — WellnessBank Android Client — Weak PIN cryptography

FOOTER: "Generated by Tachi Threat Modeling Framework — STRIDE + AI Threat Analysis" in small gray text, centered.

The overall impression should be a polished, authoritative architecture diagram with a complete reference legend — the kind you'd see in a professional security audit deliverable. Prioritize readability — component names, finding IDs, and legend entries must be legible. No hex codes, color values, or technical specifications should appear as visible text. Every element should feel intentionally designed.
