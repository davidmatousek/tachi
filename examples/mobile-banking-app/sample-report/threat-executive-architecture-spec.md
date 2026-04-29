---
schema_version: "1.4"
template: "executive-architecture"
date: "2026-04-29"
source_file: "compensating-controls.md"
data_source_type: "compensating-controls"
finding_count: 31
image_generated: false
skip_image: false
---

# Threat Infographic Specification — Executive Architecture

**Project**: WellnessBank Mobile Banking Application
**Template**: Executive Architecture (Portrait)
**Data Source**: compensating-controls.md (residual risk tier)
**Generated**: 2026-04-29

---

## 1. Metadata

| Field | Value |
|-------|-------|
| template_name | executive-architecture |
| tier_source | compensating-controls |
| source_file | /Users/david/Projects/tachi/examples/mobile-banking-app/sample-report/threats.md |
| generation_timestamp | 2026-04-29T12:50:12Z |
| qualifying_layer_count | 4 |
| total_filtered_count | 9 |
| skip_image | false |
| fallback_used | false |
| Project Name | WellnessBank Mobile Banking Application |
| Scan Date | 2026-04-29 |
| Analysis Agents | 8 |
| Total Findings | 31 |
| Risk Posture | Residual risk — 0 Critical and 9 High findings across 12 components |

> **skip_image = false**: 9 qualifying High severity findings exist across 4 layers. Gemini image generation will be attempted.

---

## 2. Architecture Layers

Layers ordered untrusted-first (position 0 at top) per portrait orientation convention.

| Position | Layer Name | Trust Level | Components | Component Count | Overflow |
|----------|-----------|-------------|------------|-----------------|---------|
| 0 | User Zone | Untrusted | Mobile Banking Customer | 1 | — |
| 1 | External Services | Untrusted | Third-Party Analytics Provider, Third-Party Payment Provider | 2 | — |
| 2 | Device Zone | Semi-Trusted | MoneyTransferActivity, WellnessAnalyticsSDK, WellnessBank Android Client, WellnessBankCredentialCache, WellnessBankDebugActivity, WellnessBankLocalDB, WellnessPaySDK | 7 | + 3 more in this layer |
| 3 | Backend Zone | Trusted | BackendUserAccountStore, WellnessBank Backend API | 2 | — |

---

## 3. Threat Callouts

6 callouts selected system-wide using Largest Remainder Method (LRM) allocation with per-layer floor ≥1. Device Zone receives 4 (floor+LRM), User Zone receives 2 (floor+LRM). External Services and Backend Zone receive 0 qualifying callouts (no High findings in those layers).

| # | Layer | Finding ID | Severity | Affected Component | Raw Description | Composite Score |
|---|-------|-----------|----------|-------------------|-----------------|-----------------|
| 1 | User Zone | R-3 | High | Mobile Banking Customer | Deniable Financial Transactions | 7.0 |
| 2 | User Zone | S-5 | High | Mobile Banking Customer | Long-Lived Session Token Replay | 7.0 |
| 3 | Device Zone | E-1 | High | WellnessBankDebugActivity | M8 Privilege-Gain: Exported Debug Activity Bypassing Auth Boundary | 8.5 |
| 4 | Device Zone | E-2 | High | MoneyTransferActivity | Unauthorized Money Transfer via Intent Hijacking and Privilege Escalation | 8.3 |
| 5 | Device Zone | T-3 | High | MoneyTransferActivity | Mobile IPC Input Validation (M4) — Intent Hijacking into Money Movement | 8.1 |
| 6 | Device Zone | T-4 | High | WellnessBank Android Client | Insufficient Mobile Binary Protections (M7) | 7.7 |

> Raw descriptions are retained verbatim for auditability. Gemini rewrites each to ≤25 plain-English words during image rendering.

**Empty-Layer Badges** (layers with zero qualifying High/Critical findings):
- External Services (position 1): 0 High/Critical findings in this layer
- Backend Zone (position 3): 0 High/Critical findings in this layer

---

## 4. Severity Distribution

| Severity | Count (Qualifying) |
|----------|--------------------|
| Critical | 0 |
| High | 9 |
| Total qualifying (Critical + High) | 9 |
| Total after per-layer dedup for callouts | 6 (LRM allocation from 9 qualifying) |

> Medium, Low, and Note findings are excluded from executive architecture callouts per template design.

---

## 5. Visual Layout Directives

- **Orientation**: Portrait (8.5:11 page aspect ratio) — this template is the ONLY tachi infographic in portrait orientation
- **Layer order**: Untrusted layers at top (position 0), trusted layers at bottom (position 3)
  - Position 0: User Zone (pastel #F0F4FF — cool blue-tinted)
  - Position 1: External Services (pastel #FFF4F0 — warm peach-tinted)
  - Position 2: Device Zone (pastel #F0FFF4 — cool green-tinted)
  - Position 3: Backend Zone (pastel #FFF0F8 — cool pink-tinted)
- **Component nodes**: Rounded rectangles with severity-colored borders (High = orange #EA580C; no findings = gray #6B7280)
- **Callout boxes**: Dashed red/orange border (severity color), warning triangle icon, leader line to component node; callout boxes must NOT overlap component nodes
- **Inter-layer arrows**: Explicit directional arrows with arrowheads, top-to-bottom between adjacent layers
- **Empty-layer treatment**: Compact factual badge ("0 High/Critical findings in this layer") — no full-band placeholder
- **Callout NON-OVERLAP**: Callouts positioned in left/right page margins alongside layer bands, not inside bands

---

## 6. Gemini Prompt Construction Notes

**Template**: executive-architecture (FR-212-6 verbatim-lock rule applies)

**Slot substitutions**:

`<<project_name>>` = WellnessBank Mobile Banking Application

`<<layer_block>>`:
```
Layer 0 (top) — User Zone [pastel fill: cool blue-tinted]:
  Components: Mobile Banking Customer [orange border — High findings S-5, R-3]

Layer 1 — External Services [pastel fill: warm peach-tinted]:
  Components: Third-Party Analytics Provider [gray border — no qualifying findings], Third-Party Payment Provider [gray border — no qualifying findings]

Layer 2 — Device Zone [pastel fill: cool green-tinted]:
  Components: MoneyTransferActivity [orange border — High findings E-2, T-3], WellnessAnalyticsSDK [gray border], WellnessBank Android Client [orange border — High findings T-4, I-4, I-2], WellnessBankCredentialCache [orange border — High finding I-7], WellnessBankDebugActivity [orange border — High finding E-1], WellnessBankLocalDB [gray border], WellnessPaySDK [gray border]
  Note: +3 additional components in this layer

Layer 3 (bottom) — Backend Zone [pastel fill: cool pink-tinted]:
  Components: BackendUserAccountStore [gray border — no qualifying findings], WellnessBank Backend API [gray border — no qualifying findings]
```

`<<callout_block>>`:
```
Callout 1: Finding R-3 [High — orange dashed border] anchored to Mobile Banking Customer (User Zone)
  Raw: "Deniable Financial Transactions"
  Rewrite to ≤25 words: Attacker could deny initiating any bank transfer — the app stores no cryptographic proof of the customer's intent.

Callout 2: Finding S-5 [High — orange dashed border] anchored to Mobile Banking Customer (User Zone)
  Raw: "Long-Lived Session Token Replay"
  Rewrite to ≤25 words: A stolen login token never expires — anyone who obtains it could log in indefinitely without the customer's knowledge.

Callout 3: Finding E-1 [High — orange dashed border] anchored to WellnessBankDebugActivity (Device Zone)
  Raw: "M8 Privilege-Gain: Exported Debug Activity Bypassing Auth Boundary"
  Rewrite to ≤25 words: A developer test screen was accidentally left in the app — anyone with a USB cable can execute banking operations without logging in.

Callout 4: Finding E-2 [High — orange dashed border] anchored to MoneyTransferActivity (Device Zone)
  Raw: "Unauthorized Money Transfer via Intent Hijacking and Privilege Escalation"
  Rewrite to ≤25 words: Any other app on the same phone could silently send money on the customer's behalf without asking for a PIN.

Callout 5: Finding T-3 [High — orange dashed border] anchored to MoneyTransferActivity (Device Zone)
  Raw: "Mobile IPC Input Validation (M4) — Intent Hijacking into Money Movement"
  Rewrite to ≤25 words: A malicious co-installed app could hijack the money-transfer screen by sending it fake instructions, triggering unauthorized fund transfers.

Callout 6: Finding T-4 [High — orange dashed border] anchored to WellnessBank Android Client (Device Zone)
  Raw: "Insufficient Mobile Binary Protections (M7)"
  Rewrite to ≤25 words: The app's code is unprotected — an attacker could reverse-engineer it in minutes to extract credentials and bypass security controls.
```

`<<empty_layer_block>>`:
```
External Services (position 1): 0 High/Critical findings in this layer
Backend Zone (position 3): 0 High/Critical findings in this layer
```

`<<flow_edges_block>>`:
```
BackendUserAccountStore → WellnessBank Backend API [data: Account Record, protocol: Internal DB]
Mobile Banking Customer → MoneyTransferActivity [data: Intent Extras (External App or Shell), protocol: Android Intent]
Mobile Banking Customer → WellnessBank Android Client [data: Login Credentials (UI Input), protocol: In-app UI]
Mobile Banking Customer → WellnessBankDebugActivity [data: adb shell am start (Debug Activity Bypass), protocol: ADB / Intent]
MoneyTransferActivity → WellnessBank Android Client [data: Money-Movement Request, protocol: Internal Android IPC]
Third-Party Payment Provider → WellnessPaySDK [data: Payment Confirmation, protocol: HTTPS]
WellnessAnalyticsSDK → Third-Party Analytics Provider [data: Telemetry Payload, protocol: HTTPS]
WellnessBank Android Client → WellnessAnalyticsSDK [data: Analytics Event, protocol: In-process]
WellnessBank Android Client → WellnessBank Backend API [data: Transaction Request, protocol: HTTPS]
WellnessBank Android Client → WellnessBankCredentialCache [data: Username + Auth Token, protocol: Internal Android IPC]
WellnessBank Android Client → WellnessBankLocalDB [data: Account Snapshot + Recent Transactions, protocol: Local SQLite]
WellnessBank Android Client → WellnessPaySDK [data: Payment Initiation, protocol: In-process]
WellnessBank Backend API → BackendUserAccountStore [data: Account Read / Write, protocol: Internal DB]
WellnessBank Backend API → WellnessBank Android Client [data: Transaction Response, protocol: HTTPS]
WellnessBankCredentialCache → WellnessBank Android Client [data: Restored Credentials on App Launch, protocol: Internal Android IPC]
WellnessBankDebugActivity → WellnessBank Android Client [data: Privileged Action without Auth Boundary, protocol: Internal Android IPC]
WellnessBankLocalDB → WellnessBank Android Client [data: Cached Account Data, protocol: Local SQLite]
WellnessPaySDK → Third-Party Payment Provider [data: Payment Authorization Request, protocol: HTTPS]
WellnessPaySDK → WellnessBank Android Client [data: Payment Result, protocol: In-process]
```

`<<clusters_block>>`:
```
Backend Zone (trusted): BackendUserAccountStore, WellnessBank Backend API
Device Zone (semi-trusted): MoneyTransferActivity, WellnessAnalyticsSDK, WellnessBank Android Client, WellnessBankCredentialCache, WellnessBankDebugActivity, WellnessBankLocalDB, WellnessPaySDK
External Services (untrusted): Third-Party Analytics Provider, Third-Party Payment Provider
User Zone (untrusted): Mobile Banking Customer
```

`<<single_zone_caption>>` = (empty — 4 layers exist, no single-zone fallback needed)

**Full Gemini prompt** uses FR-212-6 verbatim-locked block from `.claude/skills/tachi-infographics/references/executive-architecture.md` with the above slot substitutions. See that file for the exact locked text between `=== BEGIN VERBATIM PROMPT BLOCK ===` and `=== END VERBATIM PROMPT BLOCK ===` markers.
