"""
Phase 3.5 — Sidecar Tests
Tests: cold start (<10s), health endpoint, stability (30 min skipped in CI).
Requires: dist/gaia-backend.exe built via `pyinstaller gaia-backend.spec`
Skips gracefully if the frozen exe does not exist.
"""

import os
import sys
import time
import subprocess
import threading
import pytest
import httpx

SIDECAR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'dist', 'gaia-backend.exe'
)
HEALTH_URL = 'http://127.0.0.1:8008/health'
STATE_URL  = 'http://127.0.0.1:8008/api/state'


def _wait_for_health(timeout: float = 10.0) -> bool:
    """Poll /health until it responds OK or timeout."""
    deadline = time.monotonic() + timeout
    delay = 0.3
    while time.monotonic() < deadline:
        try:
            r = httpx.get(HEALTH_URL, timeout=1.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(delay)
        delay = min(delay * 1.5, 1.5)
    return False


@pytest.fixture(scope='module')
def sidecar_proc():
    """Start the frozen sidecar, yield it, then terminate."""
    if not os.path.exists(SIDECAR_PATH):
        pytest.skip(
            f'Frozen sidecar not found at {SIDECAR_PATH}. '
            'Run: pyinstaller gaia-backend.spec'
        )
    proc = subprocess.Popen(
        [SIDECAR_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    yield proc
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


class TestSidecarColdStart:
    def test_starts_within_10_seconds(self, sidecar_proc):
        """3.5.1 — sidecar must be HTTP-ready in under 10 seconds."""
        start = time.monotonic()
        assert _wait_for_health(timeout=10.0), \
            'Sidecar did not respond on /health within 10 seconds'
        elapsed = time.monotonic() - start
        print(f'[test] Sidecar ready in {elapsed:.2f}s')
        assert elapsed < 10.0


class TestSidecarHealthEndpoint:
    def test_health_returns_ok(self, sidecar_proc):
        """3.5.2 — /health must return {status: ok}."""
        _wait_for_health(timeout=15.0)
        r = httpx.get(HEALTH_URL, timeout=5.0)
        assert r.status_code == 200
        body = r.json()
        assert body.get('status') == 'ok'
        assert 'version' in body

    def test_state_endpoint_returns_valid_shape(self, sidecar_proc):
        """3.5.2 — /api/state must return expected engine keys."""
        _wait_for_health(timeout=15.0)
        r = httpx.get(STATE_URL, timeout=5.0)
        assert r.status_code == 200
        body = r.json()
        for key in ('soul_mirror', 'shadow', 'attachment', 'coherence', 'solfeggio'):
            assert key in body, f'Missing key: {key}'


@pytest.mark.skipif(
    os.environ.get('CI') == 'true',
    reason='30-minute stability test skipped in CI'
)
class TestSidecarStability:
    def test_stable_30_minutes(self, sidecar_proc):
        """3.5.3 — sidecar must remain responsive for 30 continuous minutes."""
        _wait_for_health(timeout=15.0)
        deadline = time.monotonic() + 30 * 60
        failures = 0
        checks = 0
        while time.monotonic() < deadline:
            try:
                r = httpx.get(HEALTH_URL, timeout=2.0)
                if r.status_code != 200:
                    failures += 1
            except Exception:
                failures += 1
            checks += 1
            time.sleep(10)
        assert failures == 0, \
            f'Sidecar had {failures}/{checks} health-check failures over 30 min'
