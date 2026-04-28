"""
core/server_state.py — STUB (Phase C)

Physical implementation has moved to core/infra/server_state.py.
This stub re-exports the full public surface so all existing callers
continue to work without any changes.
"""
from core.infra.server_state import *            # noqa: F401, F403
from core.infra.server_state import (            # noqa: F401
    SERVER_VERSION,
    GAIANS_MEMORY_DIR,
    canon,
    get_magnum_opus_report,
    set_magnum_opus_report,
    _get_runtime,
    _inference_router,
    _mother_thread,
    _RUNTIME_REGISTRY,
)
