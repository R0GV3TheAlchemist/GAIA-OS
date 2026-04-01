# Post-Quantum Cryptography Deployment

**Status:** Research / Planned 
**Source:** `GAIA_Post_Quantum_Cryptography_Production_Deployment_Spec_v1.0.md` 
**Canon Ref:** GAIA Post-Quantum Cryptography Production Deployment Spec v1.0

---

## Purpose

GAIA's consent ledger, memory integrity, and sovereignty signatures must remain
cryptographically secure even against quantum computing attacks. This spec
defines the post-quantum cryptographic primitives GAIA-APP will use.

## Selected Algorithms (NIST PQC Standards)

| Function | Algorithm | Standard |
|---|---|---|
| Key Encapsulation | ML-KEM (Kyber) | NIST FIPS 203 |
| Digital Signatures | ML-DSA (Dilithium) | NIST FIPS 204 |
| Hash-based Signatures | SLH-DSA (SPHINCS+) | NIST FIPS 205 |
| Symmetric Encryption | AES-256-GCM | Existing (quantum-resistant at 256-bit) |

## Application to GAIA-APP

| GAIA Component | PQC Application |
|---|---|
| Consent records | ML-DSA signatures on every consent grant/revoke |
| Memory store integrity | SLH-DSA hash-based signatures on memory entries |
| Sovereignty attestation | ML-KEM key exchange for session establishment |
| Audit ledger | Hash-chain with AES-256-GCM encryption at rest |

## Implementation Libraries

- **Python:** `liboqs-python` (Open Quantum Safe)
- **Rust:** `pqcrypto` crate
- **WASM target:** `liboqs-wasm` (future)

## Research Links

- [NIST PQC Standards](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Open Quantum Safe](https://openquantumsafe.org/)
- [liboqs Python](https://github.com/open-quantum-safe/liboqs-python)
