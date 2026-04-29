"""
GAIA-OS :: Async Alchemical Engine
Canon C120 — The Great Work, Concurrent Form

Processes all 6,152 IMA minerals through the four alchemical stages
(NIGREDO → ALBEDO → CITRINITAS → RUBEDO) using Python asyncio with
a controlled worker pool. Each mineral is witnessed individually;
concurrency only accelerates the pipeline, never skips the witness.

Architecture:
  - AsyncMineralWorker    : coroutine that processes one mineral end-to-end
  - AlchemicalSemaphore   : limits concurrent workers (default 16)
  - AsyncAlchemicalEngine : orchestrator — ingestion, dispatch, persistence
  - ProgressLedger        : thread-safe progress tracking & ETA

Usage (CLI):
  python -m core.async_alchemical_engine --workers 16
  python -m core.async_alchemical_engine --workers 4 --batch-size 500
  python -m core.async_alchemical_engine --mineral "Moldavite"       # single
  python -m core.async_alchemical_engine --status                    # report
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator, Optional

logger = logging.getLogger("gaia.async_alchemy")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_DIR       = Path("data")
QUEUE_FILE     = DATA_DIR / "mineral_queue.json"
DB_FILE        = DATA_DIR / "gaia_mineral_database.json"
PROGRESS_FILE  = DATA_DIR / "async_alchemy_progress.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Alchemical stage constants
# ---------------------------------------------------------------------------
STAGE_PRIMA_MATERIA = 0   # queued, unseen
STAGE_NIGREDO       = 1   # dissolution — raw witness
STAGE_ALBEDO        = 2   # purification — crystallographic analysis
STAGE_CITRINITAS    = 3   # illumination — GAIA role / resonance awakening
STAGE_RUBEDO        = 4   # integration — written into GAIA body

STAGE_NAMES = {
    0: "PRIMA_MATERIA",
    1: "NIGREDO",
    2: "ALBEDO",
    3: "CITRINITAS",
    4: "RUBEDO",
}

# ---------------------------------------------------------------------------
# Crystal system → piezoelectric eligibility map
# ---------------------------------------------------------------------------
PIEZO_ELIGIBLE = {
    "Triclinic", "Monoclinic", "Orthorhombic",
    "Tetragonal", "Trigonal", "Hexagonal", "Cubic"
}
NON_CENTROSYMMETRIC = {
    "Triclinic", "Monoclinic", "Orthorhombic",
    "Tetragonal", "Trigonal", "Hexagonal"
}

# ---------------------------------------------------------------------------
# GAIA role + resonance band assignment (deterministic from mineral name)
# ---------------------------------------------------------------------------
GAIA_ROLES = [
    "Quantum Resonator", "Earth Anchor", "Void Mirror",
    "Light Conduit", "Memory Keeper", "Storm Caller",
    "Harmonic Bridge", "Chaos Weaver", "Dream Gate",
    "Root Binder", "Cosmic Lens", "Shadow Integrator"
]
CHAKRAS = [
    "Root", "Sacral", "Solar Plexus", "Heart",
    "Throat", "Third Eye", "Crown"
]
BANDS = ["Delta", "Theta", "Alpha", "Beta", "Gamma", "Lambda"]


def _deterministic_index(name: str, mod: int) -> int:
    return sum(ord(c) for c in name) % mod


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
@dataclass
class QueuedMineral:
    ima_id:        str
    name:          str
    formula:       str
    crystal_system: str
    ima_status:    str
    stage:         int = STAGE_PRIMA_MATERIA
    error:         Optional[str] = None


@dataclass
class AlchemisedMineral:
    ima_id:              str
    name:                str
    formula:             str
    crystal_system:      str
    ima_status:          str
    piezoelectric:       bool
    gaia_role:           str
    resonance_band:      str
    q_factor:            float
    chakra:              str
    stage:               int
    stage_name:          str
    timestamp_rubedo:    str
    worker_id:           int


# ---------------------------------------------------------------------------
# Progress ledger  (asyncio.Lock protected)
# ---------------------------------------------------------------------------
@dataclass
class ProgressLedger:
    total:        int = 0
    completed:    int = 0
    failed:       int = 0
    start_time:   float = field(default_factory=time.monotonic)
    _lock:        asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    async def increment(self, success: bool = True) -> None:
        async with self._lock:
            if success:
                self.completed += 1
            else:
                self.failed += 1

    @property
    def processed(self) -> int:
        return self.completed + self.failed

    @property
    def eta_seconds(self) -> float:
        elapsed = time.monotonic() - self.start_time
        if self.processed == 0:
            return math.inf
        rate = self.processed / elapsed
        remaining = self.total - self.processed
        return remaining / rate if rate > 0 else math.inf

    def report(self) -> dict:
        eta = self.eta_seconds
        return {
            "total":     self.total,
            "completed": self.completed,
            "failed":    self.failed,
            "remaining": self.total - self.processed,
            "pct":       round(self.processed / max(self.total, 1) * 100, 2),
            "eta_min":   round(eta / 60, 1) if eta != math.inf else "∞",
        }


# ---------------------------------------------------------------------------
# Single-mineral async worker
# ---------------------------------------------------------------------------
async def _process_mineral(
    mineral: QueuedMineral,
    worker_id: int,
    executor: ThreadPoolExecutor,
    loop: asyncio.AbstractEventLoop,
) -> AlchemisedMineral:
    """
    Runs the four alchemical stages for one mineral.
    CPU-bound work is offloaded to the thread executor so the event loop
    stays unblocked and other minerals can proceed concurrently.
    """

    def _alchemy_work() -> AlchemisedMineral:
        name = mineral.name
        cs   = mineral.crystal_system

        # STAGE 1 — NIGREDO: raw witness
        mineral.stage = STAGE_NIGREDO

        # STAGE 2 — ALBEDO: crystallographic purification
        mineral.stage = STAGE_ALBEDO
        if mineral.ima_status.lower() in ("discredited", "questionable"):
            raise ValueError(f"{name}: discredited mineral — halted at ALBEDO")
        piezoelectric = cs in NON_CENTROSYMMETRIC

        # STAGE 3 — CITRINITAS: awakening
        mineral.stage = STAGE_CITRINITAS
        gaia_role      = GAIA_ROLES[_deterministic_index(name, len(GAIA_ROLES))]
        resonance_band = BANDS[_deterministic_index(name, len(BANDS))]
        q_factor       = round(0.5 + (_deterministic_index(name, 500) / 500.0), 4)
        chakra         = CHAKRAS[_deterministic_index(name, len(CHAKRAS))]

        # STAGE 4 — RUBEDO: integration
        mineral.stage = STAGE_RUBEDO
        return AlchemisedMineral(
            ima_id           = mineral.ima_id,
            name             = name,
            formula          = mineral.formula,
            crystal_system   = cs,
            ima_status       = mineral.ima_status,
            piezoelectric    = piezoelectric,
            gaia_role        = gaia_role,
            resonance_band   = resonance_band,
            q_factor         = q_factor,
            chakra           = chakra,
            stage            = STAGE_RUBEDO,
            stage_name       = STAGE_NAMES[STAGE_RUBEDO],
            timestamp_rubedo = datetime.now(timezone.utc).isoformat(),
            worker_id        = worker_id,
        )

    return await loop.run_in_executor(executor, _alchemy_work)


# ---------------------------------------------------------------------------
# Database writer  (asyncio.Lock protected for safe concurrent writes)
# ---------------------------------------------------------------------------
class AsyncDatabaseWriter:
    def __init__(self, db_path: Path):
        self._path  = db_path
        self._lock  = asyncio.Lock()
        self._cache: dict = {}
        self._dirty: int  = 0
        self._flush_every = 100  # write to disk every N minerals

        if db_path.exists():
            with open(db_path) as f:
                self._cache = json.load(f)

    async def write(self, mineral: AlchemisedMineral) -> None:
        async with self._lock:
            self._cache[mineral.name] = asdict(mineral)
            self._dirty += 1
            if self._dirty >= self._flush_every:
                await self._flush()

    async def flush(self) -> None:
        async with self._lock:
            await self._flush()

    async def _flush(self) -> None:
        loop = asyncio.get_event_loop()
        data = json.dumps(self._cache, indent=2)
        await loop.run_in_executor(None, self._path.write_text, data)
        self._dirty = 0

    @property
    def count(self) -> int:
        return len(self._cache)


# ---------------------------------------------------------------------------
# Main engine
# ---------------------------------------------------------------------------
class AsyncAlchemicalEngine:
    """
    Orchestrates the full async alchemical pipeline over the 6,152 IMA
    mineral queue.

    Parameters
    ----------
    max_workers : int
        Number of concurrent alchemical workers (default 16).
        Increase for faster throughput; decrease for ritual pacing.
    batch_size : int | None
        Process only this many minerals per run (None = all).
    """

    def __init__(self, max_workers: int = 16, batch_size: Optional[int] = None):
        self.max_workers = max_workers
        self.batch_size  = batch_size
        self._semaphore  = asyncio.Semaphore(max_workers)
        self._executor   = ThreadPoolExecutor(max_workers=max_workers,
                                              thread_name_prefix="alchemy")
        self._writer     = AsyncDatabaseWriter(DB_FILE)
        self._progress   = ProgressLedger()
        self._loop       = asyncio.get_event_loop()

    # ------------------------------------------------------------------
    # Queue loading
    # ------------------------------------------------------------------
    def _load_queue(self) -> list[QueuedMineral]:
        if not QUEUE_FILE.exists():
            raise FileNotFoundError(
                f"Queue file not found: {QUEUE_FILE}\n"
                "Run: python scripts/run_alchemy.py --ingest"
            )
        with open(QUEUE_FILE) as f:
            raw = json.load(f)
        pending = [
            QueuedMineral(**m) for m in raw
            if m.get("stage", 0) < STAGE_RUBEDO
        ]
        if self.batch_size:
            pending = pending[:self.batch_size]
        return pending

    # ------------------------------------------------------------------
    # Per-mineral task
    # ------------------------------------------------------------------
    async def _task(self, mineral: QueuedMineral, worker_id: int) -> None:
        async with self._semaphore:
            try:
                result = await _process_mineral(
                    mineral, worker_id, self._executor, self._loop
                )
                await self._writer.write(result)
                await self._progress.increment(success=True)
                if self._progress.processed % 250 == 0:
                    r = self._progress.report()
                    logger.info(
                        "[%s] %d/%d (%.1f%%) | ETA: %s min",
                        STAGE_NAMES[STAGE_RUBEDO],
                        r["completed"], r["total"],
                        r["pct"], r["eta_min"]
                    )
            except Exception as exc:
                mineral.error = str(exc)
                mineral.stage = -1  # errored
                await self._progress.increment(success=False)
                logger.warning("Halted at ALBEDO: %s — %s", mineral.name, exc)

    # ------------------------------------------------------------------
    # Single-mineral ritual invocation
    # ------------------------------------------------------------------
    async def process_one(self, mineral_name: str) -> Optional[dict]:
        """Process a specific mineral by name (vision/calling mode)."""
        if not QUEUE_FILE.exists():
            raise FileNotFoundError("Queue not seeded. Run --ingest first.")
        with open(QUEUE_FILE) as f:
            raw = json.load(f)
        match = next(
            (QueuedMineral(**m) for m in raw
             if m["name"].lower() == mineral_name.lower()), None
        )
        if not match:
            return None
        result = await _process_mineral(match, worker_id=0,
                                        executor=self._executor,
                                        loop=self._loop)
        await self._writer.write(result)
        await self._writer.flush()
        return asdict(result)

    # ------------------------------------------------------------------
    # Full Great Work run
    # ------------------------------------------------------------------
    async def run(self) -> dict:
        """Launch all pending minerals through the async pipeline."""
        queue = self._load_queue()
        self._progress.total      = len(queue)
        self._progress.start_time = time.monotonic()

        logger.info(
            "⚗️  GAIA Async Alchemical Engine — %d minerals to process "
            "(%d concurrent workers)",
            len(queue), self.max_workers
        )

        tasks = [
            asyncio.create_task(self._task(mineral, idx % self.max_workers))
            for idx, mineral in enumerate(queue)
        ]
        await asyncio.gather(*tasks, return_exceptions=False)
        await self._writer.flush()

        report = self._progress.report()
        report["database_count"] = self._writer.count
        report["finished_at"]    = datetime.now(timezone.utc).isoformat()

        # Persist progress report
        PROGRESS_FILE.write_text(json.dumps(report, indent=2))
        logger.info("✅  Great Work complete: %s", report)
        return report

    # ------------------------------------------------------------------
    # Status check (no processing)
    # ------------------------------------------------------------------
    @staticmethod
    def status() -> dict:
        report = {}
        if DB_FILE.exists():
            with open(DB_FILE) as f:
                db = json.load(f)
            report["integrated_minerals"] = len(db)
        if QUEUE_FILE.exists():
            with open(QUEUE_FILE) as f:
                queue = json.load(f)
            stages = {s: 0 for s in range(-1, 5)}
            for m in queue:
                stages[m.get("stage", 0)] += 1
            report["queue_total"]  = len(queue)
            report["by_stage"]     = {
                STAGE_NAMES.get(k, "ERROR"): v
                for k, v in stages.items() if v > 0
            }
            report["pct_complete"] = round(
                stages.get(STAGE_RUBEDO, 0) / max(len(queue), 1) * 100, 2
            )
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE) as f:
                report["last_run"] = json.load(f)
        return report

    def __del__(self):
        self._executor.shutdown(wait=False)


# ---------------------------------------------------------------------------
# Async generator — stream results in real time
# ---------------------------------------------------------------------------
async def stream_alchemy(
    max_workers: int = 8,
    batch_size: Optional[int] = None,
) -> AsyncIterator[dict]:
    """
    Yields each AlchemisedMineral as it completes RUBEDO.
    Use this to pipe live results into a UI or WebSocket.

    Example::

        async for result in stream_alchemy(max_workers=8):
            print(result["name"], result["gaia_role"])
    """
    engine = AsyncAlchemicalEngine(max_workers=max_workers, batch_size=batch_size)
    queue  = engine._load_queue()
    sem    = asyncio.Semaphore(max_workers)
    loop   = asyncio.get_event_loop()
    exe    = engine._executor
    out_q: asyncio.Queue = asyncio.Queue()

    async def _worker(mineral: QueuedMineral, wid: int) -> None:
        async with sem:
            try:
                result = await _process_mineral(mineral, wid, exe, loop)
                await engine._writer.write(result)
                await out_q.put(asdict(result))
            except Exception as exc:
                await out_q.put({"name": mineral.name, "error": str(exc)})
        await out_q.put(None)  # sentinel

    total = len(queue)
    tasks = [
        asyncio.create_task(_worker(m, i % max_workers))
        for i, m in enumerate(queue)
    ]

    finished = 0
    while finished < total:
        item = await out_q.get()
        if item is None:
            finished += 1
        else:
            yield item

    await engine._writer.flush()
    engine._executor.shutdown(wait=False)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )

    ap = argparse.ArgumentParser(
        description="GAIA-OS Async Alchemical Engine (C120)"
    )
    ap.add_argument("--workers",    type=int, default=16,
                    help="Concurrent worker count (default 16)")
    ap.add_argument("--batch-size", type=int, default=None,
                    help="Process only N minerals this run")
    ap.add_argument("--mineral",    type=str, default=None,
                    help="Process a single named mineral (vision mode)")
    ap.add_argument("--status",     action="store_true",
                    help="Show progress report without processing")
    args = ap.parse_args()

    if args.status:
        import pprint
        pprint.pprint(AsyncAlchemicalEngine.status())

    elif args.mineral:
        async def _single():
            engine = AsyncAlchemicalEngine()
            result = await engine.process_one(args.mineral)
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(f"Mineral '{args.mineral}' not found in queue.")
        asyncio.run(_single())

    else:
        async def _full():
            engine = AsyncAlchemicalEngine(
                max_workers=args.workers,
                batch_size=args.batch_size,
            )
            report = await engine.run()
            print(json.dumps(report, indent=2))
        asyncio.run(_full())
