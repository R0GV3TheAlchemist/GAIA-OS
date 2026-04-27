/**
 * src/hooks/useCrystal.ts
 * Crystal Mode Hook — primary interface for all UI components.
 * Canon: C90
 */

import { useEffect, useCallback, useSyncExternalStore } from 'react';
import {
  crystalStore,
  CrystalMode,
  CrystalStoreState,
  CRYSTAL_ORDER,
  CRYSTAL_LABELS,
  CRYSTAL_DECLARATIONS,
  CRYSTAL_CSS_CLASS,
} from '../store/crystalStore';

const TRANSITION_DURATION_MS = 300;

export function useCrystal() {
  const state = useSyncExternalStore<CrystalStoreState>(
    (cb: () => void) => crystalStore.subscribe(cb),
    () => crystalStore.getSnapshot(),
  );

  const { activeCrystal, previousCrystal, isTransitioning, loveFilterScore, entanglementDepth, emergencyStopped } = state;

  const setCrystal = useCallback((mode: CrystalMode) => {
    crystalStore.setCrystal(mode);
    setTimeout(() => crystalStore.setTransitioning(false), TRANSITION_DURATION_MS);
  }, []);

  const returnToSovereign = useCallback(() => {
    crystalStore.returnToSovereign();
    setTimeout(() => crystalStore.setTransitioning(false), TRANSITION_DURATION_MS);
  }, []);

  const emergencyStop = useCallback(() => {
    crystalStore.triggerEmergencyStop();
  }, []);

  // Keyboard shortcuts Cmd/Ctrl + 1-5 (C90 spec)
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (!(e.metaKey || e.ctrlKey)) return;
      const index = parseInt(e.key, 10);
      if (index >= 1 && index <= 5) {
        e.preventDefault();
        const target = CRYSTAL_ORDER[index - 1];
        if (target) setCrystal(target);
      }
    }
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [setCrystal]);

  // Apply body CSS class on crystal change
  useEffect(() => {
    const body = document.body;
    CRYSTAL_ORDER.forEach(mode => body.classList.remove(CRYSTAL_CSS_CLASS[mode]));
    body.classList.add(CRYSTAL_CSS_CLASS[activeCrystal]);
    if (isTransitioning) body.classList.add('crystal--transitioning');
    else body.classList.remove('crystal--transitioning');
  }, [activeCrystal, isTransitioning]);

  return {
    activeCrystal,
    previousCrystal,
    isTransitioning,
    loveFilterScore,
    entanglementDepth,
    emergencyStopped,
    label:               CRYSTAL_LABELS[activeCrystal],
    declaration:         CRYSTAL_DECLARATIONS[activeCrystal],
    cssClass:            CRYSTAL_CSS_CLASS[activeCrystal],
    setCrystal,
    returnToSovereign,
    emergencyStop,
    setLoveFilterScore:   (s: number) => crystalStore.setLoveFilterScore(s),
    setEntanglementDepth: (d: number) => crystalStore.setEntanglementDepth(d),
  };
}
