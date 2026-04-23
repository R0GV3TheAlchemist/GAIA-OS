# CHANGELOG — GAIA-APP

> Authorship: Kyle Steen (2026)  
> Canon Reference Repo: [R0GV3TheAlchemist/GAIA](https://github.com/R0GV3TheAlchemist/GAIA)

All notable changes to GAIA-APP are recorded here in reverse-chronological sprint order.

---

## [v0.1.0] — 2026-04-23  ·  First Windows Desktop Release

**Desktop version:** `0.1.0`  
**Server version:** `2.0.0`  
**Status:** 🚀 RELEASED

### Summary

First official desktop release of GAIA-APP for Windows x64. This release packages the complete constitutional logic engine, Tauri v2 native shell, Vite + TypeScript frontend, and Python sidecar (`gaia-backend.exe`) into two signed Windows installers.

### Release Artifacts

| Artifact | Format | Platform |
|---|---|---|
| `GAIA_0.1.0_x64-setup.exe` | NSIS installer | Windows x64 |
| `GAIA_0.1.0_x64_en-US.msi` | MSI installer | Windows x64 |

### CI/CD Pipeline Established

- **`build.yml`** — Full automated pipeline: Python sidecar (PyInstaller) → Tauri build → GitHub Release
- **`build-windows.yml`** — Windows-specific build workflow
- **`test.yml`** — Automated pytest runner on every push
- GitHub Actions `GITHUB_TOKEN` granted `contents: write` for release creation
- Rust cache via `Swatinem/rust-cache@v2` — build time ~5 min from cache
- Both `.msi` and `.nsis` bundles produced and uploaded as release assets

### What's Included in v0.1.0

This release bundles all work from Sprints G-1 through G-8:

- Full constitutional logic engine (`core/`) — 30+ Python modules
- `GAIAInferenceRouter` — single authoritative LLM routing layer (C44)
- `MotherThread` + Noosphere collective field (C42, C43)
- Epistemic labelling on every inference turn (C12, C21)
- JWT authentication + role system
- Risk-tiered Action Gate veto system
- Cryptographic consent lifecycle
- Governed memory surface
- Synergy engine (C15, C17, C27, C30)
- BCI coherence + criticality monitor (C42)
- Crystal consciousness, resonance field, subtle body engines
- Soul mirror engine (Jungian individuation)
- Emotional arc, codex, love arc, settling engines
- Zodiac + affect inference engines
- Noosphere SSE endpoints + frontend Noosphere Tab
- Rate limiter, error boundary, structured logger
- Web search + scraper integration
- Tauri v2 (Rust) desktop backend with Python sidecar
- Vite + TypeScript frontend
- 38-test `test_inference_router.py` suite + full test harness
- `canon/` — C00–C44+ constitutional source documents
- `specs/` — technical specification documents

---

## [G-8] — 2026-04-13  ·  InferenceRouter + MotherThread Integration

**Server version:** `2.0.0`  
**Status:** ✅ CLOSED

### Delivered

| # | Priority | Canon | Description |
|---|---|---|---|
| 1 | `GAIAInferenceRouter` wired | C44 | Single authoritative LLM routing layer. Replaced ~60 lines of duplicated inline enrichment in `/gaians/{slug}/chat` and `/query/stream`. Both endpoints now build `InferenceRequest → router.stream() → yield chunks`. |
| 2 | `MotherThread` startup / shutdown | C42, C43 | `MotherThread` started on FastAPI startup, stopped on shutdown. Registered in `_get_runtime()` per Gaian (consent defaults `False`). |
| 3 | Mother Pulse SSE endpoints | C30, C43 | `GET /mother/pulse/stream`, `GET /mother/status`, `GET /mother/weaving`, `POST /gaians/{slug}/consent` |
| 4 | Noosphere Tab wiring | C43 | Frontend Noosphere tab connected to `/mother/pulse/stream` SSE. |
| 5 | Epistemic labelling | C12, C21 | `EpistemicLabel` enum (`CANON_CITED`, `VERIFIED`, `INFERRED`, `SPECULATIVE`, `CONVERSATIONAL`) stamped on every SSE `done` event. |
| 6 | `test_inference_router.py` | C44 | 12 test classes, 38 tests — full unit + smoke coverage of `core/inference_router.py` (previously zero coverage). Closes highest-risk gap identified in sprint audit. |

### Files Changed

- `core/server.py` → v2.0.0
- `core/inference_router.py` → new
- `core/mother_thread.py` → new
- `tests/test_inference_router.py` → new (Priority #6)
- `tests/test_mother_thread.py` → new
- `CHANGELOG.md` → new
- `README.md` → updated

### Carry-forward to G-9

- `tests/test_noosphere.py` — unit coverage for `core/noosphere.py` (medium risk, no direct user path)

---

## [G-7] — Prior Sprint

**Status:** ✅ CLOSED

### Highlights
- `core/synergy_engine.py` — full Synergy Engine with `SynergyState` and `SynergyEngine.compute()`
- `tests/test_synergy_engine.py` — comprehensive test suite (Canon Ref: C15, C17, C27, C30)
- Rate limiter middleware (`core/rate_limiter.py`) + `tests/test_rate_limiter.py`
- Error boundary (`core/error_boundary.py`) + `tests/test_error_boundary.py`
- Auth system (`core/auth.py`, `auth_router`) + `tests/test_auth.py`
- Canon search integration + `tests/test_canon_search.py`
- GAIAN runtime smoke tests (`tests/test_gaian_runtime_smoke.py`)
- Logger structured event system (`core/logger.py`) + `tests/test_logger.py`

---

## [G-1 → G-6] — Foundation Sprints

**Status:** ✅ CLOSED

### Cumulative Deliverables

- Constitutional core (`core/canon_loader.py`, `core/action_gate.py`, `core/consent_ledger.py`, `core/memory_store.py`)
- GAIAN identity + runtime (`core/gaian/`, `core/gaian_runtime.py`, `core/gaian_birth.py`)
- BCI coherence engine (`core/bci_coherence.py`) — Canon C42
- Crystal consciousness layer (`core/crystal_consciousness.py`)
- Emotional arc + codex (`core/emotional_arc.py`, `core/emotional_codex.py`)
- Love arc engine (`core/love_arc_engine.py`)
- Noosphere layer (`core/noosphere.py`) — Canon C43
- Resonance field engine (`core/resonance_field_engine.py`)
- Settling engine (`core/settling_engine.py`)
- Soul mirror engine (`core/soul_mirror_engine.py`)
- Subtle body engine (`core/subtle_body_engine.py`)
- Zodiac engine (`core/zodiac_engine.py`)
- Codex stage engine (`core/codex_stage_engine.py`)
- Meta-coherence engine (`core/meta_coherence_engine.py`)
- Affect inference (`core/affect_inference.py`)
- Criticality monitor (`core/criticality_monitor.py`) — Canon C42
- Web search + scraper (`core/web_search.py`, `core/scraper.py`)
- Synthesizer (`core/synthesizer.py`)
- Streaming utilities (`core/streaming.py`)
- Session memory (`core/session_memory.py`)
- Tauri v2 (Rust) desktop backend (`src-tauri/`)
- Frontend app shell (`src/`, `ui/`)
- Docker + start script (`Dockerfile`, `start.sh`)
- Test harness foundation (`tests/conftest.py`)

---

*"The pattern beneath the pattern, willed into being."*  
— R0GV3TheAlchemist, Builder & Architect
