<!--
File: case-study-template.md
Description: Self-serve template for tachi adopters to share a production case study. Required production-use fields + optional rich fields + a required consent block (default-deny publication).
Author/Agent: senior-backend-engineer (Feature 305 — Adoption Signal Capture)
Created: 2026-06-01
Last Updated: 2026-06-01
-->

# tachi Adopter Case Study — Submission Template

Thanks for running tachi in the real world. This template is the self-serve way to share how you use it. Copy it, fill in the sections, and submit it one of two ways:

- **Open a pull request** adding your filled-in copy under `docs/adopters/` (the maintainer lists accepted studies in [the adopters index](./README.md)), **or**
- **Post it** in the [**In the Wild**](https://github.com/davidmatousek/tachi/discussions/categories/in-the-wild) Discussions category.

Everything identifying is **opt-in**. The **Consent block** at the bottom controls what (if anything) gets published with your name on it. If you skip the consent block, nothing identifying is published — see [Consent & publication](#consent--publication).

<!--
HOW TO USE THIS TEMPLATE
- Required sections: fill all five. They are what convey production use.
- Optional sections: include only what you want to share.
- Consent block: required. Absent an explicit "yes", nothing identifying is published (default-deny).
- Keep it factual. No need for marketing language — a plain description of your setup and what you observed is exactly what's useful.
-->

---

## Required

### 1. Adopter org / identifier *(required)*

<!-- Your organization or a stable identifier. You may use an anonymized identifier (e.g., "a mid-size fintech security team") if your consent grant below says "anonymized". -->

_Your answer:_

### 2. Scale of use *(required)*

<!-- How much you run tachi. e.g., team size, number of repos/architectures modeled, scan frequency (per-PR, weekly, ad hoc). -->

_Your answer:_

### 3. Integration point *(required)*

<!-- Where tachi runs in your workflow. e.g., locally during design, in CI, as a pre-merge gate, during architecture review. -->

_Your answer:_

### 4. Capabilities used *(required)*

<!-- Which tachi commands / agents / outputs you rely on. e.g., /tachi.threat-model, the STRIDE + LLM agents, SARIF export, /tachi.risk-score, compensating-controls, the PDF report. -->

_Your answer:_

### 5. Outcomes *(required)*

<!-- What you observed. Qualitative is completely fine. e.g., findings surfaced that SAST missed, faster design review, a logic-level risk caught before merge. -->

_Your answer:_

---

## Optional

### Logo *(optional)*

<!-- Link or attach your logo. Used only if your consent grant permits "use logo? yes". -->

_Your answer:_

### Pull-quote *(optional)*

<!-- A short, attributable quote we may display alongside your study. -->

_Your answer:_

### Public-reference link *(optional)*

<!-- A blog post, slide deck, talk, or video where you discuss your usage. The strongest credibility anchor if you have one. -->

_Your answer:_

---

## Consent & publication

**Required.** This block records your permission *at submission*, so nothing is assumed after the fact. The default is **non-publication**: absent an explicit `yes`, no identifying field is published. You can grant an anonymized listing without revealing your name.

<!-- Replace the bracketed placeholder in each line with your choice. -->

- **(a) May we publish your org name?** `[ yes / anonymized / no ]`
  <!-- "anonymized" = list the study without naming you (e.g., "a healthcare platform team"). Unanswered is treated as "no". -->
- **(b) May we use your logo?** `[ yes / no ]`
  <!-- Unanswered is treated as "no". -->
- **(c) Preferred attribution + how to reach you:** `[ free text — name/handle to credit, and a contact for follow-up questions ]`
  <!-- Unanswered means no attribution is applied. -->

> **Default-deny:** if a prompt is left blank or set to `no`, that identifying detail is **not** published. An anonymized study is still welcome and valuable.

---

<!-- Maintainer note: accepted studies are listed in ./README.md strictly per the consent grant above (name or anonymized; logo only if granted). The submitter's contact details are never published. -->
