/**
 * src/main.tsx
 * GAIA-OS React Entry Point — Phase 4b
 * Canon: C90
 *
 * Boot sequence:
 * 1. initSidecar() — Python FastAPI backend alive
 * 2. createRoot() — React 18 concurrent mode
 * 3. Mount <GaiaShell /> — the shell opens, the field lives inside
 */

import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { initSidecar } from './sidecar';
import { notificationBridge } from './shell/NotificationBridge';
import { GaiaShell } from './shell/GaiaShell';
import './field/crystal-tokens.css';
import './styles.css';

const rootEl = document.getElementById('gaia-root');
if (!rootEl) throw new Error('GAIA: #gaia-root not found in DOM.');

const root = createRoot(rootEl);

root.render(
  <StrictMode>
    <GaiaShell />
  </StrictMode>
);

initSidecar()
  .then(() => notificationBridge.init())
  .catch((err: unknown) => console.error('[GAIA] Sidecar init error:', err));
