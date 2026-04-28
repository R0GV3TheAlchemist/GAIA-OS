/**
 * GAIA Sidecar Health-Check
 * Non-blocking: shell renders immediately.
 * Backend polling runs in background.
 * Status dispatched via 'gaia:backend-status' custom event.
 * Canon: C90
 */

import { invoke } from '@tauri-apps/api/core';
import { logInfo, logWarn, logError } from './diagnostics';

const HEALTH_URL      = 'http://localhost:8008/health';
const MAX_POLL_ATTEMPTS = 40;
const MAX_AUTO_RETRIES  = 3;

function dispatch(status: 'connecting' | 'online' | 'offline') {
  window.dispatchEvent(
    new CustomEvent('gaia:backend-status', { detail: { status } })
  );
}

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
  }
  return false;
}

// Non-blocking — resolves immediately, polls in background
export async function initSidecar(): Promise<void> {
  dispatch('connecting');
  logInfo('sidecar', 'Background health-check started');

  // Fire and forget — do NOT await
  (async () => {
    let retries = 0;
    while (retries <= MAX_AUTO_RETRIES) {
      const ready = await pollHealth();
      if (ready) {
        dispatch('online');
        logInfo('sidecar', 'Backend online');
        return;
      }
      retries++;
      if (retries > MAX_AUTO_RETRIES) break;
      logWarn('sidecar', `Backend unresponsive — restart attempt ${retries}`);
      try {
        await invoke<string>('restart_backend');
      } catch (e) {
        logError('sidecar', 'restart_backend failed', e);
      }
      await new Promise(r => setTimeout(r, 1500));
    }
    dispatch('offline');
    logError('sidecar', 'Backend offline after all retries');
  })();

  // Return immediately — shell renders now
  return Promise.resolve();
}

export async function getBackendStatus(): Promise<string> {
  try {
    return await invoke<string>('get_backend_status');
  } catch {
    return 'unknown';
  }
}
