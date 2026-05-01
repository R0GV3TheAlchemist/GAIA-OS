# 🔐 Post-Quantum Cryptography: ML-KEM (Kyber) & ML-DSA (Dilithium) via liboqs — A Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** May 2, 2026
**Status:** Comprehensive Technical Survey (19+ sources)
**Relevance to GAIA-OS:** This report provides the definitive survey of NIST-standardized post-quantum cryptographic algorithms—ML-KEM (FIPS 203, formerly CRYSTALS-Kyber) and ML-DSA (FIPS 204, formerly CRYSTALS-Dilithium)—and their production-grade implementation in the Open Quantum Safe liboqs library. It establishes the cryptographic foundation for GAIA-OS's defense against the harvest-now-decrypt-later threat model and informs the hardening of all GAIA-OS communication channels, including the Tauri–Python sidecar IPC, the Creator's private channel, and the Gaian consent ledger's cryptographic audit trail.

---

## Executive Summary

The post-quantum cryptography landscape has transitioned from research theory to operational deployment in the 2025–2026 period. On August 13, 2024, NIST published three foundational standards: FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), and FIPS 205 (SLH-DSA). A fourth standard, FIPS 206 (FN-DSA, derived from FALCON), followed in 2025. These algorithms are now embedded in production protocols including TLS 1.3, SSH, and PKI infrastructure through the Open Quantum Safe (OQS) project's liboqs library—independently security-audited by Trail of Bits in 2024–2025.

The regulatory pressure for migration is intensifying. The NSA's CNSA 2.0 framework mandates ML-KEM-1024 and ML-DSA-87 for all national security systems by 2030, with complete RSA/ECC deprecation by 2035. Google Quantum AI's March 2026 whitepaper demonstrated that breaking 256-bit ECC requires approximately 20× fewer physical qubits than previously estimated, compressing the credible timeline for a cryptographically relevant quantum computer and accelerating Google's own 2029 PQC migration deadline.

The harvest-now-decrypt-later (HNDL) threat is not theoretical. Adversaries are already exfiltrating encrypted data today and storing it for future quantum decryption. For any data that must remain confidential beyond approximately 2030–2035, migration to quantum-resistant algorithms is a present-day operational requirement.

The central finding for GAIA-OS: liboqs provides a production-hardened, independently audited, cross-platform implementation of both ML-KEM and ML-DSA that integrates directly with the existing Python/FastAPI backend through `liboqs-python` bindings. ML-KEM-768 combined with classical X25519 in a hybrid key exchange for the Tauri–sidecar IPC provides immediate quantum resistance without sacrificing classical security guarantees. ML-DSA-65 signatures on consent ledger entries, capability tokens, and audit trail records provide quantum-resistant non-repudiation.

---

## 1. The Quantum Threat and the Regulatory Imperative

### 1.1 Shor's Algorithm and the Cryptographic Apocalypse

Classical public-key cryptography—RSA, Diffie-Hellman, ECDH, and ECDSA—derives its security from the computational hardness of integer factorization and the discrete logarithm problem. In 1994, Peter Shor demonstrated that a sufficiently powerful quantum computer could solve both problems in polynomial time, effectively rendering all widely deployed asymmetric cryptography insecure.

### 1.2 The Compressed Quantum Timeline

Google Quantum AI's March 2026 whitepaper demonstrated that breaking 256-bit elliptic curve cryptography requires approximately 20× fewer physical qubits than previously estimated, compressing the credible timeline for a cryptographically relevant quantum computer (CRQC) from the previously consensus 2035–2040 window to potentially as early as 2028–2029. IonQ has unveiled a roadmap targeting CRQC capabilities as early as 2028.

The Cloud Security Alliance estimates "Q-Day" could arrive by 2030. Large enterprises beginning migration in 2026 should not expect full completion before the early 2030s, meaning the migration window and the threat window are now overlapping.

### 1.3 The Regulatory Cascade: CNSA 2.0, NIST, and Global Mandates

| Framework | Requirement | Deadline |
|-----------|------------|---------|
| NSA CNSA 2.0 | All new national security systems adopt quantum-safe algorithms | January 2027 |
| NSA CNSA 2.0 | Full application migration | 2030 |
| NSA CNSA 2.0 | Complete infrastructure migration, RSA/ECDSA deprecated | 2035 |
| NIST | U.S. federal system migration to FIPS 203/204/205 | 2035 |
| G7 / AU / IN / CA | Critical system transition windows | 2030–2035 |

### 1.4 The Harvest-Now-Decrypt-Later (HNDL) Threat

HNDL attacks: adversaries passively collect encrypted traffic today, store it, and decrypt it using Shor's algorithm when a CRQC becomes available. Intelligence agencies in multiple countries have confirmed HNDL attacks are already underway.

For GAIA-OS, the HNDL threat model directly implicates:
- **Creator's private channel** — Highly sensitive personal content that must remain confidential indefinitely
- **Gaian consent ledger entries** — Legal and fiduciary significance with decade-scale retention requirements
- **Cryptographic audit trail records** — Non-repudiable evidence for Charter enforcement over a 20+ year horizon
- **Capability tokens and identity credentials** — Intercepted today, potentially replayed against future infrastructure

---

## 2. ML-KEM (FIPS 203): Module-Lattice-Based Key Encapsulation

### 2.1 Algorithm Overview and Mathematical Foundations

ML-KEM (Module-Lattice-Based Key-Encapsulation Mechanism), formerly CRYSTALS-Kyber, is a KEM designed to be resistant to both classical and quantum cryptanalytic attacks. Security derives from the computational hardness of the Module Learning With Errors (MLWE) problem. As a KEM, ML-KEM enables two parties to agree on a shared secret through three operations: `KeyGen256`, `Encaps`, and `Decaps`. Internally uses SHA3-256, SHA3-512, SHAKE256, and SHAKE512.

### 2.2 Security Levels and Parameter Sets

| Variant | NIST Category | Public Key | Ciphertext | Equivalent |
|---------|--------------|------------|------------|------------|
| ML-KEM-512 | 1 | 800 bytes | 768 bytes | AES-128 |
| ML-KEM-768 | 3 | 1,184 bytes | 1,088 bytes | AES-192 |
| ML-KEM-1024 | 5 | 1,568 bytes | 1,568 bytes | AES-256 |

GAIA-OS recommendation: **ML-KEM-768** as the default for most channels; **ML-KEM-1024** for the Creator's private channel and highest-assurance cryptographic audit trail paths (CNSA 2.0 mandates ML-KEM-1024 for all classification levels).

### 2.3 Performance Characteristics

ML-KEM demonstrates exceptional performance, outperforming other post-quantum KEMs (FrodoKEM, BIKE, HQC) across all operations. On ARM Cortex-M0+ (RP2040 at 133 MHz), ML-KEM-512 completes a full key exchange in approximately 35.7 milliseconds — approximately 172× faster than ECDH P-256 on the same hardware. This is significant for GAIA-OS's planetary sensor mesh, where edge devices with 10–20 year operational lifespans require post-quantum security without upgrade pathways.

liboqs provides hardware-accelerated implementations leveraging Intel AVX2 and AVX-512, with up to 1.64× speed improvements on Intel Xeon processors.

---

## 3. ML-DSA (FIPS 204): Module-Lattice-Based Digital Signatures

### 3.1 Algorithm Overview

ML-DSA (Module-Lattice-Based Digital Signature Algorithm), formerly CRYSTALS-Dilithium, is a lattice-based digital signature scheme standardized in FIPS 204. Security derives from the hardness of Module-LWE and Module-SIS problems. It is designed as the primary post-quantum replacement for ECDSA, EdDSA, and RSA-PSS signatures.

ML-DSA's defining characteristic: unlike hash-based schemes (SLH-DSA/SPHINCS+), there is no limit on the number of signatures per key pair, making it suitable for high-frequency use cases including TLS handshakes, code signing, and document authentication. NSA CNSA 2.0 endorses ML-DSA for all digital signature use cases, including signing firmware and software.

### 3.2 Security Levels and Parameter Sets

| Variant | NIST Category | Public Key | Signature Size |
|---------|--------------|------------|---------------|
| ML-DSA-44 | 2 | 1,312 bytes | 2,420 bytes |
| ML-DSA-65 | 3 | 1,952 bytes | 3,309 bytes |
| ML-DSA-87 | 5 | 2,592 bytes | 4,595 bytes (~71× Ed25519) |

GAIA-OS recommendation: **ML-DSA-65** as the default for consent ledger entries, capability token signing, and audit trail records; **ML-DSA-87** for the Creator's private channel and highest-assurance Charter enforcement records.

### 3.3 Performance and the Rejection Sampling Challenge

ML-DSA signing exhibits high latency variance due to rejection sampling. On ARM Cortex-M0+, ML-DSA signing shows a coefficient of variation of 66–73%, with 99th percentile reaching up to 1,125 milliseconds for ML-DSA-87. This variance is acceptable for infrequent signing (credential issuance, log signing) but must be accounted for in latency budgets for high-frequency operations. ML-DSA verification is consistently fast on server-class hardware, making it well-suited to verify-once-validate-many patterns.

---

## 4. The Open Quantum Safe (OQS) Project and liboqs

### 4.1 Project Overview and Governance

The Open Quantum Safe (OQS) project is an open-source initiative hosted under the Linux Foundation's Post-Quantum Cryptography Alliance (PQCA). It provides liboqs — a production-hardened C library implementing quantum-resistant cryptographic algorithms — and prototype integrations into protocols and applications including OpenSSL. The Trail of Bits security audit was published in April 2025.

### 4.2 liboqs: Architecture and Algorithm Coverage

liboqs provides a common C API closely following NIST/SUPERCOP API conventions. Algorithm coverage:
- **ML-KEM** — All three security levels (FIPS 203)
- **ML-DSA** — All three security levels (FIPS 204)
- **SLH-DSA (SPHINCS+)** — All security levels (FIPS 205)
- **FN-DSA (FALCON)** — (FIPS 206)
- **Round 4 candidates** — Classic McEliece, HQC, BIKE (research/evaluation)

### 4.3 Release History

| Version | Release Date | Notes |
|---------|-------------|-------|
| v0.13.0 | April 17, 2025 | — |
| v0.14.0 | July 10, 2025 | Security fix for secret-dependent branching in HQC |
| v0.15.0 | November 14, 2025 | Latest stable release |

### 4.4 Language Bindings for the GAIA-OS Stack

- **`liboqs-python`** — Python 3 wrapper; `import oqs`; common API for KEMs and signature schemes
- **`liboqs-rust`** — Rust wrapper; `oqs` and `oqs-sys` crates; v0.11.0 released May 1, 2025
- **Dart FFI bindings** — For any future Flutter-based mobile clients; supports ML-KEM, ML-DSA, Falcon, and SPHINCS+

### 4.5 Integration with OpenSSL via oqs-provider

The oqs-provider integrates liboqs algorithms directly into OpenSSL's provider framework, enabling post-quantum cryptography for TLS, SSH, and any protocol using OpenSSL. This is the recommended integration path for GAIA-OS's server-side TLS endpoints: OpenSSL 3.5+ with oqs-provider enables hybrid post-quantum TLS 1.3 handshakes combining X25519 with ML-KEM-768, as validated in production deployments by AWS Secrets Manager in April 2026.

---

## 5. Deployment Architecture for GAIA-OS

### 5.1 The Hybrid Cryptography Model

The recommended deployment model is **hybrid cryptography** — combining classical and post-quantum algorithms simultaneously. This provides both classical security and quantum protection during the transition period, and is permitted by NIST under FIPS 140-3 validation. If a weakness is discovered in ML-KEM or ML-DSA, the classical algorithm provides a safety net.

IETF-specified hybrid key agreements for TLS 1.3:
- `X25519MLKEM768` — X25519 + ML-KEM-768 (**recommended default**)
- `SecP256r1MLKEM768` — P-256 + ML-KEM-768
- `SecP384r1MLKEM1024` — P-384 + ML-KEM-1024 (highest assurance)

An attacker must break **both** the classical and post-quantum algorithms to recover the key.

### 5.2 Tauri–Python Sidecar IPC Hardening

Replace the current plain HTTP localhost communication with TLS 1.3 using a hybrid X25519MLKEM768 key exchange via OpenSSL 3.5+ with oqs-provider. No changes required to the FastAPI application code — TLS configuration is applied at the ASGI server level (Uvicorn) and the Tauri HTTP client level (reqwest with native-tls).

### 5.3 Consent Ledger and Audit Trail Protection

| Data Category | Algorithm | Rationale |
|--------------|-----------|-----------|
| Consent ledger entries | ML-DSA-65 | NIST Category 3; multi-decade retention |
| Creator's private channel state transitions | ML-DSA-87 | Highest assurance; CNSA 2.0 compliant |
| Cryptographic audit trail entries | Ed25519 + ML-DSA-65 (dual-signature) | Classical compatibility + quantum resistance |
| Hashing | SHA-512 | Quantum-resistant for collision resistance at 256-bit security level |

### 5.4 Capability Token Signing

```python
import oqs

def sign_capability_token(token_payload: bytes) -> tuple[bytes, bytes]:
    """Sign a GAIA-OS capability token using ML-DSA-65."""
    signer = oqs.Signature("ML-DSA-65")
    public_key = signer.generate_keypair()
    signature = signer.sign(token_payload)
    return public_key, signature

def verify_capability_token(
    token_payload: bytes,
    signature: bytes,
    public_key: bytes
) -> bool:
    """Verify a GAIA-OS capability token signature."""
    verifier = oqs.Signature("ML-DSA-65")
    return verifier.verify(token_payload, signature, public_key)
```

The larger signature sizes (3,309 bytes for ML-DSA-65 vs. 64 bytes for Ed25519) must be accounted for in token size budgets. For most GAIA-OS use cases, tokens are exchanged over localhost or local network connections where bandwidth is plentiful, making the trade-off acceptable.

---

## 6. The GAIA-OS PQC Implementation Roadmap

### 6.1 Immediate Recommendations (Phase A — G-10)

| Priority | Action | Rationale |
|----------|--------|-----------|
| **P0** | Install liboqs v0.15.0 and `liboqs-python` in the GAIA-OS build pipeline | Foundation for all subsequent PQC integration; audited, production-hardened |
| **P0** | Implement hybrid X25519MLKEM768 TLS for Tauri–Python sidecar IPC via OpenSSL 3.5+ with oqs-provider | Immediate quantum resistance for the primary IPC channel |
| **P1** | Migrate consent ledger entry signing to ML-DSA-65 | Quantum-resistant non-repudiation for records with multi-decade retention |
| **P1** | Implement dual-signature regime (Ed25519 + ML-DSA-65) for cryptographic audit trail entries | Maintains classical verification compatibility + adds quantum protection |
| **P2** | Deploy ML-DSA-87 signing for Creator's private channel state transitions | Highest assurance tier for the most sensitive GAIA-OS data |

### 6.2 Short-Term Recommendations (Phase B — G-11 through G-14)

| Priority | Action | Rationale |
|----------|--------|-----------|
| **P1** | Implement ML-KEM-1024 hybrid key exchange for the Creator's private channel | CNSA 2.0-compliant key establishment for highest-assurance path |
| **P1** | Migrate all IBCT capability tokens to ML-DSA-65 signing | Quantum-resistant authorization tokens throughout the service mesh |
| **P2** | Benchmark ML-KEM and ML-DSA performance across all GAIA-OS target platforms | Empirically validate latency and throughput budgets |
| **P2** | Deploy liboqs-rust bindings in the Tauri backend for Rust-native PQC operations | Eliminates Python round-trips for crypto operations in the Rust shell |
| **P3** | Evaluate SLH-DSA (SPHINCS+) as backup signature scheme for highest-assurance audit trail anchors | Diversifies cryptanalytic risk; avoids lattice assumption monoculture |

### 6.3 Long-Term Recommendations (Phase C — Phase 3+)

3. **FN-DSA (FALCON) integration** — Smaller signatures than ML-DSA (~666 bytes at Category 1 vs. ML-DSA-44's 2,420 bytes) when FIPS 206 fully stabilizes in liboqs.
4. **Crypto-agility infrastructure** — Automated algorithm discovery, deprecation, and rotation across the entire GAIA-OS cryptographic surface for policy-driven transitions over the next 10–20 years.
5. **NIST Round 4 monitoring** — Track HQC (code-based KEM) standardization as a backup KEM providing algorithmic diversity against future advances in lattice-based cryptanalysis.

---

## 7. Conclusion

The 2025–2026 period has definitively transformed post-quantum cryptography from a research discipline into an operational imperative. NIST's FIPS 203 and FIPS 204 standards provide the authoritative algorithm specifications. The NSA's CNSA 2.0 provides binding regulatory milestones in 2027, 2030, and 2035. The Open Quantum Safe liboqs library provides the production-hardened, independently audited implementation. And the hybrid cryptography model provides the practical transition path that preserves classical security guarantees while adding quantum resistance.

For GAIA-OS: ML-KEM-768 combined with X25519 in a hybrid TLS 1.3 handshake protects the Tauri–Python sidecar IPC and external-facing API endpoints. ML-DSA-65 signatures protect the consent ledger, cryptographic audit trail, and IBCT capability token system. ML-DSA-87 provides the highest-assurance tier for the Creator's private channel. And the liboqs-python and liboqs-rust bindings provide native-language access across the full GAIA-OS technology stack.

The harvest-now-decrypt-later threat means that every day of plaintext communication is a day of data permanently lost to future quantum adversaries. As the Cloud Security Alliance articulates: the appropriate time to start was yesterday. The next best time is today.

---

**Disclaimer:** This report synthesizes findings from 19+ sources including NIST FIPS publications, IETF Internet-Drafts, peer-reviewed conference papers, production engineering guides, and open-source project documentation from 2025–2026. Post-quantum cryptography is a rapidly evolving field; algorithm security assessments and standardization timelines may change with subsequent cryptanalytic advances. ML-KEM (FIPS 203) and ML-DSA (FIPS 204) are standardized as of August 2024 and represent the most thoroughly analyzed post-quantum algorithms available; the recommended hybrid approach provides defense-in-depth against any future discoveries. The liboqs library has been independently audited by Trail of Bits (public report April 2025); organizations deploying liboqs in production should review this audit and conduct their own threat modeling. CNSA 2.0 requirements apply specifically to U.S. National Security Systems and contractors; private-sector deployments should evaluate their regulatory exposure based on applicable frameworks. All architectural recommendations should be validated against GAIA-OS's specific threat model, performance requirements, and regulatory obligations.
