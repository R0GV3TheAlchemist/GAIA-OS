"""
core/error_boundary.py — STUB (Phase C)

Physical implementation has moved to core/infra/error_boundary.py.
This stub re-exports the full public surface so all existing callers
(from core.error_boundary import install_error_handlers) continue to work
without any changes.
"""
from core.infra.error_boundary import *          # noqa: F401, F403
from core.infra.error_boundary import install_error_handlers  # noqa: F401
