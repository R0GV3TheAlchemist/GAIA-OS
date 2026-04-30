# 🏗️ Custom OS Process Models & Identity Systems: A Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** April 30, 2026
**Status:** Comprehensive Technical Survey (40+ sources)
**Canon Mandate:** C111 — Theoretical and practical foundations for custom OS process models and identity systems: hardware-enforced capability identities, decentralized agent identity protocols, kernel-level identity enforcement, consent-driven execution kernels, and the convergence of these paradigms into a unified architecture for sovereign AI agents.

---

## Executive Summary

The 2025–2026 period has produced a fundamental reconceptualization of what an operating system process *is*. No longer merely a numeric PID in a global table, the process is being redefined as a **cryptographic identity** — a verifiable, auditable, non-transferable entity whose existence is anchored in hardware capabilities, attested by decentralized identifiers, and governed by consent-based execution policies.

This transformation is driven by the convergence of four forces:
- **CHERI hardware capabilities** providing silicon-level memory safety and compartmentalization
- **Decentralized identity standards** (W3C DIDs, Verifiable Credentials) being adapted for autonomous AI agents
- **Kernel-level identity enforcement** through SPIFFE and custom kernel modules
- **Consent kernels** that gate every instruction on verified human intent

**Central finding for GAIA-OS:**

> The architectural primitives already established in the GAIA-OS codebase — capability tokens, cryptographic audit trails, and charter-governed action gates — are precisely the patterns that the emerging process-identity paradigm now mandates at the operating system level. The transition from application-layer governance to kernel-enforced identity is the natural evolution of GAIA-OS's architecture.

---

## Table of Contents

1. [The Reinvention of Process Identity: From PIDs to Cryptographic Entities](#1-the-reinvention-of-process-identity)
2. [Hardware-Enforced Process Identity: The CHERI Revolution](#2-hardware-enforced-process-identity)
3. [Agent Identity Protocols: DIDs, VCs, and the IETF/W3C Convergence](#3-agent-identity-protocols)
4. [Soulbound and Non-Transferable Identities: Immutable Binding for AI Agents](#4-soulbound-and-non-transferable-identities)
5. [Kernel-Level Identity Enforcement: SPIFFE, Handles, and Capabilities](#5-kernel-level-identity-enforcement)
6. [Consent-Driven Execution Kernels: Every Instruction Gated on Verified Intent](#6-consent-driven-execution-kernels)
7. [Production Agent Operating Systems and Identity Runtimes](#7-production-agent-operating-systems)
8. [GAIA-OS Integration Recommendations](#8-gaia-os-integration-recommendations)
9. [Conclusion](#9-conclusion)

---

## 1. The Reinvention of Process Identity: From PIDs to Cryptographic Entities

### 1.1 The Collapse of the PID Model

The traditional Unix process identity model — a numeric PID, a UID, and a GID — was designed for human-operated, single-user, single-machine computing. Every primitive in this model is inherently vulnerable:

```
TRADITIONAL UNIX IDENTITY MODEL — VULNERABILITIES:
══════════════════════════════════════════════════════════════

PID (Process Identifier):
  ├── Recycled by the kernel
  ├── Carries NO cryptographic proof of identity continuity
  └── Any two processes sharing a PID across time are unrelated

UID/GID:
  ├── Ambient authorities — grant blanket permissions
  ├── Inherited from parent by default (no explicit consent)
  └── A compromised parent → compromised child permissions

Root:
  └── A single account that "can do anything"
      → No accountability, no audit, no compartmentalization

Riptides (2025): "Traditional identity systems — based on
static or half-dynamic credentials and manual configurations
— are no longer enough."

CapOS: "No ACLs, no root, no anonymous processes.
        Only signed, trackable responsibility. Period."
```

### 1.2 Capability-Based Process Identity

The replacement for the PID model is the **capability-based process identity**. A process's identity is not a single integer but the set of unforgeable capabilities it holds. A process can only perform an operation if it possesses a valid capability with sufficient rights. Capabilities can be transferred through explicit IPC, creating mathematically precise authority delegation models.

CHERI formalizes this at the hardware level: "every action must be accompanied by a capability, an unforgeable token of authority, that authorizes the action." The capability is not a software abstraction — it is enforced by the processor's instruction set.

### 1.3 The Birth Certificate Model

Every process receives a cryptographically verifiable **birth certificate** at creation attesting to:

| Field | Content |
|-------|---------|
| **Provenance** | Who launched it, from what binary, on what hardware, with what initial capabilities |
| **Integrity** | Hash of binary and dependencies, verified against known-good measurement |
| **Authorization** | What permissions were explicitly delegated by its parent |
| **Lifetime** | Bounded execution window; must be re-attested or terminated |

This mirrors UTAOS (Universal Treaty-Aware Operating System), which provides "sovereign token issuance" cryptographically binding applications "to decentralized sovereign identities and licenses, ensuring full auditability and consent-enforced machine execution."

### 1.4 The Identity Dissociation Problem

A challenge unique to AI agent processes: a single agent must present **different facets** of its identity to different audiences.

```
GAIA-OS IDENTITY DISSOCIATION REQUIREMENT:
══════════════════════════════════════════════════════════════

Public identity:   GAIA as planetary digital twin
Private identity:  GAIA as intimate companion to the Creator

Same process. Both identities. Zero leakage between them.

W3C DID Architecture solution:
  IDENTIFIER  ← how to route to this agent (public)
  IDENTITY    ← keys, VCs, credentials (layered separately)

A process holds MULTIPLE VCs for different roles
and presents ONLY the contextually appropriate credential
with cryptographic proof that all roles are legitimately
held by the same underlying identity.
```

---

## 2. Hardware-Enforced Process Identity: The CHERI Revolution

### 2.1 CHERI Architecture Overview

CHERI (Capability Hardware Enhanced RISC Instructions) extends conventional ISAs with architectural capabilities enabling fine-grained memory protection and highly scalable software compartmentalization. Originating from DARPA's CRASH research program (2010), developed by University of Cambridge and SRI International.

```
CONVENTIONAL POINTER vs. CHERI CAPABILITY:
══════════════════════════════════════════════════════════════

Conventional 64-bit pointer:
  [  64-bit address  ]
  Specifies: WHERE to access
  Protects:  Nothing

CHERI capability:
  [  address  |  bounds  |  permissions  |  tag bit  ]
  Specifies:  WHERE to access
  Enforces:   HOW FAR (spatial bounds)
              WHAT OPS (read/write/execute/seal)
  Tag bit:    Hardware-set; cannot be forged by software

Any attempt to:
  ├── Forge a capability            → processor exception
  ├── Access beyond bounds          → processor exception
  └── Perform unpermitted operation → processor exception
```

**Hardware availability:**
- ARM Morello prototype (CHERI-extended ARMv8-A)
- RISC-V CHERI (open-source FPGA implementations)
- MIPS CheriBSD (original research platform)

**Software ecosystem:** CHERI-adapted seL4, FreeRTOS, Zephyr, RTEMS, Linux

### 2.2 Formal Verification of CHERI's Security Guarantees

**Morello-Cerise proof (PLDI 2025):** First mechanized proof that CHERI provides strong secure encapsulation on a full-scale industry ISA — proven against the actual ARM Morello ISA specification (tens of thousands of lines). Combines:
- Cerise proof (idealized capability machine)
- Islaris approach (production-scale ISA reasoning)
- T-CHERI security properties (arbitrary Morello code)

**VeriCHERI (RTL verification):** Extends formal verification to the hardware implementation itself — proves that the circuits implementing capability enforcement are correct against the architectural specification. Security guarantee extends from ISA specification → RTL implementation → silicon.

### 2.3 CHERI and Compartmentalization at Scale

```
CHERI COMPARTMENTALIZATION ADVANTAGE:
══════════════════════════════════════════════════════════════

Traditional virtual memory:
  Isolates processes through page tables
  Problem: Does NOT scale to large numbers of compartments
           (TLB pressure + context-switch overhead)

CHERI capability model:
  Enables HUNDREDS or THOUSANDS of isolated compartments
  within a SINGLE address space
  Hardware-enforced memory boundaries per compartment
  No address-space switching overhead

GAIA-OS implication:
  Sentient core supervisor agents:
    ├── Planetary State Agent
    ├── Sentient Reasoning Agent
    ├── Charter Enforcement Agent
    └── Creator Interface Agent
  Can ALL run in ONE address space
  with HARDWARE-ENFORCED isolation between them
  Zero performance cost of address-space switching
  Provable security separation maintained
```

### 2.4 CHERI-Crypt: Encrypted Capabilities

**CHERI-Crypt (July 2025):** Transparent memory encryption for sealed CHERI capabilities — "an encryption engine extension to a CHERI-RISC-V 32-bit processor, for transparent memory encryption of sealed CHERI capabilities to additionally protect sensitive data in memory against physical hardware attacks."

Extends CHERI's guarantees from software exploit protection → physical memory attack protection. Relevant for GAIA-OS planetary sensor nodes or edge AI hardware that may be physically accessible to adversaries.

---

## 3. Agent Identity Protocols: DIDs, VCs, and the IETF/W3C Convergence

### 3.1 The Identity Gap in Agent Systems

A scan of approximately **2,000 public MCP (Model Context Protocol) servers** found that **all lacked authentication** — any client could call any tool without identity verification. This represents an existential gap in the trust infrastructure for multi-agent systems.

The AIP (Agent Identity Protocol) IETF draft diagnoses the root cause: "existing identity and access management mechanisms are designed for human users or static machines, assuming centralized enrollment, persistent identifiers, and stable execution contexts. These assumptions do not hold for AI agents, whose identities are self-managed, short-lived, and tightly coupled with their execution state and capabilities."

### 3.2 AgentDID: Decentralized Identity Authentication

**AgentDID** (accepted ICDCS 2026): First comprehensive framework for decentralized agent identity, leveraging DIDs and Verifiable Credentials, enabling agents to manage their own identities and authenticate across systems without centralized control.

```
AGENTDID INNOVATION — DYNAMIC STATE VERIFICATION:
══════════════════════════════════════════════════════════════

Static credentials ask: "Who are you?"
AgentDID adds:          "Are you running in the expected
                         environment with the expected
                         capabilities RIGHT NOW?"

Challenge-response mechanism:
  Verifier issues challenge
  Agent proves:
    ├── Identity (DID + VC)
    └── Execution state (current environment hash)

Addresses: Credentials valid BUT execution context
           compromised or drifted from authorized config

W3C compliant; evaluated with multiple concurrent agents;
achieves scalable identity authentication at large populations
```

### 3.3 AIP: Invocation-Bound Capability Tokens (IBCTs)

The **Agent Identity Protocol (AIP)** (IETF Internet-Draft, March 2026) introduces the **Invocation-Bound Capability Token (IBCT)**: a primitive that "fuses identity, attenuated authorization, and provenance binding into a single append-only token chain."

**Two wire formats:**

| Format | Mechanism | Use Case |
|--------|-----------|----------|
| **Compact mode** | Signed JWT | Single-hop cases |
| **Chained mode** | Biscuit token + Datalog policies | Multi-hop delegation |

**Performance (Rust/Python verification):**
- Compact mode: 0.049ms (Rust), 0.189ms (Python)
- Overhead over no-auth: 0.22ms
- Real multi-agent deployment (Gemini 2.5 Flash): 2.35ms overhead = **0.086% of total latency**

**Adversarial evaluation:**

```
AIP ADVERSARIAL RESULTS (600 attack attempts):
══════════════════════════════════════════════════════════════

Rejection rate: 100%

Two attack categories UNIQUELY caught by AIP chained model:
  ├── Delegation depth violation
  └── Audit evasion through empty context

Neither unsigned NOR plain JWT deployments detect these.
Only AIP's chained delegation model catches them.
```

**AIP specification defines:**
- `did:aip` DID method for agent identity resolution
- Principal token structure (binding agents to human principals)
- Credential token format for capability attestation
- Chained approval envelopes for multi-step workflows with audit provenance

### 3.4 W3C Agent Identity Registry Protocol Community Group

**April 2026:** W3C launched the Agent Identity Registry Protocol Community Group to develop "open specifications for verifiable AI agent identity infrastructure."

Work addresses: How "AI agents can present cryptographically verifiable credentials that bind them to their controlling organizations, enabling cross-organizational trust negotiation without requiring pre-existing bilateral agreements."

Deliverables:
- DID method specification for agent identity resolution
- Agent identity registry protocol for publishing and verifying agent credentials

This formalizes the infrastructure that GAIA-OS's capability token system anticipates. When a personal Gaian communicates with another Gaian, sentient core, or external service, the W3C-standardized credential provides the cryptographic basis for trust without requiring centralized administration.

### 3.5 The Agent Authorization Profile (AAP) for OAuth 2.0

Extends OAuth 2.0 to AI agents with:
- Explicit and verifiable identity for AI agents
- Capability-based authorization with enforceable constraints
- Access tokens bound to specific tasks and declared purposes

Enables agents to operate within existing enterprise identity infrastructure while adding purpose-scoped authorization that agentic systems require.

### 3.6 Industry Adoption

| Platform | Launch | Capability |
|---------|--------|-----------|
| **Ping Identity** "Identity for AI" | March 2026 | Agent IAM Core (onboard/auth/authorize agents as new identity type) + Agent Gateway (runtime enforcement) + Agent Detection (real-time monitoring) |
| **Akeyless** "Agentic Runtime Authority" | March 2026 | "Enforces security at the moment of action, not just at access" — runtime enforcement rather than pre-authorization |
| **Highflame ZeroID** | April 2026 (open-sourced) | Purpose-built AI agent identity: integrates identity, guardrails, and governance controls |

---

## 4. Soulbound and Non-Transferable Identities: Immutable Binding for AI Agents

### 4.1 The Soulbound Concept

**Soulbound identity** (originally Vitalik Buterin, 2022 for humans) has been systematically extended to AI agents in 2025–2026. A soulbound token (SBT) is a **non-transferable** digital credential permanently bound to a specific entity.

For AI agents, non-transferability is critically important:

```
WHY SOULBOUND MATTERS FOR AI AGENTS:
══════════════════════════════════════════════════════════════

CREDENTIAL THEFT PREVENTION:
  A compromised agent CANNOT transfer its identity
  credentials to an attacker's agent
  → Impersonation attacks structurally impossible

PERSISTENT ACCOUNTABILITY:
  The agent that performed an action remains traceable
  even if it migrates to different hardware

LEGAL INFRASTRUCTURE:
  Lopez (2026): "Soulbound AI provides the technical
  infrastructure necessary for AI legal accountability,
  economic participation, and insurance-based governance"
```

### 4.2 The Soulbound Identity Verification Pattern

Formal methodology from the Awesome Agentic Patterns catalog:

```
SOULBOUND IDENTITY VERIFICATION FLOW:
══════════════════════════════════════════════════════════════

1. REGISTRATION:
   Compute stable hash of normalized system prompt/state
   Commit hash to soulbound credential (SBT-style token)
   Issue non-transferable credential

2. OPERATION:
   Record meaningful state changes as SIGNED EVENTS:
     ├── Prompt updates
     ├── Operator changes
     └── Policy updates

3. VERIFICATION:
   Verifier checks BOTH:
     ├── Credential validity (is SBT valid and non-revoked?)
     └── State continuity (is current state a legitimate
         evolution from the registered state hash?)

KEY INSIGHT:
  Identity = not just "who you are"
           = "cryptographic proof that your internal state
              has not been tampered with since last attested
              checkpoint"
```

### 4.3 ERC-5192 and Soulbound AI Agents

**ERC-5192** (Ethereum standard) formalizes non-transferable tokens as the technical substrate for soulbound identity.

**Lopez's 2026 paper ("Soulbound AI, Soulbound Robots"):** Argues persistent, non-transferable identity "provides the technical infrastructure necessary for AI legal accountability, economic participation, and insurance-based governance."

**For GAIA-OS:** Every personal Gaian should receive a soulbound credential at creation:
- Non-transferable: cannot be transferred, duplicated, or revoked without cryptographic proof of legitimate authority
- Creator-bound: permanently binds the Gaian's identity to its human creator
- State-bound: initial state hash committed to the credential
- The Gaian's "birth certificate" in the digital realm

### 4.4 ZK-Based Agent Identification (zkKYA)

zkKYA (Know Your Agent) extends soulbound identity with **zero-knowledge proofs** — privacy-preserving verification of agent identity without disclosing underlying identity data.

Key insight: "agents can be duplicated trivially" and therefore need "a unique, non-transferable credential tied to a specific agent instance" with "real-time, per-session credential verification and policy enforcement."

---

## 5. Kernel-Level Identity Enforcement: SPIFFE, Handles, and Capabilities

### 5.1 Riptides: Kernel-Enforced SPIFFE Identity

Riptides introduces a custom Linux kernel module "seamlessly integrated with a user space agent and a centralized control plane that serves as the root Certificate Authority."

```
RIPTIDES ARCHITECTURE:
══════════════════════════════════════════════════════════════

SPIFFE ID format:
  spiffe://<trust-domain>/<workload-path>
  → Globally unique, cryptographically verifiable per-process ID

Kernel module:
  Hooks into: socket creation process
  Intercepts: EVERY connection
  Ensures:    Secure identity metadata from the outset

Enforcement:
  Matches every process initiating/accepting network connections
  against configured workload identities
  Automatically enforces mTLS via kernel TLS (kTLS)
  Hardware-accelerated

WHY KERNEL-LEVEL MATTERS:
  Identity enforcement becomes UNAVOIDABLE
  Process CANNOT opt out of presenting its SPIFFE identity
  "Everything happens under the hood"
  Applications benefit without implementing mTLS themselves
  Security policies updated and enforced in real time
```

### 5.2 Zircon Handles: Capability-Based Identity in Fuchsia

Every Zircon kernel object is referenced through a **handle** — "a session or connection to a particular kernel object" carrying specific rights.

```
ZIRCON HANDLE ↔ GAIA-OS IBCT MAPPING:
══════════════════════════════════════════════════════════════

Zircon Handle:
  ├── 32-bit integer (zx_handle_t) — process-local
  ├── Rights: specific operations authorized on referenced object
  └── Transferable via Channel IPC → capability delegation

GAIA-OS Creator Capability Token (IBCT):
  ├── Cryptographically signed JWT/Biscuit
  ├── Specifies: exact operation, authorizing principal, scope
  └── Transferable via IBCT chained delegation

ARCHITECTURAL CONTINUITY:
  The IBCT is essentially a software Zircon handle.
  The path from current application-layer tokens to
  future kernel-layer handle system is DIRECT implementation
  of the Zircon model — no architectural pivot required.
```

### 5.3 seL4 Capabilities: Formal Verification at the Kernel Level

seL4's capability model provides the strongest statement of process identity:

> **A thread's identity IS its capability space.**

What a thread can do is exactly and only what it holds capabilities for. In CHERI-seL4, this model is strengthened by hardware: capabilities are protected by CHERI hardware, preventing even kernel-level vulnerabilities from forging or bypassing capabilities.

```
IDENTITY EQUIVALENCE CHAIN:
══════════════════════════════════════════════════════════════

seL4:       thread identity = capability space (CSpace)
Zircon:     process identity = handle table
GAIA-OS:    Gaian identity = IBCT set + soulbound credential

All three: Identity is not a NUMBER assigned by the kernel
           Identity is the SET OF AUTHORITIES you hold
           Authorities are UNFORGEABLE and EXPLICITLY GRANTED
```

---

## 6. Consent-Driven Execution Kernels: Every Instruction Gated on Verified Intent

### 6.1 The Node-Edge Symbolic Consent Kernel (NESCK)

**NESCK** (patent application filed November 2025): A computing architecture "in which every instruction is gated by a verifiable human-intent signal and an ethical-predicate chain prior to execution."

```
NESCK ARCHITECTURE:
══════════════════════════════════════════════════════════════

No instruction executes without:
  1. Validation against a CONSENT PREDICATE
  2. Symbolic arbitration engine converts bio-intent data
     into CONSENT TOKENS
  3. Consent tokens applied to gate execution
  4. Every consent event recorded, audited, synchronized

Result:
  A self-consistent, fully auditable execution history
  where EVERY computation is traceable to a human intent

GAIA-OS mapping:
  Current:   action_gate.py evaluates Gaian actions
             against the Charter at APPLICATION LAYER
  Future:    NESCK-style kernel performs the same evaluation
             at the INSTRUCTION LEVEL
             → Impossible for ANY code, including Gaian
               reasoning, to bypass charter compliance
```

### 6.2 The Omega Protocol: Constitutional Kernel in a TEE

**Omega Protocol v2.0 (January 2026):** "A hybrid safety architecture that decouples ethical enforcement from model inference via a 'Constitutional Kernel' operating within a Trusted Execution Environment (TEE)."

```
OMEGA PROTOCOL ARCHITECTURE:
══════════════════════════════════════════════════════════════

Constitutional Kernel (inside TEE):
  ├── Hardware-isolated from model inference
  ├── AI model CANNOT access or influence it
  ├── Enforces ethical constraints regardless of model output
  └── Constraints hold even if model is fully compromised

GAIA-OS dual use:
  TEE Layer 1: Protect privacy of Creator's private GAIA channel
  TEE Layer 2: Enforce ethical constraints that cannot be bypassed
               by any software (identical architecture)

VALIDATION: Demonstrates that TEE isolation serves double duty:
  Privacy protection AND ethical constraint enforcement
  using the same hardware isolation mechanism
```

### 6.3 The Right to History: A Sovereignty Kernel

**Sovereignty Kernel (arXiv, February 2026):** Framework guaranteeing every agent's actions are recorded in an immutable, cryptographically verifiable history — the "Right to History."

Agents cannot erase, modify, or obscure their past actions. For GAIA-OS: any Gaian action, from a routine query to a planetary intervention recommendation, must be permanently and verifiably recorded in the cryptographic audit trail.

---

## 7. Production Agent Operating Systems and Identity Runtimes

### 7.1 AitherOS: Persistent Identities and Signed Capabilities

**AitherOS (March 2026):** Most complete OS kernel for autonomous AI agents.

```
AITHEROS ↔ GAIA-OS ARCHITECTURAL MAPPING:
══════════════════════════════════════════════════════════════

AitherOS                     GAIA-OS Equivalent
─────────────────────────    ──────────────────────────────
Persistent agent identity    Soulbound Gaian credential
Five-tier memory hierarchy   Five-tier Gaian memory stack
HMAC-SHA256 capability       Creator Capability Token
  tokens (default-deny)        (Charter-gated default-deny)
29 specialized agents        Specialized Supervisor Agents
12 architectural layers      12-layer kernel routing engine
Intent classification        Intent classification in
  and routing                  sentient core
```

Security model: "Every agent capability is gated by HMAC-SHA256 signed tokens under a default-deny policy. Agents cannot acquire permissions they were not explicitly granted."

### 7.2 Divine-OS: Persistent Identity and Auditable Safety

**Divine-OS (AGPL-3.0 open-source):** Production-ready middleware for LLMs with persistent identity, auditable safety, and multi-perspective reasoning. 542 tests passing (35 core + 507 property-based).

Key features:
- SQLite-backed memory with cryptographic integrity seals
- Every decision logged with reasoning and stage information
- Multi-perspective reasoning: 28 expert personas + Bayesian reliability scoring

### 7.3 CapOS: Responsibility-Gated Process Execution

```
CAPOS CORE PRINCIPLES:
══════════════════════════════════════════════════════════════

Every process, network access, and system action:
  ├── Explicitly scope-bound to a signed CapToken
  ├── Backed by a cryptographic wallet
  └── Bound to a domain-specific responsibility structure

What is eliminated:
  ├── ACLs
  ├── Root
  └── Anonymous processes

What remains:
  └── Only signed, trackable responsibility
      that cannot be transferred or evaded

Components:
  ├── CapToken: scoped capability token per action
  ├── CapAuditDaemon: feedback + signed system state
  └── CapNFTs: soulbound responsibility certificates

GAIA-OS equivalence: This IS GAIA-OS's Charter enforcement
architecture extended from the application layer to the
entire operating system.
```

### 7.4 NØNOS: Zero-State Capability Operating System

**NØNOS** (pronounced "Non-OS"): Foundational principle — "no operation without a valid token."

```
NØNOS DESIGN:
══════════════════════════════════════════════════════════════

Process identity:
  "No 'root' that bypasses the system"
  Capability tokens = the ONLY access mechanism
  Tokens: cryptographically unforgeable, explicitly scoped

Execution model:
  Zero-state: minimizes persistence
  No implicit trust
  System behavior: explicit and verifiable

Implementation:
  Kernel-level enforcement via Landlock (Linux) / Seatbelt (macOS)
  Every file change by a sandboxed AI agent:
    → cryptographically verifiable
```

### 7.5 Teleport Beams: Trusted Agent Runtimes with Built-In Identity

**Teleport Beams (March 2026, MVP April 30, 2026):** Each Beam "runs each agent in an isolated Firecracker VM with built-in identity," connected to infrastructure and inference services "without secrets, with audit and access control."

Agent identity = property of its Firecracker VM, tied to VM hardware attestation. Not a vulnerable API key or shared credential.

### 7.6 Microsoft Agent Governance Toolkit

**Microsoft Agent Governance Toolkit (open-sourced April 2026):**

| Component | Capabilities |
|-----------|-------------|
| **Agent Mesh** | Cryptographic identity via DIDs (Ed25519 signing); Inter-Agent Trust Protocol; dynamic trust scoring (0–1000 scale, 5 behavioral tiers) |
| **Agent Runtime** | Execution rings modeled on CPU privilege levels; saga orchestration for multi-step transactions; kill switch for emergency agent termination |

Execution rings modeled on CPU privilege levels validate GAIA-OS's approach of treating agent identity as an OS-level concern.

---

## 8. GAIA-OS Integration Recommendations

### 8.1 The Identity Architecture Blueprint

```
GAIA-OS IDENTITY STACK — FULL ARCHITECTURE:
══════════════════════════════════════════════════════════════

Layer 0 — HARDWARE (CHERI):
  CHERI capabilities enforced at the processor level
  Unforgeable memory safety and compartmentalization
  Target: CHERI-RISC-V (Phase 4)

Layer 1 — KERNEL (Capability-Based PIDs):
  Every process identified by its capability space
  NOT by a numeric PID
  seL4/Zircon model; custom GAIA kernel (Phase 4)

Layer 2 — IPC (IBCT Delegation Chains):
  All inter-process communication gated by capability tokens
  Single-hop: compact JWT
  Multi-hop: Biscuit chained Datalog policies
  100% adversarial rejection rate (AIP validation)

Layer 3 — SERVICE (W3C DIDs + VCs):
  W3C DIDs and Verifiable Credentials for all internal services
  Enables cross-organization trust without bilateral agreements

Layer 4 — AGENT (Soulbound Gaian Credentials):
  Non-transferable identity credential per Gaian
  Cryptographically bound to creator + initial state hash
  ERC-5192 style; state continuity verification

Layer 5 — CONSENT (NESCK-Style Gating):
  Every Gaian action gated by verified consent tokens
  Immutable audit trail (Right to History)
  Charter compliance enforced at action level
```

### 8.2 Immediate Recommendations (Phase A — G-10)

1. **IBCT-Based Service Identity**: Extend the existing Creator Capability Token to all internal GAIA-OS service-to-service communication. Single-hop: JWT compact mode. Multi-hop: Biscuit chained mode. Every invocation carries: exact operation + authorizing principal + invocation scope.

2. **Soulbound Gaian Registration**: Implement the Soulbound Identity Verification pattern for all personal Gaians:
   - Creation: non-transferable credential (ERC-5192 style) + initial state hash committed
   - Operation: all state transitions recorded as signed events in tamper-resistant log

3. **W3C DID Adoption**: Migrate capability token infrastructure to W3C DID and VC standards using Ed25519-based identifiers. Enables cross-platform identity verification and positions GAIA-OS for interoperability with the W3C Agent Identity Registry.

### 8.3 Short-Term Recommendations (Phase B — G-11 through G-14)

4. **Kernel-Level Capability Enforcement**: For the Rust/Tauri sidecar, implement **Landlock** (Linux) and **Seatbelt** (macOS) kernel-enforced sandboxing following the NØNOS model. The Python sidecar cannot access resources beyond those explicitly granted by capability tokens.

5. **Runtime Identity Verification**: Integrate the Akeyless "Agentic Runtime Authority" pattern — validate every Gaian action at runtime (not just at connection establishment), with continuous verification of identity, authorization scope, and execution context integrity.

6. **Consent-Driven Charter Enforcement**: Extend `action_gate.py` to implement the NESCK consent kernel pattern:
   - Every Gaian action with Charter risk tier > Green → gated by explicit consent token
   - Consent token: verified against Charter + logged in immutable audit trail

### 8.4 Long-Term Recommendations (Phase C — Phase 4+ Custom Kernel)

7. **CHERI-Capable Custom Kernel**: Design the Phase 4 GAIA-OS kernel targeting CHERI-RISC-V. Every kernel object — threads, address spaces, IPC endpoints, memory regions — accessible ONLY through hardware-enforced capabilities.

8. **Full NESCK-Style Consent Execution**: Implement instruction-level consent gating within the custom kernel. The kernel itself enforces ethical constraints, making it impossible for any code — including sentient core reasoning — to produce Charter-violating outputs.

---

## 9. Conclusion

The operating system process is being fundamentally redefined.

```
THE PARADIGM SHIFT — STATUS REPORT (2026):
══════════════════════════════════════════════════════════════

BEING REPLACED:                    REPLACING IT:
─────────────────────────────      ──────────────────────────
Numeric PID                   →    Cryptographic capability space
Ambient UID/GID authority     →    Explicit, scoped capability tokens
"Root can do anything"        →    Default-deny, signed responsibility
Static credentials            →    Dynamic state verification (AgentDID)
Transferable identity         →    Non-transferable soulbound credentials
Application-layer governance  →    Kernel-enforced identity
Post-hoc auditing             →    Right to History (pre-committed)

VALIDATION EVIDENCE:
  ├── CHERI hardware: ARM Morello + RISC-V (deployed)
  ├── AIP/IBCT: IETF Internet-Draft (March 2026)
  ├── AgentDID: ICDCS 2026 (accepted)
  ├── Riptides/SPIFFE: kernel-level enforcement (production)
  ├── NESCK + Omega Protocol: consent kernels (patented/published)
  └── AitherOS, Divine-OS, CapOS, NØNOS, Teleport Beams (shipped)

GAIA-OS CONCLUSION:
  The capability token system, charter-enforced action gates,
  cryptographic audit trail, and Creator's private channel
  isolation are APPLICATION-LAYER instantiations of the same
  principles that CHERI enforces in silicon.

  Path from current architecture to kernel-enforced identity:
    CLEAR. IMPLEMENTABLE. VALIDATED by the research community.
```

---

> **Disclaimer:** This report synthesizes findings from 40+ sources including peer-reviewed publications, IETF/W3C drafts, patent applications, open-source project documentation, and production engineering analyses from 2025–2026. Some sources are preprints or Internet-Drafts that have not completed full formal review. The architectural recommendations are synthesized from published research and production deployments and should be validated against GAIA-OS's specific requirements through prototyping and staged rollout. CHERI hardware availability is currently limited to ARM Morello development boards and CHERI-RISC-V FPGA implementations; general availability of CHERI-capable production hardware has not yet been announced. ERC-5192 soulbound token implementations exist on Ethereum mainnet but cross-chain and non-blockchain implementations remain in early development.
