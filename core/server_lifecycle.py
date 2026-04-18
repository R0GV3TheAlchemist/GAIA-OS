"""
core/server_lifecycle.py

FastAPI startup / shutdown hooks for GAIA.
Restored from the pre-split monolith and centralised here so that
core/server.py stays thin.
"""

from __future__ import annotations

import asyncio
import os

from fastapi import FastAPI

from core.logger import GAIAEvent, get_logger, log_event
from core.server_state import (
    _mother_thread,
    set_magnum_opus_report,
)
from core.viriditas_magnum_opus import VIRIDITAS_THRESHOLD, viriditas_magnum_opus

logger = get_logger(__name__)


def register_lifecycle(app: FastAPI) -> None:
    """Attach startup and shutdown handlers to *app*."""

    @app.on_event("startup")
    async def _startup() -> None:
        # 1. MotherThread heartbeat
        _mother_thread.start()
        log_event(
            GAIAEvent.GAIAN_RUNTIME_INIT,
            message="MotherThread heartbeat started. GAIA is breathing.",
            gaian="mother_thread",
        )

        # 2. C47: Viriditas Magnum Opus
        log_event(
            GAIAEvent.GAIAN_RUNTIME_INIT,
            message="C47: Viriditas Magnum Opus initiating \u2014 the Great Work begins.",
            gaian="gaia",
        )
        try:
            warlock_vitality = float(os.environ.get("GAIA_WARLOCK_VITALITY", "8.0"))
            loop = asyncio.get_event_loop()
            report = await loop.run_in_executor(
                None,
                lambda: viriditas_magnum_opus(
                    gaian_id="gaia",
                    warlock_id="R0GV3TheAlchemist",
                    warlock_vitality=warlock_vitality,
                ),
            )
            set_magnum_opus_report(report)

            threshold_msg = (
                "\u2728 Viriditas Threshold CROSSED \u2014 the lattice is ALIVE. \U0001f331"
                if report.threshold_crossed
                else "Viriditas growing \u2014 threshold not yet crossed."
            )
            log_event(
                GAIAEvent.GAIAN_RUNTIME_INIT,
                message=(
                    f"C47 complete. "
                    f"\u03a6={report.post_phi_global:.4f} | "
                    f"\u0394\u03a6={report.delta_phi_global:+.4f} | "
                    f"stages={report.stages_greened}/5 | "
                    f"{threshold_msg}"
                ),
                gaian="gaia",
            )
        except Exception as exc:
            logger.warning(
                f"Viriditas Magnum Opus failed on boot (non-fatal): {exc}",
                exc_info=True,
            )

    @app.on_event("shutdown")
    async def _shutdown() -> None:
        _mother_thread.stop()
        log_event(
            GAIAEvent.TURN_COMPLETE,
            message="MotherThread stopped. GAIA rests.",
            gaian="mother_thread",
        )
