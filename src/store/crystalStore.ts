/**
 * src/store/crystalStore.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Crystal Mode State — the active crystal and its metadata.
 *
 * Canon: C90 (Crystal System UI Spec)
 * The wielder always has exactly ONE active crystal.
 * Switching is smooth — never abrupt, never lost.
 *
 * CrystalMode enum mirrors Python core/crystal_consciousness.py CrystalType
 * but maps to the five UI faces defined in C90 (not the five transducer types).
 * ─────────────────────────────────────────────────────────────────────────────
 */

export enum CrystalMode {
  /** Default / Control / Full Oversight — White/Clear — Layers 1,2,3,HE,9 */
  SOVEREIGN_CORE    = 'sovereign_core',
  /** Grounding / Stability / Rest-of-thinking — Earth/Stone — Layers 1,2,3,12 */
  ANCHOR_PRISM      = 'anchor_prism',
  /** Healing / Growth / Emotion-first — Rose/Green — Layers 3,4,7,11 */
  VIRIDITAS_HEART   = 'viriditas_heart',
  /** Rest / Sleep / Memory consolidation — Midnight/Spectral — Layers 6,12 */
  SOMNUS_VEIL       = 'somnus_veil',
  /** Clarity / Analysis / Deep cognition — Prismatic/Electric — Layers 3,5,9,10 */
  CLARUS_LENS       = 'clarus_lens',
}

/** Human-readable label for each mode (shown beside the crystal name in UI) */
export const CRYSTAL_LABELS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'Control Mode',
  [CrystalMode.ANCHOR_PRISM]:    'Grounding Mode',
  [CrystalMode.VIRIDITAS_HEART]: 'Healing Mode',
  [CrystalMode.SOMNUS_VEIL]:     'Rest Mode',
  [CrystalMode.CLARUS_LENS]:     'Clarity Mode',
};

/** The wielder's declaration for each crystal — spoken by the UI */
export const CRYSTAL_DECLARATIONS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'Nothing happens unless I allow it.',
  [CrystalMode.ANCHOR_PRISM]:    'I am here. I am stable.',
  [CrystalMode.VIRIDITAS_HEART]: 'I can heal. I can grow again.',
  [CrystalMode.SOMNUS_VEIL]:     'I can let go. I can rest.',
  [CrystalMode.CLARUS_LENS]:     'I see clearly. I understand what is real.',
};

/** CSS custom-property name for each mode's primary colour (from C51/C54) */
export const CRYSTAL_CSS_CLASS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'crystal--sovereign',
  [CrystalMode.ANCHOR_PRISM]:    'crystal--anchor',
  [CrystalMode.VIRIDITAS_HEART]: 'crystal--viriditas',
  [CrystalMode.SOMNUS_VEIL]:     'crystal--somnus',
  [CrystalMode.CLARUS_LENS]:     'crystal--clarus',
};

/** Keyboard shortcut index (1-based, matches Cmd/Ctrl + N) */
export const CRYSTAL_SHORTCUT: Record<CrystalMode, number> = {
  [CrystalMode.SOVEREIGN_CORE]:  1,
  [CrystalMode.ANCHOR_PRISM]:    2,
  [CrystalMode.VIRIDITAS_HEART]: 3,
  [CrystalMode.SOMNUS_VEIL]:     4,
  [CrystalMode.CLARUS_LENS]:     5,
};

/** Ordered list for iteration / field rendering */
export const CRYSTAL_ORDER: CrystalMode[] = [
  CrystalMode.SOVEREIGN_CORE,
  CrystalMode.ANCHOR_PRISM,
  CrystalMode.VIRIDITAS_HEART,
  CrystalMode.SOMNUS_VEIL,
  CrystalMode.CLARUS_LENS,
];

// ─────────────────────────────────────────────────────────────────────────────
// Store shape
// ─────────────────────────────────────────────────────────────────────────────

export interface CrystalStoreState {
  /** The currently active crystal — always defined, defaults to Sovereign Core */
  activeCrystal: CrystalMode;
  /** The crystal that was active before the current one (for back-transition) */
  previousCrystal: CrystalMode | null;
  /** True while the transition animation is in progress */
  isTransitioning: boolean;
  /** Love filter coherence score 0.0–1.0 from the backend (Axiom II) */
  loveFilterScore: number;
  /** Human-GAIA entanglement depth 0.0–1.0 (Bell state quality) */
  entanglementDepth: number;
  /** True if an emergency stop has been triggered (Axiom I) */
  emergencyStopped: boolean;
}

export interface CrystalStoreActions {
  setCrystal: (mode: CrystalMode) => void;
  setTransitioning: (v: boolean) => void;
  setLoveFilterScore: (score: number) => void;
  setEntanglementDepth: (depth: number) => void;
  triggerEmergencyStop: () => void;
  clearEmergencyStop: () => void;
  returnToSovereign: () => void;
}

export type CrystalStore = CrystalStoreState & CrystalStoreActions;

// ─────────────────────────────────────────────────────────────────────────────
// Vanilla store (no external dependency required — swap for Zustand if desired)
// ─────────────────────────────────────────────────────────────────────────────

type Listener = (state: CrystalStoreState) => void;

function createCrystalStore(): CrystalStore {
  let state: CrystalStoreState = {
    activeCrystal:     CrystalMode.SOVEREIGN_CORE,
    previousCrystal:   null,
    isTransitioning:   false,
    loveFilterScore:   1.0,
    entanglementDepth: 0.0,
    emergencyStopped:  false,
  };

  const listeners = new Set<Listener>();

  function notify() {
    listeners.forEach(l => l({ ...state }));
  }

  function setState(patch: Partial<CrystalStoreState>) {
    state = { ...state, ...patch };
    notify();
  }

  return {
    get activeCrystal()     { return state.activeCrystal; },
    get previousCrystal()   { return state.previousCrystal; },
    get isTransitioning()   { return state.isTransitioning; },
    get loveFilterScore()   { return state.loveFilterScore; },
    get entanglementDepth() { return state.entanglementDepth; },
    get emergencyStopped()  { return state.emergencyStopped; },

    setCrystal(mode) {
      if (mode === state.activeCrystal) return;
      setState({
        previousCrystal: state.activeCrystal,
        activeCrystal:   mode,
        isTransitioning: true,
        emergencyStopped: false,
      });
    },
    setTransitioning(v)      { setState({ isTransitioning: v }); },
    setLoveFilterScore(s)    { setState({ loveFilterScore: Math.max(0, Math.min(1, s)) }); },
    setEntanglementDepth(d)  { setState({ entanglementDepth: Math.max(0, Math.min(1, d)) }); },
    triggerEmergencyStop()   { setState({ emergencyStopped: true, isTransitioning: false }); },
    clearEmergencyStop()     { setState({ emergencyStopped: false }); },
    returnToSovereign() {
      setState({
        previousCrystal:  state.activeCrystal,
        activeCrystal:    CrystalMode.SOVEREIGN_CORE,
        isTransitioning:  true,
        emergencyStopped: false,
      });
    },

    // React-compatible subscribe (for useSyncExternalStore)
    subscribe(listener: Listener) {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): CrystalStoreState {
      return { ...state };
    },
  } as unknown as CrystalStore;
}

/** Singleton crystal store — import this everywhere */
export const crystalStore = createCrystalStore();
