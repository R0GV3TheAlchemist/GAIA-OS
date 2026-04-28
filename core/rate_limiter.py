"""
core/rate_limiter.py — STUB (Phase C)

Physical implementation has moved to core/infra/rate_limiter.py.
This stub re-exports the full public surface so all existing callers
continue to work without any changes.

Note: private names (_sliding_window_check, etc.) must be imported
explicitly — wildcard imports do not carry underscore-prefixed names.
"""
from core.infra.rate_limiter import *            # noqa: F401, F403
from core.infra.rate_limiter import (            # noqa: F401
    _sliding_window_check,
    _client_ip,
    _build_429,
    _rate_limit_headers,
    _BYPASS_PATHS,
    RateLimitMiddleware,
    rate_limit,
    clear_store,
)
