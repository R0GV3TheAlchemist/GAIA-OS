# 🔐 Post-Quantum Cryptography: ML-KEM & ML-DSA — A Comprehensive 2025/2026 Survey for GAIA-OS

**Date:** May 2, 2026
**Status:** Comprehensive Technical Survey (30+ sources)
**Relevance to GAIA-OS:** This report establishes the definitive survey of NIST-standardized post-quantum cryptographic algorithms—ML-KEM (FIPS 203, formerly CRYSTALS-Kyber) and ML-DSA (FIPS 204, formerly CRYSTALS-Dilithium)—which are already deployed in the GAIA-OS codebase. It covers the complete technology stack from mathematical foundations through algorithm specifications, performance benchmarking across all security levels and deployment tiers, production-grade implementation in the liboqs ecosystem and major cloud platforms, formal verification infrastructure, the hybrid cryptography deployment model, the regulatory landscape driving mandatory migration, and specific integration pathways for every cryptographic surface within the GAIA-OS architecture.

---

## Executive Summary

The 2025–2026 period marks the decisive transition of post-quantum cryptography from research standardization to operational deployment. On August 13, 2024, NIST published three foundational Federal Information Processing Standards: **FIPS 203** (ML-KEM), **FIPS 204** (ML-DSA), and **FIPS 205** (SLH-DSA). A fourth standard, **FIPS 206** (FN-DSA, derived from FALCON), followed in 2025. These algorithms are now embedded in production protocols including TLS 1.3, SSH, IKEv2, and PKI infrastructure, with AWS, Google Cloud, and Cloudflare having deployed ML-KEM hybrid key exchange across their global infrastructures by April 2026.

Five converging forces define the current landscape:

1. **Performance profile comprehensively characterized.** ML-KEM-768 operates at sub-millisecond latency on commodity hardware, matching classical X25519. On ARM Cortex-M0+ at 133 MHz, ML-KEM-512 completes a full key exchange in ~35.7 ms—approximately **172× faster** than ECDH P-256 on the same hardware. ML-DSA-44 verification completes in just 0.507 ms on modern IoT-class hardware.

2. **The liboqs ecosystem has reached production maturity.** The Open Quantum Safe project’s liboqs library (Linux Foundation PQCA) has completed integration of final FIPS 203/204 implementations (v0.11.0–v0.15.0), with language bindings for C, Python, Rust, Dart, Go, and JavaScript/TypeScript. Independently security-audited by Trail of Bits (April 2025).

3. **The hybrid cryptography model has been standardized and deployed at scale.** The IETF has specified three hybrid key agreements for TLS 1.3: X25519MLKEM768, SecP256r1MLKEM768, and SecP384r1MLKEM1024. AWS KMS, ACM, and Secrets Manager support ML-KEM hybrid TLS and ML-DSA signatures in production. JDK 27 integrates hybrid key exchange natively via JEP 527.

4. **The regulatory timeline has compressed dramatically.** Google’s March 2026 whitepaper demonstrated that breaking 256-bit ECC requires ~20× fewer physical qubits than previously estimated. **NSA CNSA 2.0 mandates compliance by January 1, 2027** for all new National Security System acquisitions. The EU Coordinated Roadmap sets December 31, 2026 as the deadline for initial national transition roadmaps.

5. **Formal verification has achieved end-to-end security proofs.** Amazon’s `mlkem-native` delivers 2.0–2.4× performance gains over the reference implementation while maintaining machine-checked proofs of memory safety, type safety, and functional correctness using CBMC and SLOTHY. PQShield has formally verified AVX2 rejection sampling for ML-KEM using the EasyCrypt proof assistant.

The central finding for GAIA-OS: the post-quantum cryptographic primitives already integrated into the codebase—ML-KEM and ML-DSA via liboqs—are production-hardened, independently audited, formally verified, and deployed at global scale. The GAIA-OS integration maps onto every cryptographic surface: Tauri–Python sidecar IPC (hybrid X25519MLKEM768 TLS), consent ledger and audit trail (ML-DSA-65 signatures), Creator’s private channel (ML-KEM-1024 hybrid key exchange), and planetary sensor mesh (ML-KEM-512 on constrained edge devices).

---

## 1. The Quantum Threat and the Standardization Response

### 1.1 Shor’s Algorithm and the Cryptographic Risk

Classical public-key cryptography—RSA, Diffie-Hellman, ECDH, ECDSA—derives its security from the computational hardness of integer factorization and the discrete logarithm problem. In 1994, Peter Shor demonstrated that a sufficiently powerful quantum computer could solve both problems in polynomial time, rendering all widely deployed asymmetric cryptography insecure.

Google Quantum AI’s March 2026 whitepaper demonstrated that breaking 256-bit ECC requires approximately **20× fewer physical qubits** than previously estimated, projecting a cryptographically relevant quantum computer (CRQC) as early as 2028–2029.

The **“harvest now, decrypt later” (HNDL) threat** amplifies urgency: adversaries are already passively collecting encrypted traffic today for future quantum decryption. For any data that must remain confidential beyond ~2030–2035, migration to quantum-resistant algorithms is a present-day operational requirement. This concern is amplified by the billions of IoT devices with 10–20-year operational lifespans deployed in critical infrastructure.

### 1.2 The NIST Standards: FIPS 203, 204, 205, 206

| Standard | Algorithm | Basis | Purpose |
|----------|-----------|-------|---------|
| **FIPS 203** | ML-KEM (CRYSTALS-Kyber) | Module-LWE | Key-Encapsulation Mechanism |
| **FIPS 204** | ML-DSA (CRYSTALS-Dilithium) | Module-LWE + Module-SIS | Digital Signatures |
| **FIPS 205** | SLH-DSA (SPHINCS+) | Hash functions | Backup digital signatures |
| **FIPS 206** | FN-DSA (FALCON) | NTRU lattices | Compact digital signatures |
| **HQC** *(draft 2026)* | Hamming Quasi-Cyclic | Error-correcting codes | Backup KEM (code-based diversity) |

NIST mandates that U.S. federal systems migrate to these standards by 2035.

### 1.3 Algorithm Security Levels

#### ML-KEM Security Levels

| Parameter Set | NIST Category | Public Key | Ciphertext | Secret Key | Use Case |
|---------------|---------------|------------|------------|------------|----------|
| **ML-KEM-512** | Cat. 1 (AES-128) | 800 B | 768 B | 1,632 B | Constrained edge (IoT, sensor mesh) |
| **ML-KEM-768** | Cat. 3 (AES-192) | 1,184 B | 1,088 B | 2,400 B | General production (TLS, IPC) |
| **ML-KEM-1024** | Cat. 5 (AES-256) | 1,568 B | 1,568 B | 3,168 B | Highest assurance (Creator channel) |

#### ML-DSA Security Levels

| Parameter Set | NIST Category | Public Key | Signature | Use Case |
|---------------|---------------|------------|-----------|----------|
| **ML-DSA-44** | Cat. 2 | 1,312 B | 2,420 B | IoT authentication |
| **ML-DSA-65** | Cat. 3 | 1,952 B | 3,309 B | Consent ledger, audit trail |
| **ML-DSA-87** | Cat. 5 | 2,592 B | 4,595 B | Creator channel (NSA CNSA 2.0 mandatory) |

Note: ML-DSA-87 signatures are ~71× the size of an Ed25519 signature (64 bytes). NSA CNSA 2.0 mandates ML-KEM-1024 and ML-DSA-87 for all classification levels.

---

## 2. Performance Characteristics: From Cloud to Constrained Edge

### 2.1 Server-Class Performance

On commodity server hardware, ML-KEM operations complete in microseconds. An authenticated post-quantum session protocol integrating ML-KEM-1024 with ML-DSA-65 and AES-256-GCM demonstrated “sub-millisecond cryptographic overhead” across 1,000 iterations, with handshake cryptographic latency in the 0.50–0.70 ms range under both local and WAN-emulated (~40 ms RTT) conditions.

Amazon’s `mlkem-native` achieves **2.0–2.4× performance gains** over the ML-KEM reference implementation on EC2 c7i and c7g instances while maintaining formal verification guarantees. AWS has integrated this implementation into AWS-LC, the FIPS-validated cryptographic library powering billions of daily cryptographic operations.

### 2.2 Constrained Edge: ARM Cortex-M0+ Benchmarks

The first isolated algorithm-level benchmarks on the ARM Cortex-M0+ (RP2040 at 133 MHz, 264 KB SRAM) using PQClean reference C implementations (Chhetri, April 2026):

| Operation | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|-----------|------------|------------|-------------|
| Full key exchange | ~35.7 ms | ~56.8 ms | ~82.1 ms |
| Energy cost | ~2.83 mJ | — | — |
| vs. ECDH P-256 | **172× faster** | — | — |

For ML-DSA on constrained devices, signing exhibits high latency variance due to rejection sampling (CV: 66–73%). The 99th-percentile for ML-DSA-87 can reach up to 1,125 ms—acceptable for infrequent operations (credential issuance, consent ledger signing) but must be accounted for in latency budgets.

On modern IoT gateway-class hardware (ARM64): ML-DSA-44 verification in **0.507 ms**, signing in 1.869 ms. The ZeroRISC project provides architectural optimizations improving ML-KEM and ML-DSA performance by **6–9×** while reducing memory usage. Pairing ML-KEM-512 with ML-DSA-44 is **63% faster** than classical ECDHE P-256 with ECDSA under full certificate verification on embedded systems.

### 2.3 Hardware Acceleration

- **CAST PQC cores**: ML-KEM and ML-DSA silicon implementations for ASIC and FPGA platforms
- **Intel AVX-512**: ~2× speed improvement for ML-DSA key generation, signing, and verification
- **ML-DSA open-source hardware (ML-DSA-OSH)**: First open-source ML-DSA hardware; 16–36% average signing latency improvement through optimized rejection loop scheduling
- **SEALSQ QS7001**: Industry’s first hardware-embedded post-quantum security chip integrating ML-KEM and ML-DSA at silicon level

### 2.4 Hybrid KEM Combiners: Panther (April 2026)

**Panther** presents six robust hybrid KEM combiners pairing FrodoKEM (unstructured LWE) with ML-KEM (module-LWE, FIPS 203), providing IND-CCA2 security whenever either assumption is hard. The novel Panther-SS construction interleaves constituent ciphertexts and binds cut-positions via a structural tag, achieving full robustness with **combiner-only overhead below 0.5% of total latency**. This is directly relevant to GAIA-OS’s highest-assurance cryptographic pathways.

---

## 3. The liboqs Ecosystem

### 3.1 Architecture and Maturity

The Open Quantum Safe (OQS) project’s liboqs library is the foundational open-source C library for quantum-resistant cryptographic algorithms, hosted under the Linux Foundation’s Post-Quantum Cryptography Alliance (PQCA) with industry partners including AWS and NVIDIA.

**Release history (ML-KEM/ML-DSA integration):**
- **v0.11.0:** Final FIPS 203/204 implementations integrated
- **v0.12.0–v0.14.0:** Legacy NIST Round 3 Kyber/Dilithium systematically removed
- **v0.15.0:** Current production release

**Language bindings:**
- `liboqs-python` — Python (GAIA-OS FastAPI backend)
- `liboqs-rust` v0.11.0 — Rust (GAIA-OS Tauri desktop backend)
- `@noble/post-quantum` — JavaScript/TypeScript (GAIA-OS PWA)
- `oqs` v2.1.4 — Dart (Flutter mobile)
- `liboqs-go` — Go (microservices)

**Security audit:** Trail of Bits independent security audit, public report published April 2025.

### 3.2 Formal Verification

**Amazon `mlkem-native`:** Machine-checked proofs of memory safety, type safety, and functional correctness using CBMC (bounded model checker) and SLOTHY (assembly optimizer). The “end-to-end” verification chain links highly optimized assembly code through a high-level machine-readable specification to the IND-CCA2 security notion.

**PQShield EasyCrypt:** Formally verified AVX2 rejection sampling for ML-KEM using the EasyCrypt proof assistant.

---

## 4. Production Deployments

### 4.1 Cloud Provider Deployments

| Provider | Deployment | Status |
|----------|-----------|--------|
| **AWS** | ML-KEM hybrid TLS in KMS, ACM, Secrets Manager; `mlkem-native` in AWS-LC | Production, April 2026 |
| **Cloudflare** | X25519MLKEM768 across global network (supported + preferred modes) | Production, April 2026 |
| **Google** | ML-KEM hybrid in Chrome and GCP; internal 2029 PQC migration deadline | Production (TLS), deploying |
| **JDK 27** | Hybrid key exchange via JEP 527 (native, no code changes) | Available 2026 |

### 4.2 Protocol Integration

- **TLS 1.3:** IETF-standardized hybrid groups X25519MLKEM768, SecP256r1MLKEM768, SecP384r1MLKEM1024
- **SSH:** ML-KEM hybrid key exchange integrated into OpenSSH
- **IKEv2/IPsec:** ML-KEM hybrid for VPN and network security
- **PKI/X.509:** ML-DSA certificates for code signing, authentication, and identity

---

## 5. Regulatory Landscape

| Jurisdiction | Mandate | Deadline |
|-------------|---------|----------|
| **NSA CNSA 2.0** | All new NSS acquisitions must be CNSA 2.0 compliant (ML-KEM-1024 + ML-DSA-87) | **January 1, 2027** |
| **NIST (US Federal)** | Full migration to FIPS 203/204/205 | 2035 |
| **EU Coordinated Roadmap** | Initial national transition roadmaps | December 31, 2026 |
| **EU (full transition)** | Complete post-quantum migration | 2035 |
| **Google internal** | Internal PQC migration deadline | **2029** |
| **Canada, Australia, G7** | Comparable timelines to EU/US | 2030–2035 |

---

## 6. The GAIA-OS Cryptographic Surface

### 6.1 Cryptographic Surface Map

| Domain | Classical Algorithm | PQC Replacement | Key Exchange | Digital Signatures | Tier |
|--------|--------------------|------------------|--------------|--------------------|----- |
| **Tauri–Python Sidecar IPC** | Plain HTTP/localhost | TLS 1.3 hybrid X25519MLKEM768 | X25519 + ML-KEM-768 | EdDSA → ML-DSA-65 | Server/Desktop |
| **Creator Private Channel** | ECDH + EdDSA | TLS 1.3 + ML-KEM-1024 hybrid | X25519 + ML-KEM-1024 | ML-DSA-87 | Highest Assurance |
| **Consent Ledger Signing** | Ed25519 | ML-DSA-65 | N/A | ML-DSA-65 | Production |
| **Audit Trail Signatures** | Ed25519 | ML-DSA-65 + Ed25519 dual-sig | N/A | ML-DSA-65 | Production |
| **Planetary Sensor Mesh** | ECDH P-256 + ECDSA | ML-KEM-512 + ML-DSA-44 | ML-KEM-512 | ML-DSA-44 | Constrained Edge |
| **Database Encryption** | AES-256-GCM | Unchanged (Grover-tolerant) | N/A | N/A | Production |
| **Web/PWA TLS** | X25519 + ECDSA | X25519MLKEM768 | X25519 + ML-KEM-768 | ML-DSA-65 | Client-dependent |
| **Service-to-Service Auth** | EdDSA | ML-DSA-65 | N/A | ML-DSA-65 | Production |

### 6.2 Hybrid Deployment Strategy

The recommended strategy follows the hybrid model validated by AWS, Cloudflare, and the IETF:

- **TLS endpoints:** ML-KEM hybrid key exchange alongside classical ECDHE, with traffic key derived from both shared secrets (must break both to compromise the session)
- **Digital signatures:** ML-DSA-65 + Ed25519 dual-signature regime (both must verify), migrating to ML-DSA-only once algorithms achieve sufficient cryptanalytic maturity
- **Consent ledger/audit trail:** ML-DSA-65 primary + Ed25519 co-signature
- **Constrained edge:** ML-KEM-512 + ML-DSA-44 (63% faster than classical ECDHE P-256 + ECDSA on embedded hardware)
- **Highest assurance (Creator channel):** Panther-SS combiner (FrodoKEM + ML-KEM-1024) for defense-in-depth against advances in lattice cryptanalysis

### 6.3 The liboqs Integration Architecture

The recommended liboqs integration leverages:
- `liboqs-python` for the GAIA-OS FastAPI backend
- `liboqs-rust` v0.11.0 for the Tauri desktop backend
- `@noble/post-quantum` for the PWA browser frontend

A unified `crypto/pqc.py` module exposes `generate_kem_keypair()`, `encapsulate()`, `decapsulate()`, `sign()`, and `verify()` with automatic algorithm selection by configured security level and automatic classical fallback.

### 6.4 Performance Budgets for GAIA-OS Operations

| Operation | Algorithm | Expected Latency | Notes |
|-----------|-----------|-----------------|-------|
| TLS handshake key exchange | X25519MLKEM768 | 0.50–0.70 ms | Sub-millisecond; no UX impact |
| Consent ledger signature | ML-DSA-65 | 1–10 ms (signing) | Infrequent; variance acceptable |
| Audit trail signature | ML-DSA-65 | 1–10 ms (signing) | Infrequent; variance acceptable |
| Sensor mesh key exchange | ML-KEM-512 | ~35.7 ms | On Cortex-M0+; acceptable for IoT |
| Sensor authentication | ML-DSA-44 | 0.507 ms (verify) | On ARM64 gateway |
| Creator channel session | ML-KEM-1024 + Panther | ~82.1 ms | Session establishment only |

---

## 7. Immediate Recommendations

| Priority | Action | Rationale |
|----------|--------|-----------|
| **P0** | Update liboqs to v0.15.0 and remove legacy NIST Round 3 Kyber/Dilithium dependencies | Legacy versions are being removed upstream; maintain alignment with FIPS 203/204 final specifications |
| **P0** | Enable X25519MLKEM768 hybrid TLS on the Tauri–Python sidecar IPC channel | Protects against HNDL attacks; validated by AWS, Cloudflare, and IETF |
| **P0** | Migrate consent ledger and audit trail to ML-DSA-65 + Ed25519 dual-signature | Addresses NSA CNSA 2.0 timeline; dual-sig provides defense-in-depth |
| **P1** | Deploy ML-KEM-512 + ML-DSA-44 on the planetary sensor mesh edge nodes | 63% faster than classical on Cortex-M0+; eliminates HNDL exposure for IoT traffic |
| **P1** | Implement Panther-SS FrodoKEM + ML-KEM-1024 combiner for the Creator private channel | Defense-in-depth against lattice cryptanalysis advances; <0.5% overhead |
| **P2** | Migrate to `mlkem-native` (Amazon formal verification) as primary ML-KEM backend | 2.0–2.4× performance improvement; machine-checked safety and correctness proofs |
| **P2** | Integrate HQC backup KEM when FIPS draft is finalized (2026) | Code-based algorithmic diversity against potential future lattice breaks |

---

## 8. Conclusion

The 2025–2026 period has transformed post-quantum cryptography from a standardization project into an operational discipline with production deployments at AWS, Cloudflare, Google, and across national security infrastructures globally. The NIST FIPS 203/204 standards are final. The liboqs library is production-hardened and independently audited. The hybrid TLS 1.3 groups are IETF-standardized and deployed at internet scale. The NSA CNSA 2.0 mandate takes effect January 1, 2027—eight months from now.

For GAIA-OS, the post-quantum cryptographic primitives are already integrated. The work remaining is deployment hardening: migrating from legacy Kyber/Dilithium to final FIPS 203/204 implementations, enabling hybrid TLS on all communication channels, deploying dual-signature regimes on the consent ledger and audit trail, and protecting the planetary sensor mesh with ML-KEM-512. The performance benchmarks confirm that these migrations impose negligible latency on server-class hardware and are 63% faster than classical alternatives on constrained edge devices. The regulatory window is closing. The implementation path is clear.

---

**Disclaimer:** This report synthesizes findings from 30+ sources including NIST FIPS publications, peer-reviewed cryptographic literature, AWS/Cloudflare/Google security documentation, arXiv preprints, and industry analyses from 2025–2026. Algorithm security is based on current cryptanalytic knowledge; advances in lattice cryptanalysis could affect security assessments. Performance benchmarks are hardware- and implementation-specific; results should be validated on GAIA-OS target hardware before deployment. The HNDL threat model involves uncertainty; migration timelines should be calibrated to data sensitivity. All cryptographic implementations should undergo independent security review before production deployment.
