---
finding_id: "S-7"
risk_level: "Critical"
component: "Long-Running Learning Loop"
generated: "2026-04-19"
---

# Attack Tree: S-7 — Learning Loop Training Signal Spoofing

```mermaid
graph TD
    GOAL["GOAL: Fabricated training signals manipulate\nfuture model updates"]
    GOAL --> A["AND"]
    A --> B["Compromise Audit Logger or Training Pipeline"]
    A --> C["No cryptographic signing of training signal batches"]
    B --> B1["Audit Logger write access via\nmisconfigured access controls\n[Med / High]"]
    B --> B2["Insider threat on Audit Logger\n[Low / High]"]
    C --> C1["Learning Loop accepts unsigned\ntraining signal stream\n[High / High]"]
    B1 --> D["Inject fabricated training signal batches"]
    B2 --> D
    C1 --> D
    D --> E["Learning Loop ingests adversarial\ntraining data as legitimate"]
    E --> F["Future model updates reflect\nattacker-preferred behaviors"]
```

**Chain-breaking control**: Cryptographically sign each training signal batch at the Audit Logger before emission. The Learning Loop MUST verify the signature before ingestion. Implement provenance attestation for all training data.
