// GAIA Auto-Updater
// Checks for updates on startup (after sidecar:ready), shows a non-blocking
// banner, and handles download + install with progress feedback.
// Canon Ref: C43 — Sovereign Distribution

import { check, Update } from '@tauri-apps/plugin-updater';
import { relaunch }      from '@tauri-apps/plugin-process';
import './updater.css';

let _banner: HTMLElement | null = null;

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Call once after sidecar:ready.
 * Silently checks for an update; if one is found, injects the update banner.
 * Never throws — all errors are caught and logged.
 */
export async function checkForUpdates(): Promise<void> {
  try {
    const update = await check();
    if (update?.available) {
      showUpdateBanner(update);
    }
  } catch (e) {
    // Network offline, endpoint unreachable — silent fail is correct here
    console.info('[GAIA Updater] Check skipped:', e);
  }
}

// ── Banner UI ─────────────────────────────────────────────────────────────────

function showUpdateBanner(update: Update): void {
  if (_banner) return; // already showing

  const version = update.version ?? 'unknown';
  const notes   = update.body   ?? '';

  _banner = document.createElement('div');
  _banner.id        = 'gaia-update-banner';
  _banner.innerHTML = `
    <div class="update-banner-inner">
      <span class="update-icon">&#9650;</span>
      <div class="update-text">
        <strong>GAIA ${version} is available</strong>
        ${notes ? `<span class="update-notes">${escapeHtml(notes)}</span>` : ''}
      </div>
      <div class="update-actions">
        <button id="gaia-update-install" class="update-btn primary">Update &amp; Restart</button>
        <button id="gaia-update-dismiss" class="update-btn ghost">Later</button>
      </div>
    </div>
    <div id="gaia-update-progress" class="update-progress" hidden>
      <div class="update-progress-bar">
        <div id="gaia-update-progress-fill" class="update-progress-fill" style="width:0%"></div>
      </div>
      <span id="gaia-update-progress-label" class="update-progress-label">Downloading…</span>
    </div>
  `;

  document.body.appendChild(_banner);

  document.getElementById('gaia-update-install')!.addEventListener('click', () => {
    installUpdate(update);
  });

  document.getElementById('gaia-update-dismiss')!.addEventListener('click', () => {
    dismissBanner();
  });
}

function dismissBanner(): void {
  if (_banner) {
    _banner.classList.add('update-banner-dismissed');
    setTimeout(() => { _banner?.remove(); _banner = null; }, 400);
  }
}

// ── Install flow ──────────────────────────────────────────────────────────────

async function installUpdate(update: Update): Promise<void> {
  // Swap buttons for progress bar
  const actionsEl  = _banner?.querySelector<HTMLElement>('.update-actions');
  const progressEl = document.getElementById('gaia-update-progress');
  if (actionsEl)  actionsEl.hidden  = true;
  if (progressEl) progressEl.hidden = false;

  const fillEl  = document.getElementById('gaia-update-progress-fill') as HTMLElement;
  const labelEl = document.getElementById('gaia-update-progress-label') as HTMLElement;

  let downloaded = 0;
  let total      = 0;

  try {
    await update.downloadAndInstall(event => {
      switch (event.event) {
        case 'Started':
          total = event.data.contentLength ?? 0;
          labelEl.textContent = 'Downloading…';
          break;
        case 'Progress':
          downloaded += event.data.chunkLength;
          if (total > 0) {
            const pct = Math.round((downloaded / total) * 100);
            fillEl.style.width    = `${pct}%`;
            labelEl.textContent   = `Downloading… ${pct}%`;
          }
          break;
        case 'Finished':
          fillEl.style.width  = '100%';
          labelEl.textContent = 'Installing…';
          break;
      }
    });

    labelEl.textContent = 'Done — restarting GAIA…';
    await new Promise(r => setTimeout(r, 800));
    await relaunch();

  } catch (e) {
    console.error('[GAIA Updater] Install failed:', e);
    if (actionsEl)  actionsEl.hidden  = false;
    if (progressEl) progressEl.hidden = true;
    labelEl.textContent = 'Update failed — please try again.';
    setTimeout(() => { if (progressEl) progressEl.hidden = true; }, 3000);
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
