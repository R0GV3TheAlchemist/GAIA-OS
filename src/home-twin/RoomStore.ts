/**
 * RoomStore.ts
 *
 * Persists and loads room scan data and GAIA placement.
 * Uses the backend /room/save and /room/load endpoints.
 * Falls back to localStorage for offline resilience.
 *
 * Canon Ref: C20 (Home Twin — Spatial Presence)
 */

import { API_BASE } from '../app';

export interface RoomConfig {
  panoramaDataUrl: string;
  capturedAt: string;
}

export interface GAIAPlacement {
  surfaceId: string;
  surfaceLabel: string;
  yPercent: number;
  placedAt: string;
}

const ROOM_LS_KEY      = 'gaia_room_config';
const PLACEMENT_LS_KEY = 'gaia_room_placement';

export class RoomStore {

  // ------------------------------------------------------------------ //
  //  Room panorama                                                       //
  // ------------------------------------------------------------------ //

  async saveRoom(config: RoomConfig): Promise<void> {
    // Persist to localStorage first (always works offline)
    try { localStorage.setItem(ROOM_LS_KEY, JSON.stringify(config)); } catch {}

    // Mirror to backend (best-effort)
    try {
      await fetch(`${API_BASE}/room/save`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ panorama: config.panoramaDataUrl, captured_at: config.capturedAt }),
        signal:  AbortSignal.timeout(5000),
      });
    } catch { /* offline — LS copy is sufficient */ }
  }

  async loadRoom(): Promise<RoomConfig | null> {
    // Try backend first
    try {
      const res = await fetch(`${API_BASE}/room/load`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        if (data.panorama) {
          return { panoramaDataUrl: data.panorama, capturedAt: data.captured_at ?? '' };
        }
      }
    } catch { /* fall through to localStorage */ }

    // Fall back to localStorage
    try {
      const raw = localStorage.getItem(ROOM_LS_KEY);
      if (raw) return JSON.parse(raw) as RoomConfig;
    } catch {}

    return null;
  }

  async clearRoom(): Promise<void> {
    localStorage.removeItem(ROOM_LS_KEY);
    try {
      await fetch(`${API_BASE}/room/save`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ panorama: null }),
        signal:  AbortSignal.timeout(3000),
      });
    } catch {}
  }

  // ------------------------------------------------------------------ //
  //  GAIA placement                                                      //
  // ------------------------------------------------------------------ //

  async savePlacement(placement: GAIAPlacement): Promise<void> {
    try { localStorage.setItem(PLACEMENT_LS_KEY, JSON.stringify(placement)); } catch {}
    try {
      await fetch(`${API_BASE}/room/placement`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(placement),
        signal:  AbortSignal.timeout(3000),
      });
    } catch {}
  }

  async loadPlacement(): Promise<GAIAPlacement | null> {
    try {
      const res = await fetch(`${API_BASE}/room/placement`, { signal: AbortSignal.timeout(3000) });
      if (res.ok) { const d = await res.json(); if (d.surface_id) return d as GAIAPlacement; }
    } catch {}
    try {
      const raw = localStorage.getItem(PLACEMENT_LS_KEY);
      if (raw) return JSON.parse(raw) as GAIAPlacement;
    } catch {}
    return null;
  }
}
