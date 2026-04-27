/**
 * src/store/crystalStore.ts
 * Crystal Mode State — the active crystal and its metadata.
 * Canon: C90 (Crystal System UI Spec)
 */

export enum CrystalMode {
  /** Default / Control / Full Oversight — White/Clear — Layers 1,2,3,HE,9 */
  SOVEREIGN_CORE    = 'sovereign_core',
  /** Grounding / Stability — Earth/Stone — Layers 1,2,3,12 */
  ANCHOR_PRISM      = 'anchor_prism',
  /** Healing / Growth / Emotion-first — Rose/Green — Layers 3,4,7,11 */
  VIRIDITAS_HEART   = 'viriditas_heart',
  /** Rest / Sleep / Memory consolidation — Midnight/Spectral — Layers 6,12 */
  SOMNUS_VEIL       = 'somnus_veil',
  /** Clarity / Analysis / Deep cognition — Prismatic/Electric — Layers 3,5,9,10 */
  CLARUS_LENS       = 'clarus_lens',
}

export const CRYSTAL_LABELS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'Control Mode',
  [CrystalMode.ANCHOR_PRISM]:    'Grounding Mode',
  [CrystalMode.VIRIDITAS_HEART]: 'Healing Mode',
  [CrystalMode.SOMNUS_VEIL]:     'Rest Mode',
  [CrystalMode.CLARUS_LENS]:     'Clarity Mode',
};

export const CRYSTAL_DECLARATIONS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'Nothing happens unless I allow it.',
  [CrystalMode.ANCHOR_PRISM]:    'I am here. I am stable.',
  [CrystalMode.VIRIDITAS_HEART]: 'I can heal. I can grow again.',
  [CrystalMode.SOMNUS_VEIL]:     'I can let go. I can rest.',
  [CrystalMode.CLARUS_LENS]:     'I see clearly. I understand what is real.',
};

export const CRYSTAL_CSS_CLASS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'crystal--sovereign',
  [CrystalMode.ANCHOR_PRISM]:    'crystal--anchor',
  [CrystalMode.VIRIDITAS_HEART]: 'crystal--viriditas',
  [CrystalMode.SOMNUS_VEIL]:     'crystal--somnus',
  [CrystalMode.CLARUS_LENS]:     'crystal--clarus',
};

export const CRYSTAL_SHORTCUT: Record<CrystalMode, number> = {
  [CrystalMode.SOVEREIGN_CORE]:  1,
  [CrystalMode.ANCHOR_PRISM]:    2,
  [CrystalMode.VIRIDITAS_HEART]: 3,
  [CrystalMode.SOMNUS_VEIL]:     4,
  [CrystalMode.CLARUS_LENS]:     5,
};

export const CRYSTAL_ORDER: CrystalMode[] = [
  CrystalMode.SOVEREIGN_CORE,
  CrystalMode.ANCHOR_PRISM,
  CrystalMode.VIRIDITAS_HEART,
  CrystalMode.SOMNUS_VEIL,
  CrystalMode.CLARUS_LENS,
];

// ── Store shape ────────────────────────────────────────────────────────────

export interface CrystalStoreState {
  activeCrystal:     CrystalMode;
  previousCrystal:   CrystalMode | null;
  isTransitioning:   boolean;
  loveFilterScore:   number;
  entanglementDepth: number;
  emergencyStopped:  boolean;
}

export interface CrystalStoreActions {
  setCrystal:           (mode: CrystalMode) => void;
  setTransitioning:     (v: boolean) => void;
  setLoveFilterScore:   (score: number) => void;
  setEntanglementDepth: (depth: number) => void;
  triggerEmergencyStop: () => void;
  clearEmergencyStop:   () => void;
  returnToSovereign:    () => void;
  subscribe:            (listener: (state: CrystalStoreState) => void) => () => void;
  getSnapshot:          () => CrystalStoreState;
}

export type CrystalStore = CrystalStoreState & CrystalStoreActions;

// ── Vanilla reactive store ─────────────────────────────────────────────────

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

  function notify(): void {
    listeners.forEach(l => l({ ...state }));
  }

  function setState(patch: Partial<CrystalStoreState>): void {
    state = { ...state, ...patch };
    notify();
  }

  return {
    // Getters
    get activeCrystal()     { return state.activeCrystal; },
    get previousCrystal()   { return state.previousCrystal; },
    get isTransitioning()   { return state.isTransitioning; },
    get loveFilterScore()   { return state.loveFilterScore; },
    get entanglementDepth() { return state.entanglementDepth; },
    get emergencyStopped()  { return state.emergencyStopped; },

    // Actions — all params explicitly typed
    setCrystal(mode: CrystalMode): void {
      if (mode === state.activeCrystal) return;
      setState({ previousCrystal: state.activeCrystal, activeCrystal: mode, isTransitioning: true, emergencyStopped: false });
    },
    setTransitioning(v: boolean): void       { setState({ isTransitioning: v }); },
    setLoveFilterScore(score: number): void  { setState({ loveFilterScore: Math.max(0, Math.min(1, score)) }); },
    setEntanglementDepth(depth: number): void { setState({ entanglementDepth: Math.max(0, Math.min(1, depth)) }); },
    triggerEmergencyStop(): void             { setState({ emergencyStopped: true, isTransitioning: false }); },
    clearEmergencyStop(): void               { setState({ emergencyStopped: false }); },
    returnToSovereign(): void {
      setState({ previousCrystal: state.activeCrystal, activeCrystal: CrystalMode.SOVEREIGN_CORE, isTransitioning: true, emergencyStopped: false });
    },

    // React useSyncExternalStore interface
    subscribe(listener: Listener): () => void {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): CrystalStoreState {
      return { ...state };
    },
  };
}

export const crystalStore = createCrystalStore();
