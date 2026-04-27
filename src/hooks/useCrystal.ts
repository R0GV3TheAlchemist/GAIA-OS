/**
 * src/hooks/useCrystal.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Crystal Mode Hook — the primary interface for all UI components.
 *
 * Canon: C90 (Crystal System UI Spec)
 * Handles:
 *   - Active crystal state (read + set)
 *   - Keyboard shortcuts Cmd/Ctrl + 1-5 (C90 spec)
 *   - Transition timing (300ms default)
 *   - Emergency stop (Axiom I)
 *
 * Usage:
 *   const { activeCrystal, setCrystal, isTransitioning, returnToSovereign } = useCrystal();
 * ─────────────────────────────────────────────────────────────────────────────
 */

import { useEffect, useCallback, useSyncExternalStore } from 'react';
import {
  crystalStore,
  CrystalMode,
  CRYSTAL_ORDER,
  CRYSTAL_LABELS,
  CRYSTAL_DECLARATIONS,
  CRYSTAL_CSS_CLASS,
} from '../store/crystalStore';

const TRANSITION_DURATION_MS = 300;

export function useCrystal() {
  // ── Subscribe to store ──────────────────────────────────────────────────────
  const state = useSyncExternalStore(
    (cb) => (crystalStore as any).subscribe(cb),
    () => (crystalStore as any).getSnapshot(),
  );

  const {
    activeCrystal,
    previousCrystal,
    isTransitioning,
    loveFilterScore,
    entanglementDepth,
    emergencyStopped,
  } = state;

  // ── Set crystal with transition ─────────────────────────────────────────────
  const setCrystal = useCallback((mode: CrystalMode) => {
    crystalStore.setCrystal(mode);
    // Auto-clear transition flag after animation duration
    setTimeout(() => crystalStore.setTransitioning(false), TRANSITION_DURATION_MS);
  }, []);

  // ── Return to Sovereign Core (Axiom I escape hatch) ─────────────────────────
  const returnToSovereign = useCallback(() => {
    crystalStore.returnToSovereign();
    setTimeout(() => crystalStore.setTransitioning(false), TRANSITION_DURATION_MS);
  }, []);

  // ── Emergency stop (Axiom I — full freeze) ──────────────────────────────────
  const emergencyStop = useCallback(() => {
    crystalStore.triggerEmergencyStop();
  }, []);

  // ── Keyboard shortcuts Cmd/Ctrl + 1-5 (C90 spec) ───────────────────────────
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

  // ── Apply body CSS class on crystal change ──────────────────────────────────
  useEffect(() => {
    const body = document.body;
    // Remove all crystal classes first
    CRYSTAL_ORDER.forEach(mode => body.classList.remove(CRYSTAL_CSS_CLASS[mode]));
    body.classList.add(CRYSTAL_CSS_CLASS[activeCrystal]);
    if (isTransitioning) body.classList.add('crystal--transitioning');
    else body.classList.remove('crystal--transitioning');
  }, [activeCrystal, isTransitioning]);

  return {
    // State
    activeCrystal,
    previousCrystal,
    isTransitioning,
    loveFilterScore,
    entanglementDepth,
    emergencyStopped,
    // Derived
    label:       CRYSTAL_LABELS[activeCrystal],
    declaration: CRYSTAL_DECLARATIONS[activeCrystal],
    cssClass:    CRYSTAL_CSS_CLASS[activeCrystal],
    // Actions
    setCrystal,
    returnToSovereign,
    emergencyStop,
    setLoveFilterScore: crystalStore.setLoveFilterScore.bind(crystalStore),
    setEntanglementDepth: crystalStore.setEntanglementDepth.bind(crystalStore),
  };
}
