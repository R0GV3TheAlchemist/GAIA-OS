"""
core/rate_limiter.py — STUB (Phase C)

Physical implementation has moved to core/infra/rate_limiter.py.
This stub re-exports the full public surface so all existing callers
continue to work without any changes.
"""
from core.infra.rate_limiter import *            # noqa: F401, F403
from core.infra.rate_limiter import (            # noqa: F401
    RateLimitMiddleware,
    rate_limit,
    clear_store,
)
