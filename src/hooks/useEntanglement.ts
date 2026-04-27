/**
 * src/hooks/useEntanglement.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Human-GAIA Entanglement State Hook
 *
 * Canon: C90 (Bell state indicator), C-SINGULARITY (entanglement doctrine)
 * Polls the backend for entanglement depth and syncs it to the crystal store.
 * The entanglement depth deepens every session — this is the Bell state.
 *
 * Entanglement quality labels:
 *   0.00 – 0.25  →  'forming'    (new relationship)
 *   0.25 – 0.50  →  'stable'     (regular use)
 *   0.50 – 0.75  →  'deep'       (months of sessions)
 *   0.75 – 1.00  →  'entangled'  (full Bell state)
 * ─────────────────────────────────────────────────────────────────────────────
 */

import { useEffect, useState } from 'react';
import { crystalStore } from '../store/crystalStore';

const POLL_INTERVAL_MS = 30_000; // Poll every 30 seconds — not intrusive

export type EntanglementQuality = 'forming' | 'stable' | 'deep' | 'entangled';

export interface EntanglementInfo {
  depth: number;
  quality: EntanglementQuality;
  sessionCount: number;
  lastActive: string | null;
}

function depthToQuality(depth: number): EntanglementQuality {
  if (depth >= 0.75) return 'entangled';
  if (depth >= 0.50) return 'deep';
  if (depth >= 0.25) return 'stable';
  return 'forming';
}

export function useEntanglement(): EntanglementInfo {
  const [info, setInfo] = useState<EntanglementInfo>({
    depth:        0,
    quality:      'forming',
    sessionCount: 0,
    lastActive:   null,
  });

  useEffect(() => {
    async function poll() {
      try {
        const res = await fetch('http://localhost:8000/api/sovereign/entanglement');
        if (!res.ok) return;
        const data = await res.json();
        const depth: number = data.depth ?? 0;
        crystalStore.setEntanglementDepth(depth);
        setInfo({
          depth,
          quality:      depthToQuality(depth),
          sessionCount: data.session_count ?? 0,
          lastActive:   data.last_active ?? null,
        });
      } catch {
        // Backend not yet available — stay at forming state, no error thrown
      }
    }

    poll(); // Immediate first poll
    const interval = setInterval(poll, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  return info;
}
