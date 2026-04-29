"""
GAIA Ollama Health Probe
========================

Runs at sidecar startup to verify that:
  1. Ollama is reachable at OLLAMA_BASE_URL
  2. The configured OLLAMA_MODEL is already pulled locally
  3. If the model is missing, a clear structured event is emitted so the
     Tauri frontend can guide the user to pull it

Emitted events (written to stdout as JSON lines for the Tauri sidecar to pick up):
  {"event": "sidecar:ollama_ready",   "model": "gemma3:12b", "models_available": [...]}
  {"event": "sidecar:ollama_missing", "model": "gemma3:12b", "reason": "...",
   "pull_command": "ollama pull gemma3:12b"}
  {"event": "sidecar:ollama_offline", "reason": "Ollama not reachable at http://localhost:11434"}

Canon ref: C44 (sidecar contract — connective tissue)
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_DEFAULT_BASE_URL = "http://localhost:11434"
_DEFAULT_MODEL    = "gemma3:12b"
_TIMEOUT_S        = 5.0


def _emit(payload: dict) -> None:
    """Write a structured JSON event line to stdout for the Tauri sidecar."""
    print(json.dumps(payload), flush=True)


def probe(
    base_url: Optional[str] = None,
    model:    Optional[str] = None,
    *,
    silent: bool = False,
) -> dict:
    """
    Check Ollama availability and model presence.

    Args:
        base_url: Override OLLAMA_BASE_URL env var.
        model:    Override OLLAMA_MODEL env var.
        silent:   If True, suppress stdout event emission (useful in tests).

    Returns:
        A dict with keys: ok (bool), event (str), model (str), reason (str | None),
        models_available (list[str]).
    """
    url   = (base_url or os.environ.get("OLLAMA_BASE_URL") or _DEFAULT_BASE_URL).rstrip("/")
    model = model or os.environ.get("OLLAMA_MODEL") or os.environ.get("GAIA_MODEL") or _DEFAULT_MODEL

    # ── 1. Reachability check ────────────────────────────────────────────────
    try:
        resp = httpx.get(f"{url}/api/tags", timeout=_TIMEOUT_S)
        resp.raise_for_status()
    except httpx.ConnectError:
        reason  = f"Ollama not reachable at {url} — is Ollama running?"
        payload = {"event": "sidecar:ollama_offline", "model": model, "reason": reason}
        if not silent:
            _emit(payload)
        logger.warning(f"[OllamaHealth] {reason}")
        return {"ok": False, **payload, "models_available": []}
    except Exception as exc:
        reason  = f"Ollama health check failed: {exc}"
        payload = {"event": "sidecar:ollama_offline", "model": model, "reason": reason}
        if not silent:
            _emit(payload)
        logger.warning(f"[OllamaHealth] {reason}")
        return {"ok": False, **payload, "models_available": []}

    # ── 2. Parse available models ────────────────────────────────────────────
    try:
        data             = resp.json()
        available_models = [m["name"] for m in data.get("models", [])]
    except Exception:
        available_models = []

    # ── 3. Check if configured model is pulled ───────────────────────────────
    # Ollama model names may include a tag (e.g. "gemma3:12b") or omit it
    # (defaulting to ":latest"). We match on the base name as well.
    def _model_present(target: str, available: list[str]) -> bool:
        target_base = target.split(":")[0]
        for name in available:
            if name == target or name.split(":")[0] == target_base:
                return True
        return False

    if _model_present(model, available_models):
        payload = {
            "event":            "sidecar:ollama_ready",
            "model":            model,
            "models_available": available_models,
        }
        if not silent:
            _emit(payload)
        logger.info(f"[OllamaHealth] Ollama ready — model '{model}' is available.")
        return {"ok": True, **payload}

    # Model not pulled yet
    reason  = f"Model '{model}' is not pulled. Run: ollama pull {model}"
    payload = {
        "event":            "sidecar:ollama_missing",
        "model":            model,
        "reason":           reason,
        "pull_command":     f"ollama pull {model}",
        "models_available": available_models,
    }
    if not silent:
        _emit(payload)
    logger.warning(f"[OllamaHealth] {reason}")
    return {"ok": False, **payload}


def probe_on_startup() -> None:
    """
    Convenience wrapper intended to be called once from main.py / server startup.
    Logs the result and emits the appropriate sidecar event.
    Failure is non-fatal — GAIA will fall back to cloud backends.
    """
    try:
        result = probe()
        if result["ok"]:
            logger.info("[OllamaHealth] Startup probe passed.")
        else:
            logger.warning(
                f"[OllamaHealth] Startup probe failed: {result.get('reason', 'unknown')}"
            )
    except Exception as exc:
        logger.error(f"[OllamaHealth] Unexpected error during startup probe: {exc}")
