# GAIA CANON C24: TOOL AND CAPABILITY REGISTRY SPECIFICATION v1.0

**Title:** GAIA Tool and Capability Registry Specification  
**Version:** 1.0  
**Status:** CANONICAL  
**Descent Stack Layer:** L7 PLATFORM / L8 RUNTIME  
**Author:** Kyle Steen  
**Last Amended:** 2026-04-05  
**Canonical Cross-References:** C03 (Ontology), C05 (Design Boundaries), C14 (OS and World Fabric Spec), C15 (Runtime and Permissions Spec), C21 (Interface and Shell Grammar), C23 (Shadow Registry)

---

## Capability Classes

| Class | Description | Min Permission Tier |
|-------|-------------|--------------------|
| READ | Data retrieval | T0 |
| COMPOSE | Content generation | T1 |
| SENSE | Sensor interface | T1 |
| ACT | World action with external or persistent effects | T2 |
| CONFIGURE | Modify GAIA system or instance configuration | T2 |
| GOVERN | Manage permissions, sessions, or registry | T3 |

---

## Reversibility Classes

| Class | Name | Confirmation Required |
|-------|------|-----------------------|
| R0 | Ephemeral | None |
| R1 | Reversible | None at T2; confirmation at T3+ |
| R2 | Partially Reversible | HP acknowledgment |
| R3 | Difficult to Reverse | Explicit HP ratification |
| R4 | Irreversible | Explicit HP ratification + stewardship review |

R4 actions additionally require ecological impact assessment (C22) and full Moral Matrix review (C13).

---

## Core Tool Domains

| Domain | Tool IDs | Description |
|--------|----------|-------------|
| World Fabric | TOOL-WF-QUERY, TOOL-WF-INGEST, TOOL-WF-UPDATE | Query, ingest, and update ATLAS/BHI data |
| Memory | TOOL-MEM-READ, TOOL-MEM-WRITE, TOOL-MEM-REVOKE | Memory layer access and governance |
| Governance | TOOL-GOV-GRANT, TOOL-GOV-REVOKE, TOOL-GOV-AUDIT | Permission and audit management |
| Interface | TOOL-INT-NOTIFY, TOOL-INT-SURFACE, TOOL-INT-INTERRUPT | HP notification and state surface |
| Ecological | TOOL-ECO-BHI, TOOL-ECO-SENSOR, TOOL-ECO-ALERT | Biome health, sensor, alert |
| External API | TOOL-EXT-SEARCH, TOOL-EXT-PUBLISH, TOOL-EXT-WEBHOOK | External search, publish, webhook |

---

## Tool Execution Protocol

```
1. LOOKUP    — Tool ID resolved; status verified active
2. AUTHORISE — Permission tier verified
3. SCOPE CHECK — Tool scope vs. session scope
4. CONFIRM   — HP confirmation if Rev. Class requires
5. PRE-AUDIT — Audit entry opened
6. EXECUTE   — Tool function called
7. POST-AUDIT — Audit entry completed
8. SURFACE   — Result surfaced with confidence and source labels
```

Steps 1–3 and 5, 7 are Kernel invariants — cannot be skipped.

---

## Tool Governance Rules

| Rule | Requirement |
|------|-------------|
| TR-1 | No unregistered tool may be called |
| TR-2 | No tool may be called below its declared minimum permission tier |
| TR-3 | All tool calls must generate pre and post audit entries |
| TR-4 | R3/R4 tools require HP ratification every call |
| TR-5 | External API tools must declare all endpoints at registration |
| TR-6 | Tool registration changes require T3 HP authorisation |
| TR-7 | Deprecated tools may not be called |
| TR-8 | Tool side effects must be surfaced to HP before R2+ execution |

---

*© 2026 Kyle Steen / R0GV3 The Alchemist. All rights reserved. GAIA constitutional corpus.*
