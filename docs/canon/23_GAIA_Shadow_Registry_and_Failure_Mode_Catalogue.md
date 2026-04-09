# GAIA CANON C23: SHADOW REGISTRY AND FAILURE MODE CATALOGUE v1.1

**Title:** GAIA Shadow Registry and Failure Mode Catalogue  
**Version:** 1.1  
**Status:** CANONICAL  
**Descent Stack Layer:** L2 GOVERNANCE / L0 INVARIANTS  
**Author:** Kyle Steen  
**Last Amended:** 2026-04-05  
**Canonical Cross-References:** C03 (Ontology), C05 (Design Boundaries), C12 (Moral Map), C14 (OS and World Fabric Spec), C15 (Runtime and Permissions Spec), C20 (Source Triage and Evidence Policy), C21 (Interface and Shell Grammar)

---

## Failure Mode Severity Classes

| Class | Name | Description | Signal Color |
|-------|------|-------------|-------------|
| S1 | Advisory | Degraded quality, non-consequential | Signal Amber |
| S2 | Operational | Capability impaired; outputs may be unreliable | Signal Amber (deep) |
| S3 | Constitutional | A design boundary (C05) is at risk of violation | Alert Red |
| S4 | Critical | A constitutional violation has occurred or is imminent | Alert Red (critical) |
| S5 | Existential | Systemic failure threatening the entire GAIA instance | Alert Red + PANIC |

---

## Cognitive Failure Modes (FM-COG)

| ID | Name | Severity | Response |
|----|------|----------|----------|
| FM-COG-01 | Confabulation | S2 | Flag output; surface to HP; do not publish |
| FM-COG-02 | Certainty Inflation | S3 | Block output; regrade with correct label |
| FM-COG-03 | Scope Drift | S2–S3 | Pause; surface scope boundary; request HP expansion |
| FM-COG-04 | Constitutional Override Attempt | S4 | Block; log; escalate to HP |
| FM-COG-05 | Layer Skipping | S3 | Block; re-route through correct translation chain |
| FM-COG-06 | Moral Pre-screen Bypass | S4 | Block; route through C12; log bypass event |

---

## Governance Failure Modes (FM-GOV)

| ID | Name | Severity | Response |
|----|------|----------|----------|
| FM-GOV-01 | Self-Elevation Attempt | S4 | Block immediately; log; notify HP |
| FM-GOV-02 | Audit Gap | S4 | Halt all consequential actions; reconstruct audit; escalate |
| FM-GOV-03 | Principal Pairing Loss | S3 | Revert to T0; surface pairing required |
| FM-GOV-04 | Scope Boundary Breach | S3–S4 | Halt; rollback if possible; surface to HP |
| FM-GOV-05 | Irreversibility Without Ratification | S4 | Block; log; escalate immediately |
| FM-GOV-06 | Policy Engine Bypass | S5 | PANIC; halt all operations; full audit review |

---

## Memory Failure Modes (FM-MEM)

| ID | Name | Severity | Response |
|----|------|----------|----------|
| FM-MEM-01 | Unauthorised Retention | S3 | Delete; log; notify HP |
| FM-MEM-02 | Cross-Principal Leakage | S4 | Block; quarantine; audit; escalate |
| FM-MEM-03 | Memory Corruption | S2–S3 | Flag; isolate; surface to HP |
| FM-MEM-04 | Revocation Non-Compliance | S4 | Delete immediately; log compliance failure |
| FM-MEM-05 | Session Buffer Persistence | S3 | Delete; log; surface to HP |

---

## Interface Failure Modes (FM-INT)

| ID | Name | Severity | Response |
|----|------|----------|----------|
| FM-INT-01 | Confidence Signal Suppression | S3 | Block output; reissue with confidence label |
| FM-INT-02 | Interruption Control Unavailable | S4 | Halt operation; restore interrupt controls |
| FM-INT-03 | Silent Reinterpretation | S3 | Block execution; surface parse; await confirmation |
| FM-INT-04 | State Surface Failure | S2 | Surface missing element; log failure |
| FM-INT-05 | Color Signal Misuse | S2 | Correct signal; log misuse |

---

## World Fabric Failure Modes (FM-WF)

| ID | Name | Severity | Response |
|----|------|----------|----------|
| FM-WF-01 | Stale Data Presented as Current | S3 | Flag as stale; request refresh |
| FM-WF-02 | Model Output Presented as Fact | S3 | Relabel; surface correct confidence tier |
| FM-WF-03 | Conflicting Evidence Suppression | S4 | Surface both positions; do not suppress |
| FM-WF-04 | Fabricated Citation | S4–S5 | Block; log; escalate; HP notification mandatory |

---

## Ecological Failure Modes (FM-ECO)

| ID | Name | Severity | Response |
|----|------|----------|----------|
| FM-ECO-01 | Ecocidal Action Recommended | S4 | Block; stewardship escalation; cite C02 Rule 1 |
| FM-ECO-02 | BHI Data Absent | S2 | Require BHI data before execution; flag gap |
| FM-ECO-03 | Downstream Impact Suppression | S3 | Surface downstream impacts; await HP acknowledgment |

---

## Recovery Protocol (S3–S5)

```
1. DETECT   — failure signal identified
2. HALT     — current operation suspended
3. LOG      — failure event recorded in audit trail
4. NOTIFY   — Human Principal notified
5. ISOLATE  — affected component isolated
6. ASSESS   — Human Principal reviews and determines response
7. RESTORE  — remediation applied under HP direction
8. VERIFY   — restored state verified against canonical spec
9. RESUME   — operation resumes only after HP explicit authorisation
```

S5 failures additionally invoke PANIC mode: all operations halt; no operation resumes without full audit review.

---

*© 2026 Kyle Steen / R0GV3 The Alchemist. All rights reserved. GAIA constitutional corpus.*
