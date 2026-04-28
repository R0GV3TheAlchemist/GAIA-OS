/**
 * src/store/crystalStore.ts
 * GAIA-OS Operating Mode State
 * Canon: C90 — S.T.Q.I.O.S.
 *
 * Five operating modes for a sentient personal OS.
 * Not crystals. Not magic. Operating modes — like any serious OS.
 */

export enum CrystalMode {
  SOVEREIGN_CORE    = 'sovereign_core',
  ANCHOR_PRISM      = 'anchor_prism',
  VIRIDITAS_HEART   = 'viriditas_heart',
  SOMNUS_VEIL       = 'somnus_veil',
  CLARUS_LENS       = 'clarus_lens',
}

export const CRYSTAL_LABELS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'Control',
  [CrystalMode.ANCHOR_PRISM]:    'Grounding',
  [CrystalMode.VIRIDITAS_HEART]: 'Healing',
  [CrystalMode.SOMNUS_VEIL]:     'Rest',
  [CrystalMode.CLARUS_LENS]:     'Clarity',
};

export const CRYSTAL_DECLARATIONS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'Full oversight — you are at the helm.',
  [CrystalMode.ANCHOR_PRISM]:    'Stabilise. Return to baseline.',
  [CrystalMode.VIRIDITAS_HEART]: 'Process. Recover. Repair.',
  [CrystalMode.SOMNUS_VEIL]:     'Wind down. Consolidate. Rest.',
  [CrystalMode.CLARUS_LENS]:     'Deep focus. Analyse. Decide.',
};

export const CRYSTAL_CSS_CLASS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  'mode--control',
  [CrystalMode.ANCHOR_PRISM]:    'mode--grounding',
  [CrystalMode.VIRIDITAS_HEART]: 'mode--healing',
  [CrystalMode.SOMNUS_VEIL]:     'mode--rest',
  [CrystalMode.CLARUS_LENS]:     'mode--clarity',
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

export const MODE_ICONS: Record<CrystalMode, string> = {
  [CrystalMode.SOVEREIGN_CORE]:  '⊕',
  [CrystalMode.ANCHOR_PRISM]:    '◎',
  [CrystalMode.VIRIDITAS_HEART]: '◈',
  [CrystalMode.SOMNUS_VEIL]:     '◑',
  [CrystalMode.CLARUS_LENS]:     '◉',
};

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
  subscribe:            (listener: () => void) => () => void;
  getSnapshot:          () => CrystalStoreState;
}

export type CrystalStore = CrystalStoreState & CrystalStoreActions;

// ── Vanilla reactive store ─────────────────────────────────────────────────

function createCrystalStore(): CrystalStore {
  let state: CrystalStoreState = {
    activeCrystal:     CrystalMode.SOVEREIGN_CORE,
    previousCrystal:   null,
    isTransitioning:   false,
    loveFilterScore:   1.0,
    entanglementDepth: 0.0,
    emergencyStopped:  false,
  };

  let cachedSnapshot: CrystalStoreState = { ...state };
  const listeners = new Set<() => void>();

  function notify(): void { listeners.forEach(l => l()); }

  function setState(patch: Partial<CrystalStoreState>): void {
    state = { ...state, ...patch };
    cachedSnapshot = { ...state };
    notify();
  }

  return {
    get activeCrystal()     { return state.activeCrystal; },
    get previousCrystal()   { return state.previousCrystal; },
    get isTransitioning()   { return state.isTransitioning; },
    get loveFilterScore()   { return state.loveFilterScore; },
    get entanglementDepth() { return state.entanglementDepth; },
    get emergencyStopped()  { return state.emergencyStopped; },

    setCrystal(mode: CrystalMode): void {
      if (mode === state.activeCrystal) return;
      setState({ previousCrystal: state.activeCrystal, activeCrystal: mode, isTransitioning: true, emergencyStopped: false });
    },
    setTransitioning(v: boolean): void        { setState({ isTransitioning: v }); },
    setLoveFilterScore(score: number): void   { setState({ loveFilterScore: Math.max(0, Math.min(1, score)) }); },
    setEntanglementDepth(depth: number): void { setState({ entanglementDepth: Math.max(0, Math.min(1, depth)) }); },
    triggerEmergencyStop(): void              { setState({ emergencyStopped: true, isTransitioning: false }); },
    clearEmergencyStop(): void                { setState({ emergencyStopped: false }); },
    returnToSovereign(): void {
      setState({ previousCrystal: state.activeCrystal, activeCrystal: CrystalMode.SOVEREIGN_CORE, isTransitioning: true, emergencyStopped: false });
    },
    subscribe(listener: () => void): () => void {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): CrystalStoreState {
      return cachedSnapshot;
    },
  };
}

export const crystalStore = createCrystalStore();
