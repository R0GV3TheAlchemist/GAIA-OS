/**
 * src/main.tsx
 * GAIA-OS React Entry Point
 * Canon: C90 — Phase 3b
 *
 * Boot sequence:
 * 1. initSidecar() — Python FastAPI backend alive
 * 2. createRoot() — React 18 concurrent mode
 * 3. Mount <CrystalField /> — the field opens
 */

import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { initSidecar } from './sidecar';
import { notificationBridge } from './shell/NotificationBridge';
import { CrystalField } from './field/CrystalField';
import './field/crystal-tokens.css';
import './styles.css';

const rootEl = document.getElementById('gaia-root');
if (!rootEl) throw new Error('GAIA: #gaia-root not found in DOM.');

const root = createRoot(rootEl);

// Mount immediately with loading state — field shows before sidecar is ready
root.render(
  <StrictMode>
    <CrystalField />
  </StrictMode>
);

// Sidecar boot in parallel — hooks will reconnect when ready
initSidecar()
  .then(() => notificationBridge.init())
  .catch((err: unknown) => console.error('[GAIA] Sidecar init error:', err));
