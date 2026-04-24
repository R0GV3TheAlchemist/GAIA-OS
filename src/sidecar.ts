/**
 * GAIA Sidecar Health-Check & Loading State
 * Polls http://localhost:8008/health until the Python backend is ready.
 * Shows a full-screen loading overlay while waiting.
 * Handles crash recovery with exponential backoff (max 3 auto-retries).
 */

import { invoke } from '@tauri-apps/api/core';
import { logInfo, logWarn, logError } from './diagnostics';

const HEALTH_URL = 'http://localhost:8008/health';
const MAX_POLL_ATTEMPTS = 40;   // ~30 s total
const MAX_AUTO_RETRIES = 3;

// ── Loading overlay ────────────────────────────────────────────────────
function createOverlay(): HTMLElement {
  const el = document.createElement('div');
  el.id = 'gaia-loading-overlay';
  el.innerHTML = `
    <div class="gaia-loading-inner">
      <div class="gaia-spinner"></div>
      <p class="gaia-loading-title">GAIA</p>
      <p class="gaia-loading-sub" id="gaia-loading-msg">Initialising backend…</p>
      <p class="gaia-loading-attempt" id="gaia-loading-attempt"></p>
    </div>
  `;
  el.style.cssText = [
    'position:fixed', 'inset:0', 'z-index:9999',
    'display:flex', 'align-items:center', 'justify-content:center',
    'background:rgba(8,8,16,0.97)',
    'font-family:inherit', 'flex-direction:column',
  ].join(';');
  document.body.appendChild(el);
  return el;
}

function setOverlayMsg(msg: string, sub = '') {
  const m = document.getElementById('gaia-loading-msg');
  const a = document.getElementById('gaia-loading-attempt');
  if (m) m.textContent = msg;
  if (a) a.textContent = sub;
}

function removeOverlay() {
  const el = document.getElementById('gaia-loading-overlay');
  if (el) el.remove();
}

// ── Health poll ────────────────────────────────────────────────────────
async function pollHealth(attempts = MAX_POLL_ATTEMPTS): Promise<boolean> {
  let delay = 300;
  for (let i = 0; i < attempts; i++) {
    await new Promise(r => setTimeout(r, delay));
    try {
      const res = await fetch(HEALTH_URL, { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        logInfo('sidecar', `Backend healthy after ${i + 1} attempt(s)`);
        return true;
      }
    } catch (_) {}
    delay = Math.min(delay * 1.5, 3000);
    setOverlayMsg(
      'Initialising backend…',
      `Attempt ${i + 1} of ${attempts}`,
    );
  }
  return false;
}

// ── Public init ────────────────────────────────────────────────────────
export async function initSidecar(): Promise<void> {
  logInfo('sidecar', 'Starting health-check polling');
  const overlay = createOverlay();
  let retries = 0;

  while (retries <= MAX_AUTO_RETRIES) {
    const ready = await pollHealth();
    if (ready) {
      removeOverlay();
      logInfo('sidecar', 'Sidecar ready — overlay dismissed');
      return;
    }

    retries++;
    if (retries > MAX_AUTO_RETRIES) break;

    logWarn('sidecar', `Backend unresponsive — restarting`, { attempt: retries, max: MAX_AUTO_RETRIES });
    setOverlayMsg(
      `Backend unresponsive — restarting… (${retries}/${MAX_AUTO_RETRIES})`,
      'Please wait',
    );

    try {
      await invoke<string>('restart_backend');
      logInfo('sidecar', 'restart_backend invoked successfully');
    } catch (e) {
      logError('sidecar', 'restart_backend failed', e);
    }

    await new Promise(r => setTimeout(r, 1500));
  }

  // All retries exhausted
  logError('sidecar', 'All retries exhausted — backend failed to start', { maxRetries: MAX_AUTO_RETRIES });
  setOverlayMsg(
    '⚠ Backend failed to start',
    'Some features may be unavailable. Check logs.',
  );
  overlay.style.background = 'rgba(20,4,4,0.97)';

  await new Promise(r => setTimeout(r, 6000));
  removeOverlay();
}

// ── Backend status helper ──────────────────────────────────────────────
export async function getBackendStatus(): Promise<string> {
  try {
    return await invoke<string>('get_backend_status');
  } catch {
    return 'unknown';
  }
}
