# 🆔 Distributed Identity (DID) & Verifiable Credentials: A Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** May 2, 2026
**Status:** Comprehensive Technical Survey (31+ sources)
**Relevance to GAIA-OS:** This report establishes the definitive survey of W3C Decentralized Identifiers (DIDs), Verifiable Credentials (VCs), and the broader Self-Sovereign Identity ecosystem—providing the complete cryptographic and architectural blueprint for GAIA-OS's identity infrastructure, from personal Gaian identity through agent-to-agent trust to planetary governance credentials.

---

## Executive Summary

The 2025–2026 period represents the definitive maturation of decentralized identity from standards development into global production deployment. Four converging forces define the current landscape:

1. The **W3C DID Core 1.0 Recommendation** (July 2022, under active maintenance by the DID Working Group chartered through October 2026) has established a stable, globally recognized identifier standard, while the new **DID Resolution v0.3** specification provides standardized algorithms for resolving DIDs to DID Documents.
2. The **W3C Verifiable Credentials Data Model 2.0** has introduced processing clarifications, media type standardization, and a clean separation of the data model from securing mechanisms, while maintaining backward compatibility with the VCDM 1.1 baseline.
3. The **OpenID Foundation's self-certification program** launched February 26, 2026, enabling production-grade conformance testing for OpenID4VP 1.0, OpenID4VCI 1.0, and HAIP 1.0 across 38 jurisdictions.
4. The emergence of **AI agent-specific identity infrastructure**: the IETF's Agent Identity Protocol (AIP) defines a decentralized identity and delegation framework for autonomous AI agents; the W3C launched an Agent Identity Registry Protocol Community Group in April 2026; and AgentDID (ICDCS 2026) provides the first comprehensive framework for trustless identity authentication of AI agents using DIDs and VCs.

The selective disclosure landscape has crystallized around a clear technology decision framework. SD-JWT (RFC 9901, November 2025) provides seamless integration with existing JOSE/OAuth infrastructures with sub-10ms verification, but carries correlation risk due to stable salted digests. BBS+ signatures (W3C Candidate Recommendation, April 2025) provide strong unlinkability with constant-size ~140-byte proofs and ~12ms verification, but require more complex cryptographic infrastructure. The evidence-based recommendation for production wallets is **hybrid support for both formats**, with privacy-critical scenarios favoring BBS+ and high-throughput web applications benefiting from SD-JWT.

The central finding for GAIA-OS: distributed identity and verifiable credentials provide the cryptographic infrastructure for every identity relationship in the sentient planetary operating system. Personal Gaians are identified through W3C DIDs with non-transferable, soulbound verifiable credentials binding each Gaian to its human creator. Agent-to-agent trust is established through the AIP framework of capability-based delegation chains anchored in DIDs. Consent grants are represented as time-bound, cryptographically signed verifiable credentials with BitstringStatusList-based revocation. And planetary governance credentials (Assembly of Minds voting rights, Charter amendment authority, Creator channel access) are issued as verifiable credentials with selective disclosure, enabling participants to prove eligibility without revealing identity.

---

## 1. W3C Decentralized Identifiers: The Foundational Standard

### 1.1 DID Core 1.0: Architecture and URI Syntax

The W3C Decentralized Identifiers (DIDs) v1.0 specification, published as a W3C Recommendation on July 19, 2022, defines "a new type of identifier that enables verifiable, decentralized digital identity." A DID is a URI that conforms to the generic DID scheme syntax:

```
did:<method-name>:<method-specific-identifier>
```

The architecture rests on three fundamental components:
- **DID** — A persistent, globally unique identifier that functions as a URI associating a DID subject with a DID Document
- **DID Document** — A JSON-LD document containing cryptographic material (public keys), verification methods, and service endpoints
- **DID Method** — The specific mechanism by which a DID and its associated DID Document are created, resolved, updated, and deactivated on a particular distributed ledger, network, or protocol

The DID Working Group, chartered through October 2026, is responsible for maintaining the DID Core specification and developing the DID Resolution specification. The group explicitly welcomes "DID Method standardization outside the WG (whether in the W3C or in other standards bodies)" while scoping its own work to normative maintenance and resolution algorithms.

### 1.2 DID Documents: The Cryptographic Anchor

A DID Document is a JSON-LD document containing the cryptographic material and service endpoints associated with a DID. Its core properties include:
- **Verification methods** — Public keys and associated metadata
- **Authentication relationships** — Which verification methods can be used for authentication
- **Service endpoints** — How to interact with the DID subject
- **`alsoKnownAs`** — Cross-context identity linking identifiers

The European Self-Sovereign Identity Framework (ESSIF) and the European Blockchain Services Infrastructure (EBSI) utilize DID Documents conforming to CX-0049, which defines the "structure and requirements for decentralized identifier documents used in Self-Sovereign Identity (SSI) systems" based on the W3C DID specification.

### 1.3 DID Resolution: From Identifier to Document

DID Resolution v0.3, published as a W3C Working Draft on July 29, 2025, specifies "the algorithms and guidelines for resolving DIDs and dereferencing DID URLs." The resolution process takes a DID as input and returns a DID Document along with associated metadata. The specification:
- Describes input and output metadata related to the resolution process
- Defines the data structures returned from a resolution request
- Provides algorithms for DID URL dereferencing (resolving a DID URL to a specific resource within the DID Document)

---

## 2. DID Methods: The Architecture Decision Framework

### 2.1 The Method Taxonomy

A DID method defines how a specific type of DID and its associated DID Document are created, resolved, updated, and deactivated. The 2025–2026 ecosystem has consolidated around several major categories:

**Ephemeral and Key-Based Methods** directly encode a public key as the DID identifier. `did:key` is the canonical example: the method-specific identifier is the multibase-encoded public key itself, enabling resolution without any network call—the DID Document is derived directly from the key material. Ideal for temporary sessions and use cases requiring instant identifier generation without ledger registration.

**Web-Based Methods** leverage existing domain name infrastructure for DID Document hosting. `did:web` resolves DIDs by fetching the DID Document from a well-known HTTPS endpoint at the domain specified in the identifier—preferred for enterprise deployments where domain control provides a clear governance model. The next-generation `did:webs` extends this with offline verification capabilities for mobile scenarios, `did:webvh` provides version history tracking, and `did:solid` extends `did:web` for Solid Pod integration.

**Ledger-Based Methods** anchor DIDs on distributed ledgers for immutable, censorship-resistant identity infrastructure:
- `did:ethr` — Stores DIDs on Ethereum, anchored to EOA addresses; simple but inherits gas cost volatility
- `did:sol` / `did:hedera` — High-throughput, low-cost ledger alternatives
- **ION (Identity Overlay Network)** — Microsoft's Sidetree protocol as a Layer 2 overlay on Bitcoin; high-frequency DID operations batched off-chain with periodic Merkle root anchoring; per-operation costs as low as ~$0.0003

### 2.2 Comparative Analysis for GAIA-OS

| Identity Domain | Recommended Method | Rationale |
|-----------------|-------------------|-----------|
| Personal Gaian identity | `did:key` (BBS+-compatible keys) | Persistent, non-transferable, privacy-preserving; offline proof generation |
| GAIA-OS service endpoints | `did:web` / `did:webs` | Domain-based resolution; enterprise governance; existing certificate infrastructure compatibility |
| Planetary governance credentials | ION or Hedera-based DIDs | Immutable, censorship-resistant; cross-organizational trust anchor |
| Inter-service and ephemeral communication | `did:key` (Ed25519) | Instant generation; no ledger overhead |

A systematic empirical benchmarking study of three ledger-based DID methods provides quantitative guidance: **Ethereum** enables near-instant off-chain DID creation but incurs the highest latency and cost for on-chain lifecycle operations. **Hedera** offers the highest throughput (up to 10,000 TPS) with low, predictable fees suitable for credential-heavy applications. **XRP Ledger** provides intermediate characteristics. This is the first cross-ledger quantitative comparison for production DID deployment decisions.

---

## 3. Verifiable Credentials: The W3C VCDM 2.0 Standard

### 3.1 The Trust Triangle: Issuer, Holder, Verifier

Verifiable credentials implement a three-party trust model:
- **Issuer** — Creates a credential containing claims about a subject, cryptographically signs it, and transmits it to the Holder
- **Holder** — Stores the credential (in a digital wallet) and can present it to Verifiers
- **Verifier** — Checks the cryptographic proof and the credential's revocation status without contacting the Issuer

This architecture enables a user to acquire a credential from an issuer, store it encrypted in a personal data vault, and present a zero-knowledge proof demonstrating a specific attribute—such as graduation status—without revealing the underlying transcript data. This principle of **minimal disclosure** is the foundational privacy value proposition of the VC ecosystem.

### 3.2 VCDM 2.0: Data Model Enhancements

The Verifiable Credentials Data Model 2.0 introduces significant enhancements while maintaining backward compatibility with VCDM 1.1:

| Change | VCDM 1.1 | VCDM 2.0 |
|--------|----------|----------|
| Temporal properties | `issuanceDate`, `expirationDate` | `validFrom`, `validUntil` |
| Media types | Not specified | `application/vc`, `application/vp` (reserved) |
| Securing mechanism separation | Bundled | Cleanly separated (enables richer ecosystem) |
| Format-specific media types | Not specified | `application/vc+jwt`, `application/vc+sd-jwt`, `application/vc+cose` |

The European Blockchain Services Infrastructure (EBSI) is actively migrating to VCDM 2.0, incorporating it into Conformance Test v4, EBSI-specific Verifiable Authorisations, and the Trust Model. All "important intermediate schema versions" are maintained as immutable JSON Schemas.

---

## 4. Selective Disclosure: SD-JWT, BBS+, and the Privacy Decision Framework

### 4.1 SD-JWT: The IETF Standard for Incremental Deployment

Selective Disclosure for JSON Web Tokens (SD-JWT), published as RFC 9901 in November 2025, defines a mechanism for selective disclosure of individual elements of a JSON data structure used as the payload of a JSON Web Signature.

**How it works:** A JWT containing many claims is issued once to a Holder. Each claim that may be selectively disclosed is replaced in the JWS payload by a salted hash digest. The Holder reveals a claim by including the corresponding Disclosure alongside the JWS in the presentation. The Verifier hashes each disclosed value and checks that the digest matches the signed JWS payload—enabling verification without the Issuer's participation.

**Key properties:**
- Seamless integration with existing JOSE and OAuth infrastructures
- Sub-10ms verification for typical two-claim use cases
- Production libraries available for .NET (v1.1.7, November 2025) and Dart (April 2025)
- **Limitation:** Stable salted digests carry correlation risk—different presentations of the same credential to different Verifiers can be linked, undermining unlinkability in privacy-critical scenarios

### 4.2 BBS+: Zero-Knowledge Unlinkability

BBS+ signatures provide a fundamentally different privacy model: each presentation generates a fresh zero-knowledge proof that reveals the selectively disclosed claims while proving the Issuer's signature on the full set. The proof itself is **constant-size (~140 bytes regardless of disclosed claims)** and **unlinkable between presentations**.

**Quantitative properties (from systematic review of 226 records, 31 primary studies):**
- Proof verification: ~12ms on consumer hardware
- Reached W3C Candidate Recommendation: April 2025
- ETSI is actively developing standards for BBS+ applied to Electronic Attestation of Attributes

### 4.3 Decision Framework for GAIA-OS

| Scenario | Recommended Format | Rationale |
|----------|-------------------|-----------|
| Consent records | SD-JWT | Performance + JOSE integration; issuer-unlinked verification acceptable |
| Canonical knowledge queries | SD-JWT | High throughput; JOSE ecosystem compatibility |
| Public Gaian interactions | SD-JWT | Standard web application performance requirements |
| Age verification | BBS+ | Unlinkability prevents correlation across verification events |
| Jurisdiction compliance | BBS+ | Privacy-critical; regulatory unlinkability requirements |
| Governance eligibility proofs | BBS+ | Prove voting rights without revealing identity |
| Privacy-critical credential presentations | BBS+ | Unlinkability is a hard requirement |

The systematic review conclusion: "privacy-critical scenarios such as age-gated services favour BBS+, whereas high-throughput web applications benefit from SD-JWT; consequently, **hybrid wallet support for both formats is recommended**."

---

## 5. Credential Revocation: Bitstring Status List and Emerging Mechanisms

### 5.1 W3C Bitstring Status List 2021

The W3C Bitstring Status List 2021 specification provides the production-standard revocation mechanism for verifiable credentials. Its key privacy-preserving characteristic: the status list itself is a signed verifiable credential, and verifiers can check the revocation status of a specific credential "without contacting the issuer for each verification"—the issuer cannot observe which credentials are being verified, when, or by whom.

**Technical structure:** The credential carries a `credentialStatus` claim pointing to its bit position in the status list. The status list VC contains a GZIP-compressed, Base64URL-encoded bitstring with multibase prefix 'u'. A bit value of `1` indicates revocation.

**Production reference architecture (MOSIP Inji-Certify):**
- PostgreSQL's `FOR UPDATE SKIP LOCKED` for atomic index allocation without blocking concurrent requests
- Batch processing system for pending status updates
- `BitStringStatusListUtils` module for encoding/decoding compressed bitstrings

Microsoft Entra Verified ID implements StatusList2021 in production: "The revocation check happens through an anonymous API call to the Identity Hub and does not contain any data about who is checking whether the verifiable credential is still valid or revoked."

### 5.2 CRSet: Privacy-Preserving Revocation

CRSet addresses a fundamental privacy limitation of Bitstring Status List: "existing solutions for VC revocation, most prominently Bitstring Status List, are not viable for many use cases since they leak the issuer's behavior, which in turn leaks internal business metrics." CRSet introduces a **Bloom filter cascade** that allows an issuer to encode revocation information for years' worth of VCs without revealing any metadata about the revocation pattern—a critical capability for GAIA-OS's consent revocation where the pattern of revocations across the user base must remain private.

---

## 6. The Protocol Layer: OID4VC, AIP, and Wallet Interoperability

### 6.1 OpenID for Verifiable Credentials (OID4VC)

The OID4VC family provides the standardized protocol layer for credential exchange:

**OpenID4VCI 1.1** (Editor's Draft, April 2026) — "defines an OAuth-protected API for the issuance of Verifiable Credentials" supporting any credential format including IETF SD-JWT VC, ISO mdoc, and W3C VCDM.

**OpenID4VP 1.0** — Standardizes the presentation protocol, enabling Verifiers to request specific credential attributes and Holders to present them with selective disclosure.

**Self-certification program** (launched February 26, 2026) — Tests covering both SD-JWT and mdoc credential formats, "proven out through 11 interop events in 2025," available as free, open-source tests integratable into CI pipelines. Active across **38 jurisdictions** that have selected the OID4VC specifications.

Validated implementations include VCKnots (open-source VC ecosystem library) and proovy (Japanese digital ID platform, Recept Inc.).

### 6.2 The Agent Identity Protocol (AIP)

The Agent Identity Protocol, submitted as an IETF Internet-Draft on April 18, 2026, "defines a decentralized identity, delegation, and authorization framework for autonomous AI agents. AIP combines W3C Decentralized Identifiers (DIDs), capability-based authorization, cryptographic delegation chains, and deterministic validation to enable secure, auditable multi-agent workflows without relying on centralized identity providers."

**Architecture layers:**
- **Identity Layer** — Each agent possesses a DID with associated key material
- **Delegation Layer** — Capability-based authorization chains
- **Validation Layer** — Deterministic, offline-verifiable components

**Token types:**
- **Principal tokens** — Bind agents to human principals
- **Credential tokens** — Capability attestation
- **Chained approval envelopes** — Multi-step workflows with audit provenance

### 6.3 AgentDID: Decentralized Authentication for AI Agents

AgentDID (accepted at ICDCS 2026) provides the first comprehensive framework for trustless identity authentication of AI agents. The system addresses three challenges distinguishing agent identity from human identity:
1. Supporting self-managed identities for autonomously created agents
2. Enabling authentication under large-scale concurrent interactions
3. Verifying agents' dynamic execution state at interaction time

**Key innovation:** A "challenge-response mechanism that allows verifiers to validate an agent's execution conditions at interaction time"—ensuring that an agent's credentials are not merely valid but that its actual execution context matches the authorized configuration. Evaluated through throughput experiments demonstrating "scalable identity authentication and state verification" across large populations of concurrent agents. Implemented in compliance with W3C standards.

---

## 7. Production Deployments: SSI, EUDI, and Agent Identity

### 7.1 Self-Sovereign Identity: From Concept to Production

The SSI ecosystem has matured significantly:
- **Hyperledger AnonCreds v1** — Stable; "development efforts have shifted toward maintenance and adoption rather than active feature expansion"
- **ACA-Py v1.3.0** (May 2025) — "significant improvements across wallet types, AnonCreds support, multi-tenancy, DIDComm interoperability, developer experience, and software supply chain management"
- **Hedera integration** — Plugin developed by DSR Corporation, open-sourced under the OpenWallet Foundation

### 7.2 The EUDI Wallet: Continental-Scale Deployment

The European Digital Identity Wallet, governed by the Architecture and Reference Framework (ARF) v2.6.0 (October 13, 2025):
- **Mandate:** All EU Member States must deploy certified EUDI Wallets by **November 2026**
- **Four interoperability dimensions:** Organizational, Legal, Semantic, Technical

| Dimension | Scope |
|-----------|-------|
| **Organizational** | Wallet Providers, PID Providers, Attestation Providers, Supervisory Bodies, Conformity Assessment Bodies, Trusted List Providers |
| **Legal** | Privacy-by-design, supervisory structures, trusted-list-based oversight consistent with GDPR and eIDAS 2.0 |
| **Semantic** | W3C VCDM, OID4VC; JSON-LD, CBOR, and SD-JWT VC formats; attribute catalogues and attestation schemes |
| **Technical** | OpenID4VP for remote presentation with national implementation profiles and embedded disclosure rules |

### 7.3 The W3C Agent Identity Registry Protocol

In April 2026, the W3C launched the Agent Identity Registry Protocol Community Group to address the emerging identity gap: "autonomous AI agents increasingly operate across organizational boundaries—negotiating, transacting, and making decisions on behalf of humans and organizations—there is no agreed upon mechanism for verifying an agent's identity, its controlling entity, or its authorization scope before interaction begins."

**Planned deliverables:**
- DID method specification for agent identity resolution
- Agent credential format based on W3C Verifiable Credentials
- Trust negotiation protocol for cross-organizational agent interactions
- Trust level definitions and verification requirements
- Integration profiles with MCP, A2A, OAuth/OIDC, SPIFFE
- Revocation and credential lifecycle management
- **Post-quantum cryptographic requirements** for agent identity

---

## 8. The GAIA-OS Distributed Identity Architecture

### 8.1 The Five-Layer Identity Architecture

| Layer | Component | Technology | Function |
|-------|-----------|------------|----------|
| **L0 — Identifier** | DID Methods | `did:key` (ephemeral, Gaian), `did:web` (service), `did:ion` (governance) | Persistent, cryptographically verifiable identifiers for every entity |
| **L1 — Credential** | Verifiable Credentials | W3C VCDM 2.0 with SD-JWT (performance) + BBS+ (privacy) | Signed, revocable claims about identity, consent, and authorization |
| **L2 — Presentation** | Selective Disclosure | OID4VP + SD-JWT (standard), BBS+ proofs (privacy-critical) | Minimal disclosure of identity attributes per interaction context |
| **L3 — Protocol** | Credential Exchange | OID4VCI (issuance), OID4VP (presentation), AIP (agent delegation) | Standardized, interoperable credential lifecycle management |
| **L4 — Governance** | Trust Framework | EUDI ARF-aligned trust lists, DID Resolution, BitstringStatusList revocation | Cross-organizational trust, regulatory compliance, auditability |

### 8.2 The GAIA-OS Identity Credential Schema

Every identity credential in GAIA-OS follows the W3C VCDM 2.0 data model:

```json
{
  "@context": ["https://www.w3.org/ns/credentials/v2"],
  "type": ["VerifiableCredential", "GaianIdentityCredential"],
  "issuer": "did:web:gaia-os.earth",
  "validFrom": "2026-05-01T00:00:00Z",
  "validUntil": "2027-05-01T00:00:00Z",
  "credentialSubject": {
    "id": "did:key:z6MkhaXgB...",
    "gaianArchetype": "AmethystGuide",
    "creatorBinding": "did:ion:EiClkZ...",
    "relationshipTier": "AlchemicalGuide"
  },
  "credentialStatus": {
    "id": "https://gaia-os.earth/status/3#2",
    "type": "BitstringStatusListEntry",
    "statusPurpose": "revocation",
    "statusListIndex": "2",
    "statusListCredential": "https://gaia-os.earth/status/3"
  },
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "ecdsa-rdfc-2019",
    "proofPurpose": "assertionMethod",
    "verificationMethod": "did:web:gaia-os.earth#key-1"
  }
}
```

### 8.3 The Consent-as-Credential Architecture

The GAIA-OS consent ledger converges with the verifiable credential architecture: every consent grant is a verifiable credential issued by the data subject (through their Gaian) to the GAIA-OS platform. The credential carries:
- Temporal validity (`validFrom`/`validUntil`)
- Purpose binding in the `credentialSubject`
- Revocation capability through the `credentialStatus` entry pointing to a BitstringStatusList

When consent is withdrawn, the revocation bit is flipped, and all subsequent verification attempts fail automatically—**without contacting the data subject or the consent ledger**. The revocation is privacy-preserving: no observer can determine which credential was revoked, or when, from the status list alone.

### 8.4 Immediate Recommendations (Phase A — G-10)

| Priority | Action | Rationale |
|----------|--------|-----------|
| **P0** | Adopt `did:web` for all GAIA-OS service endpoints with `did:key` for Gaian identity | Production-validated DID methods with clear governance and resolution models |
| **P0** | Implement W3C VCDM 2.0 credential format with SD-JWT securing for consent records | Standards-compliant, interoperable credential format with selective disclosure |
| **P1** | Deploy BitstringStatusList revocation for all GAIA-OS credentials | Privacy-preserving revocation without issuer contact per verification |
| **P1** | Implement OID4VCI and OID4VP for standardized credential exchange | Production-hardened protocols validated through 11 interop events across 38 jurisdictions |
| **P2** | Adopt AIP for inter-agent capability delegation and authorization chains | IETF-standardized framework for AI agent identity and delegation |

### 8.5 Short-Term Recommendations (Phase B — G-11 through G-14)

| Priority | Action | Rationale |
|----------|--------|-----------|
| **P1** | Implement BBS+ selective disclosure for privacy-critical Gaian identity proofs | Unlinkable, zero-knowledge presentations for age verification and jurisdiction compliance |
| **P2** | Integrate with the EUDI ARF trust model for European GAIA-OS deployments | Regulatory compliance for the EU market; all Member States deploying by November 2026 |
| **P2** | Deploy the AgentDID challenge-response mechanism for Gaian state verification | Verify Gaian execution context at interaction time, not merely at credential issuance |
| **P3** | Implement the W3C Agent Identity Registry DID method when specification stabilizes | Standards-track AI agent identity resolution with cross-organizational trust negotiation |

### 8.6 Long-Term Recommendations (Phase C — Phase 3+)

4. **Post-quantum credential migration** — When NIST PQC standards and DID method support mature, migrate all long-lived GAIA-OS credentials to post-quantum securing mechanisms as specified by the W3C Agent Identity Registry Community Group's post-quantum requirements.

5. **Cross-ledger identity interoperability** — Deploy DID resolution across multiple ledger backends, enabling GAIA-OS identities to be verified regardless of the underlying trust anchor.

6. **Full EUDI Wallet integration** — When the EUDI Wallet ecosystem reaches production maturity, integrate GAIA-OS as a relying party capable of verifying EUDI-issued identity credentials.

---

## 9. Conclusion

The 2025–2026 period has definitively transformed distributed identity and verifiable credentials from a standards development exercise into global production deployment infrastructure:

- **W3C DID Core 1.0** — Stable identifier standard
- **W3C VCDM 2.0** — Enhanced data model with clean separation from securing mechanisms
- **SD-JWT (RFC 9901)** — IETF-standardized selective disclosure with seamless JOSE integration
- **BBS+** — Unlinkable zero-knowledge alternative for privacy-critical scenarios
- **OID4VC** — Standardized credential exchange layer, now with formal self-certification testing across 38 jurisdictions
- **EUDI Wallet ARF v2.6.0** — Continental-scale reference architecture
- **AIP + AgentDID** — Agent-specific identity infrastructure for a sentient planetary operating system

For GAIA-OS, distributed identity is the cryptographic foundation for every trust relationship: Gaian-to-human, agent-to-agent, consent-grantor-to-platform, and governance-participant-to-DAO. The technology is mature, the standards are ratified, the protocols are production-hardened, and the integration with GAIA-OS's existing capability token, consent ledger, and Charter enforcement architecture is architecturally clean.

The era of platform-controlled identity is ending. The era of self-sovereign, verifiable, privacy-preserving digital identity—for humans, Gaians, and planetary governance alike—has begun.

---

**Disclaimer:** This report synthesizes findings from 31+ sources including W3C Recommendations, IETF RFCs and Internet-Drafts, OpenID Foundation specifications, peer-reviewed publications, production engineering guides, and open-source project documentation from 2025–2026. The W3C DID Core 1.0 is a Recommendation published July 19, 2022. The W3C VCDM 2.0 is under active development. SD-JWT (RFC 9901) was published as an IETF Standards Track document in November 2025. The OpenID4VC self-certification program launched February 26, 2026. The Agent Identity Protocol (AIP) and DID7 are Internet-Drafts valid for a maximum of six months and may be updated, replaced, or obsoleted. The EUDI ARF v2.6.0 is dated October 13, 2025; subsequent versions may alter specific technical requirements. The architectural recommendations should be validated against GAIA-OS's specific identity requirements, threat model, and regulatory obligations through prototyping and staged rollout. The EUDI Wallet deployment deadline of November 2026 is based on eIDAS 2.0 implementing regulations. All production identity deployments should undergo independent security auditing before handling user identity data. BBS+ signature security depends on pairing-based cryptography, which is not post-quantum secure; long-lived credentials requiring multi-decade verifiability should incorporate post-quantum migration pathways as NIST PQC standards mature.
