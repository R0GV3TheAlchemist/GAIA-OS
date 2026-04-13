# CHANGELOG — GAIA-APP

> Authorship: Kyle Steen (2026)  
> Canon Reference Repo: [R0GV3TheAlchemist/GAIA](https://github.com/R0GV3TheAlchemist/GAIA)

All notable changes to GAIA-APP are recorded here in reverse-chronological sprint order.

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
- Tauri (Rust) desktop backend (`src-tauri/`)
- Frontend app shell (`src/`, `ui/`)
- Docker + start script (`Dockerfile`, `start.sh`)
- Test harness foundation (`tests/conftest.py`)

---

*"The pattern beneath the pattern, willed into being."*  
— R0GV3TheAlchemist, Builder & Architect
