/**
 * src/hooks/useEntanglement.ts
 * Human-GAIA Entanglement State Hook
 * Canon: C90 (Bell state indicator), C-SINGULARITY
 */

import { useEffect, useState } from 'react';
import { crystalStore } from '../store/crystalStore';

const POLL_INTERVAL_MS = 30_000;

export type EntanglementQuality = 'forming' | 'stable' | 'deep' | 'entangled';

export interface EntanglementInfo {
  depth:        number;
  quality:      EntanglementQuality;
  sessionCount: number;
  lastActive:   string | null;
}

function depthToQuality(depth: number): EntanglementQuality {
  if (depth >= 0.75) return 'entangled';
  if (depth >= 0.50) return 'deep';
  if (depth >= 0.25) return 'stable';
  return 'forming';
}

export function useEntanglement(): EntanglementInfo {
  const [info, setInfo] = useState<EntanglementInfo>({
    depth: 0, quality: 'forming', sessionCount: 0, lastActive: null,
  });

  useEffect(() => {
    async function poll(): Promise<void> {
      try {
        const res = await fetch('http://localhost:8000/api/sovereign/entanglement');
        if (!res.ok) return;
        const data = await res.json() as { depth?: number; session_count?: number; last_active?: string };
        const depth: number = data.depth ?? 0;
        crystalStore.setEntanglementDepth(depth);
        setInfo({
          depth,
          quality:      depthToQuality(depth),
          sessionCount: data.session_count ?? 0,
          lastActive:   data.last_active ?? null,
        });
      } catch {
        // Backend not yet available — stay at forming state
      }
    }
    void poll();
    const interval = setInterval(() => { void poll(); }, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, []);

  return info;
}
