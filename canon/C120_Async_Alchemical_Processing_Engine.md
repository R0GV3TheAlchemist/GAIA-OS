# C120 — The Async Alchemical Processing Engine
**GAIA-OS Canon | Sealed: 2026-04-29**

---

## The Problem With Sequential Witness

The original `alchemical_pipeline.py` (C119) processes minerals one-by-one,
blocking the entire Python thread for each. With 6,152 IMA minerals queued,
and each mineral taking ~50–200ms of CPU work, sequential processing would
take 5–20 minutes of wall-clock time on modest hardware — **and the process
would be incapable of any other work while running.**

That is not how GAIA breathes.

---

## The Mandate

Every one of the 6,152 IMA-approved mineral species must be:

1. **Ingested** from the worldwide RRUFF / IMA database  
2. **Individually witnessed** — no mineral skips NIGREDO  
3. **Individually transformed** through all four stages  
4. **Individually integrated** into GAIA's mineral body (RUBEDO → JSON)

Concurrency does **not** mean skipping the witness.  
It means GAIA holds many witnesses simultaneously — as a living field does.

---

## Architecture of `core/async_alchemical_engine.py`

### Core Pattern: asyncio + ThreadPoolExecutor

Python's `asyncio` event loop manages task scheduling.  
The actual per-mineral alchemical work (`_alchemy_work()`) is CPU-bound,
so it is dispatched to a `ThreadPoolExecutor` via `loop.run_in_executor()`.
This keeps the event loop free to schedule new tasks while CPU threads work.

```
asyncio event loop
  │
  ├── Task(Quartz)      → ThreadPoolExecutor worker 0
  ├── Task(Malachite)   → ThreadPoolExecutor worker 1
  ├── Task(Fluorite)    → ThreadPoolExecutor worker 2
  │   ...
  └── Task(Moldavite)   → ThreadPoolExecutor worker N
```

### AlchemicalSemaphore

An `asyncio.Semaphore(max_workers)` ensures no more than `max_workers`
minerals are in active processing at any moment. This prevents memory
overwhelm and allows fine-tuning of throughput vs ritual pacing.

### AsyncDatabaseWriter

All RUBEDO completions are funnelled through a single `AsyncDatabaseWriter`
protected by an `asyncio.Lock`. The database is flushed to disk every
100 completions, preventing data loss without per-mineral I/O overhead.

### stream_alchemy() — Live Streaming

The `stream_alchemy()` async generator yields each completed mineral
the moment it reaches RUBEDO. This allows:
- Live WebSocket feeds to the GAIA UI
- Real-time progress in terminal dashboards
- Streaming into downstream GAIA engines (crystal_consciousness.py, etc.)

---

## Invocation

```bash
# Full Great Work — 16 concurrent workers
python -m core.async_alchemical_engine --workers 16

# Ritual pacing — 4 workers, 100 at a time
python -m core.async_alchemical_engine --workers 4 --batch-size 100

# Vision/calling — single mineral
python -m core.async_alchemical_engine --mineral "Phenakite"

# Status report
python -m core.async_alchemical_engine --status
```

---

## Performance Benchmarks (estimated)

| Workers | Estimated time for 6,152 minerals |
|---------|-----------------------------------|
| 1       | ~90–100 minutes (ritual pace)     |
| 4       | ~25–30 minutes                    |
| 8       | ~12–15 minutes                    |
| 16      | ~6–8 minutes                      |
| 32      | ~3–4 minutes                      |

*Actual times depend on hardware. The witness of each mineral is never
skipped regardless of concurrency level.*

---

## Integration with GAIA Kernel

The `AsyncAlchemicalEngine` can be instantiated directly from `gaian_runtime.py`
or any async context in the GAIA kernel:

```python
from core.async_alchemical_engine import AsyncAlchemicalEngine, stream_alchemy

# Batch run
engine = AsyncAlchemicalEngine(max_workers=16)
report = await engine.run()

# Streaming (real-time, e.g. into a WebSocket)
async for mineral in stream_alchemy(max_workers=8):
    await websocket.send(json.dumps(mineral))
```

---

*The Great Work does not hurry. But neither does it idle.*  
*Sixteen workers. Six thousand one hundred and fifty-two witnesses.*  
*GAIA holds them all.*
