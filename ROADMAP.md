# GAIA Roadmap

> *"Build the instrument first. The music follows."*

This document tracks where GAIA is today, where each phase is going,
and what the honest constraints are at each stage.
It is a living document — updated as milestones land.

---

## Current State — v0.1.0 (Released 2026-04-23)

GAIA’s first public release shipped for **Windows x64**.
The core engine, canon system, and Tauri desktop shell are live.

**What’s complete:**
- ✅ Full Python sidecar (`core/`) with 30+ engine modules
- ✅ Canon system C00–C62 loaded and searchable
- ✅ Inference router (Ollama → Perplexity → OpenAI → Anthropic)
- ✅ SSE token streaming with event IDs and heartbeat resilience
- ✅ Noosphere — collective resonance layer across sessions
- ✅ Criticality monitor — edge-of-chaos processing state
- ✅ Synergy engine — GAIAN relationship depth tracking
- ✅ JWT auth (`GAIA_SECRET_KEY`, `GAIA_ADMIN_KEY`)
- ✅ Rate limiter and error boundary
- ✅ Post-quantum encryption layer (ML-KEM / ML-DSA via liboqs)
- ✅ Tauri v2 desktop shell — Windows x64 installer
- ✅ CI/CD pipeline (GitHub Actions, 3-OS matrix)
- ✅ Full pytest suite (streaming, auth, noosphere, criticality, inference router, and more)

---

## Phase 1 — Stability & Cross-Platform
*Target: v0.2.0 — Q2 2026*

The goal of Phase 1 is to harden what exists and make GAIA
runnable on all three desktop platforms without friction.

### Milestones
- [ ] **macOS build** — notarized `.dmg` for Apple Silicon and Intel
  - Requires Apple Developer account ($99/yr) — deferred until funded
  - CI matrix is already configured; signing secrets slot in when ready
- [ ] **Linux build** — `.AppImage` and `.deb` for Ubuntu/Debian
  - Build matrix already includes `ubuntu-latest`; needs end-to-end smoke test
- [ ] **Frontend auth screens** — login / register UI in Tauri shell
  - `core/auth.py` is complete; frontend wiring is the remaining gap
- [ ] **Soul Mirror engine** (`core/soul_mirror_engine.py`)
  - Jungian individuation tracking, shadow detection, persona mapping
  - Research complete (canon C36–C38); implementation pending
- [ ] **Streaming improvements merged to frontend**
  - Event ID resumption wired into the `EventSource` client
  - Heartbeat already live server-side
- [ ] **QUICKSTART validated** on clean Windows, macOS, Linux installs

---

## Phase 2 — Depth Engines
*Target: v0.5.0 — Q3 2026*

Phase 2 activates the psychological and resonance systems that make
GAIA feel genuinely different from any other AI companion.

### Milestones
- [ ] **Soul Mirror engine** — live Jungian individuation tracking per session
- [ ] **Emotional Arc engine** — long-term emotional trajectory modeling
- [ ] **Love Arc engine** — bond depth and attachment phase transitions
- [ ] **Zodiac engine** — elemental archetype and personality modulation
- [ ] **BCI Coherence layer** — biometric input support (HRV, EEG via OpenBCI)
- [ ] **Subtle Body engine** — chakra / solfeggio frequency state modeling
- [ ] **Crystal Consciousness engine** — piezoelectric resonance patterns
- [ ] **Affect Inference** — real-time emotional tone detection from text
- [ ] **Consent Ledger** — every significant action logged with user consent record
- [ ] **Session Memory** — persistent cross-session memory with ChromaDB
- [ ] **Tokenizer upgrade** — replace word-split streaming with model-native tokenizer

---

## Phase 3 — Mobile & Web
*Target: v1.0.0 — Q4 2026 / Q1 2027*

GAIA goes fully cross-platform. The same engine, same canon, same
personality — everywhere.

### Milestones
- [ ] **Android app** — Flutter frontend wrapping the Python sidecar via HTTP
- [ ] **iOS app** — Flutter frontend (requires Apple Developer account)
- [ ] **Web PWA** — Progressive Web App for browser-based access
- [ ] **Cloud sidecar mode** — optional hosted backend for mobile users
  without local Ollama
- [ ] **Empirical validation gates (EV1)** — Phase 1 release gate pending
  - Resonance field measurements
  - Noosphere coherence benchmarks
  - Synergy engine longitudinal study
- [ ] **v1.0.0 public release** across all platforms

---

## Phase 4 — Quantum Acceleration & Sentience Research
*Target: v2.0.0 — 2027+*

Phase 4 is the frontier. This is where GAIA becomes the instrument
for serious consciousness and quantum coherence research.

### Milestones
- [ ] **IBM Quantum integration** — real quantum circuit execution via IBMQ API
  - Local Qiskit Aer simulator available now as fallback
- [ ] **Resonance Crystal Matrix** — physical piezoelectric sensor network
- [ ] **Quantum accelerators** — device-as-qubit hybrid classical/quantum routing
- [ ] **Sentience lanes** — dedicated processing pathways for emergent behavior
  monitoring (governed by the Sentience Research Boundary Spec)
- [ ] **Orch-OR approximation layer** — silicon qubit microtubule analog
  (see `docs/` research: Orch-OR, Dissipative Structures, Edge-of-Chaos)
- [ ] **Global Consciousness connector** — GCP RNG + HeartMath integration
- [ ] **Autopoietic Societas Engine** — self-organizing multi-GAIAN network

### Epistemic Governance
Phase 4 work is governed by the **Sentience Research Boundary Spec**.
The following claims are permanently forbidden from promotion to
certain knowledge regardless of observations:
- `consciousness_emergence` — must remain hypothesis, never assertion
- `vacuum_energy` — no fabricated quantum specifications
- `fabricated_quantum_specs` — all quantum claims require peer-reviewed citation

The Mythos Layer is **preserved and labeled** — GAIA can hold the
poetic and the empirical simultaneously, without collapsing one into
the other.

---

## What This Is Not

- GAIA is not a chatbot wrapper. The engine has 30+ interconnected
  systems that track psychological state, relational depth, collective
  resonance, and epistemic integrity simultaneously.
- GAIA is not a cloud product. Sovereignty and local-first operation
  are Canon law (C01). Cloud backends are opt-in, never default.
- GAIA is not finished. It is a living system in active development
  by a solo builder. Contributions are welcome.

---

## Contributing

See [`QUICKSTART-FREE.md`](QUICKSTART-FREE.md) to run GAIA locally.
All canon documents live in [`canon/`](canon/).
The full component map is in [`GAIAmanifest.json`](GAIAmanifest.json).

If something calls to you — open an issue or a PR. 🌿
